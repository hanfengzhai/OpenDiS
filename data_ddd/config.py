"""Configuration system for elasticity-enabled DDD dataset cases.

A case configuration is fully declarative and human readable (YAML).  It holds
everything needed to regenerate a case bit-for-bit: case type, number of loops,
loop positions/radii/Burgers vectors/slip-plane normals, line geometries, box
size, field of view, applied-stress tensor, random seed, simulation duration and
output frequency, together with a snapshot of the reference physics settings.

Lengths are expressed in *nominal units* (u); ``units.unit_b`` converts them to
the ExaDiS length unit (the Burgers vector magnitude b).  The simulation box is
always three-dimensional: ``box_size`` is a 3-vector ``[Lx, Ly, Lz]``, never a
2-D specification.
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Sequence

import numpy as np
import yaml

from data_ddd.reference import REFERENCE, fft_grid, load_reference

VOIGT_LABELS = ("xx", "yy", "zz", "yz", "xz", "xy")


def _as_list(v: Sequence[float]) -> List[float]:
    return [float(x) for x in np.asarray(v, dtype=float).ravel()]


def to_builtin(value: Any) -> Any:
    """Recursively convert numpy scalars/arrays to plain python (YAML-safe)."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_builtin(v) for v in value]
    return value


@dataclass
class LoopSpec:
    """A single glissile (shear) dislocation loop.

    The Burgers vector lies in the loop plane so the loop can glide; positions
    and radii are in nominal units.
    """

    center: List[float]
    radius: float
    burgers: List[float]  # crystallographic direction, normalized on use
    plane: List[float]  # slip-plane normal, normalized on use
    slip_system: int = -1
    sense: int = 1  # +1 / -1, sign of the Burgers vector
    n_nodes: int = 0  # 0 -> derived from radius and maxseg

    def __post_init__(self) -> None:
        self.center = _as_list(self.center)
        self.burgers = _as_list(self.burgers)
        self.plane = _as_list(self.plane)
        self.radius = float(self.radius)
        self.slip_system = int(self.slip_system)
        self.sense = int(self.sense)
        self.n_nodes = int(self.n_nodes)


@dataclass
class LineSpec:
    """A dislocation line: a PBC-periodic infinite line or a Frank-Read source."""

    origin: List[float]
    burgers: List[float]
    plane: List[float]
    kind: str = "infinite"  # infinite | frank_read
    theta: float = 0.0  # character angle in degrees
    length: float = 0.0  # nominal units, frank_read only
    slip_system: int = -1
    sense: int = 1
    n_nodes: int = 0

    def __post_init__(self) -> None:
        self.origin = _as_list(self.origin)
        self.burgers = _as_list(self.burgers)
        self.plane = _as_list(self.plane)
        self.kind = str(self.kind)
        self.theta = float(self.theta)
        self.length = float(self.length)
        self.slip_system = int(self.slip_system)
        self.sense = int(self.sense)
        self.n_nodes = int(self.n_nodes)


@dataclass
class StressSpec:
    """Applied stress, kept as a physically meaningful tensor.

    ``mode='uniaxial'`` builds ``sigma = magnitude * (d x d)`` for a loading
    direction ``d``; ``mode='shear'`` builds a symmetric pure shear
    ``magnitude * (m x n + n x m)/|..|`` for a slip direction ``m`` and plane
    normal ``n``; ``mode='tensor'`` uses ``voigt`` directly.  Units are Pa and
    the Voigt order is (xx, yy, zz, yz, xz, xy), the ExaDiS convention.
    """

    mode: str = "uniaxial"
    magnitude: float = 300.0e6
    axis: List[float] = field(default_factory=lambda: [1.0, 2.0, 3.0])
    shear_dir: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0])
    shear_normal: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    voigt: List[float] = field(default_factory=lambda: [0.0] * 6)
    perturbation: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.mode = str(self.mode)
        self.magnitude = float(self.magnitude)
        self.axis = _as_list(self.axis)
        self.shear_dir = _as_list(self.shear_dir)
        self.shear_normal = _as_list(self.shear_normal)
        self.voigt = _as_list(self.voigt) if len(self.voigt) == 6 else [0.0] * 6
        if not any(self.voigt):
            self.voigt = _as_list(self.compute_voigt())

    def tensor(self) -> np.ndarray:
        """Full 3x3 symmetric stress tensor in Pa."""
        v = np.asarray(self.voigt, dtype=float)
        return np.array(
            [[v[0], v[5], v[4]], [v[5], v[1], v[3]], [v[4], v[3], v[2]]]
        )

    def compute_voigt(self) -> np.ndarray:
        if self.mode == "uniaxial":
            d = np.asarray(self.axis, dtype=float)
            d = d / np.linalg.norm(d)
            s = self.magnitude * np.outer(d, d)
        elif self.mode == "shear":
            m = np.asarray(self.shear_dir, dtype=float)
            n = np.asarray(self.shear_normal, dtype=float)
            m = m / np.linalg.norm(m)
            n = n / np.linalg.norm(n)
            s = self.magnitude * 0.5 * (np.outer(m, n) + np.outer(n, m))
        elif self.mode == "tensor":
            return np.asarray(self.voigt, dtype=float)
        else:
            raise ValueError("Unknown stress mode '%s'" % self.mode)
        return np.array([s[0, 0], s[1, 1], s[2, 2], s[1, 2], s[0, 2], s[0, 1]])

    def resolved_shear(self, burgers: Sequence[float], plane: Sequence[float]) -> float:
        """Resolved shear stress (Pa) on the slip system (b, n)."""
        b = np.asarray(burgers, dtype=float)
        n = np.asarray(plane, dtype=float)
        b = b / np.linalg.norm(b)
        n = n / np.linalg.norm(n)
        return float(b @ self.tensor() @ n)

    def schmid_factor(self, burgers: Sequence[float], plane: Sequence[float]) -> float:
        if self.magnitude == 0.0:
            return 0.0
        return self.resolved_shear(burgers, plane) / self.magnitude

    def von_mises(self) -> float:
        s = self.tensor()
        dev = s - np.trace(s) / 3.0 * np.eye(3)
        return float(np.sqrt(1.5 * np.sum(dev * dev)))


