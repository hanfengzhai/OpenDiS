"""Catalog of dataset cases.

Defines the reference applied stress, the controlled stress perturbations around
it, and the list of cases that make up the dataset: single / double / triple /
six / twelve loops, line-loop and multi-loop interactions, several fields of
view and several applied-stress values.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Sequence

import numpy as np

from data_ddd.config import CaseConfig, LineSpec, LoopSpec, StressSpec
from data_ddd.geometry import place_line_loop_case, place_loops
from data_ddd.reference import REFERENCE, load_reference

# Reference loading: uniaxial tension along [0 2 5].  The axis is chosen to
# maximize the smallest Schmid factor over the 12 FCC 1/2<110>{111} systems
# (min |m| = 0.085, max |m| = 0.493), so that a loop on any slip system is
# driven by the reference stress.  Classical axes such as [1 2 3] leave three
# systems with zero resolved shear.
REFERENCE_STRESS_MODE = "uniaxial"
REFERENCE_STRESS_AXIS = [0.0, 2.0, 5.0]
REFERENCE_STRESS_MAGNITUDE = 400.0e6  # Pa


def reference_stress() -> StressSpec:
    return StressSpec(
        mode=REFERENCE_STRESS_MODE,
        magnitude=REFERENCE_STRESS_MAGNITUDE,
        axis=list(REFERENCE_STRESS_AXIS),
    )


def perturb_stress(
    base: StressSpec | None = None,
    magnitude_scale: float = 1.0,
    axis_jitter_deg: float = 0.0,
    seed: int = 0,
) -> StressSpec:
    """Controlled perturbation of the reference stress.

    The perturbation keeps the tensor structure of the reference loading: the
    magnitude is scaled and the loading axis is rotated by a small angle, so the
    result is still a uniaxial tension of well-defined magnitude (Pa).
    """
    base = base or reference_stress()
    if base.mode != "uniaxial":
        raise ValueError("stress perturbations are defined for uniaxial loading")

    axis = np.asarray(base.axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    if axis_jitter_deg:
        rng = np.random.default_rng(seed)
        # rotate the axis by `axis_jitter_deg` around a random perpendicular axis
        perp = rng.standard_normal(3)
        perp = perp - np.dot(perp, axis) * axis
        perp = perp / np.linalg.norm(perp)
        angle = np.deg2rad(axis_jitter_deg)
        axis = np.cos(angle) * axis + np.sin(angle) * perp
        axis = axis / np.linalg.norm(axis)

    return StressSpec(
        mode="uniaxial",
        magnitude=base.magnitude * magnitude_scale,
        axis=list(axis),
        perturbation={
            "base_magnitude_Pa": float(base.magnitude),
            "base_axis": [float(v) for v in np.asarray(base.axis, dtype=float)],
            "magnitude_scale": float(magnitude_scale),
            "axis_jitter_deg": float(axis_jitter_deg),
            "seed": int(seed),
        },
    )


TYPE_CODES = {
    "single_loop": "loop01",
    "double_loop": "loop02",
    "triple_loop": "loop03",
    "six_loops": "loop06",
    "twelve_loops": "loop12",
    "line_loop": "line01loop01",
    "line_multiloop": "line01loop03",
}

INTERACTION_CODES = {
    "isolated": "iso",
    "coplanar": "copl",
    "dipole": "dip",
    "junction": "junc",
    "line_loop": "lnlp",
    "mixed": "mix",
}


def case_name(
    case_type: str, interaction: str, box: Sequence[float], fov: Sequence[float],
    stress: StressSpec, seed: int
) -> str:
    """Deterministic, compact case name encoding the important variables."""
    code = TYPE_CODES.get(case_type, case_type)
    icode = INTERACTION_CODES.get(interaction, interaction)
    return "%s_%s_b%03d_f%03d_s%04d_r%03d" % (
        code,
        icode,
        int(round(np.max(box))),
        int(round(np.max(fov))),
        int(round(stress.magnitude / 1.0e6)),
        seed,
    )


def default_radius(box: Sequence[float], n_loops: int) -> float:
    """Loop radius (nominal units) scaled consistently with the box size."""
    L = float(np.min(box))
    if n_loops <= 3:
        r = L / 8.0
    elif n_loops <= 6:
        r = L / 12.0
    else:
        r = L / 16.0
    return round(r * 2.0) / 2.0


def make_case(
    case_type: str,
    box: float | Sequence[float] = 32.0,
    fov: float | Sequence[float] | None = None,
    n_loops: int | None = None,
    interaction: str = "mixed",
    stress: StressSpec | None = None,
    seed: int = 1,
    radius: float | None = None,
    num_steps: int | None = None,
    write_freq: int | None = None,
    description: str = "",
    physics: Dict[str, Any] | None = None,
    line_system: int = 0,  # rank of the line's slip system by Schmid factor
    line_theta: float = 0.0,
) -> CaseConfig:
    """Build a fully specified case configuration."""
    physics = copy.deepcopy(physics or REFERENCE)
    box = np.full(3, float(box)) if np.isscalar(box) else np.asarray(box, dtype=float)
    if fov is None:
        fov = box.copy()
    fov = np.full(3, float(fov)) if np.isscalar(fov) else np.asarray(fov, dtype=float)
    stress = stress or reference_stress()

    defaults = {
        "single_loop": 1,
        "double_loop": 2,
        "triple_loop": 3,
        "six_loops": 6,
        "twelve_loops": 12,
        "line_loop": 1,
        "line_multiloop": 3,
    }
    if n_loops is None:
        n_loops = defaults.get(case_type, 1)
    if radius is None:
        radius = default_radius(box, max(n_loops, 1))

    loops: List[LoopSpec] = []
    lines: List[LineSpec] = []

    if case_type in ("line_loop", "line_multiloop"):
        line, loops = place_line_loop_case(
            n_loops, box, radius, stress, seed, line_rank=line_system, theta=line_theta
        )
        lines.append(line)
    else:
        loops = place_loops(n_loops, box, radius, stress, seed, interaction=interaction)

    out = REFERENCE["output"] if physics is None else physics["output"]
    config = CaseConfig(
        name=case_name(case_type, interaction, box, fov, stress, seed),
        case_type=case_type,
        interaction=interaction,
        description=description,
        loops=loops,
        lines=lines,
        box_size=list(box),
        fov=list(fov),
        pbc=list(physics["boundary_conditions"]["pbc"]),
        stress=stress,
        seed=seed,
        num_steps=int(num_steps or out["num_steps"]),
        write_freq=int(write_freq or out["write_freq"]),
        print_freq=int(out["print_freq"]),
        physics=physics,
    )
    return config


def default_catalog(reference_json: str | None = None) -> List[CaseConfig]:
    """The dataset: one entry per (geometry, box, field of view, stress) case."""
    physics = load_reference(reference_json)
    ref = reference_stress()
    cases: List[CaseConfig] = []

    # --- loop-number series, box size scaled with the number of loops -------
    cases.append(
        make_case("single_loop", box=32, interaction="isolated", seed=1, physics=physics,
                  description="Single glissile loop expanding under the reference stress")
    )
    # interaction cases are run longer so that the loops have time to meet
    interaction_run = {"num_steps": 150, "write_freq": 3}
    cases.append(
        make_case("double_loop", box=32, interaction="coplanar", seed=2, physics=physics,
                  **interaction_run,
                  description="Two coplanar same-sign loops: like-sign repulsion "
                              "flattens their facing sides as they expand")
    )
    cases.append(
        make_case("double_loop", box=32, interaction="junction", seed=3, physics=physics,
                  **interaction_run,
                  description="Two loops on intersecting {111} planes that zip a "
                              "<100> junction along the plane-intersection line")
    )
    cases.append(
        make_case("double_loop", box=32, interaction="dipole", seed=4, physics=physics,
                  **interaction_run,
                  description="Coplanar loop dipole (opposite Burgers vectors): the loops "
                              "meet and merge/annihilate")
    )
    cases.append(
        make_case("triple_loop", box=32, interaction="mixed", seed=5, physics=physics,
                  description="Three loops on three different slip systems")
    )
    cases.append(
        make_case("six_loops", box=64, interaction="mixed", seed=6, physics=physics,
                  description="Six loops in a 64-unit box, multi-slip interactions")
    )
    cases.append(
        make_case("twelve_loops", box=128, interaction="mixed", seed=7, physics=physics,
                  description="Twelve loops covering all 12 FCC slip systems in a 128-unit box")
    )

    # --- line-loop interactions --------------------------------------------
    cases.append(
        make_case("line_loop", box=32, interaction="line_loop", seed=8, physics=physics,
                  line_system=0, line_theta=30.0, **interaction_run,
                  description="Infinite periodic line intersected by an expanding loop")
    )
    cases.append(
        make_case("line_multiloop", box=64, interaction="line_loop", seed=9, physics=physics,
                  line_system=0, line_theta=0.0, **interaction_run,
                  description="Screw line interacting with three loops on other slip systems")
    )

    # --- field-of-view variants --------------------------------------------
    cases.append(
        make_case("triple_loop", box=32, fov=16, interaction="mixed", seed=5, physics=physics,
                  description="Three loops, half-box field of view")
    )
    cases.append(
        make_case("six_loops", box=64, fov=32, interaction="mixed", seed=6, physics=physics,
                  description="Six loops, half-box field of view")
    )
    cases.append(
        make_case("six_loops", box=64, fov=48, interaction="mixed", seed=6, physics=physics,
                  description="Six loops, three-quarter-box field of view")
    )

    # --- applied-stress series ----------------------------------------------
    for scale in (0.5, 1.5, 2.0):
        cases.append(
            make_case(
                "single_loop", box=32, interaction="isolated", seed=1, physics=physics,
                stress=perturb_stress(ref, magnitude_scale=scale),
                description="Single loop at %.0f%% of the reference stress" % (100 * scale),
            )
        )
    for seed, jitter in ((11, 5.0), (12, 10.0)):
        cases.append(
            make_case(
                "triple_loop", box=32, interaction="mixed", seed=seed, physics=physics,
                stress=perturb_stress(ref, magnitude_scale=1.0, axis_jitter_deg=jitter, seed=seed),
                description="Three loops, loading axis rotated by %.0f deg" % jitter,
            )
        )
    cases.append(
        make_case(
            "six_loops", box=64, interaction="mixed", seed=13, physics=physics,
            stress=perturb_stress(ref, magnitude_scale=1.25, axis_jitter_deg=7.0, seed=13),
            description="Six loops, perturbed stress magnitude and axis",
        )
    )

    # guard against duplicate names
    seen = set()
    unique = []
    for case in cases:
        name = case.name
        suffix = 1
        while case.name in seen:
            suffix += 1
            case.name = "%s_v%d" % (name, suffix)
        seen.add(case.name)
        unique.append(case)
    return unique
