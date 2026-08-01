"""Validation of dataset cases: configuration, initial network and finished runs.

The checks cover invalid connectivity, degenerate segments, duplicate nodes and
links, inconsistent Burgers vectors, invalid glide planes, loops leaving the
box, unintended intersections, excessive proximity to periodic images, missing
elasticity settings and incomplete simulations.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

import numpy as np

from data_ddd.config import CaseConfig
from data_ddd.reference import FCC_SLIP_SYSTEMS

PASS = "pass"
WARN = "warn"
FAIL = "fail"

ELASTICITY_FORCE_MODES = ("DDD_FFT_MODEL", "SUBCYCLING_MODEL", "CUTOFF_MODEL")


@dataclass
class Check:
    name: str
    status: str
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "data": self.data,
        }


@dataclass
class ValidationReport:
    case: str
    stage: str
    checks: List[Check] = field(default_factory=list)

    def add(self, name: str, status: str, message: str = "", **data: Any) -> Check:
        check = Check(name=name, status=status, message=message, data=data)
        self.checks.append(check)
        return check

    @property
    def failures(self) -> List[Check]:
        return [c for c in self.checks if c.status == FAIL]

    @property
    def warnings(self) -> List[Check]:
        return [c for c in self.checks if c.status == WARN]

    @property
    def ok(self) -> bool:
        return not self.failures

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case": self.case,
            "stage": self.stage,
            "ok": self.ok,
            "n_pass": len([c for c in self.checks if c.status == PASS]),
            "n_warn": len(self.warnings),
            "n_fail": len(self.failures),
            "checks": [c.to_dict() for c in self.checks],
        }

    def summary(self) -> str:
        parts = [
            "%s [%s]: %d pass, %d warn, %d fail"
            % (
                self.case,
                self.stage,
                len([c for c in self.checks if c.status == PASS]),
                len(self.warnings),
                len(self.failures),
            )
        ]
        for check in self.checks:
            if check.status != PASS:
                parts.append("  %-6s %s: %s" % (check.status.upper(), check.name, check.message))
        return "\n".join(parts)

    def write(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)


def merge_reports(reports: Sequence[ValidationReport]) -> ValidationReport:
    merged = ValidationReport(case=reports[0].case if reports else "", stage="all")
    for report in reports:
        for check in report.checks:
            merged.checks.append(
                Check(
                    name="%s/%s" % (report.stage, check.name),
                    status=check.status,
                    message=check.message,
                    data=check.data,
                )
            )
    return merged


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _min_image(delta: np.ndarray, box: np.ndarray, pbc: Sequence[bool]) -> np.ndarray:
    delta = np.array(delta, dtype=float, copy=True)
    for k in range(3):
        if pbc[k]:
            delta[..., k] -= box[k] * np.round(delta[..., k] / box[k])
    return delta


def _pairwise_min_distance(
    a: np.ndarray, b: np.ndarray, box: np.ndarray, pbc: Sequence[bool]
) -> float:
    d = a[:, None, :] - b[None, :, :]
    d = _min_image(d, box, pbc)
    return float(np.min(np.linalg.norm(d, axis=-1)))


def _is_fcc_system(burg: np.ndarray, plane: np.ndarray, tol: float = 1e-6) -> bool:
    for b_ref, n_ref in FCC_SLIP_SYSTEMS:
        b_ref = np.asarray(b_ref, dtype=float)
        n_ref = np.asarray(n_ref, dtype=float)
        b_ref = b_ref / np.linalg.norm(b_ref)
        n_ref = n_ref / np.linalg.norm(n_ref)
        same_b = np.allclose(np.abs(burg @ b_ref), 1.0, atol=1e-5)
        same_n = np.allclose(np.abs(plane @ n_ref), 1.0, atol=1e-5)
        if same_b and same_n:
            return True
    return False


# ---------------------------------------------------------------------------
# configuration-level validation
# ---------------------------------------------------------------------------
def validate_config(config: CaseConfig) -> ValidationReport:
    report = ValidationReport(case=config.name, stage="config")
    box = config.box_b
    pbc = config.pbc

    # --- box / field of view ------------------------------------------------
    if len(config.box_size) == 3 and np.all(np.asarray(config.box_size) > 0):
        report.add(
            "box_is_3d",
            PASS,
            "box is a 3-D cell %s (nominal) = %s b"
            % (list(config.box_size), [round(v, 1) for v in box]),
        )
    else:
        report.add("box_is_3d", FAIL, "box_size must be a positive 3-vector")

    if np.all(config.fov_b <= box + 1e-9):
        report.add("fov_within_box", PASS, "field of view %s u" % list(config.fov))
    else:
        report.add(
            "fov_within_box",
            FAIL,
            "field of view %s exceeds the box %s" % (list(config.fov), list(config.box_size)),
        )

    # --- elasticity / force-model settings ---------------------------------
    force = config.physics.get("force", {})
    mode = force.get("force_mode")
    if mode in ELASTICITY_FORCE_MODES:
        report.add("elasticity_enabled", PASS, "force_mode=%s" % mode)
    else:
        report.add(
            "elasticity_enabled",
            FAIL,
            "force_mode=%r is not an elasticity-enabled model %s" % (mode, ELASTICITY_FORCE_MODES),
        )
    material = config.physics.get("material", {})
    missing = [k for k in ("mu", "nu", "a", "burgmag", "crystal") if k not in material]
    if missing:
        report.add("material_parameters", FAIL, "missing material parameters: %s" % missing)
    else:
        report.add(
            "material_parameters",
            PASS,
            "mu=%.3g Pa, nu=%.3g, a=%.3g b, b=%.3g m"
            % (material["mu"], material["nu"], material["a"], material["burgmag"]),
        )
    for key in ("mobility", "time_integration", "collision", "topology", "remesh"):
        if config.physics.get(key):
            report.add("module_%s" % key, PASS, str(config.physics[key]))
        else:
            report.add("module_%s" % key, FAIL, "missing reference settings for '%s'" % key)

    if mode in ("DDD_FFT_MODEL", "SUBCYCLING_MODEL") and not all(pbc):
        report.add(
            "pbc_for_fft",
            FAIL,
            "the DDD-FFT elasticity model requires full periodic boundary conditions",
        )
    else:
        report.add("pbc_for_fft", PASS, "pbc=%s" % list(pbc))

    grid = config.fft_grid()
    spacing = box / np.asarray(grid, dtype=float)
    maxseg = float(config.physics["discretization"]["maxseg"])
    if np.all(spacing > 0.5 * maxseg):
        report.add(
            "fft_grid", PASS, "Ngrid=%s, spacing=%s b" % (grid, [round(s, 1) for s in spacing])
        )
    else:
        report.add(
            "fft_grid",
            WARN,
            "FFT grid spacing %s b is small compared with maxseg=%g b"
            % ([round(s, 1) for s in spacing], maxseg),
        )

    # --- applied stress -----------------------------------------------------
    stress = config.stress
    if not np.all(np.isfinite(stress.voigt)):
        report.add("stress_finite", FAIL, "applied stress contains non-finite values")
    else:
        report.add(
            "stress_finite",
            PASS,
            "sigma_vM=%.3g Pa, voigt=%s" % (stress.von_mises(), [float(v) for v in stress.voigt]),
        )
    tensor = stress.tensor()
    if np.allclose(tensor, tensor.T):
        report.add("stress_symmetric", PASS, "stress tensor is symmetric")
    else:
        report.add("stress_symmetric", FAIL, "stress tensor is not symmetric")
    if stress.von_mises() > 0.05 * material.get("mu", np.inf):
        report.add(
            "stress_magnitude",
            WARN,
            "applied stress %.3g Pa exceeds 5%% of mu; the response may be unphysical"
            % stress.von_mises(),
        )
    else:
        report.add("stress_magnitude", PASS, "sigma_vM/mu = %.4f" % (stress.von_mises() / material["mu"]))

    # --- per-loop checks ----------------------------------------------------
    schmid = []
    for i, loop in enumerate(config.loops):
        b = np.asarray(loop.burgers, dtype=float)
        b = b / np.linalg.norm(b)
        n = np.asarray(loop.plane, dtype=float)
        n = n / np.linalg.norm(n)
        if abs(float(b @ n)) > 1e-8:
            report.add(
                "loop%d_glissile" % i, FAIL, "Burgers vector is not contained in the glide plane"
            )
        if not _is_fcc_system(b, n):
            report.add(
                "loop%d_slip_system" % i,
                FAIL,
                "(b=%s, n=%s) is not an FCC 1/2<110>{111} system" % (loop.burgers, loop.plane),
            )
        schmid.append(abs(stress.schmid_factor(b, n)))
    if config.loops:
        if min(schmid) < 0.02:
            report.add(
                "resolved_shear",
                WARN,
                "some loops have a near-zero Schmid factor (min=%.3f); they will barely move"
                % min(schmid),
            )
        else:
            report.add(
                "resolved_shear",
                PASS,
                "Schmid factors in [%.3f, %.3f]" % (min(schmid), max(schmid)),
                schmid_factors=[round(s, 4) for s in schmid],
            )
        report.add("glide_planes", PASS, "%d loops on valid FCC slip systems" % len(config.loops))

    for i, line in enumerate(config.lines):
        b = np.asarray(line.burgers, dtype=float)
        b = b / np.linalg.norm(b)
        n = np.asarray(line.plane, dtype=float)
        n = n / np.linalg.norm(n)
        if abs(float(b @ n)) > 1e-8:
            report.add("line%d_glissile" % i, FAIL, "Burgers vector not contained in glide plane")
        elif not _is_fcc_system(b, n):
            report.add("line%d_slip_system" % i, FAIL, "not an FCC 1/2<110>{111} system")
        else:
            report.add(
                "line%d_slip_system" % i,
                PASS,
                "b=%s, n=%s, Schmid=%.3f" % (line.burgers, line.plane, abs(stress.schmid_factor(b, n))),
            )

    # --- geometric placement ------------------------------------------------
    _validate_placement(config, report, box, pbc)
    return report


def _loop_points(config: CaseConfig, samples: int = 48) -> List[np.ndarray]:
    from data_ddd.geometry import plane_basis

    unit_b = config.unit_b
    out = []
    for loop in config.loops:
        center = np.asarray(loop.center, dtype=float) * unit_b
        radius = loop.radius * unit_b
        u, v = plane_basis(loop.plane, loop.burgers)
        t = 2.0 * np.pi * np.arange(samples) / samples
        out.append(center + radius * (np.cos(t)[:, None] * u + np.sin(t)[:, None] * v))
    return out


def _validate_placement(
    config: CaseConfig, report: ValidationReport, box: np.ndarray, pbc: Sequence[bool]
) -> None:
    points = _loop_points(config)
    if not points:
        return

    # loops inside the simulation box
    outside = []
    for i, pts in enumerate(points):
        if np.any(pts < 0.0) or np.any(pts > box):
            outside.append(i)
    if outside:
        report.add(
            "loops_inside_box",
            FAIL if not all(pbc) else WARN,
            "loops %s extend outside the box (wrapped by PBC)" % outside,
        )
    else:
        report.add("loops_inside_box", PASS, "all loops lie inside the simulation box")

    # boundary margin
    margins = [
        float(min(np.min(pts), np.min(box - pts))) for pts in points
    ]
    min_margin = min(margins)
    radius_b = max(loop.radius for loop in config.loops) * config.unit_b
    if min_margin < 0.25 * radius_b:
        report.add(
            "boundary_margin",
            WARN,
            "closest approach of a loop to the box boundary is %.1f b (< 0.25 R)" % min_margin,
        )
    else:
        report.add("boundary_margin", PASS, "min boundary margin %.1f b" % min_margin)

    # proximity to own periodic images
    image_gaps = []
    for i, pts in enumerate(points):
        extent = np.max(pts, axis=0) - np.min(pts, axis=0)
        image_gaps.append(float(np.min(box - extent)))
    if min(image_gaps) < 2.0 * radius_b:
        report.add(
            "periodic_image_proximity",
            WARN,
            "smallest gap to a periodic image is %.1f b (< 2 R = %.1f b)"
            % (min(image_gaps), 2.0 * radius_b),
        )
    else:
        report.add(
            "periodic_image_proximity",
            PASS,
            "smallest gap to a periodic image is %.1f b" % min(image_gaps),
        )

    # pairwise separation / unintended intersections
    if len(points) > 1:
        intended = config.interaction in ("coplanar", "dipole", "junction", "line_loop", "mixed")
        min_sep = np.inf
        pair = None
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                d = _pairwise_min_distance(points[i], points[j], box, pbc)
                if d < min_sep:
                    min_sep, pair = d, (i, j)
        overlap_tol = 0.05 * radius_b
        near_tol = 0.5 * radius_b
        if min_sep < overlap_tol:
            report.add(
                "loop_intersections",
                FAIL,
                "loops %s overlap (min distance %.2f b)" % (list(pair), min_sep),
            )
        elif min_sep < near_tol and not intended:
            report.add(
                "loop_intersections",
                WARN,
                "loops %s are closer than 0.5 R (%.1f b) without an intended interaction"
                % (list(pair), min_sep),
            )
        else:
            report.add(
                "loop_separation",
                PASS,
                "minimum loop-loop distance %.1f b (pair %s)" % (min_sep, list(pair)),
            )


# ---------------------------------------------------------------------------
# network-level validation
# ---------------------------------------------------------------------------
def validate_network(config: CaseConfig, data: Dict[str, Any]) -> ValidationReport:
    """Validate the network exported from ExaDiS (``DisNetManager.export_data``)."""
    report = ValidationReport(case=config.name, stage="network")
    nodes = data["nodes"]
    segs = data["segs"]
    rn = np.asarray(nodes["positions"], dtype=float)
    constraints = np.asarray(nodes["constraints"], dtype=int).ravel()
    nodeids = np.asarray(segs["nodeids"], dtype=int)
    burgers = np.asarray(segs["burgers"], dtype=float)
    planes = np.asarray(segs["planes"], dtype=float)
    n_nodes, n_segs = rn.shape[0], nodeids.shape[0]
    box = config.box_b
    pbc = config.pbc

    report.add("network_size", PASS, "%d nodes, %d segments" % (n_nodes, n_segs),
               n_nodes=n_nodes, n_segs=n_segs)

    if n_nodes == 0 or n_segs == 0:
        report.add("network_nonempty", FAIL, "empty dislocation network")
        return report
    if not np.all(np.isfinite(rn)):
        report.add("finite_positions", FAIL, "non-finite nodal positions")
    else:
        report.add("finite_positions", PASS, "all nodal positions are finite")

    # connectivity
    if nodeids.min() < 0 or nodeids.max() >= n_nodes:
        report.add("segment_node_ids", FAIL, "segment references a node index out of range")
    else:
        report.add("segment_node_ids", PASS, "all segment node indices are valid")
    self_links = int(np.sum(nodeids[:, 0] == nodeids[:, 1]))
    if self_links:
        report.add("self_links", FAIL, "%d segments connect a node to itself" % self_links)
    else:
        report.add("self_links", PASS, "no self-connected segments")

    arms = np.zeros(n_nodes, dtype=int)
    np.add.at(arms, nodeids[:, 0], 1)
    np.add.at(arms, nodeids[:, 1], 1)
    dangling = np.where((arms < 2) & (constraints != 7))[0]
    isolated = np.where(arms == 0)[0]
    if isolated.size:
        report.add("isolated_nodes", FAIL, "%d nodes have no segment" % isolated.size)
    elif dangling.size:
        report.add(
            "dangling_nodes",
            FAIL,
            "%d unpinned nodes have a single arm (open dislocation line)" % dangling.size,
        )
    else:
        report.add("connectivity", PASS, "every node is pinned or has >= 2 arms")

    # duplicate links
    pairs = np.sort(nodeids, axis=1)
    unique_pairs = np.unique(pairs, axis=0)
    if unique_pairs.shape[0] != pairs.shape[0]:
        report.add(
            "duplicate_links",
            FAIL,
            "%d duplicate node pairs" % (pairs.shape[0] - unique_pairs.shape[0]),
        )
    else:
        report.add("duplicate_links", PASS, "no duplicate links")

    # segment lengths
    d = _min_image(rn[nodeids[:, 1]] - rn[nodeids[:, 0]], box, pbc)
    lengths = np.linalg.norm(d, axis=1)
    maxseg = float(config.physics["discretization"]["maxseg"])
    minseg = float(config.physics["discretization"]["minseg"])
    tiny = lengths < max(1e-8, 1e-3 * minseg)
    if np.any(tiny):
        report.add("zero_length_segments", FAIL, "%d zero-length segments" % int(tiny.sum()))
    else:
        report.add(
            "segment_lengths",
            PASS,
            "lengths in [%.2f, %.2f] b (minseg=%.1f, maxseg=%.1f)"
            % (lengths.min(), lengths.max(), minseg, maxseg),
        )
    if lengths.max() > 1.6 * maxseg:
        report.add(
            "max_segment_length",
            WARN,
            "longest segment %.1f b exceeds 1.6 maxseg (%.1f b)" % (lengths.max(), maxseg),
        )

    # duplicate nodes
    rann = float(config.physics["discretization"]["rann"])
    dup = 0
    if n_nodes < 4000:
        delta = _min_image(rn[:, None, :] - rn[None, :, :], box, pbc)
        dist = np.linalg.norm(delta, axis=-1)
        np.fill_diagonal(dist, np.inf)
        dup = int(np.sum(dist < 0.05 * rann) // 2)
    if dup:
        report.add("duplicate_nodes", FAIL, "%d coincident node pairs" % dup)
    else:
        report.add("duplicate_nodes", PASS, "no coincident nodes")

    # Burgers vectors
    bnorm = np.linalg.norm(burgers, axis=1)
    if np.any(bnorm < 1e-8):
        report.add("burgers_nonzero", FAIL, "segments with a zero Burgers vector")
    else:
        report.add("burgers_nonzero", PASS, "all Burgers vectors are non-zero")
    net_b = np.zeros((n_nodes, 3))
    np.add.at(net_b, nodeids[:, 0], burgers)
    np.add.at(net_b, nodeids[:, 1], -burgers)
    residual = np.linalg.norm(net_b, axis=1)
    free = constraints != 7
    worst = float(residual[free].max()) if np.any(free) else 0.0
    if worst > 1e-6:
        report.add(
            "burgers_conservation",
            FAIL,
            "Burgers vector is not conserved at %d nodes (max residual %.2e)"
            % (int(np.sum(residual[free] > 1e-6)), worst),
        )
    else:
        report.add("burgers_conservation", PASS, "Burgers vector conserved at every node")

    # glide planes
    pnorm = np.linalg.norm(planes, axis=1)
    if np.any(pnorm < 1e-8):
        report.add("glide_plane_defined", FAIL, "segments without a glide-plane normal")
    else:
        unit_planes = planes / pnorm[:, None]
        bn = np.abs(np.sum(burgers / bnorm[:, None] * unit_planes, axis=1))
        tn = np.abs(np.sum(d / np.maximum(lengths, 1e-30)[:, None] * unit_planes, axis=1))
        if bn.max() > 1e-5:
            report.add(
                "glide_plane_burgers",
                FAIL,
                "Burgers vector not in glide plane for some segments (max |b.n|=%.2e)" % bn.max(),
            )
        else:
            report.add("glide_plane_burgers", PASS, "b.n = 0 for all segments")
        if tn.max() > 1e-3:
            report.add(
                "glide_plane_tangent",
                WARN,
                "some segments are not contained in their glide plane (max |t.n|=%.2e)" % tn.max(),
            )
        else:
            report.add("glide_plane_tangent", PASS, "t.n = 0 for all segments")

    return report


# ---------------------------------------------------------------------------
# run-level validation
# ---------------------------------------------------------------------------
def validate_run(
    config: CaseConfig, case_dir: str, frames: Sequence[Dict[str, Any]], run_info: Dict[str, Any]
) -> ValidationReport:
    report = ValidationReport(case=config.name, stage="run")

    expected = config.num_steps // config.write_freq + 1
    annihilated = run_info.get("termination") == "network_annihilated"
    if len(frames) < expected:
        report.add(
            "frame_count",
            WARN if annihilated else FAIL,
            "expected %d trajectory frames, found %d (%s)"
            % (
                expected,
                len(frames),
                "run stopped early: the network fully annihilated"
                if annihilated
                else "incomplete simulation",
            ),
        )
    else:
        report.add("frame_count", PASS, "%d trajectory frames written" % len(frames))

    if run_info.get("returncode", 0) != 0:
        report.add("exit_status", FAIL, "simulation exited with code %s" % run_info.get("returncode"))
    else:
        report.add("exit_status", PASS, "simulation completed")

    if not frames:
        report.add("trajectory_nonempty", FAIL, "no trajectory frames")
        return report

    times = np.array([f["time"] for f in frames], dtype=float)
    if np.any(~np.isfinite(times)):
        report.add("time_finite", FAIL, "non-finite simulation times")
    elif np.any(np.diff(times) < 0):
        report.add("time_monotonic", FAIL, "simulation time is not monotonically increasing")
    else:
        report.add(
            "time_monotonic",
            PASS,
            "simulated %.3e s over %d steps" % (times[-1], config.num_steps),
            total_time_s=float(times[-1]),
        )

    n_nodes = np.array([f["positions"].shape[0] for f in frames], dtype=int)
    if n_nodes[-1] == 0:
        report.add(
            "final_network",
            WARN,
            "the dislocation network is empty at the end of the run (full annihilation)",
        )
    else:
        report.add(
            "final_network",
            PASS,
            "network has %d nodes at the end (%d initially)" % (n_nodes[-1], n_nodes[0]),
        )

    finite = all(np.all(np.isfinite(f["positions"])) for f in frames)
    report.add(
        "finite_trajectory",
        PASS if finite else FAIL,
        "all nodal positions are finite" if finite else "non-finite nodal positions in trajectory",
    )

    # the network must actually evolve
    if frames[0]["positions"].shape == frames[-1]["positions"].shape:
        motion = float(np.max(np.abs(frames[-1]["positions"] - frames[0]["positions"])))
    else:
        motion = np.inf
    if motion < 1e-6:
        report.add("network_evolution", FAIL, "the network did not move during the simulation")
    else:
        report.add(
            "network_evolution",
            PASS,
            "maximum nodal displacement %s"
            % ("topology changed" if not np.isfinite(motion) else "%.1f b" % motion),
        )
    return report
