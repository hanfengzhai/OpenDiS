"""Run a single DDD case and organize outputs."""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "core" / "exadis" / "python"),
    str(ROOT / "core" / "pydis" / "python"),
    str(ROOT / "python"),
]

import pyexadis
from pyexadis_base import (
    CalForce, Collision, DisNetManager, MobilityLaw, Remesh,
    SimulateNetwork, TimeIntegration, Topology,
)

from .geometry import build_network
from .reference import reference_state
from .stress import stress_metadata
from .validate import validate_network


def _setup_dirs(case_dir: Path) -> Dict[str, Path]:
    dirs = {
        "root": case_dir,
        "raw": case_dir / "raw",
        "processed": case_dir / "processed",
        "logs": case_dir / "logs",
        "validation": case_dir / "validation",
        "figures": case_dir / "figures",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def run_case(cfg: Dict[str, Any], case_dir: os.PathLike, log_file: Optional[Path] = None) -> Dict[str, Any]:
    case_dir = Path(case_dir)
    dirs = _setup_dirs(case_dir)

    # Save human-readable config
    with open(case_dir / "config.yaml", "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)

    stress = np.array([float(x) for x in cfg["loading"]["applied_stress"]])
    with open(case_dir / "applied_stress.json", "w") as f:
        json.dump(stress_metadata(stress), f, indent=2)

    metadata = {
        "case_id": cfg.get("case_id", case_dir.name),
        "geometry": cfg["geometry"],
        "box_size": cfg["geometry"]["box_size"],
        "field_of_view": cfg["geometry"]["field_of_view"],
        "seed": cfg["geometry"]["seed"],
        "num_loops": cfg["geometry"]["num_loops"],
        "case_type": cfg["geometry"]["case_type"],
    }
    with open(case_dir / "geometry_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    result = {"case_id": metadata["case_id"], "success": False, "errors": []}
    log_path = log_file or (dirs["logs"] / "simulation.log")

    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    with open(log_path, "w") as logf:
        old_stdout = sys.stdout
        sys.stdout = Tee(old_stdout, logf)
        try:
            pyexadis.initialize()
            N = build_network(cfg)
            data = N.export_data()
            val = validate_network(data, cfg)
            with open(dirs["validation"] / "pre_simulation.json", "w") as vf:
                json.dump({"passed": val.passed, "errors": val.errors, "warnings": val.warnings}, vf, indent=2)
            if not val.passed:
                result["errors"] = val.errors
                return result

            state = reference_state()
            state.update({
                "maxseg": float(cfg["discretization"]["maxseg"]),
                "minseg": float(cfg["discretization"]["minseg"]),
                "rtol": float(cfg["discretization"]["rtol"]),
                "rann": float(cfg["discretization"]["rann"]),
                "nextdt": float(cfg["discretization"]["nextdt"]),
            })

            calforce = CalForce(
                force_mode=cfg["force"]["mode"], state=state,
                Ngrid=cfg["force"]["Ngrid"], cell=N.cell,
            )
            mobility = MobilityLaw(
                mobility_law=cfg["mobility"]["law"], state=state,
                mob=cfg["mobility"]["mob"],
            )
            timeint = TimeIntegration(
                integrator=cfg["integrator"]["type"], state=state,
                force=calforce, mobility=mobility,
            )
            collision = Collision(collision_mode=cfg["collision"]["mode"], state=state)
            topology = Topology(
                topology_mode=cfg["topology"]["mode"], state=state,
                force=calforce, mobility=mobility,
            )
            remesh = Remesh(remesh_rule=cfg["remesh"]["rule"], state=state)

            sim = SimulateNetwork(
                calforce=calforce, mobility=mobility, timeint=timeint,
                collision=collision, topology=topology, remesh=remesh,
                state=state, max_step=cfg["simulation"]["max_step"],
                loading_mode=cfg["loading"]["mode"],
                applied_stress=stress,
                print_freq=cfg["simulation"]["print_freq"],
                write_freq=cfg["simulation"]["write_freq"],
                write_dir=str(dirs["raw"]),
            )
            sim.run(N, state)
            result["success"] = True
            from pyexadis_base import ExaDisNet
            result["final_nodes"] = N.get_disnet(ExaDisNet).net.number_of_nodes()

            # Copy stress-strain file to processed
            ss_src = dirs["raw"] / "stress_strain_dens.dat"
            if ss_src.exists():
                import shutil
                shutil.copy(ss_src, dirs["processed"] / "stress_strain_dens.dat")

        except Exception as e:
            result["errors"].append(str(e))
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            try:
                pyexadis.finalize()
            except Exception:
                pass

    with open(dirs["validation"] / "post_simulation.json", "w") as vf:
        json.dump(result, vf, indent=2)
    return result
