---
title: "My nanoGPT record is accepted"
date: 2026-10-16
description: "PR #344 is merged: 68.0 seconds on 8xH100, entry #90 in the nanoGPT world record history."
figures: 1
anchor: "modded-nanogpt #344, merged · record #90"
anchor_url: "https://github.com/KellerJordan/modded-nanogpt/pull/344"
---

My nanoGPT PR [#344](https://github.com/KellerJordan/modded-nanogpt/pull/344) merged on
18 September. It is now [entry #90 in the world record history](https://github.com/KellerJordan/modded-nanogpt#world-record-history),
listed at **1.13 minutes on 8xH100**. The accepted time was **68.0 seconds**.

The first version I [wrote about in July](/blog/96-is-enough/) took 1.297 minutes and was still
behind the record. I kept working on the packing and memory traffic, rebased onto the newer
training code, and [submitted another set of runs](/blog/eight-seconds/) in August. That is
the version that was eventually merged, with a shorter schedule after review.

## What went in

The idea was to make Q and K narrower while leaving V alone. Q and K determine where attention
goes; V carries the values. In this model I could reduce Q/K head width from 128 to 96, keep
V at 128, and still reach the required loss.

The projection width drops from `128 + 128 + 128 = 384` to `96 + 96 + 128 = 320`. I packed
those projections into FP8 and added Triton kernels for normalization, RoPE, and the layout
work around them. The later revision also moved the MLP backward work into FP8.

There were smaller savings around that. The row-major and transposed FP8 weight layouts now
come from one weight read per update. For squared ReLU, the stored output lets us recover the
positive pre-activation with a square root, so there is no need to save another activation
tensor for backward. Those details are in the PR along with the code and logs.

## The final runs

I ran the candidate and baseline back to back on the same 8xH100 node. Times and validation
losses below are means:

| run | steps | seconds | loss |
|---|---|---|---|
| baseline, two runs | 1,285 | 73.897 | 3.276600 |
| candidate, four seeds | 1,315 | 70.094 | 3.274725 |

That is **5.15% less training time** on the same hardware. The candidate's loss passed the
track's significance requirement, with a one-sided p-value of 0.001585 against 3.28.

There is a small distinction here that I got muddled in the August post. The raw candidate
mean was 70.094 seconds, or 1.1682 minutes. Applying the same-node ratio to the published
1.23-minute record gives 1.1667 minutes. That normalized value is the 1.167 in the PR title.
I have corrected the older post's table.

Before merging, ClassicLarry [removed twenty more steps and revalidated](https://github.com/KellerJordan/modded-nanogpt/pull/344#issuecomment-5725127743).
The three losses at **1,295 steps** were 3.2769, 3.2794, and 3.2785, all below the 3.28 target.
The accepted record came to 68.0 seconds.

{{< fig src="fig1.mp4" num="1" alt="The final 45 submitted steps: retain 25 and remove the last 20, reducing 1315 total steps to 1295. The maintainer's three validation losses remain below 3.28."
    caption="the last 45 steps of the submitted schedule; twenty were removed before acceptance and the shorter run was checked again"
    scene="figures/the-last-twenty-steps/scene.py" >}}

That 68.0 is the maintainer's accepted time, recorded as `73.8 - 5.8` in the merge comment.
It comes from a separate comparison. You cannot get it by subtracting twenty estimated step
times from my 70.094-second mean.

I had been concentrating on making each step faster. The review also checked whether all of
the steps were needed. In this case there was enough room below the loss threshold to remove
some. I would check the schedule earlier next time.

The board has moved on again since this result. Mine remains record #90, dated 3 August for
the submitted evidence and merged on 18 September. It is good to finally update the earlier
posts from “submitted” to “accepted.”

The [world record table](https://github.com/KellerJordan/modded-nanogpt#world-record-history),
[accepted PR](https://github.com/KellerJordan/modded-nanogpt/pull/344), and
[run logs and statistics script](https://github.com/KellerJordan/modded-nanogpt/tree/master/records/track_1_short/2026-08-03_FP8MLPBackwardPackedQKV)
are all public.
