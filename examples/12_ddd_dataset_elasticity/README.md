# Elasticity-enabled DDD dataset workflow

This directory provides a configurable dataset-generation workflow for ExaDiS
that keeps the solver physics fixed and varies only geometry/topology, stress,
box size, and field-of-view metadata.

## Reference physics

The fixed solver settings are encoded in `dataset_config.json` and match the
in-repo SimpleGlide + elasticity example:

- `force_mode = DDD_FFT_MODEL`
- `mobility_law = SimpleGlide`
- `integrator = Trapezoid`
- `collision_mode = Proximity`
- `topology_mode = TopologySerial`
- `remesh_rule = LengthBased`
- periodic box boundary conditions
- stress-control loading with shear-only stress tensor structure

## Generated case categories

The default config includes representative templates for:

- single loop
- double loops
- triple loops
- six loops
- twelve loops
- line-loop interactions
- mixed multi-loop interactions

Box scaling is set by template:

- 1/2/3 loops: box ~32
- 6 loops: box ~64
- 12 loops: box ~128

## Run

From repository root:

```bash
python3 examples/12_ddd_dataset_elasticity/generate_ddd_elasticity_dataset.py \
  --config examples/12_ddd_dataset_elasticity/dataset_config.json \
  --output-root examples/12_ddd_dataset_elasticity/generated_dataset \
  --overwrite
```

To simulate more variants per template:

```bash
python3 examples/12_ddd_dataset_elasticity/generate_ddd_elasticity_dataset.py \
  --simulate-per-template 2 \
  --overwrite
```

## Per-case outputs

Each case directory includes:

- `case_spec.json` (human-readable configuration)
- `applied_stress_tensor.json`
- `initial_geometry_metadata.json`
- `box_and_fov.json`
- `seed.json`
- `inputs/initial_config.data`
- `raw_trajectory/config.<step>.data`
- `processed/trajectory_summary.json`
- `logs/simulation.log`
- `logs/run_status.json`
- `validation_pre.json`
- `validation_post.json`
- `visualization/initial.png`
- `visualization/final.png`
- `visualization/evolution.mp4`

Global run metadata is saved in:

- `generated_dataset/dataset_run_config.json`
- `generated_dataset/manifest.json`
