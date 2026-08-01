"""Validation checks for generated networks, configurations and finished runs.

Every check returns a dict {passed: bool, detail: str}; validate_case()
aggregates them into a JSON-serializable report.  A case must pass all
pre-run checks before its simulation is started.
"""

from typing import Dict
import numpy as np

from . import paths  # noqa: F401
from .config import CaseConfig
from .reference import REFERENCE, numerical_params

from pydis import DisNet
from framework.disnet_manager import DisNetManager

TOL_ZERO_SEG = 1.0e-6
TOL_PLANE = 1.0e-6


def _segments_with_positions(G: DisNet):
    return G.get_segs_data_with_positions()


def check_sanity(G: DisNet) -> Dict:
    """Node/segment connectivity + Burgers conservation (pydis is_sane)."""
    ok = bool(G.is_sane())
    return {"passed": ok,
            "detail": "is_sane: connectivity and Burgers conservation" if ok
            else "is_sane failed (invalid connectivity or Burgers sums)"}


def check_min_degree(G: DisNet) -> Dict:
    bad = [tag for tag in G.all_nodes_tags() if G.out_degree(tag) < 2]
    return {"passed": len(bad) == 0,
            "detail": f"{len(bad)} nodes with <2 arms" if bad else
            "all nodes have >=2 arms"}


def check_duplicate_nodes(G: DisNet, tol: float = 1.0e-8) -> Dict:
    pos = G.pos_array()
    key = np.round(pos / max(tol, 1e-12)).astype(np.int64)
    _, counts = np.unique(key, axis=0, return_counts=True)
    ndup = int(np.sum(counts > 1))
    return {"passed": ndup == 0,
            "detail": f"{ndup} sets of coincident nodes" if ndup else
            "no duplicate node positions"}


def check_duplicate_links(G: DisNet) -> Dict:
    seen = set()
    dups = 0
    for (s, t) in G.all_segments_tags():
        key = tuple(sorted((s, t)))
        if key in seen:
            dups += 1
        seen.add(key)
    return {"passed": dups == 0,
            "detail": f"{dups} duplicate links" if dups else "no duplicate links"}


def check_zero_length_segments(G: DisNet, tol: float = TOL_ZERO_SEG) -> Dict:
    segs = _segments_with_positions(G)
    lens = np.linalg.norm(segs["R2"] - segs["R1"], axis=1)
    nz = int(np.sum(lens < tol))
    return {"passed": nz == 0,
            "detail": f"{nz} (nearly) zero-length segments" if nz else
            f"min segment length {lens.min():.4g}"}


def check_segment_lengths(G: DisNet, box_size: float) -> Dict:
    p = numerical_params(box_size)
    segs = _segments_with_positions(G)
    lens = np.linalg.norm(segs["R2"] - segs["R1"], axis=1)
    too_long = int(np.sum(lens > p["maxseg"] * 1.5))
    return {"passed": too_long == 0,
            "detail": (f"{too_long} segments > 1.5*maxseg" if too_long else
                       f"segment lengths in [{lens.min():.3g}, {lens.max():.3g}], "
                       f"maxseg={p['maxseg']:.3g}")}


def check_burgers_consistency(G: DisNet) -> Dict:
    """Nonzero Burgers on all segments; conservation is covered by is_sane."""
    segs = _segments_with_positions(G)
    bmag = np.linalg.norm(segs["burgers"], axis=1)
    nz = int(np.sum(bmag < 1e-10))
    return {"passed": nz == 0,
            "detail": f"{nz} segments with zero Burgers vector" if nz else
            "all segments carry a nonzero Burgers vector"}


def check_glide_planes(G: DisNet) -> Dict:
    """Unit plane normals, b in plane, and segment line in plane."""
    segs = _segments_with_positions(G)
    n = segs["planes"]
    norms = np.linalg.norm(n, axis=1)
    bad_norm = int(np.sum(np.abs(norms - 1.0) > 1e-6))
    nn = n / np.maximum(norms[:, None], 1e-300)
    b_dot_n = np.abs(np.einsum("ij,ij->i", segs["burgers"], nn))
    bad_bn = int(np.sum(b_dot_n > 1e-6))
    t = segs["R2"] - segs["R1"]
    t_dot_n = np.abs(np.einsum("ij,ij->i", t, nn))
    bad_tn = int(np.sum(t_dot_n > 1e-6))
    ok = bad_norm == 0 and bad_bn == 0 and bad_tn == 0
    return {"passed": ok,
            "detail": (f"non-unit normals: {bad_norm}, b.n != 0: {bad_bn}, "
                       f"line out of plane: {bad_tn}")}


def check_inside_box(G: DisNet, config: CaseConfig, margin: float = 0.0) -> Dict:
    """All initial nodes inside the primary cell (with optional margin)."""
    L = np.asarray(config.box_size, dtype=float)
    origin = G.cell.origin
    pos = G.pos_array()
    lo = origin + margin
    hi = origin + L - margin
    outside = int(np.sum(np.any((pos < lo) | (pos > hi), axis=1)))
    return {"passed": outside == 0,
            "detail": f"{outside} nodes outside the box" if outside else
            "all nodes inside the simulation box"}


def _min_image_dist(p, q, L):
    d = p[:, None, :] - q[None, :, :]
    d -= L * np.round(d / L)
    return np.sqrt(np.sum(d * d, axis=2))


