"""Initial-geometry builders: glissile loops, periodic lines, placements.

All lengths are in units of burgmag (b).  Loops are shear (glissile) loops:
the Burgers vector lies in the glide plane, so the loop evolves by glide only,
consistent with the SimpleGlide mobility law of the reference configuration.
"""

from typing import List, Tuple
import numpy as np

from . import paths  # noqa: F401
from .config import CaseConfig, LoopSpec, LineSpec
from .reference import REFERENCE, numerical_params

from pydis import DisNode, DisNet, Cell
from framework.disnet_manager import DisNetManager


# ---------------------------------------------------------------------------
# Slip systems (axis-aligned convention of the reference examples: Burgers
# vectors are unit vectors and glide-plane normals are orthogonal axes)
# ---------------------------------------------------------------------------
SLIP_SYSTEMS = {
    # name: (burgers, normal) with b . n = 0  -> resolved by sigma_(b,n)
    "bx_nz": (np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),  # sigma_xz
    "by_nz": (np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])),  # sigma_yz
    "bx_ny": (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])),  # sigma_xy
    "bz_ny": (np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0])),  # sigma_yz
    "by_nx": (np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0])),  # sigma_xy
    "bz_nx": (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0])),  # sigma_xz
}


def loop_n_nodes(radius: float, box_size: float,
                 seg_frac_of_maxseg: float = 0.6,
                 n_min: int = 16, n_max: int = 96) -> int:
    """Number of nodes so segment length ~ seg_frac_of_maxseg * maxseg."""
    maxseg = numerical_params(box_size)["maxseg"]
    n = int(np.ceil(2.0 * np.pi * radius / (seg_frac_of_maxseg * maxseg)))
    return int(np.clip(n, n_min, n_max))


def line_n_nodes(box_size: float, seg_frac_of_maxseg: float = 0.6,
                 n_min: int = 16, n_max: int = 128) -> int:
    maxseg = numerical_params(box_size)["maxseg"]
    n = int(np.ceil(box_size / (seg_frac_of_maxseg * maxseg)))
    return int(np.clip(n, n_min, n_max))


def make_loop_spec(center, radius, system: str, box_size: float) -> LoopSpec:
    b, n = SLIP_SYSTEMS[system]
    return LoopSpec(center=list(map(float, center)), radius=float(radius),
                    burgers=list(b), normal=list(n),
                    n_nodes=loop_n_nodes(radius, box_size))


def make_line_spec(point, direction, burgers, normal, box_size: float) -> LineSpec:
    return LineSpec(point=list(map(float, point)),
                    direction=list(map(float, direction)),
                    burgers=list(map(float, burgers)),
                    normal=list(map(float, normal)),
                    n_nodes=line_n_nodes(box_size))


