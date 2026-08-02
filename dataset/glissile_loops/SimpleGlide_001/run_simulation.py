#!/usr/bin/env python3
"""Run the SimpleGlide_001 reference simulation (do not modify this file)."""

import os
import sys
import yaml
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path[:0] = [
    os.path.join(ROOT, "core", "exadis", "python"),
    os.path.join(ROOT, "core", "pydis", "python"),
    os.path.join(ROOT, "python"),
]

import pyexadis
from pyexadis_base import (
    ExaDisNet, DisNetManager, SimulateNetwork,
    CalForce, MobilityLaw, TimeIntegration, Collision, Topology, Remesh,
)

CASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(os.path.join(CASE_DIR, "config.yaml")) as f:
        return yaml.safe_load(f)


def build_network(cfg):
    geom = cfg["geometry"]
    disc = cfg["discretization"]
    Lbox = geom["box_size"]
    G = ExaDisNet()
    G.generate_prismatic_config(
        geom["crystal"], Lbox, geom["num_loops"],
        geom["loop_radius"], disc["maxseg"], seed=geom["seed"],
    )
    return DisNetManager(G)


def build_state(cfg):
    mat = cfg["material"]
    disc = cfg["discretization"]
    return {
        "crystal": cfg["geometry"]["crystal"],
        "burgmag": mat["burgmag"],
        "mu": mat["mu"],
        "nu": mat["nu"],
        "a": mat["a"],
        "maxseg": disc["maxseg"],
        "minseg": disc["minseg"],
        "rtol": disc["rtol"],
        "rann": disc["rann"],
        "nextdt": disc["nextdt"],
    }


def main():
    cfg = load_config()
    out_dir = os.path.join(CASE_DIR, "output")
    os.makedirs(out_dir, exist_ok=True)

    pyexadis.initialize()
    N = build_network(cfg)
    state = build_state(cfg)

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
        applied_stress=np.array([float(x) for x in cfg["loading"]["applied_stress"]]),
        print_freq=cfg["simulation"]["print_freq"],
        write_freq=cfg["simulation"]["write_freq"],
        write_dir=out_dir,
    )
    sim.run(N, state)
    pyexadis.finalize()


if __name__ == "__main__":
    main()
