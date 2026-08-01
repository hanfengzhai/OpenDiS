"""Initial dislocation geometry generators for 2D (001)-plane elasticity DDD datasets."""

from __future__ import annotations

from typing import Any

import numpy as np

from paths_setup import ensure_imports

ensure_imports()
import pyexadis  # noqa: E402
from pyexadis_base import ExaDisNet, DisNetManager, NodeConstraints  # noqa: E402
from pyexadis_utils import insert_frank_read_src, insert_infinite_line  # noqa: E402

# All dataset geometries are confined to the (001) plane.
PLANE_001 = np.array([0.0, 0.0, 1.0])

# All glissile loops share one in-plane Burgers vector on (001).
# With reference sigma_xz < 0, b=[100] loops expand; Proximity collision then
# allows coplanar same-b arms to annihilate when they meet (including via PBC).
BURG_001 = np.array([1.0, 0.0, 0.0], dtype=float)


def _normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n < 1e-15:
        raise ValueError("Zero vector")
    return v / n


def _sample_centers_2d(
    rng: np.random.Generator,
    n: int,
    box: float,
    z: float,
    margin: float,
    min_sep: float,
    max_tries: int = 8000,
) -> np.ndarray:
    """
    Place centers in the z=const plane inside [margin, box-margin]^2.

    Uses a jittered grid first (robust for multi-loop packing), then falls back
    to random sampling if needed.
    """
    lo, hi = margin, box - margin
    if hi <= lo:
        raise ValueError(f"Invalid margin={margin} for box={box}")

    def _ok(c, centers):
        for p in centers:
            dxy = np.abs(c[:2] - p[:2])
            dxy = np.minimum(dxy, box - dxy)
            if np.linalg.norm(dxy) < min_sep:
                return False
        return True

    centers: list[np.ndarray] = []
    if n == 1:
        jitter = rng.uniform(-0.05, 0.05, size=2) * (hi - lo)
        c = np.array([0.5 * box + jitter[0], 0.5 * box + jitter[1], z])
        c[:2] = np.clip(c[:2], lo, hi)
        return np.asarray([c])

    # Jittered grid sized for n points
    nside = int(np.ceil(np.sqrt(n)))
    xs = np.linspace(lo, hi, nside)
    ys = np.linspace(lo, hi, nside)
    grid = np.array([[x, y] for y in ys for x in xs], dtype=float)
    rng.shuffle(grid)
    cell = max((hi - lo) / max(nside, 1), 1e-12)
    for xy in grid:
        if len(centers) >= n:
            break
        jitter = rng.uniform(-0.25, 0.25, size=2) * cell
        cxy = np.clip(xy + jitter, lo, hi)
        c = np.array([cxy[0], cxy[1], z])
        if _ok(c, centers):
            centers.append(c)

    tries = 0
    while len(centers) < n and tries < max_tries:
        tries += 1
        xy = rng.uniform(lo, hi, size=2)
        c = np.array([xy[0], xy[1], z])
        if _ok(c, centers):
            centers.append(c)

    if len(centers) < n:
        raise RuntimeError(
            f"Failed to place {n} planar centers in L={box} with margin={margin}, min_sep={min_sep}"
        )
    return np.asarray(centers)


def radius_for_nloops(base_radius: float, n_loops: int) -> float:
    """Shrink loop radius as count grows so 2D packing remains feasible."""
    if n_loops <= 1:
        return base_radius
    if n_loops <= 3:
        return 0.85 * base_radius
    if n_loops <= 6:
        return 0.65 * base_radius
    return 0.50 * base_radius


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
    plane = _normalize(plane)
    if abs(np.dot(_normalize(burg), plane)) > 1e-4:
        burg = burg - np.dot(burg, plane) * plane
        if np.linalg.norm(burg) < 1e-12:
            raise ValueError("Burgers vector parallel to plane normal")
    e1 = _normalize(burg)
    e2 = _normalize(np.cross(plane, e1))

    nseg = max(12, int(np.ceil(2.0 * np.pi * radius / maxseg)))
    istart = len(nodes)
    theta = np.linspace(0.0, 2.0 * np.pi, nseg, endpoint=False)
    for t in theta:
        p = center + radius * (np.cos(t) * e1 + np.sin(t) * e2)
        nodes.append(np.concatenate((p, [NodeConstraints.UNCONSTRAINED])))
    for i in range(nseg):
        segs.append(np.concatenate(([istart + i, istart + (i + 1) % nseg], burg, plane)))
    return nodes, segs


