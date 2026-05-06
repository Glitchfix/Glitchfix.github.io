---
title: "Anisotropic voxels, or why medical volumes hate cubes"
date: 2026-05-06T12:19:00+08:00
description: "CT stacks are 6:1 anisotropic. Resampling to cubes costs 6x memory and invents data. Now in Warp 1.13.0."
figures: 1
anchor: "warp c64a6c3, in 1.13.0"
anchor_url: "https://github.com/NVIDIA/warp/commit/c64a6c3"
---

A CT or MRI stack is not a stack of cubes. In-plane resolution might be 0.5 mm while slices sit
3 mm apart: a 6:1 aspect ratio baked into the acquisition itself. The scanner measured finely in
two axes and coarsely in the third, and the data is honest about it.

Voxel grids that only support one scalar `voxel_size` are not. They force a choice between two
bad resamplings:

- **Resample to the finest axis** and pay 6x the memory, filling the slice gaps with interpolated
  values the scanner never measured. For a signed distance field used in collision, interpolated
  detail becomes fabricated geometry.
- **Resample to the coarsest axis** and throw away the in-plane resolution you paid for.

{{< fig src="fig1.mp4" num="1" alt="a cubic voxel grid resampling a 6-to-1 anisotropic slab, versus native anisotropic voxels"
    caption="the same 64 mm volume: 2.10M cubic voxels with invented slices, or 0.35M native anisotropic voxels"
    scene="figures/anisotropic-voxels/scene.py" >}}

{{< mathline >}}64 mm cube at 0.5 mm isotropic: **2.10M** voxels &nbsp;·&nbsp; at (0.5, 0.5, 3.0): **0.35M**, no interpolation{{< /mathline >}}

## The fix was an interface, not an engine

Warp's volume machinery could already represent this: `allocate_by_tiles()` and
`allocate_by_voxels()` support anisotropic transforms through the internal transform buffers. But
the public entry points, `Volume.load_from_numpy()` and `Volume.allocate()`, assumed a scalar
`voxel_size` and crashed on a tuple. The capability existed one layer down; the interface never
exposed it.

```python
# before: scalar only
vol = wp.Volume.load_from_numpy(sdf, voxel_size=0.5)

# after: per-axis spacing, matching the acquisition
vol = wp.Volume.load_from_numpy(sdf, voxel_size=(0.5, 0.5, 3.0))
assert diagonal(vol.grid_transform) == (0.5, 0.5, 3.0)
```

The patch threads the 3-vector through to the existing machinery and adds tests that verify the
grid transform diagonal matches the requested spacing. It landed as commit `c64a6c3` and shipped
in the [Warp 1.13.0 release](https://github.com/NVIDIA/warp/blob/main/CHANGELOG.md), closing
GH-1193. The GitHub PR itself shows closed, which is how NVIDIA lands external patches through
its internal pipeline; the commit on main is the artifact.

## The subtle part: gradients

Anisotropy does not stop at storage. A finite-difference gradient on a non-uniform grid must
scale per axis:

{{< mathline >}}∂f/∂z ≈ (f[k+1] − f[k−1]) / (2 · **h_z**), &nbsp;not&nbsp; / (2 · h){{< /mathline >}}

Skip that and your SDF normals are wrong by the aspect ratio, which for a 6:1 medical stack means
collision responses pointing 80 degrees off the surface. If you adopt anisotropic voxels, audit
every gradient consumer the same day.

## Where else this shows up

Anything with a preferred axis: depth-camera volumes where range uncertainty grows with distance
while lateral resolution does not, thin-slab regions of interest, terrain where vertical detail
is cheap to waste. Cubes are a convention, not a law. The data usually knows better.
