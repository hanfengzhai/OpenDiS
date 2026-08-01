"""ddd_dataset: dataset-generation pipeline for elasticity-enabled DDD simulations.

Built on the pydis core of OpenDiS. The physical and numerical settings are
pinned to the repository's SimpleGlide reference configuration (see
reference.py); dataset cases only vary initial geometry/topology, number and
placement of loops/lines, simulation-box size, field of view, applied stress
and random seed.
"""

from . import paths  # noqa: F401  (sets up sys.path for pydis imports)
