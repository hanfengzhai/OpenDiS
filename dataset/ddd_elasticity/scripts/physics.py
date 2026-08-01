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
) -> dict[str, Any]:
    cfg = {
        "case_type": case_type,
        "n_loops": int(n_loops),
        "box_size": [float(box), float(box), float(box)],
        "field_of_view": [float(fov), float(fov), float(fov)],
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
            "Box and FOV are three-dimensional cubic extents.",
            "ForceFFT requires full 3D PBC; 64^2-style 2D box notation is invalid for the solver.",
            "Physics settings are frozen across cases; only geometry/box/FOV/stress vary.",
        ],
    }
    return cfg
