"""Run one dataset case with ExaDiS, with elasticity enabled.

Every module (force, mobility, time integration, collision, topology, remesh)
is instantiated from the reference settings stored in the case configuration, so
that all cases share the same physics and only differ by geometry, box size,
field of view and applied stress.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from typing import Any, Dict, List

import numpy as np

from data_ddd import exadis_env
from data_ddd.config import CaseConfig, load_case, save_case
from data_ddd.paths import CasePaths
from data_ddd.reference import reference_state
from data_ddd.validation import validate_config, validate_network


def build_modules(config: CaseConfig, cell, state: Dict[str, Any]):
    """Instantiate the ExaDiS modules of the reference configuration."""
    from pyexadis_base import (
        CalForce,
        Collision,
        MobilityLaw,
        Remesh,
        TimeIntegration,
        Topology,
    )

    physics = config.physics
    force_cfg = physics["force"]
    calforce = CalForce(
        force_mode=force_cfg["force_mode"],
        state=state,
        Ngrid=config.fft_grid(),
        cell=cell,
        Ec=force_cfg.get("Ec", -1.0),
    )
    mob_cfg = physics["mobility"]
    mobility = MobilityLaw(
        mobility_law=mob_cfg["mobility_law"], state=state, mob=mob_cfg["mob"]
    )
    ti_cfg = physics["time_integration"]
    timeint = TimeIntegration(
        integrator=ti_cfg["integrator"], state=state, force=calforce, mobility=mobility
    )
    collision = Collision(collision_mode=physics["collision"]["collision_mode"], state=state)
    top_cfg = physics["topology"]
    topology = Topology(
        topology_mode=top_cfg["topology_mode"],
        state=state,
        force=calforce,
        mobility=mobility,
        splitMultiNodeAlpha=top_cfg["splitMultiNodeAlpha"],
    )
    remesh = Remesh(remesh_rule=physics["remesh"]["remesh_rule"], state=state)
    return calforce, mobility, timeint, collision, topology, remesh


class NetworkExhausted(RuntimeError):
    """Raised when every dislocation has left/annihilated: the run must stop."""


def make_recording_simulation(**kwargs):
    """SimulateNetwork that records the state of every time step."""
    from pyexadis_base import SimulateNetwork

    class RecordingSimulation(SimulateNetwork):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.history: List[Dict[str, Any]] = []

        def step(self, N, state):
            from pyexadis_base import ExaDisNet

            super().step(N, state)
            disnet = N.get_disnet(ExaDisNet)
            n_nodes = int(disnet.net.number_of_nodes())
            step_index = len(self.history) + 1
            self.history.append(
                {
                    "step": step_index,
                    "time": float(state.get("time", 0.0)),
                    "dt": float(state.get("dt", 0.0)),
                    "n_nodes": n_nodes,
                    "density": float(self.density),
                    "stress_vm": float(self.stress),
                }
            )
            if n_nodes == 0:
                # ExaDiS cannot take another step on an empty network; stop here
                # and keep the frames written so far.
                disnet.write_data(
                    os.path.join(self.write_dir, "config.%d.data" % step_index)
                )
                raise NetworkExhausted(
                    "all dislocations annihilated at step %d" % step_index
                )

    return RecordingSimulation(**kwargs)


def write_metadata(config: CaseConfig, paths: CasePaths, extra: Dict[str, Any]) -> None:
    stress = config.stress
    metadata = {
        "case": config.name,
        "case_type": config.case_type,
        "interaction": config.interaction,
        "description": config.description,
        "seed": config.seed,
        "box": {
            "size_nominal": list(config.box_size),
            "size_b": [float(v) for v in config.box_b],
            "dimensionality": 3,
            "pbc": list(config.pbc),
            "unit_b": config.unit_b,
            "burgmag_m": config.physics["material"]["burgmag"],
            "size_m": [float(v) * config.physics["material"]["burgmag"] for v in config.box_b],
        },
        "field_of_view": {
            "size_nominal": list(config.fov),
            "size_b": [float(v) for v in config.fov_b],
            "center_b": [float(v) for v in config.cell_center_b],
        },
        "applied_stress": {
            "mode": stress.mode,
            "magnitude_Pa": stress.magnitude,
            "axis": list(stress.axis),
            "voigt_Pa": {
                "xx": stress.voigt[0],
                "yy": stress.voigt[1],
                "zz": stress.voigt[2],
                "yz": stress.voigt[3],
                "xz": stress.voigt[4],
                "xy": stress.voigt[5],
            },
            "tensor_Pa": [[float(v) for v in row] for row in stress.tensor()],
            "von_mises_Pa": stress.von_mises(),
            "perturbation": stress.perturbation,
        },
        "initial_geometry": {
            "n_loops": config.n_loops,
            "n_lines": config.n_lines,
            "loops": [
                {
                    "center_nominal": loop.center,
                    "center_b": [float(c) * config.unit_b for c in loop.center],
                    "radius_nominal": loop.radius,
                    "radius_b": loop.radius * config.unit_b,
                    "burgers": loop.burgers,
                    "plane": loop.plane,
                    "slip_system": loop.slip_system,
                    "sense": loop.sense,
                    "n_nodes": loop.n_nodes,
                    "schmid_factor": stress.schmid_factor(loop.burgers, loop.plane),
                }
                for loop in config.loops
            ],
            "lines": [
                {
                    "origin_nominal": line.origin,
                    "origin_b": [float(c) * config.unit_b for c in line.origin],
                    "kind": line.kind,
                    "theta_deg": line.theta,
                    "burgers": line.burgers,
                    "plane": line.plane,
                    "slip_system": line.slip_system,
                    "sense": line.sense,
                    "n_nodes": line.n_nodes,
                    "schmid_factor": stress.schmid_factor(line.burgers, line.plane),
                }
                for line in config.lines
            ],
        },
        "run": {
            "num_steps": config.num_steps,
            "write_freq": config.write_freq,
            "print_freq": config.print_freq,
        },
        "physics": config.physics,
    }
    metadata.update(extra)
    with open(paths.metadata, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)


def generate_case(config: CaseConfig, paths: CasePaths) -> Dict[str, Any]:
    """Create the case directory, build and validate the initial network."""
    exadis_env.initialize()
    from pyexadis_base import ExaDisNet

    from data_ddd.geometry import build_network

    paths.make_dirs()

    config_report = validate_config(config)
    config_report.write(os.path.join(paths.validation, "config.json"))
    if not config_report.ok:
        raise ValueError(
            "Configuration validation failed for case %s:\n%s"
            % (config.name, config_report.summary())
        )

    net, cell = build_network(config)
    data = net.export_data()

    network_report = validate_network(config, data)
    network_report.write(os.path.join(paths.validation, "network.json"))

    net.get_disnet(ExaDisNet).write_data(paths.initial_data)
    np.savez_compressed(
        paths.initial_npz,
        cell_h=np.array(cell.h),
        cell_origin=np.array(cell.origin),
        pbc=np.array(config.pbc),
        positions=data["nodes"]["positions"],
        constraints=data["nodes"]["constraints"],
        nodeids=data["segs"]["nodeids"],
        burgers=data["segs"]["burgers"],
        planes=data["segs"]["planes"],
    )

    state = reference_state(config.physics)
    run_params = {
        "state": state,
        "force": dict(config.physics["force"], Ngrid=config.fft_grid()),
        "mobility": config.physics["mobility"],
        "time_integration": config.physics["time_integration"],
        "collision": config.physics["collision"],
        "topology": config.physics["topology"],
        "remesh": config.physics["remesh"],
        "loading": {
            "loading_mode": config.physics["loading"]["loading_mode"],
            "applied_stress_voigt_Pa": list(config.stress.voigt),
        },
        "control": {
            "max_step": config.num_steps,
            "write_freq": config.write_freq,
            "print_freq": config.print_freq,
        },
    }
    with open(paths.run_params, "w", encoding="utf-8") as handle:
        json.dump(run_params, handle, indent=2)

    save_case(config, paths.config)
    write_metadata(
        config,
        paths,
        {
            "provenance": {
                "generated_by": "data_ddd.simulate.generate_case",
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
            "validation": {
                "config": config_report.to_dict()["ok"],
                "network": network_report.to_dict()["ok"],
            },
        },
    )

    if not network_report.ok:
        raise ValueError(
            "Network validation failed for case %s:\n%s"
            % (config.name, network_report.summary())
        )

    return {"config": config_report.to_dict(), "network": network_report.to_dict()}


def run_case(case_dir: str, max_step: int | None = None) -> Dict[str, Any]:
    """Run the simulation of an already generated case directory."""
    paths = CasePaths(root=case_dir)
    config = load_case(paths.config)
    if max_step is not None:
        config.num_steps = int(max_step)

    from data_ddd.geometry import build_network

    paths.make_dirs()
    exadis_env.initialize()
    net, cell = build_network(config)
    state = reference_state(config.physics)
    modules = build_modules(config, cell, state)
    calforce, mobility, timeint, collision, topology, remesh = modules

    sim = make_recording_simulation(
        calforce=calforce,
        mobility=mobility,
        timeint=timeint,
        collision=collision,
        topology=topology,
        remesh=remesh,
        cross_slip=None,
        vis=None,
        state=state,
        burgmag=state["burgmag"],
        max_step=config.num_steps,
        loading_mode=config.physics["loading"]["loading_mode"],
        applied_stress=np.array(config.stress.voigt, dtype=float),
        print_freq=config.print_freq,
        write_freq=config.write_freq,
        write_dir=paths.raw,
    )
    t0 = time.perf_counter()
    termination = "completed"
    try:
        sim.run(net, state)
    except NetworkExhausted as exc:
        termination = "network_annihilated"
        print("simulation stopped early: %s" % exc)
        sim.write_results()
    walltime = time.perf_counter() - t0

    run_info = {
        "case": config.name,
        "returncode": 0,
        "termination": termination,
        "walltime_s": walltime,
        "num_steps": config.num_steps,
        "write_freq": config.write_freq,
        "history": sim.history,
        "final_time_s": sim.history[-1]["time"] if sim.history else 0.0,
    }
    os.makedirs(paths.logs, exist_ok=True)
    with open(paths.run_info, "w", encoding="utf-8") as handle:
        json.dump(run_info, handle, indent=2)
    return run_info


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one DDD dataset case")
    parser.add_argument("case_dir", help="path of the case directory")
    parser.add_argument("--max-step", type=int, default=None)
    args = parser.parse_args(argv)
    info = run_case(args.case_dir, max_step=args.max_step)
    print("case %s finished in %.1f s (t = %.3e s)"
          % (info["case"], info["walltime_s"], info["final_time_s"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