def check_loop_separation(G: DisNet, config: CaseConfig,
                          min_gap: float = 1.0) -> Dict:
    """No unintended intersections/excessive proximity between distinct
    loops/lines at t=0 (minimum-image distances)."""
    if config.intended_interaction:
        return {"passed": True,
                "detail": "interaction intended for this case; check skipped"}
    L = np.asarray(config.box_size, dtype=float)
    # group nodes by originating primitive (loops then lines, in order)
    groups = []
    ofs = 0
    for spec in config.loops:
        groups.append((ofs, ofs + spec.n_nodes))
        ofs += spec.n_nodes
    for spec in config.lines:
        groups.append((ofs, ofs + spec.n_nodes))
        ofs += spec.n_nodes
    pos = G.pos_array()
    min_d = np.inf
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            a0, a1 = groups[i]
            b0, b1 = groups[j]
            d = _min_image_dist(pos[a0:a1], pos[b0:b1], L)
            min_d = min(min_d, float(d.min()))
    if len(groups) < 2:
        return {"passed": True, "detail": "single primitive; no pairs to check"}
    return {"passed": min_d >= min_gap,
            "detail": f"min inter-primitive distance {min_d:.3g} "
                      f"(threshold {min_gap})"}


def check_image_proximity(G: DisNet, config: CaseConfig,
                          min_gap: float = 1.0) -> Dict:
    """Excessive proximity of each primitive to its own periodic image."""
    if config.allow_boundary_proximity or config.intended_interaction:
        return {"passed": True, "detail": "boundary proximity allowed; skipped"}
    L = np.asarray(config.box_size, dtype=float)
    pos = G.pos_array()
    groups = []
    ofs = 0
    for spec in config.loops + config.lines:
        groups.append((ofs, ofs + spec.n_nodes))
        ofs += spec.n_nodes
    worst = np.inf
    for (a0, a1) in groups:
        p = pos[a0:a1]
        ext = p.max(axis=0) - p.min(axis=0)          # extent of the primitive
        gap = L - ext                                # distance to own image
        # ignore axes the primitive legitimately spans (periodic lines)
        span = ext > 0.95 * L
        if np.all(span):
            continue
        worst = min(worst, float(gap[~span].min()))
    if not np.isfinite(worst):
        return {"passed": True, "detail": "all primitives span the box"}
    return {"passed": worst >= min_gap,
            "detail": f"min distance to own periodic image {worst:.3g} "
                      f"(threshold {min_gap})"}


def check_force_model(config: CaseConfig) -> Dict:
    """Elasticity and force-model settings present and correct."""
    ok = (REFERENCE["force_mode"] == "Elasticity_SBA"
          and REFERENCE["mobility_law"] == "SimpleGlide"
          and all(k in REFERENCE for k in ("mu", "nu", "a", "burgmag")))
    sig = np.asarray(config.applied_stress_voigt, dtype=float)
    ok = ok and sig.shape == (6,) and np.all(np.isfinite(sig))
    return {"passed": bool(ok),
            "detail": ("elasticity force model, mobility and material "
                       "parameters present; stress tensor valid") if ok else
            "missing/invalid elasticity or force-model settings"}


PRE_RUN_CHECKS = [
    ("sanity", lambda DM, cfg: check_sanity(DM.get_disnet(DisNet))),
    ("min_degree", lambda DM, cfg: check_min_degree(DM.get_disnet(DisNet))),
    ("duplicate_nodes", lambda DM, cfg: check_duplicate_nodes(DM.get_disnet(DisNet))),
    ("duplicate_links", lambda DM, cfg: check_duplicate_links(DM.get_disnet(DisNet))),
    ("zero_length_segments", lambda DM, cfg: check_zero_length_segments(DM.get_disnet(DisNet))),
    ("segment_lengths", lambda DM, cfg: check_segment_lengths(
        DM.get_disnet(DisNet), float(cfg.box_size[0]))),
    ("burgers_consistency", lambda DM, cfg: check_burgers_consistency(DM.get_disnet(DisNet))),
    ("glide_planes", lambda DM, cfg: check_glide_planes(DM.get_disnet(DisNet))),
    ("inside_box", lambda DM, cfg: check_inside_box(DM.get_disnet(DisNet), cfg)),
    ("loop_separation", lambda DM, cfg: check_loop_separation(DM.get_disnet(DisNet), cfg)),
    ("image_proximity", lambda DM, cfg: check_image_proximity(DM.get_disnet(DisNet), cfg)),
    ("force_model", lambda DM, cfg: check_force_model(cfg)),
]


def validate_case(DM: DisNetManager, config: CaseConfig) -> Dict:
    """Run all pre-run checks; returns a report dict."""
    report = {"checks": {}, "passed": True}
    for name, fn in PRE_RUN_CHECKS:
        try:
            res = fn(DM, config)
        except Exception as e:  # a crashing check is a failing check
            res = {"passed": False, "detail": f"check raised: {e!r}"}
        report["checks"][name] = res
        report["passed"] = report["passed"] and res["passed"]
    return report


def validate_post_run(DM: DisNetManager, n_frames_written: int,
                      n_frames_expected: int, completed: bool,
                      termination_reason: str) -> Dict:
    """Post-run validation: completeness and final-state health."""
    G = DM.get_disnet(DisNet)
    pos = G.pos_array() if G.num_nodes() > 0 else np.zeros((0, 3))
    nan_free = bool(np.all(np.isfinite(pos)))
    sane = bool(G.is_sane()) if G.num_nodes() > 0 else True
    frames_ok = n_frames_written >= min(2, n_frames_expected)
    passed = bool(completed and nan_free and sane and frames_ok)
    return {
        "passed": passed,
        "completed": bool(completed),
        "termination_reason": termination_reason,
        "final_state_sane": sane,
        "final_state_nan_free": nan_free,
        "frames_written": int(n_frames_written),
        "frames_expected": int(n_frames_expected),
        "final_num_nodes": int(G.num_nodes()),
        "final_num_segments": int(G.num_segments()),
    }