# ---------------------------------------------------------------------------
# Node/link array construction
# ---------------------------------------------------------------------------
def _plane_axes(normal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    a1 = np.cross(n, [1.0, 0.0, 0.0])
    if np.linalg.norm(a1) < 1e-8:
        a1 = np.cross(n, [0.0, 1.0, 0.0])
    a1 /= np.linalg.norm(a1)
    a2 = np.cross(n, a1)
    return a1, a2


def loop_nodes_links(spec: LoopSpec, id_offset: int) -> Tuple[np.ndarray, np.ndarray]:
    """Discretize a circular loop into nodes and links.

    Links carry the Burgers vector and the glide-plane normal.  The loop is
    oriented counter-clockwise about the plane normal.
    """
    n = np.asarray(spec.normal, dtype=float)
    n = n / np.linalg.norm(n)
    b = np.asarray(spec.burgers, dtype=float)
    a1, a2 = _plane_axes(n)
    N = spec.n_nodes
    theta = np.arange(N) * 2.0 * np.pi / N
    pos = (np.asarray(spec.center)[None, :]
           + spec.radius * (np.outer(np.cos(theta), a1)
                            + np.outer(np.sin(theta), a2)))
    rn = np.hstack([pos, np.full((N, 1), int(DisNode.Constraints.UNCONSTRAINED))])
    links = np.zeros((N, 8))
    for i in range(N):
        links[i, 0] = id_offset + i
        links[i, 1] = id_offset + (i + 1) % N
        links[i, 2:5] = b
        links[i, 5:8] = n
    return rn, links


def line_nodes_links(spec: LineSpec, box_size: List[float],
                     id_offset: int) -> Tuple[np.ndarray, np.ndarray]:
    """Discretize a straight line threading the periodic box.

    The line closes on itself through the periodic boundary, so every node
    has exactly two arms and Burgers conservation holds without pinning.
    """
    t = np.asarray(spec.direction, dtype=float)
    if np.count_nonzero(np.abs(t) > 1e-12) != 1:
        raise ValueError("line direction must be axis-aligned for a periodic line")
    axis = int(np.abs(t).argmax())
    t = t / np.linalg.norm(t)
    L = float(box_size[axis])
    N = spec.n_nodes
    # span the box symmetrically about the origin (geometry is specified
    # relative to the box center); the point's own component along the line
    # direction is irrelevant for a periodic line
    s = -L / 2.0 + np.arange(N) * L / N
    point = np.asarray(spec.point, dtype=float).copy()
    point[axis] = 0.0
    pos = point[None, :] + np.outer(s, t)
    rn = np.hstack([pos, np.full((N, 1), int(DisNode.Constraints.UNCONSTRAINED))])
    n = np.asarray(spec.normal, dtype=float)
    n = n / np.linalg.norm(n)
    links = np.zeros((N, 8))
    for i in range(N):
        links[i, 0] = id_offset + i
        links[i, 1] = id_offset + (i + 1) % N
        links[i, 2:5] = np.asarray(spec.burgers, dtype=float)
        links[i, 5:8] = n
    return rn, links


def build_network(config: CaseConfig) -> DisNetManager:
    """Assemble the DisNetManager for a case from its geometry specs."""
    L = np.asarray(config.box_size, dtype=float)
    cell = Cell(h=np.diag(L), is_periodic=[REFERENCE["pbc"]] * 3)

    rn_list, links_list = [], []
    offset = 0
    for spec in config.loops:
        rn, links = loop_nodes_links(spec, offset)
        rn_list.append(rn)
        links_list.append(links)
        offset += rn.shape[0]
    for spec in config.lines:
        rn, links = line_nodes_links(spec, config.box_size, offset)
        rn_list.append(rn)
        links_list.append(links)
        offset += rn.shape[0]

    if not rn_list:
        raise ValueError("case has no loops and no lines")

    rn = np.vstack(rn_list)
    links = np.vstack(links_list)
    # shift geometry (specified relative to box center at 0) to the cell center
    rn[:, 0:3] += cell.center()
    return DisNetManager(DisNet(cell=cell, rn=rn, links=links))


# ---------------------------------------------------------------------------
# Random multi-loop placement
# ---------------------------------------------------------------------------
def place_loops_random(n_loops: int, box_size: float, radius: float,
                       systems: List[str], seed: int,
                       min_gap: float = 2.0, boundary_margin: float = 2.0,
                       max_tries: int = 20000) -> List[LoopSpec]:
    """Random non-overlapping loop placement with a seeded RNG.

    Loops are treated as spheres of their radius for the separation test
    (minimum-image distance under PBC), which prevents artificial overlap
    and excessive proximity to periodic images at t=0.  Centers are kept
    at least (radius + boundary_margin) away from the box faces so that the
    initial loops are wholly inside the primary cell.
    """
    rng = np.random.default_rng(seed)
    L = float(box_size)
    lo = -L / 2 + radius + boundary_margin
    hi = L / 2 - radius - boundary_margin
    if hi <= lo:
        raise ValueError(
            f"box {L} too small for loops of radius {radius} with margin")
    centers: List[np.ndarray] = []
    specs: List[LoopSpec] = []
    tries = 0
    while len(specs) < n_loops:
        tries += 1
        if tries > max_tries:
            raise RuntimeError("could not place loops without overlap; "
                               "reduce n_loops or radius")
        c = rng.uniform(lo, hi, size=3)
        ok = True
        for c2 in centers:
            d = c - c2
            d -= L * np.round(d / L)   # minimum image
            if np.linalg.norm(d) < 2.0 * radius + min_gap:
                ok = False
                break
        if not ok:
            continue
        system = systems[len(specs) % len(systems)]
        centers.append(c)
        specs.append(make_loop_spec(c, radius, system, L))
    return specs
