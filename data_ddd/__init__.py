"""data_ddd: generation of elasticity-enabled DDD datasets with OpenDiS/ExaDiS.

The package builds dislocation-dynamics cases that all share the physics of the
reference simulation (see :mod:`data_ddd.reference`) and differ only by

* initial dislocation topology and geometry,
* number and placement of loops or lines,
* simulation-box size,
* field of view,
* applied stress.
"""

from data_ddd.config import (
    CaseConfig,
    LineSpec,
    LoopSpec,
    StressSpec,
    load_case,
    save_case,
)
from data_ddd.reference import REFERENCE, reference_state

__all__ = [
    "CaseConfig",
    "LoopSpec",
    "LineSpec",
    "StressSpec",
    "load_case",
    "save_case",
    "REFERENCE",
    "reference_state",
]
