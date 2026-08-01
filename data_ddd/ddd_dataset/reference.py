"""Reference physical and numerical configuration for the dataset.

This module pins every DDD solver setting that must remain FIXED across all
dataset cases.  The values reproduce the repository's SimpleGlide reference
simulation (examples/02_frank_read_src/test_frank_read_src_pydis.py, the
in-repo counterpart of the SimpleGlide_001 reference case) with full
elastic segment-segment interactions enabled (force_mode='Elasticity_SBA',
the non-singular ParaDiS SegSegForce kernel compiled in libpydis.so).

Only the quantities listed in VARIABLE_QUANTITIES may differ between cases.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Fixed physics / solver settings (do NOT change per case)
# ---------------------------------------------------------------------------
REFERENCE = {
    # --- material parameters (SI units; lengths are in units of burgmag) ---
    "burgmag": 3.0e-10,        # Burgers vector magnitude [m]; unit of length
    "mu": 50.0e9,              # shear modulus [Pa]
    "nu": 0.3,                 # Poisson ratio [-]
    "a": 1.0,                  # non-singular core radius [b]
    # --- elasticity / force model ---
    "force_mode": "Elasticity_SBA",   # full elastic seg-seg interactions + PK
    # Ec is left as None so CalForce uses its reference default
    # Ec = mu/(4 pi) * log(a/0.1)
    "Ec": None,
    # --- mobility law ---
    "mobility_law": "SimpleGlide",
    "mob": 1.0,                # mobility prefactor (reference default)
    "vmax": 1.0e9,             # velocity cap [b/s] (reference default)
    # --- time integration ---
    "integrator": "EulerForward",
    # --- topological operations ---
    "split_mode": "MaxDiss",          # multi-node splitting
    "collision_mode": "Proximity",    # collision handling
    "remesh_rule": "LengthBased",     # remeshing
    # --- boundary conditions ---
    "pbc": True,               # periodic in all three directions
    "cell_ndiv": [8, 8, 8],    # collision cell-list subdivision
    # --- numerical discretization (scales with box size L, exactly the
    #     ratios of the reference: maxseg=0.04 L, minseg=0.01 L, rann=0.003 L)
    "maxseg_frac": 0.04,
    "minseg_frac": 0.01,
    "rann_frac": 0.003,
    # --- loading ---
    "loading_mode": "stress",
}

# Reference applied stress in Voigt order [xx, yy, zz, yz, xz, xy] (Pa).
# This is the loading convention used by pydis: the state vector is mapped to
# the full tensor by calforce.voigt_vector_to_tensor().  The reference case
# loads a single shear component sigma_xz = -400 MPa.
REFERENCE_STRESS_VOIGT = np.array([0.0, 0.0, 0.0, 0.0, -4.0e8, 0.0])

VOIGT_COMPONENTS = ["xx", "yy", "zz", "yz", "xz", "xy"]

# Quantities that are allowed to vary between dataset cases.
VARIABLE_QUANTITIES = [
    "initial dislocation topology and geometry",
    "number and placement of loops or lines",
    "simulation-box size",
    "field of view",
    "applied stress",
    "random seed",
    "simulation duration / output frequency / timestep",
]


def numerical_params(box_size: float) -> dict:
    """Discretization parameters scaled consistently with the box size."""
    return {
        "maxseg": REFERENCE["maxseg_frac"] * box_size,
        "minseg": REFERENCE["minseg_frac"] * box_size,
        "rann": REFERENCE["rann_frac"] * box_size,
    }


def make_state(box_size: float) -> dict:
    """Build the pydis state dictionary for a given box size."""
    p = numerical_params(box_size)
    return {
        "burgmag": REFERENCE["burgmag"],
        "mu": REFERENCE["mu"],
        "nu": REFERENCE["nu"],
        "a": REFERENCE["a"],
        "mob": REFERENCE["mob"],
        "maxseg": p["maxseg"],
        "minseg": p["minseg"],
        "rann": p["rann"],
    }


def voigt_to_tensor(voigt) -> np.ndarray:
    v = np.asarray(voigt, dtype=float)
    return np.array([
        [v[0], v[5], v[4]],
        [v[5], v[1], v[3]],
        [v[4], v[3], v[2]],
    ])
