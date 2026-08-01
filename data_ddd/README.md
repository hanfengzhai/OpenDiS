# `data_ddd` — elasticity-enabled DDD dataset generation

`data_ddd` builds datasets of discrete-dislocation-dynamics (DDD) simulations of
glissile loops with **elasticity enabled**, on top of the ExaDiS engine shipped
with OpenDiS (`core/exadis`). Every case shares one reference physics setup and
differs only by

* initial dislocation topology and geometry,
* number and placement of loops / lines,
* simulation-box size,
* field of view,
* applied stress.

## Reference physics (identical in every case)

`data_ddd/reference.py` is the single source of truth. It reproduces the
`SimpleGlide` glissile-loop reference simulation:

| item | value |
| --- | --- |
| crystal / material | FCC copper: `burgmag = 2.55e-10 m`, `mu = 54.6 GPa`, `nu = 0.324`, core `a = 6 b` |
| force model (elasticity) | `DDD_FFT_MODEL` — core + self + Peach-Koehler external + long-range FFT / short-range isotropic segment-segment elasticity |
| mobility law | `SimpleGlide` (ExaDiS `GLIDE`), `mob = 1000` |
| time integration | `Trapezoid`, `rtol = 1 b`, `nextdt = 5e-13 s`, `maxdt = 1e-10 s` |
| collisions | `Retroactive`, `rann = 10 b` |
| topology | `TopologyParallel`, `splitMultiNodeAlpha = 1e-3` |
| remeshing | `LengthBased`, `maxseg = 1.5 u`, `minseg = 0.4 u` |
| boundary conditions | fully periodic (required by the FFT elasticity model) |
| loading | stress control |
| output | ParaDiS-format `config.<step>.data` plus `stress_strain_dens.dat` |

Nothing in the pipeline changes these settings between cases. If an
authoritative reference directory is available, export its settings to JSON and
merge them on top with `--reference ref.json` (or the `DATA_DDD_REFERENCE`
environment variable); the JSON is deep-merged into `REFERENCE`.

## Units and box sizes

ExaDiS works in units of the Burgers vector magnitude `b`. Case configurations
use *nominal units* `u`, with `units.unit_b = 200` b per nominal unit, so the
dataset box sizes read 32 / 64 / 128 as in the reference dataset while the
actual cells are 6400 / 12800 / 25600 b (1.6 / 3.3 / 6.5 µm).

The scale matters physically: a glissile loop only expands when the resolved
shear stress exceeds its self-stress (`~mu*b/(4*pi*R) * ln(R/a)`). At
`unit_b = 200` the default loop radius is 800 b ≈ 204 nm and the self-stress is
about 66 MPa, below the resolved shear of the reference loading.

**The box is always three-dimensional.** `box_size` is a 3-vector
`[Lx, Ly, Lz]` mapped to the ExaDiS cell `h = diag(Lx, Ly, Lz) * unit_b`; a 2-D
specification such as `64^2` is rejected by `CaseConfig` and by the
`box_is_3d` validation check. The field of view `fov` is likewise a 3-vector: a
centered observation window, used for the visualization bounds and stored in the
metadata; it never changes the simulated cell.

## Reference stress and perturbations

The reference loading is a uniaxial tension of 400 MPa along `[0 2 5]`. That
axis maximizes the smallest Schmid factor over the 12 FCC 1/2<110>{111} systems
(`min |m| = 0.085`, `max |m| = 0.493`), so a loop on any slip system is driven;
classical axes such as `[1 2 3]` leave three systems with exactly zero resolved
shear. Perturbations (`catalog.perturb_stress`) scale the magnitude and rotate
the loading axis by a few degrees, which keeps the tensor structure (a uniaxial
tension in Pa) intact. The full Voigt tensor (`xx, yy, zz, yz, xz, xy`, the
ExaDiS convention) is written to `config.yaml` and `metadata.json`.

## Case directory layout

```
datasets/glissile_loops/<case>/
    config.yaml                      human-readable case configuration
    metadata.json                    stress tensor, geometry, box/FOV, seed, provenance
    inputs/initial_network.data      simulation input (ParaDiS format)
    inputs/initial_network.npz       initial nodes/segments arrays
    inputs/run_params.json           exact ExaDiS module settings used
    raw/config.<step>.data           raw trajectory written by ExaDiS
    raw/stress_strain_dens.dat       raw properties output
    processed/trajectory.npz         processed trajectory (all frames + times)
    processed/trajectory_summary.csv per-frame diagnostics
    logs/run.log, logs/run_info.json simulation log and per-step history
    validation/{config,network,run}.json
    vis/initial.png, vis/final.png, vis/evolution.mp4
```

Case names are deterministic:
`<type>_<interaction>_b<box>_f<fov>_s<stress in MPa>_r<seed>`.

## Usage

```bash
# 1. build OpenDiS with the ExaDiS python binding (once)
./configure.sh -DCMAKE_BUILD_TYPE=Release -DEXADIS_PYTHON_BINDING=On -DEXADIS_FFT=On
cmake --build build -j 8

# 2. generate the case directories (configs, inputs, validation)
PYTHONPATH=$PWD python3 -m data_ddd.pipeline generate

# 3. run the simulations (also processes raw -> processed trajectories)
PYTHONPATH=$PWD OMP_NUM_THREADS=4 python3 -m data_ddd.pipeline run

# 4. render images and evolution videos
PYTHONPATH=$PWD MPLBACKEND=Agg python3 -m data_ddd.pipeline visualize

# 5. dataset status table
PYTHONPATH=$PWD python3 -m data_ddd.pipeline report
```

Useful flags: `--dataset-root DIR`, `--cases name1,name2`, `--types single_loop`,
`--representative` (one case per geometry category), `--limit N`,
`--max-step N`, `--fps N`, `--reference ref.json`.

Single-case entry points are also available:

```bash
python3 -m data_ddd.simulate   datasets/glissile_loops/<case>   # run
python3 -m data_ddd.trajectory datasets/glissile_loops/<case>   # process
python3 -m data_ddd.visualize  datasets/glissile_loops/<case>   # render
```

## Validation

`data_ddd/validation.py` runs three stages and writes a JSON report per stage:

* **config** — 3-D box, field of view inside the box, elasticity-enabled force
  model, complete material/module settings, periodic boundary conditions for the
  FFT model, FFT grid resolution, finite and symmetric stress tensor, stress
  magnitude vs `mu`, glissile Burgers vectors on valid FCC systems, resolved
  shear (Schmid) per loop, loops inside the box, boundary margins, proximity to
  periodic images, unintended loop intersections.
* **network** — segment node indices, self-links, isolated/dangling nodes,
  duplicate links, duplicate (coincident) nodes, zero-length and over-long
  segments, non-zero Burgers vectors, Burgers-vector conservation at every node,
  `b·n = 0` and `t·n = 0` for glide planes.
* **run** — frame count vs expected, exit status, monotonic finite times, finite
  trajectory, non-empty final network, and that the network actually moved.

A run that stops early because every dislocation annihilated is reported as a
warning (physical outcome) rather than a failure.

## Adding cases

Add an entry to `catalog.default_catalog()` (or call `catalog.make_case`
directly) with the case type, box size, field of view, interaction type, stress
and seed. Geometry generators live in `data_ddd/geometry.py`:
`place_loops` (isolated / coplanar / dipole / junction / mixed),
`place_line` and `select_line_loop_systems` for line-loop cases.
