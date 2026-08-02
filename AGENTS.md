# AGENTS.md

## Cursor Cloud specific instructions

OpenDiS (Open Dislocation Simulator) is a C/C++ + Python framework for dislocation
dynamics (DD) simulations. There is **no server** — you "run" it by building the native
libraries and executing Python simulation drivers. It has two swappable compute engines:

- **ExaDiS** (`core/exadis`, LLNL, C++/Kokkos, git submodule) exposed to Python as
  `pyexadis` / `pyexadis_base`. This is the engine used by the elasticity-enabled DDD
  dataset pipeline (the main deliverable on the `cursor/ddd-elasticity-*` branch).
- **PyDiS** (`core/pydis`) — reference engine: pure Python + a C library (`libpydis.so`)
  with ctypes bindings (`pydis_lib.py`), unified by the `python/framework` layer.

The update script (run on startup) only refreshes lightweight deps: it initializes git
submodules and installs Python deps (`numpy<2`, `pyyaml`, `matplotlib`). It intentionally
does **not** build. System packages (`g++-14`, `libstdc++-14-dev`, `libfftw3-dev`,
`python3-dev`, `ffmpeg`) are baked into the VM snapshot.

### Building (required before running anything; not done by the update script)

The compiled artifacts (`lib/libpydis.so`, `lib/pydis_lib.py`,
`core/exadis/python/pyexadis*.so`) are gitignored and are **not** rebuilt by the update
script. Rebuild after any C/C++ or submodule change, following
`NyeDiffusion/data_ddd/README.md`:

```bash
cd /workspace
./configure.sh -DSYS=ubuntu -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_OPENMP=Off
cmake --build build -j "$(nproc)"
cmake --build build --target install
```

A full clean build takes ~1 minute (Kokkos + ExaDiS + FFT). `build/` is gitignored.

### Running anything requires this PYTHONPATH

```bash
export PYTHONPATH="/workspace/core/exadis/python:/workspace/core/pydis/python:/workspace/python:/workspace/lib:/workspace:$PYTHONPATH"
```

### DDD elasticity dataset pipeline (primary app)

See `NyeDiffusion/data_ddd/README.md`. Quick end-to-end check (fast, ~few seconds/case):

```bash
python3 NyeDiffusion/data_ddd/generate_dataset.py                                   # configs only
python3 NyeDiffusion/data_ddd/generate_dataset.py --run --visualize --case triple_loop --max-step 60
```

Outputs land in `dataset/glissile_loops/generated/<case>/` (raw ParaDiS trajectories,
processed stress-strain data, validation JSON, and `figures/evolution.mp4`). This tree is
gitignored.

### Non-obvious gotchas

- **Compiler:** the default `/usr/bin/c++` is clang, and it links against the GCC-14
  runtime, so `g++-14` + `libstdc++-14-dev` must be present or the CMake compiler check
  fails with `cannot find -lstdc++`. (These are installed in the snapshot.)
- **numpy must be `<2`**: `pyexadis` is built against the NumPy 1.x C ABI; NumPy 2.x will
  break `import pyexadis`. The update script pins `numpy<2`.
- **Kokkos cannot be re-initialized after `finalize()`** in one process. The pipeline
  already handles this by running visualization in a fresh subprocess
  (`run_single_case.py`); keep simulation and post-processing in separate processes.
- **PyDiS Python path is currently broken independent of setup:** importing `pydis`
  raises `NameError: name 'np' is not defined` from `python/framework/calforce_base.py`
  (a `np.array` type hint with no `import numpy`). This breaks the PyDiS-only examples and
  `tests/test1_node_force`, `tests/test2_topol_op`. The ExaDiS engine and the dataset
  pipeline are unaffected. This is a pre-existing code issue, not an environment problem.
- There is **no linter config and no git hooks** in this repo.
