#!/usr/bin/env python3
"""Generate validated, elasticity-enabled SimpleGlide DDD datasets with ExaDiS.

The reference paths named in the accompanying README are not part of this
checkout.  Consequently, ``REFERENCE_SIMPLEGLIDE`` records the closest
in-repository OpenDiS example used as the frozen solver baseline.  Do not use
this program to claim byte-for-byte equivalence with an unavailable reference.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for relative in ("python", "lib", "core/pydis/python", "core/exadis/python"):
    sys.path.insert(0, str(ROOT / relative))

REFERENCE_SIMPLEGLIDE = {
    "source": "examples/01_loop/test_disl_loop_exadis.py",
    "elasticity": {"force_mode": "LineTension", "core_energy": 1.0e6},
    "mobility": {"law": "SimpleGlide"},
    "time_integration": {"integrator": "EulerForward", "dt_s": 1.0e-9},
    "collision": {"mode": "Retroactive"},
    "topology": None,
    "remesh": None,
    "material": {
        "burgmag_m": 3.0e-10, "mu_pa": 160.0e9, "nu": 0.31, "core_a": 0.01,
        "maxseg": 0.3, "minseg": 0.1, "rann": 0.02,
    },
    "boundary_conditions": {"periodic": [True, True, True]},
    "output": {"snapshot_format": "ParaDiS .data"},
    "applied_stress_voigt_order": ["xx", "yy", "zz", "yz", "xz", "xy"],
}


@dataclass(frozen=True)
class CaseSpec:
    name: str
    geometry: str
    loop_count: int
    box_size: float
    field_of_view: float
    stress_scale: float
    seed: int
    steps: int = 30
    output_frequency: int = 5
    radius: float = 4.0


DEFAULT_CASES = (
    CaseSpec("single-l01-b032-fov016-s050-seed101", "loops", 1, 32, 16, .50, 101),
    CaseSpec("double-l02-b032-fov020-s100-seed102", "loops", 2, 32, 20, 1.00, 102),
    CaseSpec("triple-l03-b032-fov024-s150-seed103", "loops", 3, 32, 24, 1.50, 103),
    CaseSpec("six-l06-b064-fov040-s075-seed106", "loops", 6, 64, 40, .75, 106, radius=6),
    CaseSpec("twelve-l12-b128-fov080-s125-seed112", "loops", 12, 128, 80, 1.25, 112, radius=9),
    CaseSpec("line-loop-l01-b032-fov024-s100-seed121", "line_loop", 1, 32, 24, 1.00, 121),
)


def _json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def stress_tensor(scale: float) -> np.ndarray:
    """Scale the reference biaxial normal stress without changing its loading mode."""
    return scale * np.array([1.0e6, 1.0e6, 0.0, 0.0, 0.0, 0.0])


def loop_centers(count: int, box: float, radius: float, seed: int) -> list[np.ndarray]:
    """Deterministic separated centers, with a full-radius PBC safety margin."""
    margin = radius + max(2.0, .10 * box)
    if 2 * margin >= box:
        raise ValueError("loop radius leaves no boundary clearance")
    grid = int(np.ceil(count ** (1 / 3)))
    values = np.linspace(margin, box - margin, grid)
    candidates = [np.array(p, dtype=float) for p in np.ndindex(grid, grid, grid)
                  for p in [(values[p[0]], values[p[1]], values[p[2]])]]
    rng = np.random.default_rng(seed)
    rng.shuffle(candidates)
    selected: list[np.ndarray] = []
    minimum = 2.4 * radius
    for candidate in candidates:
        if all(np.linalg.norm(candidate - old) >= minimum for old in selected):
            selected.append(candidate)
            if len(selected) == count:
                return selected
    raise ValueError("cannot position separated loops in selected box")


def circle_nodes(center: np.ndarray, radius: float, nsegments: int = 20) -> np.ndarray:
    angle = np.arange(nsegments) * 2.0 * np.pi / nsegments
    return np.column_stack((
        center[0] + radius * np.cos(angle),
        center[1] + radius * np.sin(angle),
        np.full(nsegments, center[2]),
        np.zeros(nsegments),
    ))


def build_geometry(spec: CaseSpec) -> tuple[np.ndarray, np.ndarray, list[list[int]]]:
    """Return ExaDiS node/segment arrays and component segment indices."""
    nodes: list[np.ndarray] = []
    segs: list[np.ndarray] = []
    components: list[list[int]] = []
    b = np.array([1.0, 0.0, 0.0])
    plane = np.array([0.0, 0.0, 1.0])
    radius = spec.radius
    for center in loop_centers(spec.loop_count, spec.box_size, radius, spec.seed):
        start_node, start_seg = len(nodes), len(segs)
        loop = circle_nodes(center, radius)
        nodes.extend(loop)
        for i in range(len(loop)):
            segs.append(np.r_[start_node + i, start_node + (i + 1) % len(loop), b, plane])
        components.append(list(range(start_seg, len(segs))))

    if spec.geometry == "line_loop":
        # A pinned finite line follows the existing Frank--Read example's
        # representation while retaining the baseline SimpleGlide modules.
        length, nline = .45 * spec.box_size, 9
        y = spec.box_size * .5
        z = spec.box_size * .5 + 1.6 * radius
        start_node, start_seg = len(nodes), len(segs)
        for i in range(nline):
            constraint = 7 if i in (0, nline - 1) else 0
            nodes.append(np.array([spec.box_size * .5 - length / 2 + length * i / (nline - 1),
                                   y, z, constraint], dtype=float))
        for i in range(nline - 1):
            segs.append(np.r_[start_node + i, start_node + i + 1, b, plane])
        components.append(list(range(start_seg, len(segs))))

    return np.asarray(nodes), np.asarray(segs), components


def segment_distance(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> float:
    """Shortest distance of two 3D line segments (Ericson, RTCD)."""
    u, v, w = b - a, d - c, a - c
    aa, bb, cc, dd, ee = np.dot(u, u), np.dot(u, v), np.dot(v, v), np.dot(u, w), np.dot(v, w)
    denom = aa * cc - bb * bb
    if denom < 1e-14:
        sc, tc = 0.0, np.clip(ee / cc if cc else 0.0, 0.0, 1.0)
    else:
        sc, tc = np.clip((bb * ee - cc * dd) / denom, 0.0, 1.0), np.clip((aa * ee - bb * dd) / denom, 0.0, 1.0)
    return float(np.linalg.norm(w + sc * u - tc * v))


def validate_geometry(nodes: np.ndarray, segs: np.ndarray, components: list[list[int]],
                      spec: CaseSpec) -> dict:
    issues: list[str] = []
    if nodes.ndim != 2 or nodes.shape[1] != 4 or segs.ndim != 2 or segs.shape[1] != 8:
        issues.append("invalid ExaDiS node/segment array shape")
    endpoints = segs[:, :2].astype(int)
    if np.any(endpoints < 0) or np.any(endpoints >= len(nodes)) or np.any(endpoints[:, 0] == endpoints[:, 1]):
        issues.append("invalid node or segment connectivity")
    duplicate_links = len({tuple(sorted(pair)) for pair in endpoints}) != len(endpoints)
    if duplicate_links:
        issues.append("duplicate links")
    duplicates = len(np.unique(np.round(nodes[:, :3], 12), axis=0)) != len(nodes)
    if duplicates:
        issues.append("duplicate node positions")
    lengths = np.linalg.norm(nodes[endpoints[:, 1], :3] - nodes[endpoints[:, 0], :3], axis=1)
    if np.any(lengths < 1e-8):
        issues.append("zero-length or near-zero segment")
    b, p = segs[:, 2:5], segs[:, 5:8]
    if np.any(np.linalg.norm(p, axis=1) < 1e-12) or np.any(np.abs(np.sum(b * p, axis=1)) > 1e-8):
        issues.append("invalid glide-plane definitions")
    closure_failures: list[int] = []
    for node in range(len(nodes)):
        closure = np.zeros(3)
        for segment, (first, second) in enumerate(endpoints):
            if node == first:
                closure += b[segment]
            elif node == second:
                closure -= b[segment]
        # The only non-closed endpoints are explicit pinned Frank--Read anchors.
        if nodes[node, 3] != 7 and np.linalg.norm(closure) > 1e-8:
            closure_failures.append(node)
    if closure_failures:
        issues.append(f"inconsistent Burgers vectors at free nodes: {closure_failures}")
    clearance = min(np.min(nodes[:, :3]), spec.box_size - np.max(nodes[:, :3]))
    # The center-placement rule guarantees this safety distance after including
    # the loop radius; require a meaningful gap rather than a full extra radius.
    if clearance < max(.10 * spec.box_size, .50 * spec.radius) - 1e-8:
        issues.append("loop too close to a periodic image or boundary")
    component_for_seg = {s: i for i, group in enumerate(components) for s in group}
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            if component_for_seg[i] == component_for_seg[j]:
                continue
            if segment_distance(nodes[endpoints[i, 0], :3], nodes[endpoints[i, 1], :3],
                                nodes[endpoints[j, 0], :3], nodes[endpoints[j, 1], :3]) < .05 * spec.radius:
                issues.append(f"unintended component intersection: segments {i}, {j}")
                break
    return {
        "valid": not issues, "issues": issues, "node_count": int(len(nodes)),
        "segment_count": int(len(segs)), "minimum_segment_length": float(lengths.min()),
        "minimum_boundary_clearance": float(clearance), "checked": [
            "connectivity", "segment_lengths", "duplicate_nodes_links", "burgers_plane_consistency",
            "box_bounds", "intersections", "periodic_image_clearance",
        ],
        "burgers_closure": {
            "free_node_violations": closure_failures,
            "pinned_endpoint_exception": "allowed only for the explicit finite line in line_loop cases",
        },
    }


def case_metadata(spec: CaseSpec, validation: dict) -> dict:
    return {
        "case": asdict(spec),
        "box": {"cell_matrix": (np.eye(3) * spec.box_size).tolist(), "dimensions": 3,
                "periodic": [True, True, True], "field_of_view": spec.field_of_view},
        "applied_stress_pa": stress_tensor(spec.stress_scale).tolist(),
        "reference_baseline": REFERENCE_SIMPLEGLIDE,
        "geometry_validation": validation,
        "provenance_warning": (
            "The user-specified Nye_Disloc_Distance reference was unavailable in this checkout. "
            "This configuration is frozen from OpenDiS examples/01_loop/test_disl_loop_exadis.py."
        ),
    }


def write_case(spec: CaseSpec, root: Path) -> Path:
    path = root / spec.name
    path.mkdir(parents=True, exist_ok=True)
    nodes, segs, components = build_geometry(spec)
    validation = validate_geometry(nodes, segs, components, spec)
    _json(path / "configuration.json", case_metadata(spec, validation))
    _json(path / "applied_stress.json", {"voigt_order": REFERENCE_SIMPLEGLIDE["applied_stress_voigt_order"],
                                         "units": "Pa", "tensor": stress_tensor(spec.stress_scale).tolist()})
    _json(path / "initial_geometry.json", {"nodes": nodes.tolist(), "segments": segs.tolist(),
                                            "components": components, "seed": spec.seed})
    _json(path / "validation.json", validation)
    (path / "simulation.log").write_text("NOT RUN\n")
    return path


def load_case(path: Path) -> tuple[CaseSpec, np.ndarray, np.ndarray, list[list[int]]]:
    metadata = json.loads((path / "configuration.json").read_text())
    geometry = json.loads((path / "initial_geometry.json").read_text())
    return CaseSpec(**metadata["case"]), np.asarray(geometry["nodes"]), np.asarray(geometry["segments"]), geometry["components"]


def exadis_imports():
    try:
        import pyexadis
        from framework.disnet_manager import DisNetManager
        from pyexadis_base import CalForce, Collision, ExaDisNet, MobilityLaw, SimulateNetwork, TimeIntegration
    except ImportError as error:
        raise RuntimeError(
            "pyexadis is unavailable. Build OpenDiS/ExaDiS first; input generation and validation remain usable."
        ) from error
    return pyexadis, DisNetManager, CalForce, Collision, ExaDisNet, MobilityLaw, SimulateNetwork, TimeIntegration


def run_case(path: Path) -> None:
    spec, nodes, segs, components = load_case(path)
    report = validate_geometry(nodes, segs, components, spec)
    if not report["valid"]:
        _json(path / "validation.json", report)
        raise ValueError(f"refusing invalid initial geometry: {report['issues']}")
    pyexadis, DisNetManager, CalForce, Collision, ExaDisNet, MobilityLaw, SimulateNetwork, TimeIntegration = exadis_imports()
    try:
        pyexadis.initialize()
        raw = path / "raw_trajectory"
        raw.mkdir(exist_ok=True)
        cell = pyexadis.Cell(h=spec.box_size * np.eye(3), is_periodic=[True, True, True])
        network = DisNetManager(ExaDisNet(cell, nodes, segs))
        network.get_disnet(ExaDisNet).write_data(str(path / "simulation_input.data"))
        state = {
            "burgmag": 3e-10, "mu": 160e9, "nu": .31, "a": .01,
            "maxseg": .3, "minseg": .1, "rann": .02,
        }
        force = CalForce(state=state, force_mode="LineTension", Ec=1e6)
        mobility = MobilityLaw(state=state, mobility_law="SimpleGlide")
        integrator = TimeIntegration(state=state, integrator="EulerForward", dt=1e-9)
        collision = Collision(state=state, collision_mode="Retroactive")
        simulation = SimulateNetwork(
            state=state, calforce=force, mobility=mobility, timeint=integrator, collision=collision,
            topology=None, remesh=None, max_step=spec.steps, loading_mode="stress",
            applied_stress=stress_tensor(spec.stress_scale), print_freq=spec.output_frequency,
            write_freq=spec.output_frequency, write_dir=str(raw),
        )
        simulation.run(network, state)
        network.write_json(str(path / "processed_trajectory_final.json"))
        (path / "simulation.log").write_text("SUCCESS\n")
    except Exception as error:
        (path / "simulation.log").write_text(f"FAILED\n{type(error).__name__}: {error}\n")
        raise
    finally:
        pyexadis.finalize()
    snapshots = sorted(raw.glob("config.*.data"))
    if len(snapshots) < 2:
        raise RuntimeError("simulation completed without time-dependent trajectory snapshots")
    report["simulation"] = {"status": "success", "snapshots": [file.name for file in snapshots]}
    _json(path / "validation.json", report)


def _draw(ax, data: dict, title: str, field_of_view: float, box_size: float) -> None:
    positions = np.asarray(data["nodes"]["positions"])
    segs = np.asarray(data["segs"]["nodeids"], dtype=int)
    burgers = np.asarray(data["segs"]["burgers"])
    colors = ["#2878b5", "#e74c3c", "#27ae60", "#8e44ad"]
    for index, (first, second) in enumerate(segs):
        color = colors[hash(tuple(np.round(burgers[index], 6))) % len(colors)]
        ax.plot(*positions[[first, second]].T, color=color, linewidth=1.7)
    corners = np.asarray(list(itertools.product((0.0, box_size), repeat=3)))
    for first, second in itertools.combinations(corners, 2):
        if np.count_nonzero(first != second) == 1:
            ax.plot(*np.vstack((first, second)).T, color="#505050", alpha=.45, linewidth=.8)
    # The dashed cube is the downstream field of view; the solid cube is the
    # full periodic simulation cell and prevents geometry from being clipped.
    center = np.clip(positions.mean(axis=0), field_of_view / 2, box_size - field_of_view / 2)
    fov_min, fov_max = center - field_of_view / 2, center + field_of_view / 2
    fov_corners = np.asarray(list(itertools.product(*zip(fov_min, fov_max))))
    for first, second in itertools.combinations(fov_corners, 2):
        if np.count_nonzero(np.abs(first - second) > 1e-10) == 1:
            ax.plot(*np.vstack((first, second)).T, color="#808080", alpha=.35, linestyle="--", linewidth=.6)
    ax.set_xlim(0, box_size); ax.set_ylim(0, box_size); ax.set_zlim(0, box_size)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title(title)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=25, azim=-55)


def visualize_case(path: Path) -> None:
    spec, _, _, _ = load_case(path)
    pyexadis, _, _, _, _, _, _, _ = exadis_imports()
    from pyexadis_utils import read_paradis
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter
    snapshots = sorted((path / "raw_trajectory").glob("config.*.data"),
                       key=lambda file: int(file.stem.split(".")[1]))
    if len(snapshots) < 2:
        raise RuntimeError("need at least two snapshots to make an evolution video")
    figures = path / "figures"
    figures.mkdir(exist_ok=True)
    pyexadis.initialize()
    try:
        states = [read_paradis(str(snapshot)).export_data() for snapshot in snapshots]
        for label, state in (("initial", states[0]), ("final", states[-1])):
            fig = plt.figure(figsize=(7, 6))
            _draw(fig.add_subplot(111, projection="3d"), state, f"{spec.name}: {label}",
                  spec.field_of_view, spec.box_size)
            fig.savefig(figures / f"{label}.png", dpi=160)
            plt.close(fig)
        video = figures / "evolution.mp4"
        fig = plt.figure(figsize=(7, 6))
        ax = fig.add_subplot(111, projection="3d")
        writer = FFMpegWriter(fps=4, metadata={"title": spec.name})
        with writer.saving(fig, str(video), dpi=130):
            for frame, state in enumerate(states):
                ax.clear(); _draw(ax, state, f"{spec.name}: frame {frame + 1}/{len(states)}",
                                  spec.field_of_view, spec.box_size)
                writer.grab_frame()
        plt.close(fig)
    finally:
        pyexadis.finalize()
    if not video.exists() or video.stat().st_size == 0:
        raise RuntimeError("ffmpeg did not produce a readable video file")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "dataset" / "elastic_simpleglide")
    parser.add_argument("--write-cases", action="store_true", help="write all deterministic case inputs")
    parser.add_argument("--case", help="case directory name to run or visualize")
    parser.add_argument("--run", action="store_true", help="run a generated case")
    parser.add_argument("--visualize", action="store_true", help="create PNGs and MP4 from a completed case")
    args = parser.parse_args()
    if args.write_cases:
        for spec in DEFAULT_CASES:
            case = write_case(spec, args.output_root)
            print(case)
    if args.run or args.visualize:
        if not args.case:
            parser.error("--case is required with --run or --visualize")
        case_path = args.output_root / args.case
        if args.run:
            run_case(case_path)
        if args.visualize:
            visualize_case(case_path)
    if not (args.write_cases or args.run or args.visualize):
        parser.print_help()


if __name__ == "__main__":
    main()
