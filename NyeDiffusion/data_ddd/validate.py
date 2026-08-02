"""Validation checks for generated DDD networks and simulation configs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np

from .reference import load_reference_config


@dataclass
class ValidationResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.passed = False
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _segment_lengths(positions: np.ndarray, nodeids: np.ndarray, cell) -> np.ndarray:
    import pyexadis
    cell_obj = pyexadis.Cell(h=cell["h"], origin=cell.get("origin", np.zeros(3)),
                             is_periodic=cell.get("is_periodic", [1, 1, 1]))
    r1 = positions[nodeids[:, 0]]
    r2 = np.array([cell_obj.closest_image(Rref=r1[i], R=positions[nodeids[i, 1]])
                   for i in range(len(nodeids))])
    return np.linalg.norm(r2 - r1, axis=1)


def validate_network(data: Dict[str, Any], cfg: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult()
    nodes = data["nodes"]
    segs = data["segs"]
    cell = data["cell"]
    positions = nodes["positions"]
    nodeids = segs["nodeids"]
    burgers = segs["burgers"]
    planes = segs["planes"]
    box = cfg["geometry"]["box_size"]
    min_dist_boundary = 0.05 * box

    if positions.shape[0] == 0:
        result.fail("Network has zero nodes")
        return result

    if nodeids.shape[0] == 0:
        result.fail("Network has zero segments")
        return result

    # Duplicate node positions (allowed for junction cases where lines meet)
    case_type = cfg["geometry"].get("case_type", "")
    rounded = np.round(positions, decimals=8)
    _, counts = np.unique(rounded, axis=0, return_counts=True)
    if np.any(counts > 1) and case_type not in ("binary_junction", "line_loop"):
        result.fail("Duplicate node positions detected")

    # Segment lengths
    lengths = _segment_lengths(positions, nodeids, cell)
    minseg = cfg["discretization"]["minseg"]
    if np.any(lengths < 0.01 * minseg):
        result.fail(f"Near-zero segment length: min={lengths.min():.3e}")

    # Burgers / plane orthogonality
    dot_bp = np.abs(np.sum(burgers * planes, axis=1))
    if np.any(dot_bp > 1e-3):
        result.warn(f"Burgers-plane non-orthogonality: max dot={dot_bp.max():.3e}")

    # Nodes inside box (with margin)
    h = np.array(cell["h"])
    origin = np.array(cell.get("origin", np.zeros(3)))
    hinv = np.linalg.inv(h)
    s = np.matmul(positions - origin, hinv.T)
    if np.any(s < -0.01) or np.any(s > 1.01):
        result.warn("Some nodes lie outside the primary simulation cell")

    # Proximity to boundaries
    for i, p in enumerate(positions):
        s_i = np.matmul(p - origin, hinv.T)
        dist = np.minimum(s_i, 1.0 - s_i) * np.diag(h)
        if np.min(dist) < min_dist_boundary:
            result.warn(f"Node {i} is close to a periodic boundary (min dist {np.min(dist):.2f})")

    # Elasticity settings present
    ref = load_reference_config()
    if cfg["force"]["mode"] not in ("DDD_FFT_MODEL", "SUBCYCLING_MODEL"):
        result.fail(f"Force mode {cfg['force']['mode']} is not elasticity-enabled")
    if cfg["mobility"]["law"] != ref["mobility"]["law"]:
        result.warn(f"Mobility law {cfg['mobility']['law']} differs from reference")

    return result


def validate_simulation_outputs(case_dir: str) -> ValidationResult:
    import os
    result = ValidationResult()
    raw = os.path.join(case_dir, "raw")
    if not os.path.isdir(raw):
        result.fail("Missing raw/ output directory")
        return result
    configs = [f for f in os.listdir(raw) if f.startswith("config.") and f.endswith(".data")]
    if not configs:
        result.fail("No trajectory config.*.data files found")
    elif len(configs) < 2:
        result.warn("Only one trajectory frame found")
    log_path = os.path.join(case_dir, "logs", "simulation.log")
    if not os.path.isfile(log_path):
        result.warn("Missing simulation.log")
    return result
