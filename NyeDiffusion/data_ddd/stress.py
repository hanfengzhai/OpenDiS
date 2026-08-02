"""Applied-stress perturbations preserving Voigt tensor structure."""

from __future__ import annotations

from typing import Dict, List

import numpy as np


VOIGT_LABELS = ("xx", "yy", "zz", "yz", "xz", "xy")


def voigt_to_symmetric(stress: np.ndarray) -> np.ndarray:
    s = np.asarray(stress, dtype=float).ravel()
    return np.array([
        [s[0], s[5], s[4]],
        [s[5], s[1], s[3]],
        [s[4], s[3], s[2]],
    ])


def symmetric_to_voigt(tensor: np.ndarray) -> np.ndarray:
    t = np.asarray(tensor, dtype=float)
    return np.array([t[0, 0], t[1, 1], t[2, 2], t[1, 2], t[0, 2], t[0, 1]])


def perturb_stress(
    base_stress: List[float],
    mode: str = "scale",
    factor: float = 1.0,
    shear_fraction: float = 0.0,
) -> np.ndarray:
    """
    Perturb reference stress while preserving symmetry.

    Modes:
      - scale: multiply all components by factor
      - shear_boost: increase xy shear component relative to base
      - deviatoric: add deviatoric perturbation proportional to factor
    """
    s = np.array(base_stress, dtype=float)
    if mode == "scale":
        return s * factor
    if mode == "shear_boost":
        out = s.copy()
        out[5] += shear_fraction * abs(s[5]) if s[5] != 0 else shear_fraction * 1e8
        return out
    if mode == "deviatoric":
        tensor = voigt_to_symmetric(s)
        hydro = np.trace(tensor) / 3.0
        dev = tensor - hydro * np.eye(3)
        tensor = tensor + factor * dev
        return symmetric_to_voigt(tensor)
    raise ValueError(f"Unknown stress perturbation mode: {mode}")


def stress_metadata(stress: np.ndarray) -> Dict[str, float]:
    s = np.asarray(stress, dtype=float)
    tensor = voigt_to_symmetric(s)
    hydro = np.trace(tensor) / 3.0
    dev = tensor - hydro * np.eye(3)
    von_mises = np.sqrt(1.5 * np.sum(dev * dev))
    return {
        "hydrostatic_Pa": float(hydro),
        "von_mises_Pa": float(von_mises),
        **{f"sigma_{k}": float(v) for k, v in zip(VOIGT_LABELS, s)},
    }
