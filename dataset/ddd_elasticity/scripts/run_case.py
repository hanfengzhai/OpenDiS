"""Generate inputs, validate, simulate, and visualize one elasticity DDD case."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import numpy as np
import yaml

from paths_setup import CASES_DIR, CONFIGS_DIR, case_name, ensure_imports
from physics import (
    box_size_for_nloops,
    case_config_dict,
    load_reference_physics,
    make_applied_stress,
    make_state,
    solver_settings,
)
from geometry import build_geometry
from validate import validate_network, validate_simulation_outputs, write_validation
from visualize import visualize_case

_PYEXADIS_INITIALIZED = False


def _ensure_pyexadis() -> None:
    """Initialize Kokkos/pyexadis once per process."""
    global _PYEXADIS_INITIALIZED
    ensure_imports()
    import pyexadis

    if not _PYEXADIS_INITIALIZED:
        pyexadis.initialize()
        _PYEXADIS_INITIALIZED = True


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def prepare_case_dir(name: str, root: Path | None = None) -> Path:
    case_dir = (root or CASES_DIR) / name
    for sub in [
        "inputs",
        "raw_trajectory",
        "processed",
        "logs",
        "validation",
        "visualizations",
        "metadata",
    ]:
        (case_dir / sub).mkdir(parents=True, exist_ok=True)
    return case_dir


def run_simulation(case_dir: Path, cfg: dict, N, state: dict) -> None:
    ensure_imports()
    import pyexadis
    from pyexadis_base import (
        CalForce,
        MobilityLaw,
        TimeIntegration,
        Collision,
        Remesh,
        Topology,
        SimulateNetwork,
        ExaDisNet,
    )

    solver = cfg["solver"]
    simcfg = cfg["simulation"]
    applied = np.asarray(cfg["applied_stress_voigt_xx_yy_zz_yz_xz_xy"], dtype=float)

    # Persist initial network
    init_data = case_dir / "inputs" / "initial_config.data"
    N.get_disnet(ExaDisNet).write_data(str(init_data))

    calforce = CalForce(
        force_mode=solver["force_mode"],
        state=state,
        Ngrid=int(solver["ngrid"]),
        cell=N.cell,
    )
    mobility = MobilityLaw(
        mobility_law=solver["mobility_law"],
        state=state,
        mob=float(solver["mobility_mob"]),
    )
    timeint = TimeIntegration(
        integrator=solver["integrator"],
        state=state,
        force=calforce,
        mobility=mobility,
    )
    collision = Collision(collision_mode=solver["collision_mode"], state=state)
    remesh = Remesh(remesh_rule=solver["remesh_rule"], state=state)
    topology = None
    if solver.get("topology_mode"):
        topology = Topology(
            topology_mode=solver["topology_mode"],
            state=state,
            force=calforce,
            mobility=mobility,
        )

    write_dir = str(case_dir / "raw_trajectory")
    log_path = case_dir / "logs" / "simulate.log"
    sim = SimulateNetwork(
        calforce=calforce,
        mobility=mobility,
        timeint=timeint,
        collision=collision,
        topology=topology,
        remesh=remesh,
        vis=None,
        state=state,
        max_step=int(simcfg["max_step"]),
        loading_mode=solver["loading_mode"],
        applied_stress=applied,
        print_freq=int(simcfg["print_freq"]),
        plot_freq=None,
        write_freq=int(simcfg["write_freq"]),
        write_dir=write_dir,
    )

    with open(log_path, "w", encoding="utf-8") as logf, redirect_stdout(logf), redirect_stderr(logf):
        print("CASE DIR:", case_dir)
        print("APPLIED STRESS:", applied.tolist())
        print("SOLVER:", json.dumps(solver, indent=2))
        sim.run(N, state)

    # Processed trajectory: copy configs listing + stress file mirror
    proc = case_dir / "processed"
    frames = sorted((case_dir / "raw_trajectory").glob("config.*.data"))
    manifest = {
        "n_frames": len(frames),
        "frames": [p.name for p in frames],
        "stress_strain_dens": "raw_trajectory/stress_strain_dens.dat",
    }
    with open(proc / "trajectory_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    dens = case_dir / "raw_trajectory" / "stress_strain_dens.dat"
    if dens.is_file():
        shutil.copy2(dens, proc / "stress_strain_dens.dat")


def build_and_run(
    *,
    case_type: str,
    n_loops: int,
    seed: int,
    stress_factor: float = 1.0,
    box: float | None = None,
    fov: float | None = None,
    max_step: int | None = None,
    write_freq: int | None = None,
    print_freq: int | None = None,
    physics_path: Path | None = None,
    cases_root: Path | None = None,
    skip_viz: bool = False,
    skip_sim: bool = False,
) -> Path:
    physics = load_reference_physics(physics_path)
    box_f = box_size_for_nloops(physics, n_loops, override=box)
    fov_f = float(fov) if fov is not None else box_f
    state = make_state(physics, box_f)
    solver = solver_settings(physics, box_f)
    applied = make_applied_stress(physics, stress_factor)
    max_step = int(max_step if max_step is not None else physics["default_max_step"])
    write_freq = int(write_freq if write_freq is not None else physics["default_write_freq"])
    print_freq = int(print_freq if print_freq is not None else physics["default_print_freq"])
    radius = float(physics["default_radius_over_Lbox"]) * box_f
    margin = float(physics["default_boundary_margin_over_Lbox"]) * box_f
    min_sep = float(physics["default_min_loop_separation_over_radius"]) * radius

    name = case_name(case_type, n_loops, box_f, stress_factor, seed, fov=fov_f)
    case_dir = prepare_case_dir(name, root=cases_root)

    _ensure_pyexadis()
    try:
        N, geom_meta = build_geometry(
            case_type=case_type,
            crystal=physics["crystal"],
            box=box_f,
            n_loops=n_loops,
            radius=radius,
            maxseg=state["maxseg"],
            seed=seed,
            margin=margin,
            min_sep=min_sep,
        )
        cfg = case_config_dict(
            case_type=case_type,
            n_loops=n_loops,
            box=box_f,
            fov=fov_f,
            seed=seed,
            stress_factor=stress_factor,
            applied_stress=applied,
            state=state,
            solver=solver,
            geometry_meta=geom_meta,
            max_step=max_step,
            write_freq=write_freq,
            print_freq=print_freq,
            physics_source=str(physics_path or (CONFIGS_DIR / "reference_physics.yaml")),
        )
        _write_yaml(case_dir / "config.yaml", cfg)
        _write_yaml(case_dir / "metadata" / "geometry.yaml", geom_meta)
        _write_yaml(
            case_dir / "metadata" / "applied_stress.yaml",
            {
                "voigt_order": ["xx", "yy", "zz", "yz", "xz", "xy"],
                "applied_stress": applied.tolist(),
                "stress_factor": stress_factor,
                "reference_applied_stress": physics["reference_applied_stress"],
            },
        )
        _write_yaml(
            case_dir / "metadata" / "box_fov.yaml",
            {
                "box_size_3d": [box_f, box_f, box_f],
                "field_of_view_3d": [fov_f, fov_f, fov_f],
                "ngrid_3d": [solver["ngrid"], solver["ngrid"], solver["ngrid"]],
                "pbc": solver["pbc"],
                "random_seed": seed,
            },
        )

        pre = validate_network(
            N,
            zero_seg_tol=float(physics["zero_segment_tol"]),
            bn_tol=float(physics["burgers_plane_dot_tol"]),
            require_elasticity_settings=solver,
        )
        write_validation(pre, case_dir / "validation" / "pre_simulation.json")
        if not pre["ok"]:
            raise RuntimeError(f"Pre-simulation validation failed: {pre['issues']}")

        if not skip_sim:
            run_simulation(case_dir, cfg, N, state)
            post = validate_simulation_outputs(case_dir, max_step, write_freq)
            # Ensure the final network is non-empty / usable
            try:
                from pyexadis_base import ExaDisNet, DisNetManager

                final_files = sorted((case_dir / "raw_trajectory").glob("config.*.data"))
                if final_files:
                    Gf = ExaDisNet()
                    Gf.read_paradis(str(final_files[-1]))
                    nf = DisNetManager(Gf)
                    final_rep = validate_network(nf, require_elasticity_settings=solver)
                    post["final_network"] = {
                        "n_nodes": final_rep["n_nodes"],
                        "n_segments": final_rep["n_segments"],
                        "ok": final_rep["ok"],
                        "issues": final_rep["issues"],
                    }
                    if final_rep["n_nodes"] < 2 or final_rep["n_segments"] < 1:
                        post["ok"] = False
                        post["issues"].append(
                            f"Final network collapsed (nodes={final_rep['n_nodes']}, segs={final_rep['n_segments']})"
                        )
            except Exception as exc:
                post["ok"] = False
                post["issues"].append(f"Failed to validate final network: {exc}")
            write_validation(post, case_dir / "validation" / "post_simulation.json")
            if not post["ok"]:
                raise RuntimeError(f"Post-simulation validation failed: {post['issues']}")

        if not skip_viz and not skip_sim:
            viz = visualize_case(case_dir, box=box_f, fov=fov_f)
            with open(case_dir / "visualizations" / "paths.json", "w", encoding="utf-8") as f:
                json.dump(viz, f, indent=2)

        status = {"status": "success", "case_dir": str(case_dir), "case_name": name}
        with open(case_dir / "metadata" / "status.json", "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
        return case_dir
    except Exception as exc:
        err = {
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "case_name": name,
        }
        with open(case_dir / "metadata" / "status.json", "w", encoding="utf-8") as f:
            json.dump(err, f, indent=2)
        with open(case_dir / "logs" / "error.log", "w", encoding="utf-8") as f:
            f.write(err["traceback"])
        raise


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Run one elasticity-enabled DDD dataset case")
    p.add_argument("--case-type", required=True)
    p.add_argument("--n-loops", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--stress-factor", type=float, default=1.0)
    p.add_argument("--box", type=float, default=None)
    p.add_argument("--fov", type=float, default=None)
    p.add_argument("--max-step", type=int, default=None)
    p.add_argument("--write-freq", type=int, default=None)
    p.add_argument("--skip-viz", action="store_true")
    p.add_argument("--skip-sim", action="store_true")
    p.add_argument("--cases-root", type=Path, default=None)
    args = p.parse_args(argv)
    case_dir = build_and_run(
        case_type=args.case_type,
        n_loops=args.n_loops,
        seed=args.seed,
        stress_factor=args.stress_factor,
        box=args.box,
        fov=args.fov,
        max_step=args.max_step,
        write_freq=args.write_freq,
        cases_root=args.cases_root,
        skip_viz=args.skip_viz,
        skip_sim=args.skip_sim,
    )
    print(f"OK {case_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
