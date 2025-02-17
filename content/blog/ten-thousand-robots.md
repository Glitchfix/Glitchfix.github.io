---
title: "Ten thousand robots per GPU"
date: 2025-02-17T22:05:00+08:00
description: "what vectorized environments and tiled rendering actually buy in policy training"
---

Robot policy training spent years bottlenecked on a dumb thing: the simulator ran on CPU, the
policy on GPU, and the product of that marriage was a PCIe bus full of tiny tensors. Notes on
what changes when the whole loop lives on one device, from working around GPU-resident simulation
this winter.

## The three multipliers

**Vectorized environments.** Simulate thousands of robots as one batched physics step: states are
a single tensor of shape (N, ...), the policy inference is one batched forward, and PPO's rollout
collection becomes dense linear algebra instead of a Python loop. The win is not that one robot
steps faster; it is that ten thousand step *together* at the cost of a few.

**Tiled rendering.** Vision policies need pixels, and N little cameras used to mean N draw calls.
Tiled rendering packs all environments into one big framebuffer, renders once, and slices the
result back per environment. Camera-based training stops being a special expensive case.

**Staying resident.** The quiet multiplier: observations, actions, rewards, and resets never
leave the device. The moment any of them round-trips to CPU per step, Amdahl arrives with the
bill; keeping reset logic on-device (masked writes over the state tensor rather than per-env
Python) matters as much as the physics batch.

## What it costs

Everything must be tensorized, including the awkward parts: episode resets with randomized
initial states, curriculum switching, domain randomization of masses and frictions. Each becomes
a masked batched operation, and debugging one misbehaving environment inside a 10,000-wide batch
is its own skill; you learn to write invariant checks that reduce over the batch and to dump the
offending row when they trip.

The payoff is the training loop stops being an orchestration problem and becomes a single
GPU-resident program: sample efficiency stays whatever your algorithm gives you, but wall-clock
per policy iteration drops by orders of magnitude, and that changes what experiments feel
affordable. Iteration speed is the real product of the whole exercise.
