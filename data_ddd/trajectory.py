"""Convert raw ExaDiS trajectory output into processed, self-contained data.

The raw output of a run is a series of ParaDiS-format ``config.<step>.data``
files.  This module reads them back through ExaDiS, attaches the simulated time
of each frame, computes per-frame diagnostics (node/segment counts, line length,
dislocation density, Nye charge) and stores everything in a single ``.npz`` file
that the visualization step can read without ExaDiS.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from typing import Any, Dict, List

import numpy as np

from data_ddd import exadis_env
from data_ddd.config import CaseConfig, load_case
from data_ddd.paths import CasePaths
from data_ddd.validation import validate_run

_STEP_RE = re.compile(r"config\.(\d+)\.data$")


def raw_frame_files(raw_dir: str) -> List[tuple]:
    frames = []
    for name in os.listdir(raw_dir):
        match = _STEP_RE.match(name)
        if match:
            frames.append((int(match.group(1)), os.path.join(raw_dir, name)))
    return sorted(frames)


def _min_image(delta: np.ndarray, box: np.ndarray, pbc) -> np.ndarray:
    delta = np.array(delta, dtype=float, copy=True)
    for k in range(3):
        if pbc[k]:
            delta[..., k] -= box[k] * np.round(delta[..., k] / box[k])
    return delta


def read_frames(config: CaseConfig, paths: CasePaths) -> List[Dict[str, Any]]:
    """Read the raw trajectory frames of a case."""
    exadis_env.initialize()
    import pyexadis
    from pyexadis_base import ExaDisNet

    times = {0: 0.0}
    if os.path.exists(paths.run_info):
        with open(paths.run_info, "r", encoding="utf-8") as handle:
            info = json.load(handle)
        for record in info.get("history", []):
            times[int(record["step"])] = float(record["time"])

    frames = []
    for step, path in raw_frame_files(paths.raw):
        net = ExaDisNet(pyexadis.read_paradis(path))
        data = net.export_data()
        frames.append(
            {
                "step": step,
                "time": times.get(step, float("nan")),
                "positions": np.asarray(data["nodes"]["positions"], dtype=float),
                "constraints": np.asarray(data["nodes"]["constraints"], dtype=int).ravel(),
                "nodeids": np.asarray(data["segs"]["nodeids"], dtype=int),
                "burgers": np.asarray(data["segs"]["burgers"], dtype=float),
                "planes": np.asarray(data["segs"]["planes"], dtype=float),
            }
        )
    return frames


def frame_diagnostics(config: CaseConfig, frame: Dict[str, Any]) -> Dict[str, float]:
    box = config.box_b
    pbc = config.pbc
    rn = frame["positions"]
    nodeids = frame["nodeids"]
    if nodeids.size == 0:
        return {
            "n_nodes": int(rn.shape[0]),
            "n_segs": 0,
            "line_length_b": 0.0,
            "density_m2": 0.0,
            "nye_norm": 0.0,
        }
    d = _min_image(rn[nodeids[:, 1]] - rn[nodeids[:, 0]], box, pbc)
    lengths = np.linalg.norm(d, axis=1)
    volume = float(np.prod(box))
    burgmag = float(config.physics["material"]["burgmag"])
    density = float(lengths.sum() / volume / burgmag**2)
    alpha = np.einsum("ij,ik->jk", frame["burgers"], d) / volume
    return {
        "n_nodes": int(rn.shape[0]),
        "n_segs": int(nodeids.shape[0]),
        "line_length_b": float(lengths.sum()),
        "density_m2": density,
        "nye_norm": float(np.linalg.norm(alpha)),
    }


def process_case(case_dir: str) -> Dict[str, Any]:
    paths = CasePaths(root=case_dir)
    config = load_case(paths.config)
    paths.make_dirs()

    frames = read_frames(config, paths)
    if not frames:
        raise RuntimeError("no raw trajectory frames found in %s" % paths.raw)

    arrays: Dict[str, np.ndarray] = {
        "cell_h": np.diag(config.box_b),
        "cell_origin": np.zeros(3),
        "box_b": config.box_b,
        "fov_b": config.fov_b,
        "pbc": np.array(config.pbc),
        "steps": np.array([f["step"] for f in frames], dtype=int),
        "times": np.array([f["time"] for f in frames], dtype=float),
        "applied_stress_voigt": np.array(config.stress.voigt, dtype=float),
    }
    rows = []
    for index, frame in enumerate(frames):
        arrays["positions_%04d" % index] = frame["positions"]
        arrays["nodeids_%04d" % index] = frame["nodeids"]
        arrays["burgers_%04d" % index] = frame["burgers"]
        arrays["planes_%04d" % index] = frame["planes"]
        diag = frame_diagnostics(config, frame)
        rows.append(dict(step=frame["step"], time_s=frame["time"], **diag))
    arrays["n_frames"] = np.array(len(frames))
    np.savez_compressed(paths.trajectory, **arrays)

    with open(paths.trajectory_summary, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    run_info = {"returncode": 0}
    if os.path.exists(paths.run_info):
        with open(paths.run_info, "r", encoding="utf-8") as handle:
            run_info = json.load(handle)
    report = validate_run(config, case_dir, frames, run_info)
    report.write(os.path.join(paths.validation, "run.json"))

    return {
        "case": config.name,
        "n_frames": len(frames),
        "validation": report.to_dict(),
        "summary": rows,
    }


def load_trajectory(path: str) -> Dict[str, Any]:
    """Load a processed trajectory (no ExaDiS needed)."""
    data = np.load(path)
    n_frames = int(data["n_frames"])
    frames = []
    for index in range(n_frames):
        frames.append(
            {
                "step": int(data["steps"][index]),
                "time": float(data["times"][index]),
                "positions": data["positions_%04d" % index],
                "nodeids": data["nodeids_%04d" % index],
                "burgers": data["burgers_%04d" % index],
                "planes": data["planes_%04d" % index],
            }
        )
    return {
        "cell_h": data["cell_h"],
        "cell_origin": data["cell_origin"],
        "box_b": data["box_b"],
        "fov_b": data["fov_b"],
        "pbc": data["pbc"],
        "applied_stress_voigt": data["applied_stress_voigt"],
        "frames": frames,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process the raw trajectory of a case")
    parser.add_argument("case_dir")
    args = parser.parse_args(argv)
    result = process_case(args.case_dir)
    print("processed %s: %d frames, validation ok=%s"
          % (result["case"], result["n_frames"], result["validation"]["ok"]))
    return 0 if result["validation"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
