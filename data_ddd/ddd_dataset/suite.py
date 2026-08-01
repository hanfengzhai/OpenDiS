"""Definition of the dataset case suite.

Builds deterministic CaseConfig objects for every case category:
  - single loop (reference stress -> shrink; scaled stress -> expansion)
  - double loops (random placement, two slip systems)
  - double coplanar loops (intentional loop-loop coalescence)
  - triple loops
  - six loops (box 64)
  - twelve loops (box 128)
  - line-loop interaction
  - field-of-view variations
  - applied-stress perturbations around the reference

Box sizes are full 3D cubic cells (the pydis Cell requires a 3x3 h matrix,
so "box 32" means a 32^3 cell in units of b).  The geometry is scaled with
the box so loops neither overlap nor start close to periodic images.
"""

from typing import List
import numpy as np

from .config import (CaseConfig, build_applied_stress, stress_label)
from .geometry import make_loop_spec, make_line_spec, place_loops_random
from .reference import REFERENCE_STRESS_VOIGT

# base Voigt loads (Pa): single-system and two-system variants of the
# reference load sigma_xz = -400 MPa (Voigt order [xx yy zz yz xz xy])
BASE_XZ = np.array(REFERENCE_STRESS_VOIGT)                      # sigma_xz
BASE_XZ_YZ = np.array([0.0, 0.0, 0.0, -4.0e8, -4.0e8, 0.0])     # sigma_yz + sigma_xz


def _name(cat: str, L: float, sigma, seed: int, fov: float = None) -> str:
    n = f"{cat}_box{int(L):03d}_{stress_label(sigma)}_seed{seed:02d}"
    if fov is not None and fov != L:
        n += f"_fov{int(fov):03d}"
    return n


def _case(cat, L, loops, lines, sigma, seed, max_step, fov=None,
          write_freq=10, intended_interaction=False, notes=""):
    fov = L if fov is None else fov
    return CaseConfig(
        name=_name(cat, L, sigma, seed, fov),
        case_type=cat,
        seed=seed,
        box_size=[float(L)] * 3,
        fov=[float(fov)] * 3,
        loops=loops,
        lines=lines,
        applied_stress_voigt=[float(s) for s in sigma],
        dt=1.0e-10,
        max_step=max_step,
        write_freq=write_freq,
        intended_interaction=intended_interaction,
        notes=notes,
    )


