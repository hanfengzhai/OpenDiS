# Elastic SimpleGlide DDD dataset workflow

`../../tools/generate_elastic_ddd_dataset.py` generates six deterministic
three-dimensional, periodic ExaDiS cases:

- single, double, triple, six, and twelve separated glissile loops;
- a pinned finite line interacting with a glissile loop.

The baseline is frozen from
`examples/01_loop/test_disl_loop_exadis.py`: line-tension elasticity,
`SimpleGlide`, forward Euler (`1e-9 s`), retroactive collision, no topology
operation/remesh, and the same material constants.  Stress values are scalar
perturbations of its Voigt tensor `[1e6, 1e6, 0, 0, 0, 0] Pa`, preserving its
biaxial normal-loading convention.

The requested `Nye_Disloc_Distance/.../SimpleGlide_001` and
`NyeDiffusion/data_ddd` paths were unavailable in this checkout.  The
per-case `configuration.json` therefore records this provenance warning.
Do not treat this workflow as exact parity with those unavailable files until
they are mounted and compared.

## Commands

```bash
# Generate and validate all inputs (does not require a compiled backend)
python3 tools/generate_elastic_ddd_dataset.py --write-cases

# Build the backend once ExaDiS dependencies are available
CXX=g++ ./configure.sh -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
cmake --build build --target install

# Run and render an individual case
python3 tools/generate_elastic_ddd_dataset.py --case single-l01-b032-fov016-s050-seed101 --run
python3 tools/generate_elastic_ddd_dataset.py --case single-l01-b032-fov016-s050-seed101 --visualize
```

Each case contains its readable configuration, exact stress tensor, initial
geometry, validation result, ExaDiS input, raw `config.*.data` trajectory,
processed final JSON, simulation log, and `figures/{initial,final}.png` plus
`figures/evolution.mp4` after a successful run.
