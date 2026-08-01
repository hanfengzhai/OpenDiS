"""Reference physics helpers for elasticity-enabled DDD cases."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from paths_setup import CONFIGS_DIR


def load_yaml(path: Path | str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_reference_physics(path: Path | str | None = None) -> dict[str, Any]:
    path = Path(path) if path else CONFIGS_DIR / "reference_physics.yaml"
    return load_yaml(path)


def box_size_for_nloops(physics: dict[str, Any], n_loops: int, override: float | None = None) -> float:
    if override is not None:
        return float(override)
    key = str(int(n_loops))
    mapping = physics["box_size_by_nloops"]
    if key not in mapping:
        # Fallback: scale roughly with cube root of loop count relative to 3 loops @ 32
        if n_loops <= 3:
            return 32.0
        if n_loops <= 6:
            return 64.0
        return 128.0
    return float(mapping[key])


def ngrid_for_box(physics: dict[str, Any], box: float) -> int:
    mapping = physics["ngrid_by_box"]
    key = f"{float(box):.1f}"
    if key in mapping:
        return int(mapping[key])
    # nearest known box
    boxes = sorted(float(k) for k in mapping)
    nearest = min(boxes, key=lambda b: abs(b - box))
    return int(mapping[f"{nearest:.1f}"])


def make_state(physics: dict[str, Any], box: float) -> dict[str, Any]:
    """Build ExaDiS state dict scaled consistently with box size."""
    state = {
        "crystal": physics["crystal"],
        "burgmag": float(physics["burgmag"]),
        "mu": float(physics["mu"]),
        "nu": float(physics["nu"]),
        "a": float(physics["a_over_Lbox"]) * box,
        "maxseg": float(physics["maxseg_over_Lbox"]) * box,
        "minseg": float(physics["minseg_over_Lbox"]) * box,
        "rtol": float(physics["rtol"]),
        "nextdt": float(physics["nextdt"]),
    }
    if physics.get("rann") is not None:
        state["rann"] = float(physics["rann"])
    return state


def make_applied_stress(physics: dict[str, Any], stress_factor: float = 1.0) -> np.ndarray:
    """
    Perturb only the magnitude of the reference shear loading, preserving
    Voigt structure [xx, yy, zz, yz, xz, xy].
    """
    ref = np.asarray(physics["reference_applied_stress"], dtype=float).copy()
    if ref.shape != (6,):
        raise ValueError(f"reference_applied_stress must be length-6 Voigt, got {ref.shape}")
    # Scale non-zero components (reference is pure sigma_xy)
    out = ref * float(stress_factor)
    return out


def solver_settings(physics: dict[str, Any], box: float) -> dict[str, Any]:
    return {
        "force_mode": physics["force_mode"],
        "mobility_law": physics["mobility_law"],
        "mobility_mob": float(physics["mobility_mob"]),
        "integrator": physics["integrator"],
        "collision_mode": physics["collision_mode"],
        "topology_mode": physics.get("topology_mode"),
        "remesh_rule": physics["remesh_rule"],
        "loading_mode": physics["loading_mode"],
        "ngrid": ngrid_for_box(physics, box),
        "pbc": list(physics["pbc"]),
        "box": [float(box), float(box), float(box)],  # 3D cubic, not 2D
    }


def case_config_dict(
    *,
    case_type: str,
    n_loops: int,
    box: float,
    fov: float,
    seed: int,
    stress_factor: float,
    applied_stress: np.ndarray,
    state: dict[str, Any],
    solver: dict[str, Any],
    geometry_meta: dict[str, Any],
    max_step: int,
    write_freq: int,
    print_freq: int,
    physics_source: str,
    physics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    physics = physics or {}
    cfg = {
        "case_type": case_type,
        "n_loops": int(n_loops),
        "dimensionality": physics.get("dimensionality", "2D"),
        "glide_plane": physics.get("glide_plane", "001"),
        "plane_normal": physics.get("plane_normal", [0.0, 0.0, 1.0]),
        # Solver cell is always 3D (ForceFFT). Dataset FOV is the in-plane LxL on 001.
        "box_size_solver_3d": [float(box), float(box), float(box)],
        "field_of_view_001_2d": [float(fov), float(fov)],
        "field_of_view_note": f"{fov:g}^2 on the 001 plane (in-plane); solver cell is {box:g}^3",
        "random_seed": int(seed),
        "stress_factor": float(stress_factor),
        "applied_stress_voigt_xx_yy_zz_yz_xz_xy": applied_stress.tolist(),
        "state": deepcopy(state),
        "solver": deepcopy(solver),
        "geometry": deepcopy(geometry_meta),
        "simulation": {
            "max_step": int(max_step),
            "write_freq": int(write_freq),
            "print_freq": int(print_freq),
        },
        "physics_source": physics_source,
        "notes": [
            "All dislocations are constrained to the (001) plane (2D glide).",
            "Dataset FOV/box sizing is the in-plane LxL extent (e.g. 64^2 on 001).",
            "ForceFFT still requires a 3D cubic periodic cell L^3 with full PBC.",
            "Reference stress is sigma_xz < 0 so (001)[100] loops expand.",
        ],
    }
    return cfg
