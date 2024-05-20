---
title: "Restoring a cloud backup, carefully"
date: 2024-05-20T21:14:00+08:00
description: "the failure modes of bringing storage back from object stores, from the openstorage trenches"
anchor: "libopenstorage #2442, merged"
anchor_url: "https://github.com/libopenstorage/openstorage/pull/2442"
---

My cloud backup restore work merged into openstorage this month
([#2442](https://github.com/libopenstorage/openstorage/pull/2442)). Backup restore is one of
those features that is trivial in the demo and hairy everywhere else, so here are the failure
modes that actually shaped the implementation.

**Restore is a write path wearing a read path's clothes.** Reading from the object store is the
easy half; the hard half is that you are reconstructing a volume that must end bit-perfect while
the cluster around it keeps living: nodes reschedule, the target may move mid-restore, and the
operation has to either survive that or fail cleanly enough to retry. Idempotency is not an
optimization here, it is the correctness model.

**Status must be a state machine, not a boolean.** A restore that is `in-progress` from the API's
point of view might be waiting on the object store, replaying locally, or stalled on a node that
left. Collapsing those into one flag is how you get support tickets that say "it's stuck" with no
further information ever extractable. Structured, queryable state transitions were half the
patch.

**The object store lies by omission.** Eventually consistent listings mean a freshly written
backup may not enumerate completely; restoring from a listing you do not verify against the
manifest is a silent partial restore. Trust the manifest, verify the objects, never the listing.

**Test the sad paths as first-class citizens.** Kill the restore mid-flight and re-issue it. Take
the destination offline during replay. Point at a manifest whose objects are missing. Each of
those found a bug the happy path never would have, which is the storage-engineering catechism:
the failure modes are the product.

I did not expect volume restore to be the feature that taught me the most this year, and it was
not close.