def build_planar_loops_001(
    box: float,
    n_loops: int,
    radius: float,
    maxseg: float,
    seed: int,
    margin: float,
    min_sep: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    """One or more circular glissile loops on (001), all with the same Burgers vector."""
    rng = np.random.default_rng(seed)
    cell = pyexadis.Cell(h=box * np.eye(3), is_periodic=[1, 1, 1])
    z = 0.5 * box
    centers = _sample_centers_2d(rng, n_loops, box, z, margin, min_sep)
    b = BURG_001.copy()

    nodes, segs = [], []
    loop_meta = []
    for i in range(n_loops):
        # Slight radius jitter for multi-loop diversity
        ri = radius * float(rng.uniform(0.92, 1.08)) if n_loops > 1 else radius
        nodes, segs = insert_circular_glissile_loop(
            cell, nodes, segs, b, PLANE_001, ri, centers[i], maxseg
        )
        loop_meta.append(
            {
                "index": i,
                "center": centers[i].tolist(),
                "radius": float(ri),
                "burgers": b.tolist(),
                "plane": PLANE_001.tolist(),
                "plane_name": "001",
            }
        )

    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "planar_circular_loops_001",
        "n_loops": n_loops,
        "radius": radius,
        "maxseg": maxseg,
        "seed": seed,
        "loops": loop_meta,
        "common_burgers": b.tolist(),
        "loop_kind": "circular_glissile_001",
        "dimensionality": "2D",
        "glide_plane": "001",
        "plane_normal": PLANE_001.tolist(),
        "z_plane": float(z),
    }
    return DisNetManager(G), meta


def build_line_loop_001(
    box: float,
    radius: float,
    maxseg: float,
    seed: int,
    margin: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    """Infinite in-plane line + circular loop, both on (001)."""
    rng = np.random.default_rng(seed)
    cell = pyexadis.Cell(h=box * np.eye(3), is_periodic=[1, 1, 1])
    z = 0.5 * box
    nodes, segs = [], []

    b = BURG_001.copy()
    # Edge line along y (theta=90° from b in the plane)
    origin = np.array([0.35 * box, 0.50 * box, z])
    origin[:2] += rng.uniform(-0.03, 0.03, size=2) * box
    origin[:2] = np.clip(origin[:2], margin, box - margin)
    nodes, segs = insert_infinite_line(
        cell, nodes, segs, b, PLANE_001, origin, theta=90.0, maxseg=maxseg
    )

    center = np.array([0.65 * box, 0.50 * box, z])
    center[:2] += rng.uniform(-0.04, 0.04, size=2) * box
    center[:2] = np.clip(center[:2], margin + radius, box - margin - radius)
    nodes, segs = insert_circular_glissile_loop(
        cell, nodes, segs, b, PLANE_001, radius, center, maxseg
    )

    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "line_loop_001",
        "n_loops": 1,
        "n_lines": 1,
        "radius": radius,
        "maxseg": maxseg,
        "seed": seed,
        "common_burgers": b.tolist(),
        "line": {
            "burgers": b.tolist(),
            "plane": PLANE_001.tolist(),
            "origin": origin.tolist(),
            "theta_deg": 90.0,
        },
        "loop": {
            "center": center.tolist(),
            "burgers": b.tolist(),
            "plane": PLANE_001.tolist(),
            "radius": float(radius),
        },
        "loop_kind": "line_loop_001",
        "dimensionality": "2D",
        "glide_plane": "001",
        "plane_normal": PLANE_001.tolist(),
        "z_plane": float(z),
    }
    return DisNetManager(G), meta


