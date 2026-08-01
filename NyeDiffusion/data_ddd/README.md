# DDD Elasticity Dataset Generation

Pipeline for generating elasticity-enabled dislocation dynamics datasets with
`SimpleGlide` mobility, based on the authoritative reference case
`dataset/glissile_loops/SimpleGlide_001`.

## Prerequisites

```bash
# Build OpenDiS / ExaDiS (once)
cd /workspace
./configure.sh -DSYS=ubuntu -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_OPENMP=Off
cmake --build build -j $(nproc)
cmake --build build --target install

# Python dependencies
pip install 'numpy<2' pyyaml matplotlib --break-system-packages
sudo apt-get install ffmpeg libfftw3-dev python3-dev g++-14 libstdc++-14-dev
```

## Reference case

`dataset/glissile_loops/SimpleGlide_001/` defines the fixed physics settings:
- BCC glissile prismatic loops
- `DDD_FFT_MODEL` elastic forces
- `SimpleGlide` mobility
- Trapezoid time integration, Retroactive collisions, TopologySerial

**Do not modify files in `SimpleGlide_001/`.**

## Generate dataset

```bash
export PYTHONPATH="/workspace/core/exadis/python:/workspace/core/pydis/python:/workspace/python:/workspace:$PYTHONPATH"

# Generate configs only
python3 NyeDiffusion/data_ddd/generate_dataset.py

# Generate, run simulations, and create videos
python3 NyeDiffusion/data_ddd/generate_dataset.py --run --visualize --max-step 60

# Run a single category
python3 NyeDiffusion/data_ddd/generate_dataset.py --run --visualize --case six_loop
```

## Output layout (per case)

```
dataset/glissile_loops/generated/<case_name>/
  config.yaml              # human-readable configuration
  applied_stress.json      # stress tensor metadata
  geometry_metadata.json   # box, FOV, seed, topology
  raw/                     # ParaDiS trajectory (config.*.data)
  processed/               # stress-strain-density time series
  logs/simulation.log
  validation/              # pre/post simulation checks
  figures/
    initial_state.png
    final_state.png
    evolution.mp4
```

## Box-size scaling

| Loops | Box size (3D cubic) |
|-------|---------------------|
| 1–3   | 32                  |
| 6     | 64                  |
| 12    | 128                 |

The simulation box is always three-dimensional (`h = L * I₃`). Field of view
controls visualization crop only.

## Case types

| Type | Description |
|------|-------------|
| `single_loop` | One prismatic glissile loop |
| `double_loop` | Two loops |
| `triple_loop` | Three loops |
| `six_loop` | Six loops (box 64) |
| `twelve_loop` | Twelve loops (box 128) |
| `line_loop` | Frank-Read source + infinite line |
| `binary_junction` | Two intersecting dislocation lines |
