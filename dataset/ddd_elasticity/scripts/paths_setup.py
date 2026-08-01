"""Shared path / import setup for the elasticity DDD dataset pipeline."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATASET_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = DATASET_ROOT / "cases"
CONFIGS_DIR = DATASET_ROOT / "configs"
ARTIFACTS_DIR = DATASET_ROOT / "artifacts"

_PATHS = [
    ROOT / "python",
    ROOT / "lib",
    ROOT / "core" / "exadis" / "python",
    ROOT / "core" / "pydis" / "python",
]


def ensure_imports() -> None:
    for p in _PATHS:
        sp = str(p)
        if sp not in sys.path:
            sys.path.insert(0, sp)
    os.environ.setdefault("OMP_PROC_BIND", "false")
    os.environ.setdefault("OMP_NUM_THREADS", os.environ.get("OMP_NUM_THREADS", "4"))


def case_name(
    case_type: str,
    n_loops: int,
    box: float,
    stress_factor: float,
    seed: int,
    fov: float | None = None,
) -> str:
    """Deterministic short case directory name."""
    sf = f"{stress_factor:g}".replace(".", "p")
    base = f"{case_type}_n{n_loops}_L{int(box)}_s{sf}_seed{seed}"
    if fov is not None and abs(fov - box) > 1e-9:
        base += f"_fov{int(fov)}"
    return base
