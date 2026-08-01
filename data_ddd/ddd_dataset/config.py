"""Case configuration system for the DDD dataset.

A CaseConfig fully specifies one simulation case: geometry/topology of the
initial dislocation network, box size, field of view, applied stress, seed,
duration and output frequency.  It serializes to a human-readable JSON file
(config.json) stored in each case directory.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
import numpy as np

from .reference import (REFERENCE, REFERENCE_STRESS_VOIGT, VOIGT_COMPONENTS,
                        numerical_params, voigt_to_tensor)


@dataclass
class LoopSpec:
    """A circular glissile (prismatic-free, shear) dislocation loop.

    The Burgers vector lies in the glide plane (b . n = 0) so the loop can
    expand/shrink by glide under the SimpleGlide mobility law.
    """
    center: List[float]          # loop center [b]
    radius: float                # loop radius [b]
    burgers: List[float]         # Burgers vector (units of b)
    normal: List[float]          # glide-plane normal (unit vector)
    n_nodes: int                 # number of discretization nodes


@dataclass
class LineSpec:
    """An infinite straight dislocation line threading the periodic box.

    The line runs along a box axis (direction must be axis-aligned so that
    it closes on itself through the periodic boundaries).
    """
    point: List[float]           # a point on the line [b]
    direction: List[float]       # line direction (axis-aligned unit vector)
    burgers: List[float]         # Burgers vector (units of b)
    normal: List[float]          # glide-plane normal (unit vector)
    n_nodes: int                 # number of discretization nodes


@dataclass
class CaseConfig:
    # identification
    name: str
    case_type: str               # e.g. single_loop, double_loop, line_loop ...
    seed: int
    # geometry / domain
    box_size: List[float]        # full 3D box [Lx, Ly, Lz] in units of b
    fov: List[float]             # field of view (visualization/processing window)
    loops: List[LoopSpec] = field(default_factory=list)
    lines: List[LineSpec] = field(default_factory=list)
    # loading: Voigt [xx, yy, zz, yz, xz, xy] in Pa
    applied_stress_voigt: List[float] = field(
        default_factory=lambda: list(REFERENCE_STRESS_VOIGT))
    stress_scale: float = 1.0        # scale applied to the reference stress
    stress_perturb_frac: float = 0.0  # relative random shear perturbation
    # duration / output
    dt: float = 1.0e-10          # timestep [s]
    max_step: int = 200
    write_freq: int = 10
    # validation intent flags
    intended_interaction: bool = False   # loops are allowed/meant to interact
    allow_boundary_proximity: bool = False
    notes: str = ""

    # ------------------------------------------------------------------
    def stress_tensor(self) -> np.ndarray:
        return voigt_to_tensor(self.applied_stress_voigt)

    def to_dict(self) -> dict:
        d = asdict(self)
        # add derived, human-readable metadata
        L = float(self.box_size[0])
        d["derived"] = {
            "applied_stress_tensor_Pa": self.stress_tensor().tolist(),
            "voigt_order": VOIGT_COMPONENTS,
            "numerical_params": numerical_params(L),
            "n_loops": len(self.loops),
            "n_lines": len(self.lines),
            "length_unit": f"burgmag = {REFERENCE['burgmag']} m",
        }
        d["reference"] = {
            "description": ("Fixed solver settings pinned to the SimpleGlide "
                            "elasticity reference configuration"),
            "settings": {k: (v if not isinstance(v, np.ndarray) else v.tolist())
                         for k, v in REFERENCE.items()},
        }
        return d

    def save(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filename: str) -> "CaseConfig":
        with open(filename) as f:
            d = json.load(f)
        d.pop("derived", None)
        d.pop("reference", None)
        d["loops"] = [LoopSpec(**l) for l in d.get("loops", [])]
        d["lines"] = [LineSpec(**l) for l in d.get("lines", [])]
        return cls(**d)


# ---------------------------------------------------------------------------
# Applied-stress construction
# ---------------------------------------------------------------------------
def build_applied_stress(base_voigt=None, scale: float = 1.0,
                         perturb_frac: float = 0.0,
                         seed: Optional[int] = None) -> np.ndarray:
    """Build an applied-stress Voigt vector around the reference stress.

    The perturbation is a random symmetric *traceless* (deviatoric) tensor:
    hydrostatic stress produces no glide driving force under the SimpleGlide
    mobility (velocity is projected onto glide planes), so perturbing the
    deviatoric part preserves the physically meaningful loading structure.
    The perturbation magnitude is perturb_frac * max|sigma_base|.
    """
    base = np.array(REFERENCE_STRESS_VOIGT if base_voigt is None else base_voigt,
                    dtype=float)
    sigma = scale * base
    if perturb_frac > 0.0:
        rng = np.random.default_rng(seed)
        # random symmetric tensor
        A = rng.standard_normal((3, 3))
        S = 0.5 * (A + A.T)
        S -= np.eye(3) * np.trace(S) / 3.0            # traceless
        S /= max(np.abs(S).max(), 1e-300)             # normalize to unit max
        mag = perturb_frac * np.abs(sigma).max()
        dv = mag * np.array([S[0, 0], S[1, 1], S[2, 2],
                             S[1, 2], S[0, 2], S[0, 1]])
        sigma = sigma + dv
    return sigma


def stress_label(voigt) -> str:
    """Short deterministic label for the dominant stress component."""
    v = np.asarray(voigt, dtype=float)
    i = int(np.abs(v).argmax())
    mpa = v[i] / 1e6
    return f"s{VOIGT_COMPONENTS[i]}{mpa:+05.0f}MPa".replace("+", "p").replace("-", "m")
