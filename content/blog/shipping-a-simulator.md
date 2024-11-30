---
title: "Shipping a simulator"
date: 2024-11-30T16:40:00+08:00
description: "release engineering looks different when the artifact is a world: USD stages, physics steps, render workers"
---

I have been doing release engineering for large-scale robotics simulation lately, and shipping
a simulator turns out to be a different discipline from shipping a service. The differences are
worth writing down while they still surprise me.

**The artifact is a world.** A release is not a binary; it is a USD scene graph, the physics that
steps it, the action graphs that wire sensors to logic, and the render workers that draw it, all
pinned to versions that agree with each other. USD's layering and composition is the reason this
is tractable at all: scenes compose from layers the way software composes from libraries, and a
release is a resolved composition.

**Determinism is a feature with a spec.** Physics timestep, solver iterations, random seeds, and
GPU kernel selection all feed reproducibility, and a validation pipeline for a simulator is
partly a battery of runs asserting that yesterday's trajectories still happen today, within
tolerance. Deciding the tolerance is the actual engineering: too tight and every driver update
breaks the build, too loose and regressions walk through wearing a lab coat.

**The pipeline tests the tests.** End-to-end triggers run scene load, physics step, sensor
capture, and render across the worker fleet before anything tags. What I underestimated: the
render worker chart is as much a part of correctness as the physics, because a policy trained on
frames from a stale renderer learned a world nobody ships anymore.

**ROS 2 is a boundary, not a feature.** The bridge to robot middleware is where simulation time
meets wall-clock time, and the impedance mismatch (sim time pausing, stepping, running faster
than real time) is a permanent source of subtle bugs downstream. Treating the bridge as a
versioned contract with its own validation, rather than a convenience layer, is the only stance
that survived contact.

The through-line: a simulator release is a claim that *this world behaves lawfully*, and the
release pipeline is the proof apparatus. I came for the graphics; I am staying for the
epistemology.
