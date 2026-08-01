"""Visualization of dislocation-network trajectories.

Renders the initial and final configurations as PNG images and the full time
evolution as an MP4 video, using a fixed camera, a fixed axis convention and a
consistent box representation across all cases.  Dislocation segments are
colored by Burgers-vector family (slip-system category).

Only numpy/matplotlib are required: the input is the processed trajectory
produced by :mod:`data_ddd.trajectory`.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection  # noqa: E402

from data_ddd.paths import CasePaths  # noqa: E402
from data_ddd.trajectory import load_trajectory  # noqa: E402

# Fixed camera and figure geometry shared by every case.  The view direction
# (elev=35, azim=-135) is chosen so that no {111} glide plane is seen edge-on:
# the smallest angle between the view direction and any {111} normal keeps
# |cos| >= 0.33, so loops on every slip system stay visible as ellipses.
VIEW_ELEV = 35.0
VIEW_AZIM = -135.0
FIG_SIZE = (7.2, 6.4)
FIG_DPI = 100
FPS = 8

# stable colors per Burgers-vector family
BURGERS_COLORS: List[Tuple[Tuple[float, float, float], str]] = [
    ((1.0, 1.0, 0.0), "#1f77b4"),
    ((1.0, -1.0, 0.0), "#ff7f0e"),
    ((1.0, 0.0, 1.0), "#2ca02c"),
    ((1.0, 0.0, -1.0), "#d62728"),
    ((0.0, 1.0, 1.0), "#9467bd"),
    ((0.0, 1.0, -1.0), "#8c564b"),
    ((1.0, 0.0, 0.0), "#17becf"),
    ((0.0, 1.0, 0.0), "#bcbd22"),
    ((0.0, 0.0, 1.0), "#e377c2"),
]
DEFAULT_COLOR = "#7f7f7f"


def canonical_burgers(b: np.ndarray) -> Tuple[float, float, float]:
    """Direction of a Burgers vector, with a canonical sign (+/-b are one family)."""
    norm = np.linalg.norm(b)
    if norm < 1e-12:
        return (0.0, 0.0, 0.0)
    d = b / norm
    for value in d:
        if abs(value) > 1e-8:
            if value < 0:
                d = -d
            break
    return tuple(np.round(d, 4))


def burgers_color(b: np.ndarray) -> Tuple[str, str]:
    """Return the (color, label) of the Burgers-vector family of ``b``."""
    d = np.asarray(canonical_burgers(b), dtype=float)
    if not np.any(d):
        return DEFAULT_COLOR, "b = 0"
    for ref, color in BURGERS_COLORS:
        ref = np.asarray(ref, dtype=float)
        ref = ref / np.linalg.norm(ref)
        if abs(float(np.dot(d, ref))) > 1.0 - 1e-4:
            ints = np.round(ref * np.sqrt(2.0)).astype(int)
            if np.allclose(np.abs(ints), np.abs(ref * np.sqrt(2.0)), atol=1e-3):
                label = "1/2[%d%d%d]" % tuple(ints)
            else:
                label = "[%.2f %.2f %.2f]" % tuple(ref)
            return color, label
    return DEFAULT_COLOR, "[%.2f %.2f %.2f]" % tuple(d)


def _wrap(point: np.ndarray, box: np.ndarray, pbc: Sequence[bool]) -> np.ndarray:
    out = np.array(point, dtype=float, copy=True)
    for k in range(3):
        if pbc[k]:
            out[k] -= box[k] * np.floor(out[k] / box[k])
    return out


def _min_image(delta: np.ndarray, box: np.ndarray, pbc: Sequence[bool]) -> np.ndarray:
    out = np.array(delta, dtype=float, copy=True)
    for k in range(3):
        if pbc[k]:
            out[k] -= box[k] * np.round(out[k] / box[k])
    return out


def split_pbc_segment(
    r1: np.ndarray, r2: np.ndarray, box: np.ndarray, pbc: Sequence[bool]
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Split a segment at the periodic boundaries so every piece stays in the box."""
    eps = 1e-12
    pieces = []
    r1 = _wrap(r1, box, pbc)
    r2 = r1 + _min_image(r2 - r1, box, pbc)
    for _ in range(8):
        d = r2 - r1
        t_min, axis, sign = 1.0, -1, 0
        for k in range(3):
            if not pbc[k]:
                continue
            if d[k] > eps:
                t, s = (box[k] - r1[k]) / d[k], 1
            elif d[k] < -eps:
                t, s = (0.0 - r1[k]) / d[k], -1
            else:
                continue
            if eps < t < t_min:
                t_min, axis, sign = t, k, s
        if axis < 0:
            pieces.append((r1.copy(), r2.copy()))
            return pieces
        crossing = r1 + t_min * d
        pieces.append((r1.copy(), crossing.copy()))
        shift = np.zeros(3)
        shift[axis] = -sign * box[axis]
        r1 = crossing + shift
        r2 = r2 + shift
    pieces.append((r1.copy(), r2.copy()))
    return pieces


