"""Headless case runner.

Builds the network from a CaseConfig, validates it, assembles the reference
solver modules (elasticity force, SimpleGlide mobility, EulerForward
integration, MaxDiss topology, Proximity collision, LengthBased remesh) and
advances the simulation using the pydis SimulateNetwork.step() so the
operation ordering is identical to the reference driver.  Writes raw
trajectory frames (JSON), processed trajectory data (NPZ + CSV), a
simulation log, validation results and a status file into the case directory.
"""

import json
import os
import time
import traceback
import numpy as np

from . import paths  # noqa: F401
from .config import CaseConfig
from .geometry import build_network
from .reference import REFERENCE, make_state
from .validate import validate_case, validate_post_run
from .calforce_ext import CalForceElasticity

from pydis import DisNet, CellList
from pydis import MobilityLaw, TimeIntegration, Topology, Collision, Remesh
from pydis import SimulateNetwork
from framework.disnet_manager import DisNetManager


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return json.JSONEncoder.default(self, obj)


def _dump_json(obj, filename):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=2, cls=NumpyEncoder)


def build_modules(net: DisNetManager, config: CaseConfig):
    """Assemble the fixed reference solver modules for one case."""
    L = float(config.box_size[0])
    state = make_state(L)
    nbrlist = CellList(cell=net.cell, n_div=REFERENCE["cell_ndiv"])

    calforce = CalForceElasticity(force_mode=REFERENCE["force_mode"],
                                  state=state)
    mobility = MobilityLaw(mobility_law=REFERENCE["mobility_law"], state=state,
                           vmax=REFERENCE["vmax"])
    timeint = TimeIntegration(integrator=REFERENCE["integrator"],
                              dt=config.dt, state=state)
    topology = Topology(split_mode=REFERENCE["split_mode"], state=state,
                        force=calforce, mobility=mobility)
    collision = Collision(collision_mode=REFERENCE["collision_mode"],
                          state=state, nbrlist=nbrlist)
    remesh = Remesh(remesh_rule=REFERENCE["remesh_rule"], state=state)

    sim = SimulateNetwork(calforce=calforce, mobility=mobility,
                          timeint=timeint, topology=topology,
                          collision=collision, remesh=remesh, vis=None,
                          state=state, max_step=config.max_step,
                          loading_mode=REFERENCE["loading_mode"],
                          applied_stress=np.array(config.applied_stress_voigt),
                          print_freq=None, plot_freq=None,
                          write_freq=None, save_state=False)
    return sim, state


def _network_stats(G: DisNet):
    segs = G.get_segs_data_with_positions()
    if segs["R1"].shape[0] == 0:
        return 0, 0, 0.0
    lens = np.linalg.norm(segs["R2"] - segs["R1"], axis=1)
    return G.num_nodes(), G.num_segments(), float(lens.sum())


def _capture_frame(net: DisNetManager):
    data = net.export_data()
    return {
        "positions": np.array(data["nodes"]["positions"], dtype=float),
        "tags": np.array(data["nodes"]["tags"], dtype=int),
        "nodeids": np.array(data["segs"]["nodeids"], dtype=int),
        "burgers": np.array(data["segs"]["burgers"], dtype=float),
        "planes": np.array(data["segs"]["planes"], dtype=float),
    }


