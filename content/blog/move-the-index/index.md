---
title: "Move the index, not the data"
date: 2026-06-10T11:23:00+08:00
description: "a 3.53x MoE routing speedup, and the general principle hiding under it"
figures: 1
anchor: "cosmos-framework #20, merged"
anchor_url: "https://github.com/NVIDIA/cosmos-framework/pull/20"
---

Mixture-of-experts routing has a step nobody looks at. After the router picks *top-k* experts per
token, the tokens have to physically move to their experts and back. The reference implementation
in the Qwen3-VL MoE path did this with `gather` and `scatter_add_`, and to feed those ops it first
expanded the index tensor across the hidden dimension.

Stop and price that expansion.

{{< mathline >}}T × k indices &nbsp;→&nbsp; (T × k) × H int64 &nbsp;=&nbsp; **1.07 GB** at T=4096, k=8, H=4096{{< /mathline >}}

{{< fig src="fig1.mp4" num="1" alt="index tensor expanding across the hidden dimension, then shrinking to a 1-D vector"
    caption="the index tensor before and after: same information, 4096x the bytes"
    scene="figures/move-the-index/scene.py" >}}

A gigabyte of pure index traffic, twice per layer (once to route, once to combine), carrying no
information that the original quarter-megabyte vector did not already carry. Every entry is
repeated H times so that `gather` can consume it.

The fix is one line, twice: `index_select` and `index_add_` take the 1-D index directly and
broadcast internally.

```python
# before: haul (T·k, H) int64 through memory, twice
idx = topk_idx.view(-1, 1).expand(-1, H)
x_routed = x.gather(0, idx)
out.scatter_add_(0, idx, y)

# after: the index stays 1-D; the op broadcasts
idx = topk_idx.view(-1)
x_routed = x.index_select(0, idx)
out.index_add_(0, idx, y)
```

Same arithmetic. The results match the reference to a relative difference of 0.005, which is
floating-point accumulation order, not a change of algorithm: `index_add_` and `scatter_add_` do
not sum in the same sequence. Being able to say *why* the diff is nonzero is most of the review
conversation.

Measured on an RTX 6000 Ada in BF16, the focused routing harness drops from **13.81 ms to
3.92 ms, a 3.53x speedup**. The change merged as
[cosmos-framework #20](https://github.com/NVIDIA/cosmos-framework/pull/20).

## Why nobody noticed

The waste scales linearly in both *top-k* and hidden size, so it is invisible at toy
configurations and dominant at production ones. Pricing the same expansion across sizes:

| T | k | H | expanded idx | 1-D idx |
|---|---|---|---|---|
| 1024 | 2 | 1024 | 16.8 MB | 16 KB |
| 4096 | 8 | 4096 | 1.07 GB | 262 KB |
| 8192 | 8 | 8192 | 4.29 GB | 524 KB |

At the top row nobody would ever profile this. At the middle row it quietly dominates the routing
step. The expansion also lands awkwardly on the memory system: the same few integers repeated H
times defeat the point of a wide load, so achieved bandwidth is worse than the byte count alone
suggests.

## The general principle

**Move indices at the width of the index, never at the width of the data.** The reduction factor
is exactly H. Anywhere a gather touches a wide tensor, check what shape the index had when it
entered the op: embedding lookups, routing tables, token dropping, KV-cache page tables. The
pattern repeats, and so does the fix.
