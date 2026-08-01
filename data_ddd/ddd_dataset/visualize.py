"""Trajectory visualization: evolution video (mp4) + initial/final snapshots.

Uses a consistent camera (elev=20, azim=-60), a wireframe box for the
simulation cell, the field-of-view window of the case for the axis limits,
and colors dislocation segments by their Burgers-vector family.
"""

import os
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.animation import FFMpegWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from .config import CaseConfig

CAMERA = {"elev": 20, "azim": -60}
PALETTE = plt.get_cmap("tab10").colors


def load_trajectory(case_dir: str) -> dict:
    """Load the processed trajectory saved by the runner."""
    npz = np.load(os.path.join(case_dir, "processed", "trajectory.npz"))
    steps = npz["frame_steps"]
    frames = []
    for k in range(len(steps)):
        frames.append({
            "positions": npz[f"positions_{k:04d}"],
            "nodeids": npz[f"nodeids_{k:04d}"],
            "burgers": npz[f"burgers_{k:04d}"],
            "planes": npz[f"planes_{k:04d}"],
        })
    return {"frames": frames, "steps": steps, "times": npz["frame_times"],
            "box_size": npz["box_size"], "fov": npz["fov"]}


def _burgers_family(b: np.ndarray) -> tuple:
    """Canonical key for a Burgers-vector family (sign-independent)."""
    bn = b / max(np.linalg.norm(b), 1e-300)
    for c in bn:
        if abs(c) > 1e-8:
            if c < 0:
                bn = -bn
            break
    return tuple(np.round(bn, 3))


def _min_image(d: np.ndarray, L: np.ndarray) -> np.ndarray:
    return d - L * np.round(d / L)


def _frame_lines(frame: dict, L: np.ndarray, center: np.ndarray):
    """Segment endpoint pairs mapped into the primary cell, grouped by
    Burgers family."""
    pos = frame["positions"]
    ids = frame["nodeids"]
    burg = frame["burgers"]
    # map node1 into the box (minimum image w.r.t. the box center)
    grouped = {}
    for i in range(ids.shape[0]):
        p1 = pos[ids[i, 0]]
        p2 = pos[ids[i, 1]]
        p1m = center + _min_image(p1 - center, L)
        p2m = p1m + _min_image(p2 - p1, L)
        fam = _burgers_family(burg[i])
        grouped.setdefault(fam, []).append([p1m, p2m])
    return grouped


class TrajectoryRenderer:
    def __init__(self, case_dir: str):
        self.case_dir = case_dir
        self.config = CaseConfig.load(os.path.join(case_dir, "config.json"))
        self.traj = load_trajectory(case_dir)
        self.L = np.asarray(self.traj["box_size"], dtype=float)
        self.center = self.L / 2.0            # cell origin is at 0
        self.fov = np.asarray(self.traj["fov"], dtype=float)
        # stable family -> color mapping across the whole trajectory
        fams = []
        for fr in self.traj["frames"]:
            for i in range(fr["burgers"].shape[0]):
                fam = _burgers_family(fr["burgers"][i])
                if fam not in fams:
                    fams.append(fam)
        self.fam_colors = {f: PALETTE[i % len(PALETTE)]
                           for i, f in enumerate(sorted(fams))}

    # ------------------------------------------------------------------
    def _setup_axes(self, ax):
        half = self.fov / 2.0
        lo = self.center - half
        hi = self.center + half
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_zlim(lo[2], hi[2])
        ax.set_xlabel("x [b]")
        ax.set_ylabel("y [b]")
        ax.set_zlabel("z [b]")
        ax.set_box_aspect([1, 1, 1])
        ax.view_init(**CAMERA)

    def _draw_box(self, ax):
        """Wireframe of the simulation cell."""
        lo = np.zeros(3)
        hi = self.L
        corners = np.array([[x, y, z] for x in (lo[0], hi[0])
                            for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6),
                 (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]
        segs = [[corners[a], corners[b]] for a, b in edges]
        ax.add_collection(Line3DCollection(segs, colors="0.6",
                                           linewidths=0.8, linestyles=":"))

    def _draw_frame(self, ax, k: int):
        ax.cla()
        self._setup_axes(ax)
        self._draw_box(ax)
        frame = self.traj["frames"][k]
        grouped = _frame_lines(frame, self.L, self.center)
        for fam, lines in grouped.items():
            ax.add_collection(Line3DCollection(
                np.array(lines), colors=[self.fam_colors[fam]],
                linewidths=1.6))
        # legend of Burgers families
        handles = [Line2D([0], [0], color=self.fam_colors[f], lw=2,
                          label=f"b = [{f[0]:g} {f[1]:g} {f[2]:g}]")
                   for f in self.fam_colors]
        ax.legend(handles=handles, loc="upper left", fontsize=8)
        step = self.traj["steps"][k]
        t = self.traj["times"][k]
        n_seg = frame["nodeids"].shape[0]
        ax.set_title(f"{self.config.name}\n"
                     f"step {step}  t = {t:.3e} s   {n_seg} segments")

    # ------------------------------------------------------------------
    def snapshot(self, k: int, filename: str, dpi: int = 140):
        fig = plt.figure(figsize=(7.2, 6.4))
        ax = fig.add_subplot(projection="3d")
        self._draw_frame(ax, k)
        fig.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    def video(self, filename: str, fps: int = 8, dpi: int = 120):
        fig = plt.figure(figsize=(7.2, 6.4))
        ax = fig.add_subplot(projection="3d")
        writer = FFMpegWriter(fps=fps, metadata={"title": self.config.name})
        with writer.saving(fig, filename, dpi=dpi):
            for k in range(len(self.traj["frames"])):
                self._draw_frame(ax, k)
                writer.grab_frame()
        plt.close(fig)


def visualize_case(case_dir: str) -> dict:
    """Render initial/final snapshots and the evolution video for a case."""
    vis_dir = os.path.join(case_dir, "vis")
    os.makedirs(vis_dir, exist_ok=True)
    rend = TrajectoryRenderer(case_dir)
    n = len(rend.traj["frames"])
    out = {
        "initial": os.path.join(vis_dir, "initial.png"),
        "final": os.path.join(vis_dir, "final.png"),
        "video": os.path.join(vis_dir, "evolution.mp4"),
        "n_frames": n,
    }
    rend.snapshot(0, out["initial"])
    rend.snapshot(n - 1, out["final"])
    rend.video(out["video"])
    return out
