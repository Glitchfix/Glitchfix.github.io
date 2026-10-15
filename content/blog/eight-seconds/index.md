---
title: "Where the eight seconds were hiding"
date: 2026-08-05T09:21:00+08:00
lastmod: 2026-10-16
description: "packing narrow QK into FP8 and hunting memory traffic: 70.094 seconds on 8xH100, 5.15% under the record's same-node baseline"
anchor: "modded-nanogpt #344, merged"
anchor_url: "https://github.com/KellerJordan/modded-nanogpt/pull/344"
---

*October update: this submission was [accepted as record #90](/blog/the-last-twenty-steps/)
on 18 September, at 68.0 seconds after the maintainer shortened the schedule. The measurements
below describe the submitted configuration; the follow-up explains the accepted one.*

My first speedrun submission ran [1.297 minutes](/blog/96-is-enough/): reduced-width QK, packed
FP8 attention, 5.4% behind the published record. The profile said the idea was right and the implementation
was leaving time on the table, because the packing and transpose paths were bandwidth-bound. If
the bottleneck is memory traffic, the remaining work is an inventory problem: find every byte
that moves without needing to.

The revised submission averaged **70.094 seconds**, or **1.1682 minutes**. Its normalized
record time was **1.167 minutes**. The earlier run averaged 77.812 seconds, nearly eight seconds
longer, but also used 1,425 steps against the revised 1,315. The rebase picked up a shorter
schedule; that entire gap cannot be assigned to kernel changes. The same-node comparison below
is the measurement that isolates the submitted configuration's advantage over its baseline.

## The inventory

Three places where the revised implementation removed traffic.

**FP8 stopped too early.** The packed QKV projection ran in FP8, but the MLP backward path
still had work to move into FP8. Extending it across all four MLP GEMMs and both projections
reduced traffic around the training step.

**Weight layouts were reading the same source twice.** The packed path needs row-major and
transposed FP8 views of the weight bank. Emit both from one weight read per optimizer update,
then reuse them in forward and backward. Updating the weights still requires refreshing the
layouts; the redundant read is what disappears.

**Intermediates carried recoverable information.** The squared-ReLU output already contains
enough information to reconstruct the positive pre-activation for backward. Dropping the saved
copy removes a write and a later read. The revised packing paths also avoid materialized
concatenations and full-size absolute-value temporaries, and keep QK-norm and RoPE lane swaps
in registers.

## Measuring honestly

Speedrun numbers have a methodology problem: nodes differ, and a record set on one machine is not
automatically comparable to a run on another. So the PR carries a same-node baseline: the current
record configuration, re-run on the same 8xH100 box, same session, averaged **73.897 seconds**.
The candidate averaged **70.094 seconds**, a **5.15% reduction in training time**.

| run | steps | measured seconds | vs same-node baseline |
|---|---|---|---|
| record config, two runs on the same node | 1,285 | 73.897 | 0 |
| submitted candidate, four seeds | 1,315 | 70.094 | **-5.15%** |

Applying that ratio to the published 1.23-minute record gives **1.1667 minutes**, the normalized
time in the PR title. It is distinct from the raw 1.1682-minute candidate mean. Mean validation
loss was 3.274725 across four seeds, with a one-sided p-value of 0.001585 against 3.28.

The [PR](https://github.com/KellerJordan/modded-nanogpt/pull/344) carries the H100 logs and
same-node baseline. At the time of this post it was an open submission below that baseline;
the [acceptance follow-up](/blog/the-last-twenty-steps/) records what happened next.

## What generalizes

The follow-up gains came from several places, and the schedule accounts for part of the total
change. The systems work kept finding the same species of waste: **bytes moving that carried no
new information**. The first revision changed the attention geometry; the next made that
geometry cheaper to execute.

That is the actual lesson I keep relearning about GPUs: after the first good idea, the follow-up
gains are almost always in the traffic, and the traffic only shows itself when you go byte
counting.
