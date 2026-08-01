#!/usr/bin/env python3
"""Generate elasticity-enabled DDD datasets with fixed solver physics.

This workflow keeps force/mobility/topology/time-integration settings fixed to a
SimpleGlide + DDD_FFT_MODEL reference and varies only:
  * applied stress magnitude (same tensor structure),
  * initial topology/geometry,
  * number of loops/lines,
  * box size and field of view.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import os
import random
import re
import subprocess
import sys
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection


REPO_ROOT = Path(__file__).resolve().parents[2]
PYEXADIS_DIR = REPO_ROOT / "core" / "exadis" / "python"
if str(PYEXADIS_DIR) not in sys.path:
    sys.path.insert(0, str(PYEXADIS_DIR))

import pyexadis  # noqa: E402
from pyexadis_base import (  # noqa: E402
    CalForce,
    Collision,
    DisNetManager,
    ExaDisNet,
    MobilityLaw,
    NodeConstraints,
    Remesh,
    SimulateNetwork,
    TimeIntegration,
    Topology,
)
from pyexadis_utils import insert_infinite_line  # noqa: E402


@dataclass
class CaseSpec:
    template_idx: int
    case_type: str
    interaction_type: str
    variant_idx: int
    seed: int
    num_loops: int
    num_lines: int
    box_size: float
    loop_radius: float
    fov_fraction: float
    stress_multiplier: float
    applied_stress: List[float]
    simulate: bool


def to_2d_array(arr: np.ndarray | Sequence, cols: int, dtype=float) -> np.ndarray:
    a = np.array(arr, dtype=dtype)
    if a.size == 0:
        return np.empty((0, cols), dtype=dtype)
    return a.reshape((-1, cols))


def normalize(v: np.ndarray, eps: float = 1e-14) -> np.ndarray:
    nrm = float(np.linalg.norm(v))
    if nrm < eps:
        raise ValueError(f"Cannot normalize near-zero vector: {v}")
    return v / nrm


def slip_systems_fcc() -> List[Tuple[np.ndarray, np.ndarray]]:
    systems = [
        (np.array([0.0, 1.0, -1.0]), np.array([1.0, 1.0, 1.0])),
        (np.array([1.0, 0.0, -1.0]), np.array([1.0, 1.0, 1.0])),
        (np.array([1.0, -1.0, 0.0]), np.array([1.0, 1.0, 1.0])),
        (np.array([0.0, 1.0, -1.0]), np.array([-1.0, 1.0, 1.0])),
        (np.array([1.0, 0.0, 1.0]), np.array([-1.0, 1.0, 1.0])),
        (np.array([1.0, 1.0, 0.0]), np.array([-1.0, 1.0, 1.0])),
    ]
    out = []
    for b, n in systems:
        out.append((normalize(b), normalize(n)))
    return out


def orthonormal_basis_from_plane(n: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n = normalize(n)
    trial = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(trial, n)) > 0.9:
        trial = np.array([0.0, 1.0, 0.0])
    u = normalize(np.cross(n, trial))
    v = normalize(np.cross(n, u))
    return u, v


def add_circular_loop(
    nodes: List[np.ndarray],
    segs: List[np.ndarray],
    center: np.ndarray,
    radius: float,
    burg: np.ndarray,
    plane: np.ndarray,
    nseg: int,
) -> None:
    burg = normalize(burg)
    plane = normalize(plane)
    if abs(float(np.dot(burg, plane))) > 1e-6:
        raise ValueError("Invalid loop definition: Burgers vector not in glide plane")
    u, v = orthonormal_basis_from_plane(plane)
    start = len(nodes)
    for i in range(nseg):
        theta = 2.0 * math.pi * i / nseg
        pos = center + radius * (math.cos(theta) * u + math.sin(theta) * v)
        nodes.append(
            np.array([pos[0], pos[1], pos[2], NodeConstraints.UNCONSTRAINED], dtype=float)
        )
    for i in range(nseg):
        n1 = start + i
        n2 = start + (i + 1) % nseg
        segs.append(np.concatenate(([n1, n2], burg, plane)).astype(float))


def random_loop_centers(
    rng: random.Random,
    count: int,
    box_size: float,
    radius: float,
    min_clearance_factor: float = 2.6,
    max_tries: int = 10000,
) -> List[np.ndarray]:
    centers: List[np.ndarray] = []
    margin = max(2.0 * radius, 0.08 * box_size)
    low, high = margin, box_size - margin
    min_dist = min_clearance_factor * radius

    for _ in range(max_tries):
        if len(centers) == count:
            return centers
        c = np.array([rng.uniform(low, high), rng.uniform(low, high), rng.uniform(low, high)])
        if all(np.linalg.norm(c - p) >= min_dist for p in centers):
            centers.append(c)

    raise RuntimeError(
        f"Could not place {count} loops in box={box_size} with radius={radius}."
    )


def parse_step_from_filename(path: Path) -> int:
    m = re.match(r"config\.(\d+)\.data$", path.name)
    if not m:
        return -1
    return int(m.group(1))


def load_network_data(data_file: Path) -> Dict:
    g = ExaDisNet()
    g.read_paradis(str(data_file))
    n = DisNetManager(g)
    return n.export_data()


def load_readable_frames(frame_files: Sequence[Path]) -> Tuple[List[Path], List[Dict], List[Dict]]:
    readable_files: List[Path] = []
    readable_data: List[Dict] = []
    skipped: List[Dict] = []
    for p in frame_files:
        try:
            d = load_network_data(p)
            readable_files.append(p)
            readable_data.append(d)
        except Exception as exc:  # pylint: disable=broad-except
            skipped.append({"path": str(p), "error": str(exc)})
    return readable_files, readable_data, skipped


def shortest_distance_segment_segment(
    p1: np.ndarray, q1: np.ndarray, p2: np.ndarray, q2: np.ndarray
) -> float:
    # Closest points between two 3D segments.
    u = q1 - p1
    v = q2 - p2
    w = p1 - p2
    a = np.dot(u, u)
    b = np.dot(u, v)
    c = np.dot(v, v)
    d = np.dot(u, w)
    e = np.dot(v, w)
    D = a * c - b * b
    sc, sN, sD = D, D, D
    tc, tN, tD = D, D, D
    eps = 1e-14

    if D < eps:
        sN = 0.0
        sD = 1.0
        tN = e
        tD = c
    else:
        sN = b * e - c * d
        tN = a * e - b * d
        if sN < 0.0:
            sN = 0.0
            tN = e
            tD = c
        elif sN > sD:
            sN = sD
            tN = e + b
            tD = c

    if tN < 0.0:
        tN = 0.0
        if -d < 0.0:
            sN = 0.0
        elif -d > a:
            sN = sD
        else:
            sN = -d
            sD = a
    elif tN > tD:
        tN = tD
        if (-d + b) < 0.0:
            sN = 0.0
        elif (-d + b) > a:
            sN = sD
        else:
            sN = (-d + b)
            sD = a

    sc = 0.0 if abs(sN) < eps else sN / sD
    tc = 0.0 if abs(tN) < eps else tN / tD
    dp = w + sc * u - tc * v
    return float(np.linalg.norm(dp))


def validate_network(
    cell: pyexadis.Cell,
    nodes: np.ndarray,
    segs: np.ndarray,
    case_spec: CaseSpec,
) -> Dict:
    report: Dict = {"errors": [], "warnings": [], "metrics": {}}
    box = np.array(cell.h, dtype=float)
    lengths = np.linalg.norm(box, axis=0)
    tol_len = 1e-8 * float(np.min(lengths))
    n_nodes = nodes.shape[0]
    n_segs = segs.shape[0]
    if n_nodes == 0 and n_segs == 0:
        report["warnings"].append("Empty network (all dislocations annihilated).")
        report["valid"] = True
        return report

    pos = to_2d_array(nodes[:, :3], 3, dtype=float)
    node_ids = to_2d_array(segs[:, :2], 2, dtype=int)
    burgers = to_2d_array(segs[:, 2:5], 3, dtype=float)
    planes = to_2d_array(segs[:, 5:8], 3, dtype=float)

    report["metrics"]["node_count"] = int(n_nodes)
    report["metrics"]["segment_count"] = int(n_segs)

    # Connectivity and index checks.
    deg = np.zeros(n_nodes, dtype=int)
    seen_links = set()
    for i, (n1, n2) in enumerate(node_ids):
        if n1 < 0 or n1 >= n_nodes or n2 < 0 or n2 >= n_nodes:
            report["errors"].append(f"segment[{i}] has invalid node ids ({n1}, {n2})")
            continue
        deg[n1] += 1
        deg[n2] += 1
        pair = (min(int(n1), int(n2)), max(int(n1), int(n2)))
        if pair in seen_links:
            report["errors"].append(f"duplicate segment link between nodes {pair}")
        else:
            seen_links.add(pair)

    isolated = np.where(deg == 0)[0]
    if isolated.size > 0:
        report["errors"].append(f"{isolated.size} isolated nodes found")

    too_high_degree = np.where(deg > 6)[0]
    if too_high_degree.size > 0:
        report["warnings"].append(f"{too_high_degree.size} nodes have degree > 6")

    # Segment geometry checks.
    seg_lengths = []
    for i, (n1, n2) in enumerate(node_ids):
        r1 = pos[n1]
        r2 = np.array(cell.closest_image(Rref=r1, R=pos[n2]), dtype=float)
        L = float(np.linalg.norm(r2 - r1))
        seg_lengths.append(L)
        if L <= tol_len:
            report["errors"].append(f"segment[{i}] has near-zero length ({L:.3e})")

    seg_lengths = np.array(seg_lengths, dtype=float)
    if seg_lengths.size > 0:
        report["metrics"]["min_segment_length"] = float(np.min(seg_lengths))
        report["metrics"]["max_segment_length"] = float(np.max(seg_lengths))
        report["metrics"]["mean_segment_length"] = float(np.mean(seg_lengths))

    # Duplicate node positions.
    dups = 0
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if np.linalg.norm(pos[i] - pos[j]) < tol_len:
                dups += 1
    if dups > 0:
        report["errors"].append(f"{dups} duplicate node-position pairs detected")

    # Burgers and glide-plane consistency.
    for i in range(n_segs):
        b = burgers[i]
        n = planes[i]
        bnorm = float(np.linalg.norm(b))
        nnorm = float(np.linalg.norm(n))
        if bnorm < 1e-10:
            report["errors"].append(f"segment[{i}] has near-zero Burgers vector")
            continue
        if nnorm < 1e-10:
            report["errors"].append(f"segment[{i}] has near-zero glide-plane normal")
            continue
        n_unit = n / nnorm
        b_unit = b / bnorm
        if abs(float(np.dot(b_unit, n_unit))) > 1e-5:
            report["errors"].append(
                f"segment[{i}] has inconsistent Burgers/plane orthogonality"
            )

    # Box inclusion and periodic image proximity.
    origin = np.array(cell.origin, dtype=float)
    for i, p in enumerate(pos):
        if np.any(p < origin - 1e-8) or np.any(p > origin + lengths + 1e-8):
            report["errors"].append(f"node[{i}] lies outside simulation box")

    margin = 0.08 * case_spec.box_size
    if pos.size > 0:
        min_to_face = np.min(np.vstack([pos - origin, origin + lengths - pos]), axis=0)
        if float(np.min(min_to_face)) < margin:
            report["warnings"].append(
                "Some nodes are close to periodic-image boundaries (possible image interaction)."
            )

    # Unintended intersections.
    if n_segs <= 200:
        threshold = max(0.03 * case_spec.loop_radius, tol_len)
        for i in range(n_segs):
            a1, a2 = node_ids[i]
            p1 = pos[a1]
            q1 = np.array(cell.closest_image(Rref=p1, R=pos[a2]), dtype=float)
            for j in range(i + 1, n_segs):
                b1, b2 = node_ids[j]
                if len({int(a1), int(a2), int(b1), int(b2)}) < 4:
                    continue
                p2 = pos[b1]
                q2 = np.array(cell.closest_image(Rref=p2, R=pos[b2]), dtype=float)
                d = shortest_distance_segment_segment(p1, q1, p2, q2)
                if d < threshold:
                    report["warnings"].append(
                        f"segment[{i}] and segment[{j}] are very close ({d:.3e})"
                    )
                    if case_spec.interaction_type in {"isolated_loop", "paired_loops"}:
                        report["errors"].append(
                            f"unexpected near-intersection between segments {i} and {j}"
                        )
                        break
            if report["errors"]:
                break

    report["valid"] = len(report["errors"]) == 0
    return report


def build_case_name(spec: CaseSpec) -> str:
    stress_label = f"{spec.stress_multiplier:.2f}".replace(".", "p")
    return (
        f"{spec.case_type}_n{spec.num_loops:02d}_l{spec.num_lines:02d}"
        f"_box{int(spec.box_size):03d}_fov{int(spec.fov_fraction * 100):03d}"
        f"_s{stress_label}_v{spec.variant_idx:02d}_seed{spec.seed}"
    )


def setup_solver_settings(
    reference_physics: Dict, box_size: float
) -> Tuple[Dict, Dict, Dict, Dict, Dict, Dict, Dict]:
    state = dict(reference_physics["state"])
    state["maxseg"] = reference_physics["maxseg_ratio"] * box_size
    state["minseg"] = reference_physics["minseg_ratio"] * box_size
    force = dict(reference_physics["force"])
    mobility = dict(reference_physics["mobility"])
    timeint = dict(reference_physics["time_integration"])
    collision = dict(reference_physics["collision"])
    topology = dict(reference_physics["topology"])
    remesh = dict(reference_physics["remesh"])
    return state, force, mobility, timeint, collision, topology, remesh


def build_geometry(case_spec: CaseSpec) -> Tuple[pyexadis.Cell, np.ndarray, np.ndarray, Dict]:
    rng = random.Random(case_spec.seed)
    cell = pyexadis.Cell(
        h=case_spec.box_size * np.eye(3), is_periodic=[1, 1, 1], origin=np.zeros(3)
    )

    nodes: List[np.ndarray] = []
    segs: List[np.ndarray] = []

    systems = slip_systems_fcc()
    loop_centers = random_loop_centers(
        rng=rng,
        count=case_spec.num_loops,
        box_size=case_spec.box_size,
        radius=case_spec.loop_radius,
    )

    loop_meta = []
    for i in range(case_spec.num_loops):
        b, n = systems[i % len(systems)]
        if case_spec.interaction_type in {"mixed_slip_systems"} and i % 2 == 1:
            b = -b
        if case_spec.interaction_type in {"triple_loop_cluster", "line_loop_crossing"} and i % 3 == 1:
            b, n = systems[(i + 2) % len(systems)]
        nseg = max(24, int(round(2.0 * math.pi * case_spec.loop_radius / (0.04 * case_spec.box_size))))
        add_circular_loop(
            nodes=nodes,
            segs=segs,
            center=loop_centers[i],
            radius=case_spec.loop_radius,
            burg=b,
            plane=n,
            nseg=nseg,
        )
        loop_meta.append(
            {
                "center": loop_centers[i].tolist(),
                "radius": case_spec.loop_radius,
                "burgers": b.tolist(),
                "plane": n.tolist(),
                "segments": nseg,
            }
        )

    line_meta = []
    for i in range(case_spec.num_lines):
        b, n = systems[(i + 3) % len(systems)]
        origin = np.array(
            [
                rng.uniform(0.2 * case_spec.box_size, 0.8 * case_spec.box_size),
                rng.uniform(0.2 * case_spec.box_size, 0.8 * case_spec.box_size),
                rng.uniform(0.2 * case_spec.box_size, 0.8 * case_spec.box_size),
            ]
        )
        theta = rng.uniform(-75.0, 75.0)
        nodes, segs = insert_infinite_line(
            cell=cell,
            nodes=nodes,
            segs=segs,
            burg=b,
            plane=n,
            origin=origin,
            theta=theta,
            maxseg=0.06 * case_spec.box_size,
            trial=False,
        )
        line_meta.append({"origin": origin.tolist(), "burgers": b.tolist(), "plane": n.tolist(), "theta": theta})

    nodes_arr = to_2d_array(nodes, 4, dtype=float)
    segs_arr = to_2d_array(segs, 8, dtype=float)

    # Wrap periodic coordinates into [0, L).
    nodes_arr[:, :3] = np.mod(nodes_arr[:, :3], case_spec.box_size)
    meta = {"loops": loop_meta, "lines": line_meta}
    return cell, nodes_arr, segs_arr, meta


def draw_box(ax, origin: np.ndarray, box_h: np.ndarray) -> None:
    p = origin
    h = box_h
    corners = p + np.array(
        [
            [0, 0, 0],
            h[0],
            h[0] + h[1],
            h[1],
            h[2],
            h[0] + h[2],
            h[0] + h[1] + h[2],
            h[1] + h[2],
        ]
    )
    edges = np.array(
        [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7],
        ]
    )
    ax.add_collection(Line3DCollection(corners[edges], linewidths=0.6, colors="k", alpha=0.4))


def segment_colors_from_burgers(burgers: np.ndarray) -> List[str]:
    colors: List[str] = []
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    for b in burgers:
        idx = int(np.argmax(np.abs(b))) % len(palette)
        sign = np.sign(b[np.argmax(np.abs(b))])
        if sign < 0:
            idx = (idx + 3) % len(palette)
        colors.append(palette[idx])
    return colors


def render_frame(
    ax,
    data: Dict,
    fov_fraction: float,
    camera_elev: float = 18.0,
    camera_azim: float = -58.0,
) -> None:
    cell = data["cell"]
    h = np.array(cell["h"], dtype=float)
    origin = np.array(cell["origin"], dtype=float)
    center = origin + 0.5 * np.sum(h, axis=0)

    nodes = to_2d_array(data["nodes"]["positions"], 3, dtype=float)
    segs = to_2d_array(data["segs"]["nodeids"], 2, dtype=int)
    burgers = to_2d_array(data["segs"]["burgers"], 3, dtype=float)

    if segs.size > 0 and nodes.size > 0:
        segments = []
        for i in range(segs.shape[0]):
            n1, n2 = segs[i]
            p1 = nodes[n1]
            p2 = nodes[n2]
            segments.append([p1, p2])
        colors = segment_colors_from_burgers(burgers)
        ax.add_collection(Line3DCollection(segments, linewidths=1.0, colors=colors))

    draw_box(ax, origin=origin, box_h=h)
    side = fov_fraction * float(np.min(np.linalg.norm(h, axis=0)))
    half = 0.5 * side
    ax.set_xlim(center[0] - half, center[0] + half)
    ax.set_ylim(center[1] - half, center[1] + half)
    ax.set_zlim(center[2] - half, center[2] + half)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("DDD network evolution")
    ax.view_init(elev=camera_elev, azim=camera_azim)
    try:
        ax.set_box_aspect([1, 1, 1])
    except Exception:
        pass


def create_visualizations(
    frame_files: Sequence[Path],
    frame_data: Sequence[Dict],
    fov_fraction: float,
    out_dir: Path,
    max_frames_for_video: int = 80,
) -> Dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    sampled_files = list(frame_files)
    sampled_data = list(frame_data)
    if len(sampled_files) > max_frames_for_video:
        idx = np.linspace(0, len(sampled_files) - 1, max_frames_for_video).astype(int)
        sampled_files = [sampled_files[i] for i in idx]
        sampled_data = [sampled_data[i] for i in idx]

    info = {"frame_count": len(sampled_data), "video_ok": False}

    # Initial and final static images.
    for label, data in [("initial", sampled_data[0]), ("final", sampled_data[-1])]:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")
        render_frame(ax, data, fov_fraction=fov_fraction)
        fig.savefig(out_dir / f"{label}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    # Animation.
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    def update(i: int):
        ax.cla()
        render_frame(ax, sampled_data[i], fov_fraction=fov_fraction)
        ax.set_title(f"DDD network evolution (frame {i+1}/{len(sampled_data)})")
        return []

    ani = animation.FuncAnimation(fig, update, frames=len(sampled_data), interval=180, blit=False)
    video_path = out_dir / "evolution.mp4"
    writer = animation.FFMpegWriter(fps=6, bitrate=2400)
    ani.save(str(video_path), writer=writer)
    plt.close(fig)

    # Readability check via ffprobe.
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(video_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {video_path}: {proc.stderr.strip()}")
    parsed = json.loads(proc.stdout)
    streams = parsed.get("streams", [])
    if not streams:
        raise RuntimeError(f"No streams found in generated video {video_path}")
    info["video_ok"] = True
    info["video_streams"] = streams
    return info


def compute_trajectory_summary(frame_files: Sequence[Path], frame_data: Sequence[Dict]) -> Dict:
    summary = {"frames": [], "num_frames": len(frame_files)}
    for p, data in zip(frame_files, frame_data):
        cell = data["cell"]
        h = np.array(cell["h"], dtype=float)
        vol = float(abs(np.linalg.det(h)))
        nodes = to_2d_array(data["nodes"]["positions"], 3, dtype=float)
        segs = to_2d_array(data["segs"]["nodeids"], 2, dtype=int)
        total_length = 0.0
        for n1, n2 in segs:
            total_length += float(np.linalg.norm(nodes[n2] - nodes[n1]))
        step = parse_step_from_filename(p)
        summary["frames"].append(
            {
                "step": int(step),
                "path": str(p),
                "node_count": int(nodes.shape[0]),
                "segment_count": int(segs.shape[0]),
                "total_line_length": total_length,
                "line_length_per_volume": total_length / vol if vol > 0 else None,
            }
        )
    return summary


def generate_case_specs(config: Dict, simulate_per_template: int) -> List[CaseSpec]:
    ref_stress = np.array(config["reference_physics"]["reference_applied_stress"], dtype=float)
    fov_vals = config["fov_fractions"]
    multipliers = config["stress_multipliers"]
    base_seed = int(config["random_seed"])
    variants = int(config["variants_per_template"])
    specs: List[CaseSpec] = []

    for tidx, t in enumerate(config["case_templates"]):
        for vidx in range(variants):
            mul = float(multipliers[vidx % len(multipliers)])
            fov = float(fov_vals[(vidx + tidx) % len(fov_vals)])
            app = (mul * ref_stress).tolist()
            seed = base_seed + 1000 * tidx + vidx
            simulate = vidx < simulate_per_template
            specs.append(
                CaseSpec(
                    template_idx=tidx,
                    case_type=t["case_type"],
                    interaction_type=t["interaction_type"],
                    variant_idx=vidx,
                    seed=seed,
                    num_loops=int(t["num_loops"]),
                    num_lines=int(t["num_lines"]),
                    box_size=float(t["box_size"]),
                    loop_radius=float(t["loop_radius_fraction"]) * float(t["box_size"]),
                    fov_fraction=fov,
                    stress_multiplier=mul,
                    applied_stress=app,
                    simulate=simulate,
                )
            )
    return specs


def run_case(
    spec: CaseSpec,
    config: Dict,
    out_root: Path,
    overwrite: bool,
) -> Dict:
    case_name = build_case_name(spec)
    case_dir = out_root / case_name
    if case_dir.exists() and not overwrite:
        raise FileExistsError(f"Case directory already exists: {case_dir}")
    case_dir.mkdir(parents=True, exist_ok=True)

    input_dir = case_dir / "inputs"
    raw_dir = case_dir / "raw_trajectory"
    processed_dir = case_dir / "processed"
    logs_dir = case_dir / "logs"
    viz_dir = case_dir / "visualization"
    for d in [input_dir, raw_dir, processed_dir, logs_dir, viz_dir]:
        d.mkdir(parents=True, exist_ok=True)

    case_meta = {"case_name": case_name, "spec": asdict(spec)}
    (case_dir / "case_spec.json").write_text(json.dumps(case_meta, indent=2), encoding="utf-8")
    (case_dir / "applied_stress_tensor.json").write_text(
        json.dumps({"applied_stress": spec.applied_stress}, indent=2), encoding="utf-8"
    )

    # Build and validate geometry.
    cell, nodes, segs, geometry_meta = build_geometry(spec)
    pre_report = validate_network(cell, nodes, segs, spec)
    (case_dir / "validation_pre.json").write_text(
        json.dumps(pre_report, indent=2), encoding="utf-8"
    )
    if not pre_report.get("valid", False):
        raise RuntimeError(f"Pre-simulation validation failed for {case_name}")

    (case_dir / "initial_geometry_metadata.json").write_text(
        json.dumps(geometry_meta, indent=2), encoding="utf-8"
    )
    (case_dir / "box_and_fov.json").write_text(
        json.dumps(
            {"box_size": spec.box_size, "field_of_view_fraction": spec.fov_fraction},
            indent=2,
        ),
        encoding="utf-8",
    )
    (case_dir / "seed.json").write_text(json.dumps({"seed": spec.seed}, indent=2), encoding="utf-8")

    net = DisNetManager(ExaDisNet(cell, nodes, segs))
    net.get_disnet(ExaDisNet).write_data(str(input_dir / "initial_config.data"))

    # Keep reference solver settings fixed.
    reference = config["reference_physics"]
    state, force_cfg, mobility_cfg, timeint_cfg, coll_cfg, top_cfg, remesh_cfg = setup_solver_settings(
        reference, spec.box_size
    )
    sim_cfg = dict(reference["simulation"])
    applied_stress = np.array(spec.applied_stress, dtype=float)

    run_status = {
        "simulated": False,
        "success": not spec.simulate,
        "error": None,
        "traceback": None,
        "trajectory_frames": 0,
    }
    log_file = logs_dir / "simulation.log"

    if spec.simulate:
        with open(log_file, "w", encoding="utf-8") as fh, contextlib.redirect_stdout(fh), contextlib.redirect_stderr(fh):
            try:
                calforce = CalForce(force_mode=force_cfg["force_mode"], state=state, Ngrid=force_cfg["Ngrid"], cell=net.cell, Ec=force_cfg["Ec"])
                mobility = MobilityLaw(
                    mobility_law=mobility_cfg["mobility_law"],
                    state=state,
                    mob=mobility_cfg["mob"],
                )
                timeint = TimeIntegration(
                    integrator=timeint_cfg["integrator"],
                    state=state,
                    force=calforce,
                    mobility=mobility,
                )
                collision = None
                if coll_cfg.get("enabled", True):
                    collision = Collision(collision_mode=coll_cfg["collision_mode"], state=state)

                topology = None
                if top_cfg.get("enabled", True):
                    topology = Topology(
                        topology_mode=top_cfg["topology_mode"],
                        state=state,
                        force=calforce,
                        mobility=mobility,
                    )

                remesh = None
                if remesh_cfg.get("enabled", True):
                    remesh = Remesh(remesh_rule=remesh_cfg["remesh_rule"], state=state)

                sim = SimulateNetwork(
                    calforce=calforce,
                    mobility=mobility,
                    timeint=timeint,
                    collision=collision,
                    topology=topology,
                    remesh=remesh,
                    vis=None,
                    state=state,
                    loading_mode=reference["loading_mode"],
                    applied_stress=applied_stress,
                    max_step=int(sim_cfg["max_step"]),
                    print_freq=int(sim_cfg["print_freq"]),
                    write_freq=int(sim_cfg["write_freq"]),
                    write_dir=str(raw_dir),
                )
                sim.run(net, state)
                run_status["simulated"] = True
                run_status["success"] = True
            except Exception as exc:  # pylint: disable=broad-except
                run_status["simulated"] = True
                run_status["success"] = False
                run_status["error"] = str(exc)
                run_status["traceback"] = traceback.format_exc()

    frame_files = sorted(raw_dir.glob("config.*.data"), key=parse_step_from_filename)
    readable_files, readable_data, skipped_frames = load_readable_frames(frame_files)
    run_status["trajectory_frames"] = len(readable_files)
    run_status["unreadable_frames"] = skipped_frames
    if spec.simulate and (not run_status["success"] or len(readable_files) == 0):
        raise RuntimeError(f"Simulation failed or produced no frames for {case_name}: {run_status['error']}")

    # Post-simulation validation and processing.
    post_report = pre_report
    traj_summary = {}
    viz_summary = {}
    if spec.simulate:
        final_data = readable_data[-1]
        pos = to_2d_array(final_data["nodes"]["positions"], 3, dtype=float)
        con = to_2d_array(final_data["nodes"]["constraints"], 1, dtype=float)
        post_nodes = np.hstack([pos, con]) if pos.size > 0 else np.empty((0, 4), dtype=float)
        nid = to_2d_array(final_data["segs"]["nodeids"], 2, dtype=float)
        burg = to_2d_array(final_data["segs"]["burgers"], 3, dtype=float)
        plane = to_2d_array(final_data["segs"]["planes"], 3, dtype=float)
        post_segs = np.hstack([nid, burg, plane]) if nid.size > 0 else np.empty((0, 8), dtype=float)
        post_report = validate_network(cell, post_nodes, post_segs, spec)
        traj_summary = compute_trajectory_summary(readable_files, readable_data)
        viz_summary = create_visualizations(readable_files, readable_data, spec.fov_fraction, viz_dir)

    (case_dir / "validation_post.json").write_text(
        json.dumps(post_report, indent=2), encoding="utf-8"
    )
    (processed_dir / "trajectory_summary.json").write_text(
        json.dumps(traj_summary, indent=2), encoding="utf-8"
    )
    (logs_dir / "run_status.json").write_text(json.dumps(run_status, indent=2), encoding="utf-8")
    (viz_dir / "visualization_summary.json").write_text(
        json.dumps(viz_summary, indent=2), encoding="utf-8"
    )

    return {
        "case_name": case_name,
        "case_dir": str(case_dir),
        "simulated": spec.simulate,
        "success": run_status["success"] if spec.simulate else True,
        "trajectory_frames": len(frame_files),
        "video_path": str(viz_dir / "evolution.mp4") if spec.simulate else None,
    }


def validate_reference_settings(reference: Dict) -> None:
    required = {
        "force": ("force_mode", "DDD_FFT_MODEL"),
        "mobility": ("mobility_law", "SimpleGlide"),
        "time_integration": ("integrator", "Trapezoid"),
    }
    for block, (key, expected) in required.items():
        found = reference.get(block, {}).get(key)
        if found != expected:
            raise ValueError(f"Reference settings mismatch: {block}.{key}={found}, expected {expected}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate elasticity-enabled DDD dataset cases.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent / "dataset_config.json",
        help="Path to dataset config JSON.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parent / "generated_dataset",
        help="Dataset output root.",
    )
    parser.add_argument(
        "--simulate-per-template",
        type=int,
        default=None,
        help="Override number of simulated variants per case template.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing case directories.",
    )
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    simulate_per_template = (
        int(config["simulate_per_template"])
        if args.simulate_per_template is None
        else int(args.simulate_per_template)
    )
    validate_reference_settings(config["reference_physics"])

    out_root = args.output_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    # Persist full run config for reproducibility.
    (out_root / "dataset_run_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    specs = generate_case_specs(config, simulate_per_template=simulate_per_template)

    results = []
    failures = []
    pyexadis.initialize()
    try:
        for spec in specs:
            try:
                result = run_case(spec, config, out_root, overwrite=args.overwrite)
                results.append(result)
                print(f"[OK] {result['case_name']} simulated={result['simulated']}")
            except Exception as exc:  # pylint: disable=broad-except
                fail = {"case_name": build_case_name(spec), "error": str(exc)}
                failures.append(fail)
                print(f"[FAIL] {fail['case_name']}: {fail['error']}")
    finally:
        pyexadis.finalize()

    manifest = {
        "output_root": str(out_root),
        "total_cases": len(specs),
        "successful_cases": len(results),
        "failed_cases": len(failures),
        "results": results,
        "failures": failures,
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Hard fail if any simulated case failed.
    if failures:
        raise SystemExit(1)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
