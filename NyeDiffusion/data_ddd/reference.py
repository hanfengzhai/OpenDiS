"""Load authoritative physics settings from SimpleGlide_001 reference case."""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = ROOT / "dataset" / "glissile_loops" / "SimpleGlide_001"
REFERENCE_CONFIG = REFERENCE_DIR / "config.yaml"


def load_reference_config() -> Dict[str, Any]:
    with open(REFERENCE_CONFIG) as f:
        return yaml.safe_load(f)


def _as_float(x) -> float:
    return float(x)


def reference_state(ref: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ref = ref or load_reference_config()
    mat, disc, geom = ref["material"], ref["discretization"], ref["geometry"]
    return {
        "crystal": geom["crystal"],
        "burgmag": _as_float(mat["burgmag"]),
        "mu": _as_float(mat["mu"]),
        "nu": _as_float(mat["nu"]),
        "a": _as_float(mat["a"]),
        "maxseg": _as_float(disc["maxseg"]),
        "minseg": _as_float(disc["minseg"]),
        "rtol": _as_float(disc["rtol"]),
        "rann": _as_float(disc["rann"]),
        "nextdt": _as_float(disc["nextdt"]),
    }


def scale_discretization_for_box(ref: Dict[str, Any], box_size: float) -> Dict[str, float]:
    """Scale segment lengths with box size while keeping reference ratios."""
    ref_box = ref["geometry"]["box_size"]
    ratio = box_size / ref_box
    disc = ref["discretization"]
    return {
        "maxseg": _as_float(disc["maxseg"]) * ratio,
        "minseg": _as_float(disc["minseg"]) * ratio,
        "rtol": _as_float(disc["rtol"]),
        "rann": _as_float(disc["rann"]),
        "nextdt": _as_float(disc["nextdt"]),
    }


def box_size_for_loop_count(num_loops: int) -> float:
    if num_loops <= 3:
        return 32.0
    if num_loops <= 6:
        return 64.0
    return 128.0


def make_case_config(
    case_type: str,
    num_loops: int,
    seed: int = 1,
    stress_scale: float = 1.0,
    fov: float | None = None,
    box_size: float | None = None,
    max_step: int | None = None,
) -> Dict[str, Any]:
    """Build a case config by perturbing only geometry, box, FOV, stress, and duration."""
    ref = load_reference_config()
    cfg = copy.deepcopy(ref)
    box = box_size if box_size is not None else box_size_for_loop_count(num_loops)
    disc = scale_discretization_for_box(ref, box)

    cfg["case_id"] = f"{case_type}_n{num_loops}_b{int(box)}_s{seed}"
    cfg["geometry"]["case_type"] = case_type
    cfg["geometry"]["num_loops"] = num_loops
    cfg["geometry"]["box_size"] = box
    cfg["geometry"]["loop_radius"] = 0.21 * box
    cfg["geometry"]["field_of_view"] = fov if fov is not None else box
    cfg["geometry"]["seed"] = seed
    cfg["discretization"].update(disc)

    base_stress = [float(s) for s in ref["loading"]["applied_stress"]]
    cfg["loading"]["applied_stress"] = [s * stress_scale for s in base_stress]
    if max_step is not None:
        cfg["simulation"]["max_step"] = max_step

    # Scale FFT grid with box (keep ~1 cell per loop diameter)
    cfg["force"]["Ngrid"] = max(16, int(box))

    return cfg


def save_case_config(cfg: Dict[str, Any], path: os.PathLike) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
