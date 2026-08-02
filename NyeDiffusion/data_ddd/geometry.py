"""Initial geometry builders for glissile-loop DDD cases."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pyexadis
from pyexadis_base import DisNetManager, ExaDisNet, NodeConstraints
from pyexadis_utils import insert_frank_read_src, insert_infinite_line


def _make_cell(box_size: float, pbc: bool = True) -> pyexadis.Cell:
    return pyexadis.Cell(h=box_size * np.eye(3), is_periodic=[pbc, pbc, pbc])


def build_prismatic_loops(cfg: Dict[str, Any]) -> DisNetManager:
    geom, disc = cfg["geometry"], cfg["discretization"]
    G = ExaDisNet()
    G.generate_prismatic_config(
        geom["crystal"], geom["box_size"], geom["num_loops"],
        geom["loop_radius"], disc["maxseg"], seed=geom["seed"],
    )
    return DisNetManager(G)


def build_line_loop(cfg: Dict[str, Any]) -> DisNetManager:
    """One prismatic loop plus one infinite dislocation line (line-loop interaction)."""
    geom, disc = cfg["geometry"], cfg["discretization"]
    box = geom["box_size"]
    cell = _make_cell(box)
    nodes: List[np.ndarray] = []
    segs: List[np.ndarray] = []

    # BCC glissile system: 1/2<111>{110}
    burg = np.array([1.0, 1.0, 1.0])
    plane = np.array([0.0, -1.0, 1.0])
    center = np.array(cell.center()) + np.array([0.15 * box, 0.0, 0.0])
    insert_frank_read_src(
        cell, nodes, segs, burg, plane, 0.35 * box, center,
        theta=0.0, numnodes=12,
    )

    line_origin = np.array(cell.center()) - np.array([0.15 * box, 0.0, 0.0])
    insert_infinite_line(
        cell, nodes, segs, -burg, plane, line_origin,
        theta=45.0, maxseg=disc["maxseg"],
    )

    rn = np.array(nodes)
    links = np.array(segs)
    return DisNetManager(ExaDisNet(cell, rn, links))


def build_double_junction(cfg: Dict[str, Any]) -> DisNetManager:
    """Two intersecting dislocation lines (binary junction interaction)."""
    geom = cfg["geometry"]
    box = geom["box_size"]
    # DDD_FFT elasticity requires periodic boundaries
    cell = _make_cell(box, pbc=True)
    center = np.array(cell.center())
    z0 = 0.12 * box
    b1 = np.array([-1.0, 1.0, 1.0])
    b2 = np.array([1.0, -1.0, 1.0])

    rn = np.array([
        [0.0, -z0, -z0, NodeConstraints.PINNED_NODE],
        [0.0, 0.0, 0.0, NodeConstraints.UNCONSTRAINED],
        [0.0, z0, z0, NodeConstraints.PINNED_NODE],
        [-z0, 0.0, -z0, NodeConstraints.PINNED_NODE],
        [0.0, 0.0, 0.0, NodeConstraints.UNCONSTRAINED],
        [z0, 0.0, z0, NodeConstraints.PINNED_NODE],
    ], dtype=float)
    rn[:, :3] += center

    xi1, xi2 = rn[2, :3] - rn[1, :3], rn[5, :3] - rn[4, :3]
    n1 = np.cross(b1, xi1)
    n2 = np.cross(b2, xi2)
    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)
    links = np.zeros((4, 8))
    links[0] = np.concatenate(([0, 1], b1, n1))
    links[1] = np.concatenate(([1, 2], b1, n1))
    links[2] = np.concatenate(([3, 4], b2, n2))
    links[3] = np.concatenate(([4, 5], b2, n2))
    return DisNetManager(ExaDisNet(cell, rn, links))


BUILDERS = {
    "single_loop": build_prismatic_loops,
    "double_loop": build_prismatic_loops,
    "triple_loop": build_prismatic_loops,
    "six_loop": build_prismatic_loops,
    "twelve_loop": build_prismatic_loops,
    "line_loop": build_line_loop,
    "binary_junction": build_double_junction,
}


def build_network(cfg: Dict[str, Any]) -> DisNetManager:
    case_type = cfg["geometry"]["case_type"]
    builder = BUILDERS.get(case_type, build_prismatic_loops)
    return builder(cfg)
