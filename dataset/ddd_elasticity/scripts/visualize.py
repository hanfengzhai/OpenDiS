"""Trajectory visualization for elasticity DDD datasets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np

from paths_setup import ensure_imports

ensure_imports()

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection  # noqa: E402

import pyexadis  # noqa: E402
from pyexadis_base import ExaDisNet, DisNetManager  # noqa: E402


def _parse_step(path: Path) -> int:
    m = re.search(r"config\.(\d+)\.data$", path.name)
    if not m:
        raise ValueError(f"Cannot parse step from {path}")
    return int(m.group(1))


def load_frames(traj_dir: Path) -> list[tuple[int, DisNetManager]]:
    files = sorted(traj_dir.glob("config.*.data"), key=_parse_step)
    frames = []
    for f in files:
        G = ExaDisNet()
        G.read_paradis(str(f))
        frames.append((_parse_step(f), DisNetManager(G)))
    return frames


def _segment_polylines(N: DisNetManager, ref_center: np.ndarray):
    """Return all segments imaged near ref_center (full network, no FOV culling)."""
    G = N.get_disnet(ExaDisNet)
    data = G.export_data()
    cell = data["cell"]
    cell_obj = pyexadis.Cell(
        h=cell["h"], origin=cell.get("origin", [0, 0, 0]), is_periodic=cell.get("is_periodic", [1, 1, 1])
    )
    rn = np.asarray(data["nodes"]["positions"], dtype=float)
    if rn.size == 0:
        return [], np.zeros((0, 3))
    segs = data["segs"]
    ids = np.asarray(segs["nodeids"], dtype=int).reshape(-1, 2) if len(segs["nodeids"]) else np.zeros((0, 2), dtype=int)
    burgs = np.asarray(segs["burgers"], dtype=float).reshape(-1, 3) if len(segs["burgers"]) else np.zeros((0, 3))
    lines = []
    colors = []
    for (i0, i1), b in zip(ids, burgs):
        r1 = np.asarray(cell_obj.closest_image(Rref=ref_center, R=rn[i0]))
        r2 = np.asarray(cell_obj.closest_image(Rref=r1, R=rn[i1]))
        lines.append([r1, r2])
        bb = b / (np.linalg.norm(b) + 1e-30)
        colors.append(0.45 + 0.55 * bb)
    return lines, np.asarray(colors) if colors else np.zeros((0, 3))


def _draw_box(ax, origin: np.ndarray, box: np.ndarray, color="0.3", lw=0.8):
    o = origin
    Lx, Ly, Lz = box
    corners = np.array(
        [
            [o[0], o[1], o[2]],
            [o[0] + Lx, o[1], o[2]],
            [o[0] + Lx, o[1] + Ly, o[2]],
            [o[0], o[1] + Ly, o[2]],
            [o[0], o[1], o[2] + Lz],
            [o[0] + Lx, o[1], o[2] + Lz],
            [o[0] + Lx, o[1] + Ly, o[2] + Lz],
            [o[0], o[1] + Ly, o[2] + Lz],
        ]
    )
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]
    for i, j in edges:
        ax.plot(
            [corners[i, 0], corners[j, 0]],
            [corners[i, 1], corners[j, 1]],
            [corners[i, 2], corners[j, 2]],
            color=color,
            lw=lw,
        )


def _draw_plane_square(ax, center_xy, edge, z, color="#c45c26", lw=1.4):
    """Draw an in-plane FOV square on the 001 (z=const) plane."""
    half = 0.5 * edge
    x0, y0 = center_xy
    xs = [x0 - half, x0 + half, x0 + half, x0 - half, x0 - half]
    ys = [y0 - half, y0 - half, y0 + half, y0 + half, y0 - half]
    zs = [z] * 5
    ax.plot(xs, ys, zs, color=color, lw=lw)


def render_frame(
    N: DisNetManager,
    *,
    box: float,
    fov: float,
    title: str,
    out_path: Path | None = None,
    elev: float = 78.0,
    azim: float = -90.0,
):
    """
    Render a true top-down 2D view of the (001) glide plane (x–y).

    The solver cell is still 3D, but all dataset dislocations are planar on z=L/2.
    """
    _ = elev, azim  # kept for API compatibility; 2D top-down view does not use them
    origin = np.zeros(3)
    center = origin + 0.5 * box
    lines, colors = _segment_polylines(N, center)

    fig = plt.figure(figsize=(8.0, 8.0), dpi=100)
    ax = fig.add_subplot(111)
    if len(lines):
        for seg, col in zip(lines, colors):
            seg = np.asarray(seg)
            ax.plot(seg[:, 0], seg[:, 1], color=np.clip(col, 0, 1), lw=2.4, solid_capstyle="round")
        pts = np.unique(np.vstack([np.asarray(seg) for seg in lines])[:, :2], axis=0)
        ax.scatter(pts[:, 0], pts[:, 1], c="k", s=10, zorder=3)

    # Box footprint on 001
    ax.plot(
        [0, box, box, 0, 0],
        [0, 0, box, box, 0],
        color="0.2",
        lw=1.4,
    )
    if abs(fov - box) > 1e-9:
        half = 0.5 * fov
        ax.plot(
            [center[0] - half, center[0] + half, center[0] + half, center[0] - half, center[0] - half],
            [center[1] - half, center[1] - half, center[1] + half, center[1] + half, center[1] - half],
            color="#c45c26",
            lw=1.6,
        )

    ax.set_xlim(0, box)
    ax.set_ylim(0, box)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    suffix = "  —  2D (001) plane"
    if not len(lines):
        suffix += " [annihilated]"
        ax.text(0.5 * box, 0.5 * box, "annihilated", ha="center", va="center", color="0.45", fontsize=14)
    ax.set_title(title + suffix, fontsize=11)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, bbox_inches="tight", pad_inches=0.15)
    return fig, ax


def make_video(
    traj_dir: Path,
    out_mp4: Path,
    *,
    box: float,
    fov: float,
    fps: int = 4,
) -> Path:
    import subprocess
    import imageio.v2 as imageio

    frames = load_frames(traj_dir)
    if not frames:
        raise RuntimeError(f"No frames in {traj_dir}")

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_mp4.parent / "_frames_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    pngs = []
    for step, N in frames:
        png = tmp_dir / f"frame_{step:06d}.png"
        fig, _ = render_frame(N, box=box, fov=fov, title=f"step {step}", out_path=png)
        plt.close(fig)
        pngs.append(png)

    # Normalize all frames to a common even size for libx264
    arrays = [np.asarray(imageio.imread(p)) for p in pngs]
    max_h = max(a.shape[0] for a in arrays)
    max_w = max(a.shape[1] for a in arrays)
    max_h += max_h % 2
    max_w += max_w % 2

    def _fit(img: np.ndarray) -> np.ndarray:
        h, w = img.shape[:2]
        out = np.zeros((max_h, max_w, img.shape[2]), dtype=img.dtype)
        out[:h, :w] = img
        if h < max_h:
            out[h:, :w] = img[-1:, :, :]
        if w < max_w:
            out[:, w:] = out[:, w - 1 : w, :]
        return out

    # Prefer system ffmpeg for robust encoding
    pattern = str(tmp_dir / "enc_%06d.png")
    for i, arr in enumerate(arrays):
        imageio.imwrite(pattern % (i + 1), _fit(arr))
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        pattern,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for p in tmp_dir.glob("*"):
        p.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass
    return out_mp4


def box_fov_from_config(cfg: dict) -> tuple[float, float]:
    """Read solver box edge and in-plane FOV from case config (new or legacy keys)."""
    if "box_size_solver_3d" in cfg:
        box = float(cfg["box_size_solver_3d"][0])
    else:
        box = float(cfg["box_size"][0])
    if "field_of_view_001_2d" in cfg:
        fov = float(cfg["field_of_view_001_2d"][0])
    elif "field_of_view" in cfg:
        fov = float(cfg["field_of_view"][0])
    else:
        fov = box
    return box, fov


def visualize_case(case_dir: Path, box: float, fov: float) -> dict[str, str]:
    traj = case_dir / "raw_trajectory"
    vis = case_dir / "visualizations"
    vis.mkdir(parents=True, exist_ok=True)
    frames = load_frames(traj)
    if not frames:
        raise RuntimeError(f"No trajectory frames for {case_dir}")

    init_step, N0 = frames[0]
    final_step, N1 = frames[-1]
    init_png = vis / "initial.png"
    final_png = vis / "final.png"
    fig, _ = render_frame(N0, box=box, fov=fov, title=f"initial (step {init_step})", out_path=init_png)
    plt.close(fig)
    fig, _ = render_frame(N1, box=box, fov=fov, title=f"final (step {final_step})", out_path=final_png)
    plt.close(fig)
    mp4 = vis / "evolution.mp4"
    make_video(traj, mp4, box=box, fov=fov, fps=4)
    return {
        "initial": str(init_png),
        "final": str(final_png),
        "video": str(mp4),
    }
