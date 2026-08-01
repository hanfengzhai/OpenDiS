"""Command-line driver of the DDD dataset pipeline.

Subcommands::

    python -m data_ddd.pipeline generate   # write case directories + inputs
    python -m data_ddd.pipeline run        # run the simulations
    python -m data_ddd.pipeline process    # raw -> processed trajectories
    python -m data_ddd.pipeline visualize  # images + evolution videos
    python -m data_ddd.pipeline all        # everything, in order
    python -m data_ddd.pipeline report     # dataset status summary
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Iterable, List, Optional

from data_ddd.catalog import default_catalog
from data_ddd.config import CaseConfig, load_case
from data_ddd.exadis_env import REPO_ROOT
from data_ddd.paths import DEFAULT_DATASET_ROOT, CasePaths, case_paths


def _select(cases: List[CaseConfig], args: argparse.Namespace) -> List[CaseConfig]:
    selected = cases
    if getattr(args, "cases", None):
        wanted = {c.strip() for c in args.cases.split(",") if c.strip()}
        selected = [c for c in selected if c.name in wanted]
    if getattr(args, "types", None):
        wanted = {t.strip() for t in args.types.split(",") if t.strip()}
        selected = [c for c in selected if c.case_type in wanted]
    if getattr(args, "representative", False):
        seen = set()
        unique = []
        for case in selected:
            key = (case.case_type, case.interaction)
            if key in seen:
                continue
            seen.add(key)
            unique.append(case)
        selected = unique
    if getattr(args, "limit", None):
        selected = selected[: args.limit]
    return selected


def existing_case_dirs(dataset_root: str, args: argparse.Namespace) -> List[str]:
    if not os.path.isdir(dataset_root):
        return []
    names = sorted(
        d for d in os.listdir(dataset_root)
        if os.path.isfile(os.path.join(dataset_root, d, "config.yaml"))
    )
    configs = [load_case(os.path.join(dataset_root, n, "config.yaml")) for n in names]
    selected = _select(configs, args)
    return [os.path.join(dataset_root, c.name) for c in selected]


def cmd_generate(args: argparse.Namespace) -> int:
    from data_ddd.simulate import generate_case

    cases = _select(default_catalog(args.reference), args)
    os.makedirs(args.dataset_root, exist_ok=True)
    index = []
    failures = 0
    for case in cases:
        paths = case_paths(args.dataset_root, case.name)
        print("[generate] %s" % case.name, flush=True)
        try:
            reports = generate_case(case, paths)
            status = "generated"
            message = ""
        except Exception as exc:  # noqa: BLE001 - report and continue
            reports, status, message = {}, "failed", str(exc)
            failures += 1
            print("  FAILED: %s" % exc, flush=True)
        index.append(
            {
                "case": case.name,
                "case_type": case.case_type,
                "interaction": case.interaction,
                "box_size": case.box_size,
                "fov": case.fov,
                "n_loops": case.n_loops,
                "n_lines": case.n_lines,
                "stress_MPa": case.stress.magnitude / 1e6,
                "seed": case.seed,
                "status": status,
                "message": message,
                "dir": os.path.relpath(paths.root, REPO_ROOT),
            }
        )
    with open(os.path.join(args.dataset_root, "index.json"), "w", encoding="utf-8") as handle:
        json.dump({"cases": index}, handle, indent=2)
    print("generated %d/%d cases" % (len(cases) - failures, len(cases)))
    return 1 if failures else 0


def _run_subprocess(cmd: List[str], log_path: str) -> Dict[str, Any]:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO_ROOT + os.pathsep + env.get("PYTHONPATH", "")
    env.setdefault("MPLBACKEND", "Agg")
    start = time.perf_counter()
    with open(log_path, "a", encoding="utf-8") as log:
        log.write("\n$ %s\n" % " ".join(cmd))
        log.flush()
        proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    return {"returncode": proc.returncode, "walltime_s": time.perf_counter() - start}


def cmd_run(args: argparse.Namespace) -> int:
    dirs = existing_case_dirs(args.dataset_root, args)
    if not dirs:
        print("no generated cases found in %s" % args.dataset_root)
        return 1
    failures = 0
    for case_dir in dirs:
        paths = CasePaths(root=case_dir)
        name = os.path.basename(case_dir)
        print("[run] %s" % name, flush=True)
        cmd = [sys.executable, "-m", "data_ddd.simulate", case_dir]
        if args.max_step:
            cmd += ["--max-step", str(args.max_step)]
        result = _run_subprocess(cmd, paths.run_log)
        if result["returncode"] != 0:
            failures += 1
            print("  FAILED (see %s)" % paths.run_log, flush=True)
            continue
        print("  done in %.1f s" % result["walltime_s"], flush=True)
        if not args.no_process:
            result = _run_subprocess(
                [sys.executable, "-m", "data_ddd.trajectory", case_dir], paths.run_log
            )
            if result["returncode"] != 0:
                failures += 1
                print("  PROCESSING FAILED (see %s)" % paths.run_log, flush=True)
    print("ran %d/%d cases" % (len(dirs) - failures, len(dirs)))
    return 1 if failures else 0


def cmd_process(args: argparse.Namespace) -> int:
    dirs = existing_case_dirs(args.dataset_root, args)
    failures = 0
    for case_dir in dirs:
        paths = CasePaths(root=case_dir)
        print("[process] %s" % os.path.basename(case_dir), flush=True)
        result = _run_subprocess(
            [sys.executable, "-m", "data_ddd.trajectory", case_dir], paths.run_log
        )
        failures += result["returncode"] != 0
    return 1 if failures else 0


def cmd_visualize(args: argparse.Namespace) -> int:
    dirs = existing_case_dirs(args.dataset_root, args)
    failures = 0
    for case_dir in dirs:
        paths = CasePaths(root=case_dir)
        if not os.path.exists(paths.trajectory):
            print("[visualize] %s: no processed trajectory, skipping"
                  % os.path.basename(case_dir))
            failures += 1
            continue
        print("[visualize] %s" % os.path.basename(case_dir), flush=True)
        cmd = [sys.executable, "-m", "data_ddd.visualize", case_dir, "--fps", str(args.fps)]
        if args.no_video:
            cmd.append("--no-video")
        result = _run_subprocess(cmd, os.path.join(paths.logs, "visualize.log"))
        if result["returncode"] != 0:
            failures += 1
            print("  FAILED (see %s)" % os.path.join(paths.logs, "visualize.log"))
    return 1 if failures else 0


def _case_status(case_dir: str) -> Dict[str, Any]:
    paths = CasePaths(root=case_dir)
    status: Dict[str, Any] = {"case": os.path.basename(case_dir)}
    try:
        config = load_case(paths.config)
        status.update(
            case_type=config.case_type,
            interaction=config.interaction,
            box=config.box_size[0],
            fov=config.fov[0],
            n_loops=config.n_loops,
            n_lines=config.n_lines,
            stress_MPa=round(config.stress.magnitude / 1e6, 1),
            seed=config.seed,
        )
    except Exception:  # noqa: BLE001
        status["case_type"] = "unreadable"
    for key, path in (
        ("inputs", paths.initial_data),
        ("trajectory", paths.trajectory),
        ("initial_png", paths.initial_png),
        ("final_png", paths.final_png),
        ("video", paths.video),
    ):
        status[key] = os.path.exists(path)
    n_raw = 0
    if os.path.isdir(paths.raw):
        n_raw = len([f for f in os.listdir(paths.raw) if f.endswith(".data")])
    status["n_raw_frames"] = n_raw
    validation = {}
    for stage in ("config", "network", "run"):
        path = os.path.join(paths.validation, "%s.json" % stage)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                report = json.load(handle)
            validation[stage] = {
                "ok": report["ok"],
                "warn": report["n_warn"],
                "fail": report["n_fail"],
            }
    status["validation"] = validation
    if os.path.exists(paths.run_info):
        with open(paths.run_info, "r", encoding="utf-8") as handle:
            info = json.load(handle)
        status["walltime_s"] = round(info.get("walltime_s", 0.0), 1)
        status["final_time_s"] = info.get("final_time_s", 0.0)
    status["complete"] = bool(
        status.get("trajectory") and status.get("video") and status.get("initial_png")
        and validation.get("run", {}).get("ok", False)
    )
    return status


def cmd_report(args: argparse.Namespace) -> int:
    dirs = existing_case_dirs(args.dataset_root, args)
    rows = [_case_status(d) for d in dirs]
    out = {"dataset_root": args.dataset_root, "n_cases": len(rows), "cases": rows}
    path = os.path.join(args.dataset_root, "dataset_report.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=2)

    header = "%-42s %-14s %-6s %-5s %-7s %-7s %-6s %s" % (
        "case", "type", "box", "fov", "frames", "video", "valid", "walltime"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            "%-42s %-14s %-6s %-5s %-7s %-7s %-6s %s"
            % (
                row["case"],
                row.get("case_type", "?"),
                row.get("box", "?"),
                row.get("fov", "?"),
                row.get("n_raw_frames", 0),
                "yes" if row.get("video") else "no",
                "ok" if row.get("validation", {}).get("run", {}).get("ok") else "-",
                "%.1fs" % row["walltime_s"] if "walltime_s" in row else "-",
            )
        )
    complete = sum(1 for r in rows if r["complete"])
    print("\n%d/%d cases complete; report written to %s" % (complete, len(rows), path))
    return 0 if complete == len(rows) and rows else 1


def cmd_all(args: argparse.Namespace) -> int:
    status = cmd_generate(args)
    status |= cmd_run(args)
    status |= cmd_visualize(args)
    cmd_report(args)
    return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset-root", default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--cases", default=None, help="comma-separated case names")
    parser.add_argument("--types", default=None, help="comma-separated case types")
    parser.add_argument("--representative", action="store_true",
                        help="one case per (case type, interaction) category")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--reference", default=None,
                        help="JSON file overriding the reference physics settings")
    parser.add_argument("--max-step", type=int, default=None)
    parser.add_argument("--no-process", action="store_true")
    parser.add_argument("--no-video", action="store_true")
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("command",
                        choices=["generate", "run", "process", "visualize", "all", "report"])
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "generate": cmd_generate,
        "run": cmd_run,
        "process": cmd_process,
        "visualize": cmd_visualize,
        "all": cmd_all,
        "report": cmd_report,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
