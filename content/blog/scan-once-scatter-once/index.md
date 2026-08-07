---
title: "Scan once, scatter once"
date: 2026-08-07T21:55:00+08:00
description: "cutting route reads 48x in the scheduler of Cursor's MoE megakernel, and the third sighting of the same bug"
figures: 1
anchor: "mixture-of-kittens #10, open"
anchor_url: "https://github.com/cursor/mixture-of-kittens/pull/10"
---

Cursor open-sourced [Mixture-of-Kittens](https://github.com/cursor/mixture-of-kittens) last week:
a fully deterministic MoE training megakernel for NVL72 racks, built on ThunderKittens (vendored
as a submodule), powering the production training of Composer. The design is worth a paragraph.
Instead of separate compute and communication kernels stitched together by launch boundaries,
MoK splits each GPU's SMs into a compute group running the expert FFNs and a communication group
moving tokens between the rack's 72 GPUs over NVLink, the two coordinating through local
counters. Macrobatches cycle through a fixed ring buffer, so the GPU never waits on a CPU.
Dispatch pulls and combine pushes, each direction chosen for measured reasons. And determinism
is a feature with a customer: the floating-point order is fixed, so identical inputs produce
bitwise-identical outputs, which is what makes ablations and on-policy RL post-training
trustworthy. Cursor reports MoE layers ate more than half of end-to-end training time before
this, and 1.41x end-to-end after.

I went reading with a specific smell in mind. My [Cosmos routing patch](/blog/move-the-index/)
came from noticing MoE dispatch work scaling with a dimension it had no business scaling with.
Once you have hit that pattern, you check for it everywhere expert routing appears. The place it
appears in MoK is the schedule kernel: the stage that turns router projections into the dispatch
table telling every peer which tokens to pull for which expert, entirely on device, at under 3%
of MoK's runtime. Small, serial, and exactly the kind of code where a stray scaling term can
hide.

The scheduler assigns a block to each expert and peer pair,
and each of those blocks scans the peer's full route list twice. Every route belongs to exactly
one expert, but every expert's block reads all of them, so scheduling work grows with the
*global* expert count:

{{< mathline >}}route reads &nbsp;=&nbsp; P·R + 2·E·R, &nbsp;for E global experts, P peers, R routes per peer{{< /mathline >}}

That `E` should not be there. At 384 experts, EP8, 7,168 tokens, top-8 routing, it prices out to
**44,498,944 route reads** for work that a single pass over each peer's routes could establish.

{{< fig src="fig1.mp4" num="1" alt="every expert block scanning all routes twice, versus a count, prefix, scatter pipeline touching each route once per pass"
    caption="the E in the read count is the bug: every expert's block rescans routes that belong to exactly one expert"
    scene="figures/scan-once-scatter-once/scene.py" >}}

## The fix is a counting sort

The [replacement scheduler](https://github.com/cursor/mixture-of-kittens/pull/10) has four
explicit stages, which anyone who has written a counting sort will recognize:

1. **Count** routes per local expert, peer, and logical scheduler thread.
2. **Prefix** the per-thread counts to recover the existing thread-major offsets.
3. **Pad** each expert segment and compute its base row.
4. **Scatter** each route once, using the existing peer round-robin layout.

Four 256-thread blocks cover each peer's fixed 1,024 logical scheduler threads. Route reads fall
to `2·P·R`: **917,504** for the case above, a 48x cut, at the cost of `E·1024` int32 counters
(393,216 for 384 experts) and their prefix scan.

The part that took the care is what does *not* change. MoK's whole product is determinism, so
the new scheduler reproduces the old one's output ordering and 256-token expert padding exactly.
The validation reflects that: exact GPU output match against the previous scheduler on 16
realistic and adversarial cases, and exact CPU reference match on 945 randomized ones. Exact,
not approximately; a scheduler that reorders anything is a different scheduler.

## Measured, including where it loses

An isolated scheduler benchmark on one H200 at EP8 and 7,168 local tokens:

| config | before | after | speedup |
|---|---|---|---|
| Qwen3.5-397B-A17B | 179.3 us | 99.3 us | **1.81x** |
| Kimi K2.7 Code | 116.7 us | 81.0 us | 1.44x |
| DeepSeek-V4-Pro | 91.6 us | 68.2 us | 1.34x |
| GLM-5.2 | 85.9 us | 72.8 us | 1.18x |

The speedup tracks the expert count, which is exactly what removing an `E` term predicts.

For scale: the scheduler is under 3% of MoK's runtime, so nobody's training run gets 1.8x
faster from this. It trims a thin slice, and thin slices are still worth trimming when the fix
also simplifies the code it lives in.

And where it does not win: at 384 experts with only 512 local tokens, EP8 through EP64 is a wash
(0.97x to 1.03x), and **EP4 regresses to 0.83x**, since with few peers and few routes the old
rescans were cheap and the counting machinery is pure overhead. Small batches per peer are not
where this scheduler spends its time, but the number belongs in the record anyway.

One more honest boundary from the PR: MoK targets Blackwell (SM100/SM103), and the builds pass
clean on both, but the machine I have is an H200, so runtime validation ran on an isolated SM90
build of the scheduler. The target-hardware performance run is still owed.

## Third sighting

This is the third time the same bug has written a patch for me. In Megatron-LM's MoE paths it
was oversized intermediates. In [Cosmos](/blog/move-the-index/) it was indices hauled at the
width of the hidden dimension. Here it is a scheduler rescanning routes at the width of the
global expert count. Different codebases, one principle: **work should scale with what you own,
never with what everyone else has.** Each route has one expert; touch it like it does.
