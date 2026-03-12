---
title: "Contact lists that remember"
date: 2026-03-12T23:04:00+08:00
description: "bonded-particle DEM needs pair state that survives the substep. I proposed it upstream; it wasn't taken. The idea still matters."
anchor: "warp PR #1271, closed"
anchor_url: "https://github.com/NVIDIA/warp/pull/1271"
---

I proposed a persistent contact list for Warp: a data structure for bonded-particle DEM where
contacts are built once and updated incrementally, with per-contact state travelling along. The
PR was
[not taken upstream](https://github.com/NVIDIA/warp/pull/1271), and that is fine; this post is
about why the idea matters anyway, and what I would do differently.

## The problem

The standard particle-simulation loop rebuilds its neighbor set every substep from a hash grid.
For plain repulsive contact that is correct and simple: pairs need no memory, so recomputing them
loses nothing.

Bonded materials break this. A bond has a rest length set at formation. Strain is displacement
relative to *that remembered length*, and a bond that exceeds its strain threshold breaks
permanently. Rebuild the pair set from scratch and every pair arrives with no memory: it cannot
know its rest length, so it cannot know it is stretched, so it can never break. Fracture is
history, and a memoryless loop cannot represent history.

```python
contacts = ContactList(hash_grid, radius)
contacts.rest_length = dist(contacts.pairs)     # set at bond time
contacts.bonded = ones(len(contacts))
for step in range(substeps):
    contacts.update()                           # drop separated, add new, CARRY state
    strain = (dist(contacts.pairs) - contacts.rest_length) / contacts.rest_length
    contacts.bonded &= strain < strain_max      # once broken, permanently broken
```

The same shape appears anywhere contact has memory: stick-slip friction that must remember where
sticking began, adhesion that holds until it does not, plastic deformation, which is path
dependence by definition.

## Why the GPU makes it interesting

The pair set changes every step, so the layout must support insertion and removal without
reallocation, and the per-contact payload has to be permuted alongside the pairs. I used a flat
CSR-like layout so pairs and their floats move together. The validation that matters is a
reversibility test: load below threshold and release, the material returns to rest; load past
threshold, and it must never heal. A bond model that heals is the failure mode to check first.

## What I would do differently

The PR was 967 lines proposing a new core data structure, when the maintainer-suggested route was
a pure-Warp example demonstrating the pattern. Ship the example first, let the abstraction earn
its way in later. Big proposal, small appetite: my mistake, and a reusable lesson about
contributing to mature codebases.
