"""Reference DDD configuration shared by every case of the dataset.

Every setting that must stay identical across the dataset lives here: material
parameters, the elasticity-enabled force model, the mobility law, time
integration, topological operations, collisions, remeshing and the output
conventions.  Dataset cases are only allowed to differ by initial geometry and
topology, number of loops/lines, box size, field of view and applied stress.

The reference values are those of the `SimpleGlide` glissile-loop reference
simulation: FCC copper, `SimpleGlide` (GLIDE) mobility, and the DDD-FFT force
model, which is the elasticity-enabled force model of ExaDiS (core + self +
Peach-Koehler external + long-range FFT / short-range isotropic segment-segment
interactions).

If an authoritative reference directory is available on the machine that runs
the pipeline, a JSON file exported from it can be merged on top of these values
with :func:`load_reference` so that the dataset tracks the reference exactly.
"""

from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict

# --------------------------------------------------------------------------
# Length units
# --------------------------------------------------------------------------
# ExaDiS works in units of the Burgers vector magnitude ``burgmag``.  Dataset
# configurations are expressed in "nominal units" (u) so that the box sizes read
# 32 / 64 / 128 as in the reference dataset; ``unit_b`` is the number of
# ExaDiS length units (i.e. of b) per nominal unit.
#
# unit_b = 200 puts the 32-unit box at 6400 b = 1.63 um and the default loop
# radius at 800 b = 204 nm.  At that scale the loop self-stress (~66 MPa) is
# below the resolved shear stress of the reference loading, so glissile loops
# expand rather than collapse; smaller scales would make every loop shrink.
UNIT_B = 200.0

REFERENCE: Dict[str, Any] = {
    "description": (
        "Elasticity-enabled glissile-loop reference (SimpleGlide): FCC Cu, "
        "DDD-FFT force model, GLIDE mobility, trapezoid integration, "
        "retroactive collisions, parallel topology, length-based remeshing."
    ),
    "units": {
        # nominal length unit expressed in units of b
        "unit_b": UNIT_B,
        "length": "b (burgmag)",
        "stress": "Pa",
        "time": "s",
    },
    "material": {
        "crystal": "fcc",
        "burgmag": 2.55e-10,  # m
        "mu": 54.6e9,  # Pa
        "nu": 0.324,
        "a": 6.0,  # core radius, units of b
    },
    "discretization": {
        # kept constant in absolute (b) units for every box size so that the
        # discretization physics does not change between cases
        "maxseg": 1.5 * UNIT_B,  # 75 b
        "minseg": 0.4 * UNIT_B,  # 20 b
        "rann": 10.0,  # annihilation/collision distance, b
        "rtol": 1.0,  # integration position tolerance, b
        # DDD-FFT grid: constant grid spacing (in b) across box sizes
        "fft_grid_spacing": 2.0 * UNIT_B,  # 100 b
        "fft_grid_min": 8,
        "fft_grid_max": 64,
    },
    "force": {
        "force_mode": "DDD_FFT_MODEL",  # elasticity enabled
        "Ec": -1.0,  # <0: ExaDiS default core energy mu*b^2/(4 pi)
    },
    "mobility": {
        "mobility_law": "SimpleGlide",
        "mob": 1000.0,
    },
    "time_integration": {
        "integrator": "Trapezoid",
        "nextdt": 5.0e-13,  # s
        "maxdt": 1.0e-10,  # s
    },
    "collision": {
        "collision_mode": "Retroactive",
    },
    "topology": {
        "topology_mode": "TopologyParallel",
        "splitMultiNodeAlpha": 1.0e-3,
    },
    "remesh": {
        "remesh_rule": "LengthBased",
    },
    "cross_slip": None,
    "loading": {
        "loading_mode": "stress",
    },
    "boundary_conditions": {
        # DDD-FFT elasticity requires full periodic boundary conditions
        "pbc": [True, True, True],
    },
    "output": {
        "config_format": "paradis",  # config.<step>.data written by ExaDiS
        "properties_file": "stress_strain_dens.dat",
        "write_freq": 2,
        "print_freq": 5,
        "num_steps": 100,
    },
}

# FCC 1/2<110>{111} slip systems, in the same convention as ExaDiS' FCC crystal
# (src/crystal.h): Burgers vectors are normalized 1/2<110>, planes are {111}.
FCC_SLIP_SYSTEMS = [
    ([1.0, 1.0, 0.0], [1.0, -1.0, 1.0]),
    ([1.0, 1.0, 0.0], [-1.0, 1.0, 1.0]),
    ([1.0, -1.0, 0.0], [1.0, 1.0, 1.0]),
    ([1.0, -1.0, 0.0], [1.0, 1.0, -1.0]),
    ([1.0, 0.0, 1.0], [1.0, 1.0, -1.0]),
    ([1.0, 0.0, 1.0], [-1.0, 1.0, 1.0]),
    ([1.0, 0.0, -1.0], [1.0, 1.0, 1.0]),
    ([1.0, 0.0, -1.0], [1.0, -1.0, 1.0]),
    ([0.0, 1.0, 1.0], [1.0, 1.0, -1.0]),
    ([0.0, 1.0, 1.0], [1.0, -1.0, 1.0]),
    ([0.0, 1.0, -1.0], [1.0, 1.0, 1.0]),
    ([0.0, 1.0, -1.0], [-1.0, 1.0, 1.0]),
]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_reference(reference_json: str | None = None) -> Dict[str, Any]:
    """Return the reference settings, optionally merged with a JSON override.

    ``reference_json`` defaults to the ``DATA_DDD_REFERENCE`` environment
    variable, which allows pointing the pipeline at settings exported from an
    authoritative reference simulation directory.
    """
    reference_json = reference_json or os.environ.get("DATA_DDD_REFERENCE")
    reference = copy.deepcopy(REFERENCE)
    if reference_json:
        with open(reference_json, "r", encoding="utf-8") as handle:
            reference = _deep_merge(reference, json.load(handle))
    return reference


def fft_grid(box_b: float, reference: Dict[str, Any] | None = None) -> int:
    """Number of FFT grid points per direction for a cubic box of size ``box_b``."""
    reference = reference or REFERENCE
    disc = reference["discretization"]
    n = int(round(box_b / disc["fft_grid_spacing"]))
    n = max(disc["fft_grid_min"], min(disc["fft_grid_max"], n))
    # keep an even grid size, which FFT implementations handle best
    if n % 2:
        n += 1
    return n


def reference_state(reference: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Build the ExaDiS ``state`` dictionary from the reference settings."""
    reference = reference or REFERENCE
    material = reference["material"]
    disc = reference["discretization"]
    timeint = reference["time_integration"]
    state = {
        "crystal": material["crystal"],
        "burgmag": material["burgmag"],
        "mu": material["mu"],
        "nu": material["nu"],
        "a": material["a"],
        "maxseg": disc["maxseg"],
        "minseg": disc["minseg"],
        "rann": disc["rann"],
        "rtol": disc["rtol"],
        "nextdt": timeint["nextdt"],
        "maxdt": timeint["maxdt"],
    }
    return state
