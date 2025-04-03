---
title: "The KV cache is the product"
date: 2025-04-03T08:47:00+08:00
description: "serving economics from first principles: bytes per token, GQA, paged allocation, and why batch size is set by memory rather than compute"
---

If you want to understand LLM serving, ignore the model for a minute and price the cache.

Every generated token attends over every previous token, and recomputing all of that per step
would be quadratic misery, so inference stores each layer's keys and values. That store is the KV
cache, and its arithmetic runs the business:

{{< mathline >}}bytes per token = 2 · layers · kv_heads · head_dim · dtype_bytes{{< /mathline >}}

Concrete: a 7B-class model with 32 layers, 8 KV heads of width 128, fp16, is 128 KB per token
after grouped-query attention, roughly 0.5 GB per 4k-token sequence. An 80 GB card holding a 14 GB
model has room for maybe a hundred concurrent 4k sequences before the cache, not the weights,
is what evicts you.

## Why batch size is a memory number

Decode is memory-bandwidth-bound: each step reads the whole model plus the growing cache to
produce one token per sequence. GPUs earn their keep on batched matmuls, so throughput serving
wants the batch as large as possible, and the cache is what caps it. That single fact explains
most serving architecture of the past two years:

- **GQA** shrinks kv_heads, cutting cache size by the sharing factor, trading a little quality
  for a lot of concurrency. It saves memory and bandwidth, not FLOPs.
- **Paged allocation** (the vLLM insight) stops reserving max-context contiguous buffers per
  sequence. Cache lives in fixed-size pages with a per-sequence page table; fragmentation
  collapses and utilization jumps. It is virtual memory, rediscovered where it was needed.
- **Prefix sharing** lets sequences with a common prompt share pages copy-on-write, which is why
  system prompts and few-shot prefixes are nearly free at high concurrency.
- **Quantized cache** (fp8 or int8 K/V) halves the bytes again, and the accuracy question is
  empirical per model.

## The mental model

Prefill is compute-bound (one big parallel pass over the prompt), decode is memory-bound (many
small passes), and the cache is the working set that decides how many decodes ride each weight
read. When someone quotes tokens per second, ask at what batch, and when someone quotes batch,
ask how big the cache was. The cache is the product; the model is just what fills it.
