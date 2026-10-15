---
title: "96 is enough: shrinking attention's routing vectors"
date: 2026-07-24T09:38:00+08:00
lastmod: 2026-10-16
description: "Q and K decide where to look; V carries what's found. They don't need the same width."
figures: 1
anchor: "modded-nanogpt #344, merged"
anchor_url: "https://github.com/KellerJordan/modded-nanogpt/pull/344"
---

*October update: the later revision of this submission was
[accepted as record #90](/blog/the-last-twenty-steps/) on 18 September, at 68.0 seconds.
This post describes the original July experiment.*

The [modded-nanogpt speedrun](https://github.com/KellerJordan/modded-nanogpt) is the best
benchmark culture in open ML: one task, one target loss, wall-clock time on 8xH100, and every
trick on the leaderboard is reproducible. I wanted on the board, and I had one idea I kept coming
back to.

Attention computes `softmax(QK^T / sqrt(d)) V`. Look at what each matrix is *for*. Q and K exist
only to produce a scalar score per token pair: they are routing vectors, deciding where to look.
V is the payload, the content that actually flows to the residual stream. There is no law that
the routing geometry needs the same dimensionality as the payload.

And in this codebase the routing vectors are normalized before use, so only their direction
carries information. A unit vector in 96 dimensions is not obviously a worse router than one in
128. The hyperspherical view in [nGPT](https://arxiv.org/abs/2410.01131) is what pushed me to
try it; no code from anywhere was copied, which the PR states plainly.

## The change

Q and K head width drops from 128 to 96. V stays at 128, and so does the residual stream, so
model capacity where it matters is untouched.

{{< fig src="fig1.mp4" num="1" alt="Q K V widths: 128/128/128 narrowing to 96/96/128, then packing into one projection"
    caption="routing narrows, payload stays wide; then all three projections pack into one FP8 GEMM"
    scene="figures/96-is-enough/scene.py" >}}

That alone saves 25% of the Q and K projection work, and 16.7% of the whole QKV projection width
(384 columns down to 320). But the second half of the change matters as much: the three
projections pack into a single FP8 GEMM, one kernel launch and one weight read instead of three.

```python
d_model, d_v, d_qk = 128, 128, 96

W_packed = concat([W_q, W_k, W_v], dim=out)   # out = 96 + 96 + 128 = 320
qkv = fp8_matmul(x, W_packed)                 # one launch, one weight read
q, k, v = split(qkv, [d_qk, d_qk, d_v])

q, k = rms_norm(q), rms_norm(k)               # direction is all that survives
q, k = rope(q), rope(k)
scores = q @ k.transpose(-2, -1) / sqrt(d_qk) # a scalar per pair, whatever d_qk is
```

The fiddly part is everything around that GEMM: the packed layout needs its own Triton kernels
for normalization, RoPE, and the backward pass, and the transposed weight views have to be cached
rather than rebuilt per step. None of it is deep; all of it is where the time went.

## Not the same as GQA

Grouped-query attention reduces the *number* of K and V heads to shrink the KV cache. This
change reduces the *width* of each Q and K head and leaves head count alone. They are orthogonal
axes and they compose: one attacks cache memory, the other attacks projection compute and
bandwidth.

## Where it landed

My submission ran **1.297 minutes** on the reference 8xH100 node. The record had just moved to
1.23 four days earlier, so this first cut landed 5.4% behind the front of the board: a
submission, not a crown. The PR is
[#344](https://github.com/KellerJordan/modded-nanogpt/pull/344), with full training logs
attached as evidence, per speedrun rules.

What I know from the profile: the packing and transpose paths are bandwidth-bound, so the benefit
should grow on parts with faster memory. On an 8xH200 box the same change measured a noticeably
larger gain than on H100, which supports the theory and points at where the remaining time is
hiding. That hunt is still on.
