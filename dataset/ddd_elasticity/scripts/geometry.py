"""Initial dislocation geometry generators for elasticity DDD datasets."""

from __future__ import annotations

from typing import Any

import numpy as np

from paths_setup import ensure_imports

ensure_imports()
import pyexadis  # noqa: E402
from pyexadis_base import ExaDisNet, DisNetManager, NodeConstraints  # noqa: E402
from pyexadis_utils import insert_frank_read_src, insert_infinite_line  # noqa: E402


FCC_BURGS = np.array(
    [
        [0.0, 1.0, -1.0],
        [1.0, 0.0, -1.0],
        [1.0, -1.0, 0.0],
        [0.0, 1.0, -1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0],
        [1.0, 0.0, -1.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, -1.0, 0.0],
    ],
    dtype=float,
)
FCC_PLANES = np.array(
    [
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [1.0, -1.0, 1.0],
        [1.0, -1.0, 1.0],
        [1.0, -1.0, 1.0],
        [1.0, 1.0, -1.0],
        [1.0, 1.0, -1.0],
        [1.0, 1.0, -1.0],
    ],
    dtype=float,
)


def _normalize_rows(a: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(a, axis=1, keepdims=True)
    return a / n


def _sample_centers(
    rng: np.random.Generator,
    n: int,
    box: float,
    margin: float,
    min_sep: float,
    max_tries: int = 5000,
) -> np.ndarray:
    """Sample centers inside [margin, box-margin]^3 with minimum separation."""
    lo, hi = margin, box - margin
    if hi <= lo:
        raise ValueError(f"Invalid margin={margin} for box={box}")
    centers = []
    tries = 0
    while len(centers) < n and tries < max_tries:
        tries += 1
        c = rng.uniform(lo, hi, size=3)
        if all(np.linalg.norm(c - np.asarray(p)) >= min_sep for p in centers):
            # Also keep away from periodic images of already placed centers
            ok = True
            for p in centers:
                d = np.abs(c - np.asarray(p))
                d = np.minimum(d, box - d)
                if np.linalg.norm(d) < min_sep:
                    ok = False
                    break
            if ok:
                centers.append(c)
    if len(centers) < n:
        raise RuntimeError(
            f"Failed to place {n} centers in L={box} with margin={margin}, min_sep={min_sep}"
        )
    return np.asarray(centers)


def insert_circular_glissile_loop(
    cell,
    nodes: list,
    segs: list,
    burg: np.ndarray,
    plane: np.ndarray,
    radius: float,
    center: np.ndarray,
    maxseg: float,
) -> tuple[list, list]:
    """Insert a planar circular glissile loop (b · n ≈ 0)."""
    burg = np.asarray(burg, dtype=float)
    plane = np.asarray(plane, dtype=float)
    plane = plane / np.linalg.norm(plane)
    burg = burg / np.linalg.norm(burg) * np.linalg.norm(burg)  # keep magnitude
    # Use unit burgers direction for geometry; keep provided magnitude
    bhat = burg / np.linalg.norm(burg)
    if abs(np.dot(bhat, plane)) > 1e-4:
        # Project burgers into plane to enforce glissile condition
        burg = burg - np.dot(burg, plane) * plane
        if np.linalg.norm(burg) < 1e-12:
            raise ValueError("Burgers vector parallel to plane normal")
    e1 = burg / np.linalg.norm(burg)
    e2 = np.cross(plane, e1)
    e2 = e2 / np.linalg.norm(e2)

    nseg = max(8, int(np.ceil(2.0 * np.pi * radius / maxseg)))
    istart = len(nodes)
    theta = np.linspace(0.0, 2.0 * np.pi, nseg, endpoint=False)
    for t in theta:
        p = center + radius * (np.cos(t) * e1 + np.sin(t) * e2)
        nodes.append(np.concatenate((p, [NodeConstraints.UNCONSTRAINED])))
    for i in range(nseg):
        segs.append(np.concatenate(([istart + i, istart + (i + 1) % nseg], burg, plane)))
    return nodes, segs


def build_prismatic_loops(
    crystal: str,
    box: float,
    n_loops: int,
    radius: float,
    maxseg: float,
    seed: int,
) -> tuple[DisNetManager, dict[str, Any]]:
    """Use ExaDiS native prismatic (glissile) loop generator."""
    G = ExaDisNet()
    G.generate_prismatic_config(crystal, box, n_loops, radius, maxseg=maxseg, seed=seed)
    meta = {
        "generator": "generate_prismatic_config",
        "crystal": crystal,
        "n_loops": n_loops,
        "radius": radius,
        "maxseg": maxseg,
        "seed": seed,
        "loop_kind": "prismatic_glissile",
    }
    return DisNetManager(G), meta


def build_circular_loops(
    crystal: str,
    box: float,
    n_loops: int,
    radius: float,
    maxseg: float,
    seed: int,
    margin: float,
    min_sep: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    cell = pyexadis.Cell(h=box * np.eye(3), is_periodic=[1, 1, 1])
    burgs = _normalize_rows(FCC_BURGS.copy())
    planes = _normalize_rows(FCC_PLANES.copy())
    centers = _sample_centers(rng, n_loops, box, margin, min_sep)
    nodes, segs = [], []
    loop_meta = []
    for i in range(n_loops):
        isys = i % len(burgs)
        b = burgs[isys]
        n = planes[isys]
        nodes, segs = insert_circular_glissile_loop(
            cell, nodes, segs, b, n, radius, centers[i], maxseg
        )
        loop_meta.append(
            {
                "index": i,
                "center": centers[i].tolist(),
                "radius": float(radius),
                "burgers": b.tolist(),
                "plane": n.tolist(),
                "slip_system": int(isys),
            }
        )
    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "circular_glissile_loops",
        "crystal": crystal,
        "n_loops": n_loops,
        "radius": radius,
        "maxseg": maxseg,
        "seed": seed,
        "loops": loop_meta,
        "loop_kind": "circular_glissile",
    }
    return DisNetManager(G), meta


def build_line_loop(
    crystal: str,
    box: float,
    radius: float,
    maxseg: float,
    seed: int,
    margin: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    """One infinite line + one circular loop on an interacting slip system."""
    rng = np.random.default_rng(seed)
    cell = pyexadis.Cell(h=box * np.eye(3), is_periodic=[1, 1, 1])
    burgs = _normalize_rows(FCC_BURGS.copy())
    planes = _normalize_rows(FCC_PLANES.copy())

    # Line on system 0
    b_line, n_line = burgs[0], planes[0]
    origin = np.array([0.5, 0.35, 0.5]) * box
    nodes, segs = [], []
    nodes, segs = insert_infinite_line(
        cell, nodes, segs, b_line, n_line, origin, theta=90.0, maxseg=maxseg
    )

    # Loop on a non-parallel system, offset toward the line
    b_loop, n_loop = burgs[3], planes[3]
    center = np.array([0.5, 0.55, 0.5]) * box
    # jitter within margin bounds
    jitter = rng.uniform(-0.05, 0.05, size=3) * box
    center = np.clip(center + jitter, margin, box - margin)
    nodes, segs = insert_circular_glissile_loop(
        cell, nodes, segs, b_loop, n_loop, radius, center, maxseg
    )

    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "line_loop",
        "crystal": crystal,
        "n_loops": 1,
        "n_lines": 1,
        "radius": radius,
        "maxseg": maxseg,
        "seed": seed,
        "line": {
            "burgers": b_line.tolist(),
            "plane": n_line.tolist(),
            "origin": origin.tolist(),
            "theta_deg": 90.0,
        },
        "loop": {
            "center": center.tolist(),
            "burgers": b_loop.tolist(),
            "plane": n_loop.tolist(),
            "radius": float(radius),
        },
        "loop_kind": "line_loop",
    }
    return DisNetManager(G), meta


def build_glissile_junction(
    box: float,
    seed: int,
    maxseg: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    """Two Frank-Read sources arranged for a glissile junction (FCC)."""
    rng = np.random.default_rng(seed)
    disloc_length = 0.55 * box
    cell = pyexadis.Cell(h=box * np.eye(3), is_periodic=[1, 1, 1])
    nodes, segs = [], []

    b1 = 1.0 / np.sqrt(2.0) * np.array([0.0, 1.0, 1.0])
    p1 = np.array([1.0, 1.0, -1.0])
    b2 = 1.0 / np.sqrt(2.0) * np.array([1.0, 0.0, -1.0])
    p2 = np.array([1.0, -1.0, 1.0])

    linter = np.cross(p1, p2)
    linter = linter / np.linalg.norm(linter)
    phi1 = 25.0 + float(rng.uniform(-5, 5))
    phi2 = 25.0 + float(rng.uniform(-5, 5))
    y1 = np.cross(linter, p1)
    y1 = y1 / np.linalg.norm(y1)
    ldir1 = np.cos(phi1 * np.pi / 180.0) * linter + np.sin(phi1 * np.pi / 180.0) * y1
    y2 = np.cross(linter, p2)
    y2 = y2 / np.linalg.norm(y2)
    ldir2 = np.cos(phi2 * np.pi / 180.0) * linter + np.sin(phi2 * np.pi / 180.0) * y2

    center = 0.5 * box * np.ones(3)
    delta = 0.02 * disloc_length * np.array([1.0, 1.0, 0.0])
    numnodes = max(8, int(np.ceil(disloc_length / maxseg)) + 1)
    nodes, segs = insert_frank_read_src(
        cell, nodes, segs, b1, p1, disloc_length, center + delta, linedir=ldir1, numnodes=numnodes
    )
    nodes, segs = insert_frank_read_src(
        cell, nodes, segs, b2, p2, disloc_length, center - delta, linedir=ldir2, numnodes=numnodes
    )
    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "glissile_junction_fr_sources",
        "n_loops": 0,
        "n_fr_sources": 2,
        "disloc_length": float(disloc_length),
        "phi1_deg": float(phi1),
        "phi2_deg": float(phi2),
        "seed": seed,
        "loop_kind": "glissile_junction",
    }
    return DisNetManager(G), meta


def build_line_prismatic_loop(
    crystal: str,
    box: float,
    radius: float,
    maxseg: float,
    seed: int,
) -> tuple[DisNetManager, dict[str, Any]]:
    """Infinite line plus a native prismatic loop (more stable than planar circular)."""
    rng = np.random.default_rng(seed)
    # Start from a prismatic loop ensemble with 1 loop, then append a line via export/import
    Gloop = ExaDisNet()
    Gloop.generate_prismatic_config(crystal, box, 1, radius, maxseg=maxseg, seed=seed)
    data = Gloop.export_data()
    cell = pyexadis.Cell(
        h=data["cell"]["h"],
        origin=data["cell"].get("origin", [0, 0, 0]),
        is_periodic=data["cell"].get("is_periodic", [1, 1, 1]),
    )
    nodes = []
    for p, c in zip(data["nodes"]["positions"], data["nodes"]["constraints"]):
        nodes.append(np.concatenate((np.asarray(p, dtype=float), [int(np.asarray(c).ravel()[0])])))
    segs = []
    for (i0, i1), b, n in zip(
        data["segs"]["nodeids"], data["segs"]["burgers"], data["segs"]["planes"]
    ):
        segs.append(np.concatenate(([int(i0), int(i1)], np.asarray(b, float), np.asarray(n, float))))

    burgs = _normalize_rows(FCC_BURGS.copy())
    planes = _normalize_rows(FCC_PLANES.copy())
    b_line, n_line = burgs[0], planes[0]
    origin = np.array([0.30, 0.30, 0.55]) * box
    origin = origin + rng.uniform(-0.03, 0.03, size=3) * box
    nodes, segs = insert_infinite_line(
        cell, nodes, segs, b_line, n_line, origin, theta=90.0, maxseg=maxseg
    )
    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "line_prismatic_loop",
        "crystal": crystal,
        "n_loops": 1,
        "n_lines": 1,
        "radius": radius,
        "maxseg": maxseg,
        "seed": seed,
        "line": {
            "burgers": b_line.tolist(),
            "plane": n_line.tolist(),
            "origin": origin.tolist(),
            "theta_deg": 90.0,
        },
        "loop_kind": "line_loop",
    }
    return DisNetManager(G), meta


def build_geometry(
    case_type: str,
    crystal: str,
    box: float,
    n_loops: int,
    radius: float,
    maxseg: float,
    seed: int,
    margin: float,
    min_sep: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    # Prefer ExaDiS prismatic glissile loops: planar circular loops can collapse
    # under the reference shear loading and leave an empty network.
    if case_type in ("single_loop", "double_loop", "triple_loop", "six_loops", "twelve_loops", "fov_variant"):
        return build_prismatic_loops(crystal, box, max(n_loops, 1), radius, maxseg, seed)
    if case_type == "line_loop":
        return build_line_prismatic_loop(crystal, box, radius, maxseg, seed)
    if case_type == "glissile_junction":
        return build_glissile_junction(box, seed, maxseg)
    raise ValueError(f"Unknown case_type={case_type}")