def frame_segments(
    frame: Dict[str, Any], box: np.ndarray, pbc: Sequence[bool]
) -> Tuple[np.ndarray, List[str], Dict[str, str]]:
    """Segment endpoints, colors and legend entries of one frame."""
    rn = frame["positions"]
    nodeids = frame["nodeids"]
    lines, colors, legend = [], [], {}
    for index in range(nodeids.shape[0]):
        n1, n2 = nodeids[index]
        color, label = burgers_color(frame["burgers"][index])
        legend[label] = color
        for p1, p2 in split_pbc_segment(rn[n1], rn[n2], box, pbc):
            lines.append([p1, p2])
            colors.append(color)
    return np.array(lines) if lines else np.zeros((0, 2, 3)), colors, legend


def _box_edges(origin: np.ndarray, box: np.ndarray) -> np.ndarray:
    o = np.asarray(origin, dtype=float)
    h = np.diag(np.asarray(box, dtype=float))
    corners = o + np.array(
        [
            np.zeros(3), h[0], h[0] + h[1], h[1],
            h[2], h[0] + h[2], h[0] + h[1] + h[2], h[1] + h[2],
        ]
    )
    edges = np.array(
        [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4],
         [0, 4], [1, 5], [2, 6], [3, 7]]
    )
    return corners[edges]


def setup_axes(ax, box: np.ndarray, fov: np.ndarray, title: str = "") -> None:
    """Fixed camera, axis convention, cell and field-of-view representation."""
    center = 0.5 * box
    lo = center - 0.5 * fov
    hi = center + 0.5 * fov
    ax.add_collection(
        Line3DCollection(_box_edges(np.zeros(3), box), colors="k", linewidths=0.8, alpha=0.45)
    )
    if not np.allclose(fov, box):
        ax.add_collection(
            Line3DCollection(
                _box_edges(lo, fov), colors="tab:red", linewidths=0.9, alpha=0.7, linestyles="--"
            )
        )
    # a small margin keeps the cell wireframe strictly inside the plot area, and
    # an orthographic projection avoids perspective making in-box lines look as
    # if they crossed the cell faces
    margin = 0.04 * fov
    ax.set_xlim(lo[0] - margin[0], hi[0] + margin[0])
    ax.set_ylim(lo[1] - margin[1], hi[1] + margin[1])
    ax.set_zlim(lo[2] - margin[2], hi[2] + margin[2])
    try:
        ax.set_proj_type("ortho")
    except AttributeError:  # pragma: no cover - old matplotlib
        pass
    ax.set_xlabel("x [b]")
    ax.set_ylabel("y [b]")
    ax.set_zlabel("z [b]")
    ax.view_init(elev=VIEW_ELEV, azim=VIEW_AZIM)
    try:
        ax.set_box_aspect(list(fov / np.max(fov)))
    except AttributeError:  # pragma: no cover - old matplotlib
        pass
    if title:
        ax.set_title(title, fontsize=10)


