"""Initial dislocation geometries for the DDD dataset.

Builds glissile (shear) loops, PBC-periodic infinite lines and Frank-Read
sources, and assembles them into an ExaDiS network.  Loops are discretized with
the reference ``maxseg``, and their Burgers vector always lies in their glide
plane so that they are glissile.

Geometry is generated in nominal units and converted to ExaDiS length units (b)
when the network is built.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from data_ddd.config import CaseConfig, LineSpec, LoopSpec, StressSpec
from data_ddd.reference import FCC_SLIP_SYSTEMS

UNCONSTRAINED = 0
PINNED_NODE = 7

# offset (in units of the loop radius) between junction loops along the line
# where their glide planes intersect
JUNCTION_STAGGER = 0.05


def slip_system(index: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return the normalized (Burgers vector, plane normal) of an FCC system."""
    b, n = FCC_SLIP_SYSTEMS[index % len(FCC_SLIP_SYSTEMS)]
    b = np.asarray(b, dtype=float)
    n = np.asarray(n, dtype=float)
    return b / np.linalg.norm(b), n / np.linalg.norm(n)


def plane_basis(normal: Sequence[float], burgers: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    """Orthonormal in-plane basis (screw direction, edge direction)."""
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    u = np.asarray(burgers, dtype=float)
    u = u - np.dot(u, n) * n
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    return u, v / np.linalg.norm(v)


def expansion_sense(burgers: Sequence[float], plane: Sequence[float], stress: StressSpec) -> int:
    """Sign of the Burgers vector that makes a right-handed loop expand.

    For a loop traversed right-handed about ``+n`` the Peach-Koehler force has
    an outward radial component ``-b.sigma.n``; the loop therefore expands when
    ``b.sigma.n < 0``.
    """
    b = np.asarray(burgers, dtype=float)
    n = np.asarray(plane, dtype=float)
    n = n / np.linalg.norm(n)
    tau = float(b @ stress.tensor() @ n)
    if tau == 0.0:
        return 1
    return -1 if tau > 0.0 else 1


def rank_systems(stress: StressSpec) -> List[int]:
    """Slip-system indices ordered by decreasing |Schmid factor|.

    Loops are preferentially assigned to well-loaded systems so that they glide
    instead of collapsing under their own line tension.
    """
    scores = []
    for index in range(len(FCC_SLIP_SYSTEMS)):
        b, n = slip_system(index)
        scores.append((abs(stress.schmid_factor(b, n)), -index, index))
    scores.sort(reverse=True)
    return [s[2] for s in scores]


def select_line_loop_systems(
    stress: StressSpec, n_loops: int, line_rank: int = 0
) -> Tuple[int, List[int]]:
    """Slip systems of a line-loop case.

    The line takes a well-loaded system (``line_rank`` counts from the best
    oriented one); the loops take the next best-loaded systems whose glide
    planes intersect the line's plane, so that the expanding loops actually run
    into the line instead of gliding parallel to it.
    """
    ranked = rank_systems(stress)
    line_sys = int(ranked[line_rank % len(ranked)])
    _, line_plane = slip_system(line_sys)
    loop_systems: List[int] = []
    for index in ranked:
        if index == line_sys:
            continue
        _, n = slip_system(index)
        if abs(float(n @ line_plane)) > 0.99:
            continue
        loop_systems.append(int(index))
        if len(loop_systems) == n_loops:
            break
    while len(loop_systems) < n_loops:
        loop_systems.append(int(ranked[len(loop_systems) % len(ranked)]))
    return line_sys, loop_systems


def loop_node_count(radius_b: float, maxseg_b: float, minimum: int = 8) -> int:
    n = int(np.ceil(2.0 * np.pi * radius_b / maxseg_b))
    return max(minimum, n)


def build_loop(
    loop: LoopSpec,
    unit_b: float,
    maxseg_b: float,
    nodes: List[np.ndarray],
    segs: List[np.ndarray],
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Append a circular glissile loop to ``nodes``/``segs`` (ExaDiS b units)."""
    center = np.asarray(loop.center, dtype=float) * unit_b
    radius = float(loop.radius) * unit_b
    burg = np.asarray(loop.burgers, dtype=float)
    burg = loop.sense * burg / np.linalg.norm(burg)
    plane = np.asarray(loop.plane, dtype=float)
    plane = plane / np.linalg.norm(plane)

    if abs(float(np.dot(burg, plane))) > 1e-8:
        raise ValueError(
            "Loop Burgers vector %r is not contained in glide plane %r"
            % (loop.burgers, loop.plane)
        )

    u, v = plane_basis(plane, burg)
    n_nodes = loop.n_nodes or loop_node_count(radius, maxseg_b)
    loop.n_nodes = n_nodes

    istart = len(nodes)
    theta = 2.0 * np.pi * np.arange(n_nodes) / n_nodes
    for t in theta:
        p = center + radius * (np.cos(t) * u + np.sin(t) * v)
        nodes.append(np.concatenate((p, [UNCONSTRAINED])))
    for i in range(n_nodes):
        segs.append(
            np.concatenate(([istart + i, istart + (i + 1) % n_nodes], burg, plane))
        )
    return nodes, segs


def build_line(
    line: LineSpec,
    cell,
    unit_b: float,
    maxseg_b: float,
    nodes: List[np.ndarray],
    segs: List[np.ndarray],
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Append a dislocation line to ``nodes``/``segs`` using ExaDiS utilities."""
    from pyexadis_utils import insert_frank_read_src, insert_infinite_line

    origin = np.asarray(line.origin, dtype=float) * unit_b
    burg = np.asarray(line.burgers, dtype=float)
    burg = line.sense * burg / np.linalg.norm(burg)
    plane = np.asarray(line.plane, dtype=float)
    plane = plane / np.linalg.norm(plane)

    n_before = len(nodes)
    if line.kind == "infinite":
        nodes, segs = insert_infinite_line(
            cell, nodes, segs, burg, plane, origin, theta=line.theta, maxseg=maxseg_b
        )
    elif line.kind == "frank_read":
        length = float(line.length) * unit_b
        n_nodes = line.n_nodes or max(6, int(np.ceil(length / maxseg_b)) + 1)
        nodes, segs = insert_frank_read_src(
            cell, nodes, segs, burg, plane, length, origin,
            theta=line.theta, numnodes=n_nodes,
        )
    else:
        raise ValueError("Unknown line kind '%s'" % line.kind)
    line.n_nodes = len(nodes) - n_before
    return nodes, segs


def build_network(config: CaseConfig):
    """Build the ExaDiS network (``DisNetManager``) of a case configuration."""
    import pyexadis
    from pyexadis_base import DisNetManager, ExaDisNet

    unit_b = config.unit_b
    maxseg_b = float(config.physics["discretization"]["maxseg"])
    h = np.diag(config.box_b)
    cell = pyexadis.Cell(h=h, is_periodic=list(config.pbc))

    nodes: List[np.ndarray] = []
    segs: List[np.ndarray] = []
    for loop in config.loops:
        build_loop(loop, unit_b, maxseg_b, nodes, segs)
    for line in config.lines:
        build_line(line, cell, unit_b, maxseg_b, nodes, segs)

    if not nodes:
        raise ValueError("Case '%s' produced an empty dislocation network" % config.name)

    net = ExaDisNet(cell, nodes, segs)
    return DisNetManager(net), cell


def network_arrays(config: CaseConfig) -> Dict[str, Any]:
    """Build the raw node/segment arrays of a case without instantiating ExaDiS.

    Only supported for loop-only configurations; line geometries require the
    ExaDiS periodic-image utilities.
    """
    unit_b = config.unit_b
    maxseg_b = float(config.physics["discretization"]["maxseg"])
    nodes: List[np.ndarray] = []
    segs: List[np.ndarray] = []
    for loop in config.loops:
        build_loop(loop, unit_b, maxseg_b, nodes, segs)
    return {
        "nodes": np.array(nodes) if nodes else np.zeros((0, 4)),
        "segs": np.array(segs) if segs else np.zeros((0, 8)),
    }


# ---------------------------------------------------------------------------
# Placement helpers used to build the dataset catalog
# ---------------------------------------------------------------------------
def _lattice_sites(n_sites: int, box: np.ndarray, margin: float) -> np.ndarray:
    """Evenly spread ``n_sites`` sites in the box, keeping a boundary margin."""
    if n_sites == 1:
        return np.array([0.5 * box])
    # choose a grid (nx, ny, nz) with nx*ny*nz >= n_sites, as cubic as possible
    best = None
    for nx in range(1, n_sites + 1):
        for ny in range(1, n_sites + 1):
            for nz in range(1, n_sites + 1):
                if nx * ny * nz < n_sites:
                    continue
                spread = max(nx, ny, nz) - min(nx, ny, nz)
                waste = nx * ny * nz - n_sites
                key = (waste, spread, nx * ny * nz)
                if best is None or key < best[0]:
                    best = (key, (nx, ny, nz))
    nx, ny, nz = best[1]
    lo = margin
    sites = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                frac = np.array(
                    [
                        (i + 0.5) / nx,
                        (j + 0.5) / ny,
                        (k + 0.5) / nz,
                    ]
                )
                sites.append(lo + frac * (box - 2.0 * lo))
    return np.array(sites[:n_sites])


def place_loops(
    n_loops: int,
    box: Sequence[float],
    radius: float,
    stress: StressSpec,
    seed: int,
    interaction: str = "mixed",
    jitter: float = 0.10,
    systems: Sequence[int] | None = None,
    spread: float | None = None,
) -> List[LoopSpec]:
    """Generate loop specifications (nominal units) for a case.

    ``interaction`` controls how slip systems and positions are correlated:

    * ``isolated``  - loops on distinct slip systems, evenly spread out
    * ``coplanar``  - loops sharing one slip system, centers in a common glide
      plane so that they meet and react while gliding
    * ``dipole``    - coplanar loops with alternating Burgers-vector sign
    * ``junction``  - loops on intersecting {111} planes placed close enough to
      form junctions
    * ``mixed``     - loops cycling through all 12 slip systems
    """
    rng = np.random.default_rng(seed)
    box = np.asarray(box, dtype=float)
    margin = 1.6 * radius
    sites = _lattice_sites(n_loops, box, margin)

    ranked = rank_systems(stress)

    if interaction in ("coplanar", "dipole"):
        # a well-loaded system, chosen among the four best-oriented ones
        sys_index = int(ranked[int(rng.integers(0, 4))])
        b, n = slip_system(sys_index)
        u, v = plane_basis(n, b)
        center = 0.5 * box
        # centers spread inside the common glide plane, close enough that a
        # moderate expansion brings the loops into contact
        span = (spread if spread is not None else 2.3) * radius
        offsets = (np.arange(n_loops) - 0.5 * (n_loops - 1)) * span
        loops = []
        for i, off in enumerate(offsets):
            perp = ((i % 3) - 1) * span * (1 if n_loops > 3 else 0)
            pos = center + off * u + perp * v
            pos += 0.2 * jitter * radius * rng.standard_normal(3) if jitter else 0.0
            sense = expansion_sense(b, n, stress)
            if interaction == "dipole" and i % 2:
                sense = -sense
            loops.append(
                LoopSpec(
                    center=pos,
                    radius=radius,
                    burgers=b,
                    plane=n,
                    slip_system=sys_index,
                    sense=sense,
                )
            )
        return loops

    if interaction == "junction" and systems is None:
        # Loops on intersecting {111} planes.  Both glide planes contain the
        # intersection line L; each loop is centered at ~1.15 R from L, inside
        # its own plane.  Expanding loops therefore reach L at the same place at
        # the same time and make contact along it, which is what allows a
        # junction to form.  (Offsetting the loops *along* L instead makes their
        # intersections with L drift apart as they grow, and they never meet.)
        systems, planes = [], []
        for index in ranked:
            _, n = slip_system(index)
            if any(abs(float(n @ p)) > 0.99 for p in planes):
                continue
            systems.append(int(index))
            planes.append(n)
            if len(systems) == n_loops:
                break
        while len(systems) < n_loops:
            systems.append(int(ranked[len(systems) % len(ranked)]))
            planes.append(slip_system(systems[-1])[1])
        axis = np.cross(planes[0], planes[1 % len(planes)])
        if np.linalg.norm(axis) < 1e-8:
            axis = np.array([0.0, 0.0, 1.0])
        axis = axis / np.linalg.norm(axis)
        center = 0.5 * box
        # 1.30 R lets both fronts reach the intersection line together; this
        # value is calibrated to produce a <100> junction (see README)
        standoff = (spread if spread is not None else 1.30) * radius
        loops = []
        for i in range(n_loops):
            b, n = slip_system(systems[i])
            # in-plane direction perpendicular to the intersection line
            w = np.cross(axis, n)
            w = w / np.linalg.norm(w)
            sign = 1.0 if i % 2 == 0 else -1.0
            # a small stagger along L keeps the contact from being perfectly
            # symmetric, but it must stay small or the loops miss each other
            pos = (
                center
                + sign * standoff * w
                + (i - 0.5 * (n_loops - 1)) * JUNCTION_STAGGER * radius * axis
            )
            loops.append(
                LoopSpec(
                    center=pos,
                    radius=radius,
                    burgers=b,
                    plane=n,
                    slip_system=int(systems[i]),
                    sense=expansion_sense(b, n, stress),
                )
            )
        return loops

    if systems is None:
        if interaction == "junction":
            # well-loaded systems with distinct glide planes, so that the loops
            # meet on intersecting {111} planes and can form junctions
            systems, planes = [], []
            for index in ranked:
                _, n = slip_system(index)
                if any(abs(float(n @ p)) > 0.99 for p in planes):
                    continue
                systems.append(index)
                planes.append(n)
                if len(systems) == n_loops:
                    break
            while len(systems) < n_loops:
                systems.append(ranked[len(systems) % len(ranked)])
        elif interaction == "isolated":
            systems = [int(ranked[i % len(ranked)]) for i in range(n_loops)]
        elif n_loops >= len(FCC_SLIP_SYSTEMS):
            # mixed: cover every slip system when there are enough loops
            systems = [i % len(FCC_SLIP_SYSTEMS) for i in range(n_loops)]
        else:
            # mixed: spread over the best-loaded systems in a seeded order
            pool = ranked[: max(n_loops, min(8, len(ranked)))]
            systems = [int(p) for p in rng.permutation(pool)[:n_loops]]

    order = rng.permutation(len(sites))
    loops = []
    for i in range(n_loops):
        pos = sites[order[i]].copy()
        if jitter:
            pos = pos + jitter * radius * rng.standard_normal(3)
        pos = np.clip(pos, margin, box - margin)
        b, n = slip_system(int(systems[i]))
        loops.append(
            LoopSpec(
                center=pos,
                radius=radius,
                burgers=b,
                plane=n,
                slip_system=int(systems[i]),
                sense=expansion_sense(b, n, stress),
            )
        )
    return loops


def place_line_loop_case(
    n_loops: int,
    box: Sequence[float],
    radius: float,
    stress: StressSpec,
    seed: int,
    line_rank: int = 0,
    theta: float = 0.0,
    kind: str = "infinite",
    approach: float = 1.2,
) -> Tuple[LineSpec, List[LoopSpec]]:
    """Line + loops placed so that the expanding loops run into the line.

    Each loop is centered at ``approach * radius`` from the point where the line
    pierces the loop's glide plane, so the line starts just outside the loop and
    the two react once the loop has expanded by ~20%.
    """
    rng = np.random.default_rng(seed)
    box = np.asarray(box, dtype=float)
    line_sys, loop_systems = select_line_loop_systems(stress, n_loops, line_rank=line_rank)
    line = place_line(box, stress, seed, system=line_sys, theta=theta, kind=kind)
    line_origin = np.asarray(line.origin, dtype=float)
    lb, ln = slip_system(line_sys)
    lu, lv = plane_basis(ln, lb)
    ldir = np.cos(np.deg2rad(theta)) * lu + np.sin(np.deg2rad(theta)) * lv

    loops: List[LoopSpec] = []
    spacing = 2.4 * radius
    for i, index in enumerate(loop_systems):
        b, n = slip_system(index)
        # a point on the line, spread out so the loops do not overlap
        pierce = line_origin + (i - 0.5 * (len(loop_systems) - 1)) * spacing * ldir
        u, v = plane_basis(n, b)
        angle = 2.0 * np.pi * i / max(len(loop_systems), 1) + 0.3 * rng.standard_normal()
        w = np.cos(angle) * u + np.sin(angle) * v
        center = pierce + approach * radius * w
        # wrap rather than clip: the cell is periodic, so wrapping preserves the
        # loop's position relative to the (equally periodic) line
        center = np.mod(center, box)
        loops.append(
            LoopSpec(
                center=center,
                radius=radius,
                burgers=b,
                plane=n,
                slip_system=int(index),
                sense=expansion_sense(b, n, stress),
            )
        )
    return line, loops


def place_line(
    box: Sequence[float],
    stress: StressSpec,
    seed: int,
    system: int,
    theta: float = 0.0,
    kind: str = "infinite",
    offset: Sequence[float] | None = None,
) -> LineSpec:
    """Generate a dislocation-line specification (nominal units)."""
    rng = np.random.default_rng(seed)
    box = np.asarray(box, dtype=float)
    b, n = slip_system(system)
    origin = 0.5 * box + (np.asarray(offset, dtype=float) if offset is not None else 0.0)
    origin = origin + 0.01 * float(np.min(box)) * rng.standard_normal(3)
    # a straight line glides in the direction that lowers its energy; the sign
    # only sets the glide direction, so keep the expansion convention
    sense = expansion_sense(b, n, stress)
    return LineSpec(
        origin=origin,
        burgers=b,
        plane=n,
        kind=kind,
        theta=theta,
        slip_system=system,
        sense=sense,
    )
