"""Visualize dislocation network trajectories and save MP4 animations."""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import pyexadis
from pyexadis_base import ExaDisNet, DisNetManager


def _parse_config_frames(raw_dir: Path) -> List[Tuple[int, Path]]:
    frames = []
    for f in sorted(raw_dir.glob("config.*.data")):
        step = int(f.stem.split(".")[-1])
        frames.append((step, f))
    return sorted(frames, key=lambda x: x[0])


def _load_frame(path: Path) -> Dict[str, Any]:
    G = ExaDisNet()
    G.read_paradis(str(path))
    return G.export_data()


def _plot_frame(ax, data: Dict[str, Any], fov: float, center: Optional[np.ndarray] = None):
    cell = data["cell"]
    import pyexadis as pxe
    cell_obj = pxe.Cell(h=cell["h"], origin=cell.get("origin", np.zeros(3)),
                        is_periodic=cell.get("is_periodic", [1, 1, 1]))
    h = np.array(cell["h"])
    origin = np.array(cell.get("origin", np.zeros(3)))
    if center is None:
        center = origin + 0.5 * np.sum(h, axis=0)

    nodes = data["nodes"]["positions"]
    segs = data["segs"]
    if nodes.size == 0:
        return

    rn = np.array([cell_obj.closest_image(Rref=center, R=n) for n in nodes])
    segsnid = segs["nodeids"]
    r1 = rn[segsnid[:, 0]]
    r2 = np.array([cell_obj.closest_image(Rref=r1[i], R=rn[segsnid[i, 1]])
                   for i in range(len(segsnid))])
    p_segs = np.hstack((r1, r2))

    ax.cla()
    if p_segs.size > 0:
        ls = p_segs.reshape((-1, 2, 3))
        lc = Line3DCollection(ls, linewidths=1.0, colors="steelblue")
        ax.add_collection(lc)

    half = fov / 2.0
    ax.set_xlim(center[0] - half, center[0] + half)
    ax.set_ylim(center[1] - half, center[1] + half)
    ax.set_zlim(center[2] - half, center[2] + half)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=25, azim=-60)
    try:
        ax.set_box_aspect([1, 1, 1])
    except AttributeError:
        pass

    # Box wireframe
    c = origin + np.array([
        [0, 0, 0], h[0], h[0] + h[1], h[1], h[2],
        h[0] + h[2], h[0] + h[1] + h[2], h[1] + h[2],
    ])
    boxedges = np.array([
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7],
    ])
    bc = Line3DCollection(c[boxedges], linewidths=0.4, colors="k", alpha=0.3)
    ax.add_collection(bc)


def visualize_case(case_dir: os.PathLike, fps: int = 8) -> Dict[str, str]:
    case_dir = Path(case_dir)
    pyexadis.initialize()
    fig_dir = case_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = case_dir / "raw"

    with open(case_dir / "config.yaml") as f:
        import yaml
        cfg = yaml.safe_load(f)
    fov = cfg["geometry"]["field_of_view"]
    box = cfg["geometry"]["box_size"]
    center = np.array([box / 2, box / 2, box / 2])

    frames = _parse_config_frames(raw_dir)
    if not frames:
        raise FileNotFoundError(f"No trajectory frames in {raw_dir}")

    outputs = {}
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Static initial and final
    for label, idx in [("initial", 0), ("final", -1)]:
        step, path = frames[idx]
        data = _load_frame(path)
        _plot_frame(ax, data, fov, center)
        ax.set_title(f"{cfg.get('case_id', case_dir.name)} — {label} (step {step})")
        out = fig_dir / f"{label}_state.png"
        fig.savefig(out, dpi=120, bbox_inches="tight")
        outputs[label] = str(out)

    # Animation frames
    anim_dir = fig_dir / "frames"
    anim_dir.mkdir(exist_ok=True)
    frame_paths = []
    for i, (step, path) in enumerate(frames):
        data = _load_frame(path)
        _plot_frame(ax, data, fov, center)
        ax.set_title(f"step {step}")
        fp = anim_dir / f"frame_{i:04d}.png"
        fig.savefig(fp, dpi=100, bbox_inches="tight")
        frame_paths.append(fp)

    plt.close(fig)

    video_path = fig_dir / "evolution.mp4"
    _frames_to_mp4(frame_paths, video_path, fps=fps)
    outputs["video"] = str(video_path)

    with open(fig_dir / "visualization_metadata.json", "w") as f:
        json.dump({"fps": fps, "num_frames": len(frames), "outputs": outputs}, f, indent=2)
    pyexadis.finalize()
    return outputs


def _frames_to_mp4(frame_paths: List[Path], output: Path, fps: int = 8) -> None:
    import subprocess
    pattern = str(frame_paths[0].parent / "frame_%04d.png")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", pattern,
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
