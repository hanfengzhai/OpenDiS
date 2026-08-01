"""Layout of a dataset case directory."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_DATASET_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "glissile_loops"
)


@dataclass
class CasePaths:
    root: str

    @property
    def config(self) -> str:
        return os.path.join(self.root, "config.yaml")

    @property
    def metadata(self) -> str:
        return os.path.join(self.root, "metadata.json")

    @property
    def inputs(self) -> str:
        return os.path.join(self.root, "inputs")

    @property
    def initial_data(self) -> str:
        return os.path.join(self.inputs, "initial_network.data")

    @property
    def initial_npz(self) -> str:
        return os.path.join(self.inputs, "initial_network.npz")

    @property
    def run_params(self) -> str:
        return os.path.join(self.inputs, "run_params.json")

    @property
    def raw(self) -> str:
        return os.path.join(self.root, "raw")

    @property
    def processed(self) -> str:
        return os.path.join(self.root, "processed")

    @property
    def trajectory(self) -> str:
        return os.path.join(self.processed, "trajectory.npz")

    @property
    def trajectory_summary(self) -> str:
        return os.path.join(self.processed, "trajectory_summary.csv")

    @property
    def logs(self) -> str:
        return os.path.join(self.root, "logs")

    @property
    def run_log(self) -> str:
        return os.path.join(self.logs, "run.log")

    @property
    def run_info(self) -> str:
        return os.path.join(self.logs, "run_info.json")

    @property
    def validation(self) -> str:
        return os.path.join(self.root, "validation")

    @property
    def vis(self) -> str:
        return os.path.join(self.root, "vis")

    @property
    def initial_png(self) -> str:
        return os.path.join(self.vis, "initial.png")

    @property
    def final_png(self) -> str:
        return os.path.join(self.vis, "final.png")

    @property
    def video(self) -> str:
        return os.path.join(self.vis, "evolution.mp4")

    def make_dirs(self) -> None:
        for path in (self.root, self.inputs, self.raw, self.processed, self.logs,
                     self.validation, self.vis):
            os.makedirs(path, exist_ok=True)


def case_paths(dataset_root: str, name: str) -> CasePaths:
    return CasePaths(root=os.path.join(dataset_root, name))
