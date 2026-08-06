---
title: "Machines that imagine ahead"
date: 2026-08-06T11:02:00+08:00
description: "the thesis this notebook keeps circling: acting well requires rehearsing the future, and rehearsal only matters if it costs less than reality"
---

Watch your own hand reach for a glass. Before contact, your grip is already sized to the weight
you expect; your arm is already braced for the friction you predict. None of this is conscious.
The rehearsal happened somewhere cheap, milliseconds ahead of reality, and the action you
executed was the one that already worked in the rehearsal.

Robots mostly do not do this, and it shows. The demos stutter because each action meets the
world unrehearsed. The field's name for the fix is world models: systems that predict what
happens next, so that acting becomes choosing among imagined futures rather than gambling on one.
I think this framing is right and incomplete. The missing half is economic.

**Imagination is only useful if it is cheaper than reality.** A rehearsal that costs as much as
the act teaches you nothing you could not learn by acting. The entire value of an internal world
is the exchange rate: how many futures can you try for the price of one real attempt? That single
ratio quietly governs the field. It is why a video model that renders beautiful futures at ten
times slower than real time is a research demo, and the same model at a tenth of real time would
be a robot's inner life.

Seen through that lens, the work in this notebook stops being miscellaneous:

- [Reconstruction](/blog/anisotropic-voxels/) turns plain video into worlds that can be
  re-entered: the memory that imagination replays.
- GPU simulation and [physics](/blog/contact-lists/) supply consequences: an imagination that
  only predicts appearances cannot predict a bond breaking or a grip slipping.
- And the [inference](/blog/kv-cache-product/) [engineering](/blog/eight-seconds/), the part
  that looks least glamorous, is the exchange rate itself. Every millisecond off a forward pass
  buys more futures per decision. Speed is not a nicety here; speed is what makes imagination
  affordable at all.

The bet underneath [my operating plan](/blog/operating-plan/) is that this loop closes within the
decade: real scenes captured into rehearsable worlds, physics that makes the rehearsals honest,
and inference cheap enough that a machine tries a thousand futures before its coffee gets cold,
so to speak. The pieces exist today in separate rooms. They want to be one system.

I am building along this thread. The notebook will stay ahead of the announcement, which is how
I prefer it: the reasoning in public, the product when it is ready. If the thesis is wrong, these
posts will document exactly where I fooled myself, which would make them more valuable, and
considerably more entertaining, for everyone else.
