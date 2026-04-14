---
title: "Making a video model fit: distill, cache, offload"
date: 2026-04-14T18:36:00+08:00
description: "getting a 14B image-to-video pipeline through a 48 GB card, and what each trick trades away"
---

I spent a stretch this year making a 14B-parameter image-to-video diffusion pipeline run on
hardware it had no business fitting on: a 48 GB workstation card that peaked at 41 to 44 GB, which
leaves margin thin enough that one careless buffer ends the run. Notes on the three levers that
made it work, and the price of each.

## Step distillation

A diffusion sampler that needs 50 denoising steps is 50 forward passes per clip. Distillation
trains a student to take the teacher's many small denoising steps as fewer large ones; 50 to 4 is
a 12.5x cut in sampler cost, and it is the single biggest lever available. The price: it is a
different checkpoint, not a runtime flag. Fidelity loss is real and task-dependent, and you
cannot dial it back at inference time.

## Timestep caching

Adjacent denoising steps produce similar updates. TeaCache-style caching estimates, from the
change in the input, whether the model's output would meaningfully differ from the previous step;
when the estimate says no, reuse the previous update and skip the forward entirely.

```python
acc += relative_change(x, prev_in)
if acc < threshold:
    x = x + prev_update          # skip the model call
    continue
```

The threshold is an explicit fidelity dial, which makes this the most honest of the three tricks:
you can see exactly what you are trading. It composes with distillation, though with only 4 steps
left the redundancy between steps shrinks, and so does the win.

## Activation offload

VRAM that does not fit can spill: pinned host memory takes activations during the forward pass
and returns them for backward or reuse, trading PCIe bandwidth for residency. On a 4 to 7 GB
margin this is what turned OOM crashes into slow completions. The price is wall-clock, and the
implementation detail that matters is *pinned* memory; pageable host buffers stall the copy
engine and the slowdown stops being graceful.

## The accounting

Every one of these is a trade against the same budget: distillation spends fidelity once at
training time, caching spends it tunably at inference, offload spends latency to buy memory.
Nothing is free. The job is knowing the exchange rates on your workload before you pay.