def draw_frame(ax, frame, box, fov, pbc, title: str, show_nodes: bool = True) -> None:
    ax.cla()
    setup_axes(ax, box, fov, title)
    lines, colors, legend = frame_segments(frame, box, pbc)
    if lines.shape[0]:
        # segments outside the field of view are kept as faint context
        center = 0.5 * np.asarray(box, dtype=float)
        half = 0.5 * np.asarray(fov, dtype=float)
        mid = lines.mean(axis=1)
        inside = np.all(np.abs(mid - center) <= half, axis=1)
        if np.any(~inside):
            ax.add_collection(
                Line3DCollection(
                    lines[~inside], colors="0.6", linewidths=0.7, alpha=0.45
                )
            )
        if np.any(inside):
            ax.add_collection(
                Line3DCollection(
                    lines[inside],
                    colors=[c for c, keep in zip(colors, inside) if keep],
                    linewidths=1.4,
                )
            )
        if show_nodes:
            rn = np.array([_wrap(p, box, pbc) for p in frame["positions"]])
            visible = np.all(np.abs(rn - center) <= half, axis=1)
            if np.any(visible):
                rn = rn[visible]
                ax.scatter(rn[:, 0], rn[:, 1], rn[:, 2], c="k", s=2.0, alpha=0.35)
    handles = [
        Line2D([0], [0], color=color, lw=2, label="b = %s" % label)
        for label, color in sorted(legend.items())
    ]
    if handles:
        ax.legend(handles=handles, loc="upper left", fontsize=7, framealpha=0.85)


def frame_title(case: str, frame: Dict[str, Any], stress_vm: float) -> str:
    return "%s\nstep %d   t = %.3e s   sigma_vM = %.0f MPa   %d nodes" % (
        case,
        frame["step"],
        frame["time"],
        stress_vm / 1e6,
        frame["positions"].shape[0],
    )


def von_mises(voigt: np.ndarray) -> float:
    v = np.asarray(voigt, dtype=float)
    s = np.array([[v[0], v[5], v[4]], [v[5], v[1], v[3]], [v[4], v[3], v[2]]])
    dev = s - np.trace(s) / 3.0 * np.eye(3)
    return float(np.sqrt(1.5 * np.sum(dev * dev)))


def render_case(case_dir: str, fps: int = FPS, video: bool = True) -> Dict[str, Any]:
    """Render initial/final images and the evolution video of a case."""
    paths = CasePaths(root=case_dir)
    traj = load_trajectory(paths.trajectory)
    frames = traj["frames"]
    if not frames:
        raise RuntimeError("empty trajectory in %s" % paths.trajectory)

    box = np.asarray(traj["box_b"], dtype=float)
    fov = np.asarray(traj["fov_b"], dtype=float)
    pbc = [bool(p) for p in np.asarray(traj["pbc"]).ravel()]
    stress_vm = von_mises(traj["applied_stress_voigt"])
    case = os.path.basename(os.path.normpath(case_dir))
    os.makedirs(paths.vis, exist_ok=True)

    outputs = {}
    for label, frame, path in (
        ("initial", frames[0], paths.initial_png),
        ("final", frames[-1], paths.final_png),
    ):
        fig = plt.figure(figsize=FIG_SIZE, dpi=FIG_DPI)
        ax = fig.add_subplot(111, projection="3d")
        draw_frame(ax, frame, box, fov, pbc, frame_title(case, frame, stress_vm))
        fig.tight_layout()
        fig.savefig(path, dpi=FIG_DPI)
        plt.close(fig)
        outputs[label] = path

    if video:
        from matplotlib import animation

        fig = plt.figure(figsize=FIG_SIZE, dpi=FIG_DPI)
        ax = fig.add_subplot(111, projection="3d")

        def update(index: int):
            draw_frame(ax, frames[index], box, fov, pbc,
                       frame_title(case, frames[index], stress_vm))
            return []

        anim = animation.FuncAnimation(fig, update, frames=len(frames), blit=False)
        writer = animation.FFMpegWriter(
            fps=fps, bitrate=2400, metadata={"title": case, "artist": "data_ddd"}
        )
        anim.save(paths.video, writer=writer, dpi=FIG_DPI)
        plt.close(fig)
        outputs["video"] = paths.video

    outputs["n_frames"] = len(frames)
    return outputs


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a DDD case trajectory")
    parser.add_argument("case_dir")
    parser.add_argument("--fps", type=int, default=FPS)
    parser.add_argument("--no-video", action="store_true")
    args = parser.parse_args(argv)
    out = render_case(args.case_dir, fps=args.fps, video=not args.no_video)
    print("rendered %s (%d frames): %s" % (args.case_dir, out["n_frames"],
                                           ", ".join(k for k in out if k != "n_frames")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