def build_suite() -> List[CaseConfig]:
    cases = []

    # ------------------------------------------------------------------
    # 1) single loop, reference stress (-400 MPa sigma_xz): sub-critical
    #    loop -> self-stress dominated shrinkage and annihilation
    L = 32.0
    sigma = build_applied_stress(BASE_XZ, scale=1.0)
    cases.append(_case(
        "loop01", L,
        loops=[make_loop_spec([0, 0, 0], 8.0, "bx_nz", L)],
        lines=[], sigma=sigma, seed=1, max_step=200, write_freq=5,
        notes="single glissile loop at the reference stress; "
              "sub-critical radius -> shrinks by self-stress"))

    # 2) single loop, scaled stress (-4 GPa sigma_xz): super-critical
    #    -> expands by glide, reacts with its own periodic images beyond
    #    r = L/2 and mutually annihilates (intentional; full loop lifecycle)
    sigma = build_applied_stress(BASE_XZ, scale=10.0)
    cases.append(_case(
        "loop01", L,
        loops=[make_loop_spec([0, 0, 0], 8.0, "bx_nz", L)],
        lines=[], sigma=sigma, seed=1, max_step=150,
        intended_interaction=True,
        notes="single glissile loop at 10x reference stress -> expands; "
              "periodic self-image reaction beyond r=L/2 is intentional"))

    # 3) applied-stress perturbations around the (scaled) reference stress:
    #    random deviatoric perturbation of 10% of the dominant component
    for seed in (11, 12):
        sigma = build_applied_stress(BASE_XZ, scale=10.0,
                                     perturb_frac=0.10, seed=seed)
        cases.append(_case(
            "loop01", L,
            loops=[make_loop_spec([0, 0, 0], 8.0, "bx_nz", L)],
            lines=[], sigma=sigma, seed=seed, max_step=75, write_freq=5,
            notes="single loop with 10% random deviatoric stress "
                  "perturbation around 10x reference stress"))

    # 4) field-of-view variations: larger box (48) and reduced FOV window
    L48 = 48.0
    sigma = build_applied_stress(BASE_XZ, scale=10.0)
    cases.append(_case(
        "loop01", L48,
        loops=[make_loop_spec([0, 0, 0], 8.0, "bx_nz", L48)],
        lines=[], sigma=sigma, seed=1, max_step=150,
        notes="single loop in a larger box (different field of view)"))
    cases.append(_case(
        "loop01", L,
        loops=[make_loop_spec([0, 0, 0], 6.0, "bx_nz", L)],
        lines=[], sigma=sigma, seed=2, max_step=90, write_freq=5, fov=24.0,
        notes="single loop with reduced field-of-view window (24^3) "
              "inside a 32^3 box"))

    # ------------------------------------------------------------------
    # 5) double loops, random placement on two slip systems
    sigma = build_applied_stress(BASE_XZ_YZ, scale=10.0)
    loops = place_loops_random(2, L, radius=6.0, systems=["bx_nz", "by_nz"],
                               seed=21, min_gap=2.0, boundary_margin=1.5)
    cases.append(_case(
        "loop02", L, loops=loops, lines=[], sigma=sigma, seed=21,
        max_step=100, write_freq=5,
        notes="two loops on two slip systems; expansion under "
              "sigma_xz + sigma_yz"))

    # 6) double coplanar loops (intentional coalescence interaction)
    sigma = build_applied_stress(BASE_XZ, scale=10.0)
    loops = [make_loop_spec([-7.5, 0, 0], 6.0, "bx_nz", L),
             make_loop_spec([7.5, 0, 0], 6.0, "bx_nz", L)]
    cases.append(_case(
        "loop02c", L, loops=loops, lines=[], sigma=sigma, seed=22,
        max_step=150, intended_interaction=True,
        notes="two coplanar loops with the same Burgers vector; expansion "
              "drives collision and coalescence into a single loop"))

    # 7) triple loops
    sigma = build_applied_stress(BASE_XZ_YZ, scale=10.0)
    loops = place_loops_random(3, L, radius=5.0,
                               systems=["bx_nz", "by_nz", "bx_nz"],
                               seed=31, min_gap=1.5, boundary_margin=1.0)
    cases.append(_case(
        "loop03", L, loops=loops, lines=[], sigma=sigma, seed=31,
        max_step=100, write_freq=5,
        notes="three loops on mixed slip systems"))

    # ------------------------------------------------------------------
    # 8) six loops, box 64
    L64 = 64.0
    sigma = build_applied_stress(BASE_XZ_YZ, scale=10.0)
    loops = place_loops_random(6, L64, radius=10.0,
                               systems=["bx_nz", "by_nz"],
                               seed=41, min_gap=2.0, boundary_margin=1.5)
    cases.append(_case(
        "loop06", L64, loops=loops, lines=[], sigma=sigma, seed=41,
        max_step=200, notes="six loops in a 64^3 box"))

    # 9) twelve loops, box 128
    L128 = 128.0
    sigma = build_applied_stress(BASE_XZ_YZ, scale=10.0)
    loops = place_loops_random(12, L128, radius=16.0,
                               systems=["bx_nz", "by_nz"],
                               seed=51, min_gap=3.0, boundary_margin=2.0)
    cases.append(_case(
        "loop12", L128, loops=loops, lines=[], sigma=sigma, seed=51,
        max_step=300, notes="twelve loops in a 128^3 box"))

    # ------------------------------------------------------------------
    # 10) line-loop interaction: straight periodic line and a coplanar loop
    #     on the same glide plane / Burgers vector
    sigma = build_applied_stress(BASE_XZ, scale=10.0)
    line = make_line_spec(point=[-9.0, 0.0, 0.0], direction=[0, 1, 0],
                          burgers=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0],
                          box_size=L)
    loop = make_loop_spec([4.0, 0.0, 0.0], 6.0, "bx_nz", L)
    cases.append(_case(
        "lineloop", L, loops=[loop], lines=[line], sigma=sigma, seed=61,
        max_step=150, intended_interaction=True,
        notes="periodic straight line (b=[100], n=[001]) and coplanar "
              "expanding loop -> line-loop reaction"))

    # ensure unique names
    names = [c.name for c in cases]
    assert len(names) == len(set(names)), f"duplicate case names: {names}"
    return cases


# Representative subset covering every major geometry category (used by
# run_suite --representative)
REPRESENTATIVE_TYPES = ["loop01", "loop02", "loop02c", "loop03", "loop06",
                        "loop12", "lineloop"]
