---
title: "Blockwise parallel generation"
date: 2025-10-08T20:11:00+08:00
description: "diffusion language models trade the autoregressive bottleneck for a denoising one. notes from building an overlay"
---

Notes from a project I spent the autumn on: a diffusion language model overlay for an existing
autoregressive training stack, with blockwise parallel generation and a corruption curriculum in
the style of the recent diffusion-LM wave.

## The trade at the core

Autoregressive decoding produces one token per forward pass; the sequential dependency is the
product. Diffusion LMs instead corrupt whole spans and learn to denoise them, so generation
proposes an entire block per pass and refines it over a handful of iterations. The bottleneck
moves: latency stops scaling with tokens and starts scaling with denoising rounds times block
size. Whether that is a win depends entirely on how many rounds you need, which depends on how
the corruption schedule was trained.

## What the curriculum does

Training samples a corruption level per block: sometimes light (a few masked tokens, easy local
repair) and sometimes heavy (most of the block gone, the model must plan structure). The
scheduling of that distribution is the whole game. Too much light corruption and the model only
learns cleanup, generating incoherent long spans. Too much heavy and it wastes capacity learning
to write from nothing while inference mostly asks for refinement. The curricula that worked
shifted mass from heavy to light as training progressed, matching what inference actually asks
of each round: early rounds face heavy corruption, late rounds face nearly clean text.

## What surprised me

- **Infrastructure reuse is high.** The transformer trunk, parallelism, and optimizer state care
  nothing about the objective. The changes concentrate in the data pipeline, the attention mask
  (bidirectional within a block), and the sampler.
- **Evaluation is the hard part.** Perplexity of a denoiser is not comparable to an
  autoregressive model's, so you are forced onto downstream tasks and generation quality early,
  and those are noisy signals to steer training by.
- **The failure mode is confident patchwork**: blocks that are locally fluent and globally
  disconnected, because nothing in the objective ties a block's plan to its neighbors beyond the
  visible context. The fixes people use, block overlap and re-noising boundaries, are tape over
  a real seam.

The line I keep for this class of model: parallel generation is not faster autoregression, it is
a different animal that happens to share weights, and it needs its own instincts.
