---
title: "What FlashAttention actually buys"
date: 2025-09-09T21:33:00+08:00
description: "not fewer FLOPs. the same quadratic arithmetic with linear memory traffic, and why the distinction decides everything downstream"
---

The most common wrong sentence about FlashAttention is that it makes attention *compute* faster.
It does not touch the arithmetic: every QK^T score is still computed, the FLOPs are still O(T²).
What changes is where the intermediate lives.

## The actual problem

Naive attention materializes the T-by-T score matrix in HBM: write O(T²) values, read them back
for softmax, write again, read again for the value product. At long context the kernel is not
compute-bound at all; it is a memory-traffic machine that happens to do math between transfers.

FlashAttention tiles the computation so each block of scores lives and dies in on-chip SRAM: the
online softmax trick keeps running row maxima and sums so the normalization is exact without ever
holding the full row. HBM traffic drops from O(T²) to O(T), and the result is bit-for-bit exact
attention, not an approximation. That exactness is why adoption was instant: there is no
quality-speed tradeoff to argue about.

## Why the distinction matters downstream

Once you see the memory-bound framing, several things follow:

- **Speedup grows with context length**, because the eliminated traffic is the quadratic term.
  Short sequences barely notice; long-context models are built on it.
- **The backward pass recomputes rather than stores.** Keeping the score matrix for backward
  would reintroduce the O(T²) memory, so FlashAttention recomputes tiles during backward: spend
  FLOPs, save bytes. The same trade as activation checkpointing, chosen for the same reason.
- **It does nothing for the KV cache.** Decode-time memory pressure comes from storing K and V
  for every past token; that is a different budget, attacked by GQA and paged allocation, and no
  amount of attention tiling changes it.

## The transferable lesson

Count bytes before you count FLOPs. On modern GPUs the arithmetic is rarely the wall; the wall is
HBM, and the biggest wins in the last few years of systems ML, this kernel included, are
restructurings that keep the same math while refusing to write the intermediate down.
