---
title: "Where the eight seconds were hiding"
date: 2026-08-05T09:21:00+08:00
description: "packing narrow QK into FP8 and hunting memory traffic: 1.297 to 1.167 minutes, 5.15% under the record's same-node baseline"
anchor: "modded-nanogpt #344, open"
anchor_url: "https://github.com/KellerJordan/modded-nanogpt/pull/344"
---

My first speedrun submission ran [1.297 minutes](/blog/96-is-enough/): reduced-width QK, packed
FP8 attention, 4.8% behind the record. The profile said the idea was right and the implementation
was leaving time on the table, because the packing and transpose paths were bandwidth-bound. If
the bottleneck is memory traffic, the remaining work is an inventory problem: find every byte
that moves without needing to.

Two weeks of that hunt took the run to **1.167 minutes**. The gap between the two numbers is just
under eight seconds, and every one of them came out of memory traffic rather than arithmetic.

## The inventory

Three finds, in descending order of what they paid.

**Weights were crossing the bus in the wrong precision.** The packed QKV projection ran in FP8,
but parts of the surrounding step still read and wrote higher-precision copies that existed only
as staging. Cutting the staging so tensors stay in FP8 across the whole packed path reduced
training memory traffic directly; that commit is the single largest chunk of the eight seconds.

**Transposed views were being rebuilt.** The packed layout needs both row-major and transposed
views of the weight bank, forward and backward. Rebuilding the transpose per step is quadratic
politeness: cache both views once, invalidate on update, and the transpose cost drops out of the
steady state.

**The layout kernels were leaving coalescing on the floor.** The custom Triton kernels around the
packed GEMM (norm, RoPE, backward shuffles) were correct but not tight against the 320-column
packed shape. Retuning block sizes for the actual layout, rather than the 384-column shape the
defaults assumed, recovered the rest.

## Measuring honestly

Speedrun numbers have a methodology problem: nodes differ, and a record set on one machine is not
automatically comparable to a run on another. So the PR carries a same-node baseline: the current
record configuration, re-run on the same 8xH100 box, same session, gave 1.2304 minutes. Against
that baseline my 1.167 is **5.15% faster**.

| run | minutes | vs same-node baseline |
|---|---|---|
| record config, re-run same node | 1.2304 | 0 |
| first submission | 1.297 | +5.4% |
| current submission | 1.167 | **-5.15%** |

The PR is [open](https://github.com/KellerJordan/modded-nanogpt/pull/344) with the H100 logs and
an H200 evidence run attached. Until it merges, the honest sentence is: an open submission, under
the record's same-node baseline. The leaderboard decides the rest.

## What generalizes

The eight seconds were never in one place. They were spread across staging copies, rebuilt views,
and mistuned block sizes, each individually too small to show up as a line in a profile summary,
all of them the same species: **bytes moving that carried no new information**. The first PR
changed the architecture; this one changed nothing conceptual at all. There was a day where I
stared at the trace convinced the idea was exhausted, and the idea was fine. The implementation
was the idea, the second time.

That is the actual lesson I keep relearning about GPUs: after the first good idea, the follow-up
gains are almost always in the traffic, and the traffic only shows itself when you go byte
counting.