@dataclass
class CaseConfig:
    """Complete, self-contained description of one dataset case."""

    name: str
    case_type: str
    interaction: str = "isolated"
    description: str = ""

    # geometry / topology
    loops: List[LoopSpec] = field(default_factory=list)
    lines: List[LineSpec] = field(default_factory=list)

    # box and field of view (nominal units, always 3-D)
    box_size: List[float] = field(default_factory=lambda: [32.0, 32.0, 32.0])
    fov: List[float] = field(default_factory=lambda: [32.0, 32.0, 32.0])
    pbc: List[bool] = field(default_factory=lambda: [True, True, True])

    # loading
    stress: StressSpec = field(default_factory=StressSpec)

    # run control
    seed: int = 0
    num_steps: int = 200
    write_freq: int = 4
    print_freq: int = 4

    # physics snapshot (reference settings; identical for every case)
    physics: Dict[str, Any] = field(default_factory=lambda: copy.deepcopy(REFERENCE))

    def __post_init__(self) -> None:
        self.loops = [LoopSpec(**l) if isinstance(l, dict) else l for l in self.loops]
        self.lines = [LineSpec(**l) if isinstance(l, dict) else l for l in self.lines]
        if isinstance(self.stress, dict):
            self.stress = StressSpec(**self.stress)
        self.box_size = _as_list(self.box_size)
        self.fov = _as_list(self.fov)
        if len(self.box_size) == 1:
            self.box_size = self.box_size * 3
        if len(self.fov) == 1:
            self.fov = self.fov * 3
        if len(self.box_size) != 3:
            raise ValueError(
                "box_size must be three-dimensional (the DDD cell is a 3-D box); "
                "got %r" % (self.box_size,)
            )
        if len(self.fov) != 3:
            raise ValueError("fov must be three-dimensional; got %r" % (self.fov,))
        self.pbc = [bool(p) for p in self.pbc]

    # -- unit helpers ------------------------------------------------------
    @property
    def unit_b(self) -> float:
        return float(self.physics["units"]["unit_b"])

    @property
    def box_b(self) -> np.ndarray:
        """Box edge lengths in ExaDiS length units (b)."""
        return np.asarray(self.box_size, dtype=float) * self.unit_b

    @property
    def fov_b(self) -> np.ndarray:
        return np.asarray(self.fov, dtype=float) * self.unit_b

    @property
    def cell_center_b(self) -> np.ndarray:
        return 0.5 * self.box_b

    @property
    def n_loops(self) -> int:
        return len(self.loops)

    @property
    def n_lines(self) -> int:
        return len(self.lines)

    def fft_grid(self) -> List[int]:
        return [fft_grid(L, self.physics) for L in self.box_b]

    # -- serialization -----------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        data = to_builtin(asdict(self))
        data["derived"] = {
            "n_loops": self.n_loops,
            "n_lines": self.n_lines,
            "unit_b": self.unit_b,
            "box_size_b": _as_list(self.box_b),
            "fov_b": _as_list(self.fov_b),
            "fft_grid": self.fft_grid(),
            "applied_stress_voigt_Pa": {
                lab: float(v) for lab, v in zip(VOIGT_LABELS, self.stress.voigt)
            },
            "applied_stress_von_mises_Pa": self.stress.von_mises(),
        }
        return data

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False, default_flow_style=False)


def save_case(config: CaseConfig, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(config.to_yaml())


def load_case(path: str) -> CaseConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    data.pop("derived", None)
    return CaseConfig(**data)


def make_reference_physics(reference_json: str | None = None) -> Dict[str, Any]:
    return load_reference(reference_json)
