"""Validation checks for DDD networks and completed simulations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from paths_setup import ensure_imports

ensure_imports()
from pyexadis_base import ExaDisNet, DisNetManager  # noqa: E402


def _network_arrays(N: DisNetManager) -> dict[str, Any]:
    G = N.get_disnet(ExaDisNet)
    data = G.export_data()
    cell = data["cell"]
    h = np.asarray(cell["h"], dtype=float)
    box = np.array([h[0, 0], h[1, 1], h[2, 2]])
    nodes = data["nodes"]
    segs = data["segs"]
    return {
        "h": h,
        "box": box,
        "origin": np.asarray(cell.get("origin", [0, 0, 0]), dtype=float),
        "pbc": cell.get("is_periodic", [1, 1, 1]),
        "positions": np.asarray(nodes["positions"], dtype=float),
        "tags": np.asarray(nodes["tags"], dtype=int),
        "constraints": np.asarray(nodes["constraints"], dtype=int),
        "nodeids": np.asarray(segs["nodeids"], dtype=int),
        "burgers": np.asarray(segs["burgers"], dtype=float),
        "planes": np.asarray(segs["planes"], dtype=float),
    }


def validate_network(
    N: DisNetManager,
    *,
    zero_seg_tol: float = 1e-8,
    bn_tol: float = 1e-4,
    require_elasticity_settings: dict[str, Any] | None = None,
    check_outside_box: bool = True,
    require_planar_001: bool = False,
    planarity_z_tol: float = 1e-6,
) -> dict[str, Any]:
    """Return a validation report with ok flag and list of issues."""
    issues: list[str] = []
    warnings: list[str] = []
    a = _network_arrays(N)

    n_nodes = a["positions"].shape[0]
    n_segs = a["nodeids"].shape[0]
    if n_nodes < 2:
        issues.append(f"Too few nodes: {n_nodes}")
    if n_segs < 1:
        issues.append(f"Too few segments: {n_segs}")

    # Connectivity
    if n_segs > 0:
        bad_ids = (a["nodeids"] < 0) | (a["nodeids"] >= n_nodes)
        if np.any(bad_ids):
            issues.append(f"Invalid node indices in {int(bad_ids.any(axis=1).sum())} segments")

        # Duplicate directed links
        links = [tuple(x) for x in a["nodeids"]]
        if len(links) != len(set(links)):
            issues.append("Duplicate directed segment links detected")

        # Zero-length / near-zero segments (with PBC image)
        from paths_setup import ensure_imports

        ensure_imports()
        import pyexadis

        cell = pyexadis.Cell(h=a["h"], origin=a["origin"], is_periodic=a["pbc"])
        lengths = []
        for i0, i1 in a["nodeids"]:
            r1 = a["positions"][i0]
            r2 = np.asarray(cell.closest_image(Rref=r1, R=a["positions"][i1]))
            L = float(np.linalg.norm(r2 - r1))
            lengths.append(L)
            if L < zero_seg_tol:
                issues.append(f"Near-zero segment length {L:g} between nodes {i0}-{i1}")
        lengths = np.asarray(lengths)

        # Burgers consistency / zero burgers
        bnorm = np.linalg.norm(a["burgers"], axis=1)
        if np.any(bnorm < zero_seg_tol):
            issues.append(f"Zero Burgers vector on {(bnorm < zero_seg_tol).sum()} segments")

        # Glide plane validity: n non-zero and roughly orthogonal to b
        pnorm = np.linalg.norm(a["planes"], axis=1)
        if np.any(pnorm < zero_seg_tol):
            warnings.append(f"Missing/zero plane normal on {(pnorm < zero_seg_tol).sum()} segments")
        else:
            bn = np.abs(np.sum(a["burgers"] * a["planes"], axis=1)) / (bnorm * pnorm + 1e-30)
            # Prismatic loops have mixed characters; only flag strongly non-orthogonal if claimed glissile circular
            bad_bn = bn > max(bn_tol, 0.15)
            if np.any(bad_bn):
                warnings.append(
                    f"{int(bad_bn.sum())} segments have |b·n|/(|b||n|) > {max(bn_tol, 0.15):g}"
                )

    # Duplicate nodes (exact)
    if n_nodes > 0:
        rounded = np.round(a["positions"], decimals=10)
        uniq = np.unique(rounded, axis=0)
        if uniq.shape[0] != n_nodes:
            warnings.append(f"Possible duplicate node positions: {n_nodes - uniq.shape[0]} extras")

    # Outside box (folded coords should lie in [origin, origin+box])
    if check_outside_box and n_nodes > 0:
        lo = a["origin"]
        hi = a["origin"] + a["box"]
        # Allow tiny numerical tolerance
        eps = 1e-8 * np.max(a["box"])
        outside = np.any((a["positions"] < lo - eps) | (a["positions"] > hi + eps), axis=1)
        if np.any(outside):
            warnings.append(
                f"{int(outside.sum())} nodes outside [origin, origin+box] before folding "
                "(may be ok if solver folds on read)"
            )

    # Periodic-image proximity: nodes very close to their own periodic image via short box edge
    # (flag if min coordinate extent of all nodes is almost full box while diameter large — skip)
    # Instead: flag if any node is within eps of a boundary AND we have only one loop near corner.
    # Keep as soft warning if nodes within 1% of boundary.
    if n_nodes > 0:
        frac = (a["positions"] - a["origin"]) / a["box"]
        near_boundary = np.any((frac < 0.02) | (frac > 0.98), axis=1)
        if near_boundary.mean() > 0.5:
            warnings.append("More than half of nodes lie within 2% of a periodic boundary")

    if require_elasticity_settings is not None:
        force_mode = require_elasticity_settings.get("force_mode")
        if force_mode not in ("DDD_FFT_MODEL", "SUBCYCLING_MODEL"):
            issues.append(f"Missing/invalid elasticity force_mode={force_mode}")
        if require_elasticity_settings.get("ngrid", 0) <= 0:
            issues.append("FFT Ngrid must be positive")
        pbc = require_elasticity_settings.get("pbc", [])
        if list(pbc) != [1, 1, 1] and list(pbc) != [True, True, True]:
            issues.append(f"ForceFFT requires full 3D PBC, got pbc={pbc}")

    # 2D (001) planarity: all nodes near a common z, planes ~ [001], b · n ~ 0
    planarity = None
    if require_planar_001 and n_nodes > 0:
        z = a["positions"][:, 2]
        zspan = float(z.max() - z.min())
        zmean = float(z.mean())
        planarity = {"z_mean": zmean, "z_span": zspan, "tol": float(planarity_z_tol)}
        if zspan > max(planarity_z_tol, 1e-8 * float(np.max(a["box"]))):
            issues.append(f"Network not planar on 001: z_span={zspan:g} > tol={planarity_z_tol:g}")
        if n_segs > 0:
            p = a["planes"]
            pnorm = np.linalg.norm(p, axis=1) + 1e-30
            p_hat = p / pnorm[:, None]
            # alignment with ±001
            align = np.abs(p_hat[:, 2])
            bad_plane = align < 0.99
            if np.any(bad_plane):
                issues.append(
                    f"{int(bad_plane.sum())} segments do not have plane normal ≈ [001]"
                )
            b = a["burgers"]
            bn = np.abs(np.sum(b * p_hat, axis=1)) / (np.linalg.norm(b, axis=1) + 1e-30)
            if np.any(bn > max(bn_tol, 1e-3)):
                issues.append(
                    f"{int((bn > max(bn_tol, 1e-3)).sum())} segments violate b·n≈0 on 001"
                )
            # burgers should be in-plane (bz ≈ 0)
            bz = np.abs(b[:, 2]) / (np.linalg.norm(b, axis=1) + 1e-30)
            if np.any(bz > 1e-3):
                issues.append(f"{int((bz > 1e-3).sum())} segments have out-of-plane Burgers")
            # Dataset policy: all glissile content shares one Burgers vector b=[100]
            b_unit = b / (np.linalg.norm(b, axis=1)[:, None] + 1e-30)
            ref = np.array([1.0, 0.0, 0.0])
            align = np.abs(np.sum(b_unit * ref[None, :], axis=1))
            if np.any(align < 0.999):
                issues.append(
                    f"{int((align < 0.999).sum())} segments do not share common Burgers b=[100]"
                )

    report = {
        "ok": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "n_nodes": int(n_nodes),
        "n_segments": int(n_segs),
        "box": a["box"].tolist(),
        "segment_length_min": float(np.min(lengths)) if n_segs else None,
        "segment_length_max": float(np.max(lengths)) if n_segs else None,
        "segment_length_mean": float(np.mean(lengths)) if n_segs else None,
        "planarity_001": planarity,
    }
    return report


def validate_simulation_outputs(
    case_dir: Path,
    max_step: int,
    write_freq: int,
    allow_early_stop: bool = False,
) -> dict[str, Any]:
    issues = []
    warnings = []
    raw_dir = case_dir / "raw_trajectory"
    if not raw_dir.is_dir():
        issues.append("Missing raw_trajectory directory")
        return {"ok": False, "issues": issues, "warnings": warnings}

    configs = sorted(raw_dir.glob("config.*.data"))
    if not configs:
        issues.append("No config.*.data trajectory files")
    else:
        found = set()
        for p in configs:
            try:
                found.add(int(p.name.split(".")[1]))
            except Exception:
                warnings.append(f"Unexpected filename {p.name}")
        if 0 not in found:
            issues.append("Missing initial trajectory frame config.0.data")
        expected = {0}
        expected.update(range(write_freq, max_step + 1, write_freq))
        missing = sorted(expected - found)
        if missing and not allow_early_stop:
            issues.append(f"Missing trajectory frames: {missing[:10]}{'...' if len(missing)>10 else ''}")
        elif missing and allow_early_stop:
            warnings.append(
                f"Early stop before max_step; missing later frames: "
                f"{missing[:10]}{'...' if len(missing)>10 else ''}"
            )

    log = case_dir / "logs" / "simulate.log"
    if not log.is_file():
        warnings.append("Missing simulate.log")
    else:
        text = log.read_text(encoding="utf-8", errors="replace")
        if "RUN TIME:" not in text and "Error" in text:
            issues.append("Simulation log indicates failure")
        if "Error:" in text or "FATAL" in text:
            issues.append("Fatal error detected in simulation log")

    dens = raw_dir / "stress_strain_dens.dat"
    if not dens.is_file():
        warnings.append("Missing stress_strain_dens.dat")

    return {"ok": len(issues) == 0, "issues": issues, "warnings": warnings, "n_frames": len(configs)}


def write_validation(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