def run_case(case_dir: str, force: bool = False) -> dict:
    """Run the simulation for the case stored in case_dir.

    Expects case_dir/config.json.  Returns the status dictionary.
    """
    config = CaseConfig.load(os.path.join(case_dir, "config.json"))
    out_dir = os.path.join(case_dir, "output")
    proc_dir = os.path.join(case_dir, "processed")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    status_path = os.path.join(case_dir, "status.json")
    if os.path.exists(status_path) and not force:
        with open(status_path) as f:
            status = json.load(f)
        if status.get("success"):
            return status

    log_path = os.path.join(case_dir, "simulation.log")
    log_f = open(log_path, "w")

    def log(msg):
        stamp = time.strftime("%H:%M:%S")
        log_f.write(f"[{stamp}] {msg}\n")
        log_f.flush()
        print(f"[{config.name}] {msg}", flush=True)

    status = {"name": config.name, "success": False, "steps_completed": 0,
              "termination_reason": "", "wall_time_s": 0.0}
    t_start = time.time()
    try:
        log(f"building network: {len(config.loops)} loops, "
            f"{len(config.lines)} lines, box={config.box_size}")
        net = build_network(config)

        # ---- pre-run validation --------------------------------------
        report = validate_case(net, config)
        _dump_json(report, os.path.join(case_dir, "validation.json"))
        if not report["passed"]:
            failed = [k for k, v in report["checks"].items() if not v["passed"]]
            raise RuntimeError(f"pre-run validation failed: {failed}")
        log("pre-run validation passed "
            f"({len(report['checks'])} checks)")

        net.write_json(os.path.join(case_dir, "initial_network.json"))

        sim, state = build_modules(net, config)
        log(f"modules: force={REFERENCE['force_mode']} "
            f"mobility={REFERENCE['mobility_law']} dt={config.dt:g} "
            f"max_step={config.max_step} stress(Voigt)="
            f"{np.array(config.applied_stress_voigt)}")

        # ---- time stepping --------------------------------------------
        frames = []
        frame_steps = []
        summary_rows = []
        n_frames_expected = config.max_step // config.write_freq + 1

        def write_frame(step):
            net.write_json(os.path.join(out_dir, f"disnet_{step:06d}.json"))
            frames.append(_capture_frame(net))
            frame_steps.append(step)

        write_frame(0)
        G = net.get_disnet(DisNet)
        nn, ns, ltot = _network_stats(G)
        summary_rows.append((0, 0.0, nn, ns, ltot))
        log(f"step 0: nodes={nn} segs={ns} total_length={ltot:.2f}")

        termination = "max_step reached"
        step = 0
        for step in range(1, config.max_step + 1):
            sim.step(net, state)
            G = net.get_disnet(DisNet)

            if G.num_nodes() == 0:
                write_frame(step)
                summary_rows.append((step, step * config.dt, 0, 0, 0.0))
                termination = "network fully annihilated"
                log(f"step {step}: network fully annihilated; stopping")
                break

            pos = G.pos_array()
            if not np.all(np.isfinite(pos)):
                termination = "numerical blow-up (NaN/Inf positions)"
                raise RuntimeError(termination)

            if step % config.write_freq == 0:
                write_frame(step)
                nn, ns, ltot = _network_stats(G)
                summary_rows.append((step, step * config.dt, nn, ns, ltot))
                log(f"step {step}: nodes={nn} segs={ns} "
                    f"total_length={ltot:.2f}")

        status["steps_completed"] = step

        # ---- processed trajectory --------------------------------------
        npz = {"frame_steps": np.array(frame_steps, dtype=int),
               "frame_times": np.array(frame_steps, dtype=float) * config.dt,
               "box_size": np.array(config.box_size, dtype=float),
               "fov": np.array(config.fov, dtype=float)}
        for k, fr in enumerate(frames):
            for key, arr in fr.items():
                npz[f"{key}_{k:04d}"] = arr
        np.savez_compressed(os.path.join(proc_dir, "trajectory.npz"), **npz)
        with open(os.path.join(proc_dir, "summary.csv"), "w") as f:
            f.write("step,time_s,n_nodes,n_segments,total_line_length_b\n")
            for row in summary_rows:
                f.write(f"{row[0]},{row[1]:.6e},{row[2]},{row[3]},{row[4]:.4f}\n")

        # ---- post-run validation ---------------------------------------
        post = validate_post_run(net, n_frames_written=len(frames),
                                 n_frames_expected=n_frames_expected,
                                 completed=True,
                                 termination_reason=termination)
        with open(os.path.join(case_dir, "validation.json")) as f:
            report = json.load(f)
        report["post_run"] = post
        report["passed"] = report["passed"] and post["passed"]
        _dump_json(report, os.path.join(case_dir, "validation.json"))
        if not post["passed"]:
            raise RuntimeError(f"post-run validation failed: {post}")

        status["success"] = True
        status["termination_reason"] = termination
        status["n_frames"] = len(frames)
        log(f"run finished: {termination}; {len(frames)} frames written")
    except Exception as e:
        status["success"] = False
        status["error"] = repr(e)
        status["traceback"] = traceback.format_exc()
        log(f"FAILED: {e!r}")
        log(status["traceback"])
    finally:
        status["wall_time_s"] = round(time.time() - t_start, 2)
        _dump_json(status, status_path)
        log_f.close()
    return status
