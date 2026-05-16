---
title: "Three small patches, three training-system lessons"
date: 2026-05-16T10:42:00+08:00
description: "a hook, a metadata dialect, and test coverage: what Megatron-LM taught me about extension seams"
anchor: "Megatron-LM #4596 #4664 #4686"
anchor_url: "https://github.com/NVIDIA/Megatron-LM/pulls?q=is%3Apr+author%3AGlitchfix"
---

Three of my patches merged into Megatron-LM this month. None is large. Each taught me something
about how training systems should be built, which makes them worth writing down together.

## A hook beats a monkey-patch ([#4686](https://github.com/NVIDIA/Megatron-LM/pull/4686))

RL post-training needs two things the default GPT forward throws away: log-probabilities of
specific chosen tokens, and hidden states for a value head. Materializing full vocab logits to get
them is often the largest tensor in the step; a 32k vocab times a long sequence in fp32 can top
everything else in memory. So downstream RL callers were monkey-patching `GPTModel.forward`,
which breaks on every refactor and silently misses the pipeline schedule plan, which has its own
postprocess path.

The patch adds a keyword-only `output_postprocess_fn` wired through both paths. The library stays
ignorant of what the caller wants; that is what makes it acceptable upstream.

```python
def rl_postprocess(hidden, output_layer):
    logits_chosen = output_layer.gather_for(hidden, chosen_tokens)  # never the full vocab
    return logprob(logits_chosen), value_head(hidden)
```

The lesson: expose the seam, never the objective. A hook present in one code path and absent from
its twin is worse than no hook at all.

## Metadata dialects rot silently ([#4664](https://github.com/NVIDIA/Megatron-LM/pull/4664))

Megatron parameters can declare their sharding two ways: the legacy attributes
(`tensor_model_parallel`, `partition_dim`) and the DTensor annotation. The FSDP DTensor
checkpoint writer understood only the new dialect. GDN fused tensors, whose copied meta tensors
carry only the legacy attributes, were invisible to it, and saving failed.

The fix reads the old dialect as a fallback. The scarier version of this bug does not error: it
writes a sharded tensor as replicated, loads without complaint, and is simply wrong. The test to
have is a round-trip that saves at one parallel degree, loads at another, and asserts
bit-identical reassembly.

The lesson: metadata that travels separately from the data will eventually disagree with it.

## Coverage is a contribution ([#4596](https://github.com/NVIDIA/Megatron-LM/pull/4596))

The DSv4 hybrid layers combine CSA and HCA attention, hash-based MoE routing, and clamped SwiGLU.
No integration test exercised the combination. Mine does, 170 lines, one file. It is not a
headline and it found real seams. Test-only PRs are underrated as a way to learn a codebase:
reviewers approve them readily, and writing one forces you to understand every interacting piece.
