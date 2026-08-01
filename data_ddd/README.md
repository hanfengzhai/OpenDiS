# data_ddd — elasticity-enabled DDD dataset pipeline

A dataset-generation workflow for dislocation-dynamics (DDD) simulations built
on the **pydis** core of OpenDiS, with full elastic segment–segment
interactions enabled (`force_mode='Elasticity_SBA'`, the non-singular ParaDiS
`SegSegForce` kernel compiled in `lib/libpydis.so`).

The physical and numerical settings are pinned to the repository's SimpleGlide
reference configuration (`examples/02_frank_read_src/test_frank_read_src_pydis.py`,
the in-repo counterpart of the `SimpleGlide_001` reference case), see
`ddd_dataset/reference.py`:

| fixed setting        | value |
|----------------------|-------|
| force model          | `Elasticity_SBA` (elastic seg–seg + Peach–Koehler) |
| mobility law         | `SimpleGlide` (`mob=1.0`, `vmax=1e9`) |
| time integration     | `EulerForward` |
| topology             | `MaxDiss` multi-node splitting |
| collision            | `Proximity` |
| remesh               | `LengthBased` |
| material             | `mu=50 GPa`, `nu=0.3`, `a=1.0 b`, `burgmag=3e-10 m` |
| boundary conditions  | periodic in x, y, z (cubic cell, 3×3 `h` matrix) |
| discretization       | `maxseg=0.04 L`, `minseg=0.01 L`, `rann=0.003 L` |
| reference stress     | Voigt `[xx,yy,zz,yz,xz,xy] = [0,0,0,0,-4e8,0]` Pa |

Only the following vary between cases: initial topology/geometry, number and
placement of loops/lines, box size (full 3-D cubic cell — “box 32” means a
32³ cell in units of b), field of view, applied stress, random seed, duration
and output frequency.

## Prerequisites

Build the pydis C force kernels once (produces `lib/libpydis.so` and the
ctypes bindings `lib/pydis_lib.py`):

```bash
cmake -S core/pydis -B build_pydis -DCMAKE_BUILD_TYPE=Release
cmake --build build_pydis -j4
cmake --build build_pydis --target install
cp core/pydis/lib/libpydis.so core/pydis/lib/pydis_lib.py lib/
```

Python needs `numpy` and `matplotlib`; videos need `ffmpeg` on PATH.

## Usage

```bash
# 1) generate all case directories (config + initial geometry + validation)
python3 data_ddd/generate_cases.py

# 2) run one case
python3 data_ddd/run_case.py data_ddd/dataset/glissile_loops/<case_name>

# 3) render initial/final snapshots + evolution video
python3 data_ddd/visualize_case.py data_ddd/dataset/glissile_loops/<case_name>

# or do everything in one shot (generate + run + visualize + summary)
python3 data_ddd/run_suite.py            # optionally --only <substr>
```

## Case suite

| category  | description                                        | box  |
|-----------|----------------------------------------------------|------|
| loop01    | single loop: reference stress (shrinks), 10× stress (expands), 10% stress perturbations, larger box, reduced FOV | 32/48 |
| loop02    | double loops on two slip systems                   | 32   |
| loop02c   | double coplanar loops → coalescence                | 32   |
| loop03    | triple loops on mixed slip systems                 | 32   |
| loop06    | six loops                                          | 64   |
| loop12    | twelve loops                                       | 128  |
| lineloop  | periodic straight line + coplanar expanding loop   | 32   |

Loops are glissile shear loops (`b ⟂ n`, b in the glide plane) discretized so
the segment length ≈ 0.6·maxseg. Multi-loop cases use seeded random placement
with minimum-image separation and boundary margins so there is no artificial
overlap or unintended image proximity at t = 0.

## Case directory layout

```
dataset/glissile_loops/<case_name>/
  config.json             # human-readable config: stress tensor (Voigt+3×3),
                          # geometry metadata, box/FOV, seed, fixed reference
  initial_network.json    # initial dislocation network
  validation.json         # pre-run checks + post-run completeness checks
  simulation.log          # timestamped run log
  status.json             # success flag, steps, wall time, termination reason
  output/disnet_*.json    # raw trajectory frames (OpenDiS JSON format)
  processed/trajectory.npz  # per-frame positions/segments/Burgers/planes
  processed/summary.csv   # step, time, node/segment counts, total line length
  vis/initial.png         # initial-state snapshot
  vis/final.png           # final-state snapshot
  vis/evolution.mp4       # network-evolution video
```

## Validation checks (per case, `validation.json`)

- node/segment connectivity + Burgers conservation (`is_sane`)
- minimum node degree, duplicate nodes, duplicate links
- zero-length / overlong segments
- nonzero Burgers vectors, glide-plane validity (`|n|=1`, `b·n=0`, line in plane)
- geometry inside the simulation box
- unintended loop–loop intersections (minimum-image distances)
- excessive proximity to periodic images
- presence of elasticity/force-model settings and a valid stress tensor
- post-run: completion, frame count, NaN-free and sane final network

## Notes

- `ddd_dataset/calforce_ext.py` adds a `OneNodeForce` implementation for the
  elasticity force mode (needed by MaxDiss topology at junction nodes formed
  in collisions); it uses exactly the same non-singular seg–seg kernel as the
  reference `NodeForce_Elasticity_SBA`, so the physics is unchanged.
- Applied-stress perturbations are random symmetric **deviatoric** tensors
  scaled to a fraction of the dominant stress component (hydrostatic stress
  does not drive glide), applied on top of the reference load, in Pa.
- The elastic force evaluation is O(N²) in segment count, so wall time grows
  quickly for the large multi-loop cases.
