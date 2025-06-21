---
title: "Walk on spheres: solving PDEs with random walks"
date: 2025-06-21T14:26:00+08:00
description: "a Monte Carlo method that never meshes the domain, and why it fits the GPU so well"
---

My favorite algorithm of the year is from 1956. Walk on spheres solves Laplace boundary problems
with random walks, never meshes the domain, and maps onto a GPU so naturally it feels designed
for one. Notes from implementing it in a GPU kernel framework.

## The method in one paragraph

To evaluate the harmonic solution u(x) with boundary values g: from the query point, find the
distance d to the nearest boundary, jump to a uniformly random point on the sphere of radius d,
and repeat. The walk ends when it lands within epsilon of the boundary; record g there. The mean
of many walks converges to u(x). The correctness comes from the mean value property of harmonic
functions: the value at a sphere's center equals its average over the sphere, so each jump is an
unbiased sample of the same quantity.

```python
def walk(x, sdf, g, eps=1e-4):
    while True:
        d = sdf(x)                      # distance to nearest boundary
        if d < eps:
            return g(nearest_boundary_point(x))
        x = x + d * random_unit_vector()
```

## Why the GPU loves it

Every walk is independent: no mesh, no linear system, no synchronization, just millions of walks
in flight, one per thread. The only shared data is the geometry query, and if the boundary is a
signed distance field the inner loop is exactly the sphere-tracing primitive graphics people have
tuned for years. Variance behaves like all Monte Carlo: error shrinks as one over the square root
of the walk count, so a batched estimator with Welford's online mean and variance gives you
uncertainty for free while walks stream in.

Two properties make it practically interesting rather than a curiosity. It is *local*: evaluating
u at one point costs walks at that point only, with no global solve, so querying a handful of
points in a huge domain is dramatically cheaper than meshing the domain. And it is *robust to
geometry*: gnarly boundaries that would take hours of meshing are just an SDF lookup.

## Where it strains

Walks slow to a crawl in narrow corridors, since the sphere radius collapses; boundary conditions
beyond Dirichlet take real care (Neumann is its own literature); and it answers point queries,
not full fields, so it competes with solvers only when you want values at scattered locations.
Inside those bounds, it is the cheapest field estimator I know, and the recent research wave
extending it says I am not alone in thinking so.