def build_glissile_junction_001(
    box: float,
    seed: int,
    maxseg: float,
) -> tuple[DisNetManager, dict[str, Any]]:
    """Two Frank-Read sources on the (001) plane (in-plane junction interaction)."""
    rng = np.random.default_rng(seed)
    cell = pyexadis.Cell(h=box * np.eye(3), is_periodic=[1, 1, 1])
    z = 0.5 * box
    nodes, segs = [], []

    length = 0.45 * box
    # Same Burgers for both FR sources (glissile on 001); they interact/annihilate
    # under Proximity collision rather than forming a multi-slip junction.
    b = BURG_001.copy()
    center = np.array([0.5 * box, 0.5 * box, z])
    delta = 0.03 * box
    c1 = center + np.array([-delta, 0.0, 0.0])
    c2 = center + np.array([delta, 0.0, 0.0])
    phi1 = 35.0 + float(rng.uniform(-5, 5))
    phi2 = -35.0 + float(rng.uniform(-5, 5))
    numnodes = max(10, int(np.ceil(length / maxseg)) + 1)

    # linedir in plane: rotate [1,0,0] by phi about z
    def ldir(phi_deg):
        ph = phi_deg * np.pi / 180.0
        return np.array([np.cos(ph), np.sin(ph), 0.0])

    nodes, segs = insert_frank_read_src(
        cell, nodes, segs, b, PLANE_001, length, c1, linedir=ldir(phi1), numnodes=numnodes
    )
    nodes, segs = insert_frank_read_src(
        cell, nodes, segs, b, PLANE_001, length, c2, linedir=ldir(phi2), numnodes=numnodes
    )

    # Force all nodes exactly onto z-plane (FR insert is already planar if linedir.z=0)
    for i, node in enumerate(nodes):
        node = np.asarray(node, dtype=float)
        node[2] = z
        nodes[i] = node

    G = ExaDisNet(cell, nodes, segs)
    meta = {
        "generator": "glissile_junction_fr_001",
        "n_loops": 0,
        "n_fr_sources": 2,
        "disloc_length": float(length),
        "phi1_deg": float(phi1),
        "phi2_deg": float(phi2),
        "seed": seed,
        "loop_kind": "glissile_junction_001",
        "dimensionality": "2D",
        "glide_plane": "001",
        "plane_normal": PLANE_001.tolist(),
        "z_plane": float(z),
        "common_burgers": b.tolist(),
        "burgers": [b.tolist(), b.tolist()],
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
    """
    Build 2D (001)-plane geometries for all case types.

    The simulation cell remains 3D cubic (ForceFFT requires 3D PBC), but every
    dislocation node lies on z = L/2 with plane normal [001].
    """
    _ = crystal  # material crystal type is set in solver state; geometry is (001) 2D
    if case_type in (
        "single_loop",
        "double_loop",
        "triple_loop",
        "six_loops",
        "twelve_loops",
        "fov_variant",
    ):
        n = max(n_loops, 1)
        r = radius_for_nloops(radius, n)
        # Keep loops clear of the FOV/box boundary and of each other.
        margin_eff = max(margin, r + 0.04 * box)
        min_sep_eff = min(min_sep, 2.05 * r) if n > 1 else min_sep
        # If still over-constrained, relax separation toward a packable value.
        usable = box - 2.0 * margin_eff
        if n > 1 and min_sep_eff > usable / np.ceil(np.sqrt(n)):
            min_sep_eff = 0.90 * usable / np.ceil(np.sqrt(n))
        return build_planar_loops_001(
            box,
            n,
            r,
            maxseg,
            seed,
            margin_eff,
            min_sep_eff,
        )
    if case_type == "line_loop":
        return build_line_loop_001(box, radius, maxseg, seed, margin)
    if case_type == "glissile_junction":
        return build_glissile_junction_001(box, seed, maxseg)
    raise ValueError(f"Unknown case_type={case_type}")
