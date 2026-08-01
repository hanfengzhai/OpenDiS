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
    segs = data["segs"]
    ids = np.asarray(segs["nodeids"], dtype=int)
    burgs = np.asarray(segs["burgers"], dtype=float)
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


def render_frame(
    N: DisNetManager,
    *,
    box: float,
    fov: float,
    title: str,
    out_path: Path | None = None,
    elev: float = 22.0,
    azim: float = -60.0,
):
    origin = np.zeros(3)
    center = origin + 0.5 * box
    lines, colors = _segment_polylines(N, center)

    # Size chosen so ffmpeg macro-block padding is minimal (approx 800x800 after save)
    fig = plt.figure(figsize=(8.0, 8.0), dpi=100)
    ax = fig.add_subplot(111, projection="3d")
    if len(lines):
        lc = Line3DCollection(lines, colors=np.clip(colors, 0, 1), linewidths=2.8, alpha=1.0)
        ax.add_collection3d(lc)
        # Node markers improve visibility for compact prismatic loops
        pts = np.unique(np.vstack([np.asarray(seg) for seg in lines]), axis=0)
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c="k", s=12, depthshade=False)
    _draw_box(ax, origin, np.array([box, box, box]), color="0.25", lw=1.2)
    if abs(fov - box) > 1e-9:
        fov_origin = center - 0.5 * fov
        _draw_box(ax, fov_origin, np.array([fov, fov, fov]), color="#c45c26", lw=1.4)

    ax.set_xlim(origin[0], origin[0] + box)
    ax.set_ylim(origin[1], origin[1] + box)
    ax.set_zlim(origin[2], origin[2] + box)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=11)
    ax.set_box_aspect((1, 1, 1))
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
