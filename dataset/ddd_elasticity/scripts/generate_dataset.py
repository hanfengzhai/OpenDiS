#!/usr/bin/env python3
"""Generate the elasticity-enabled DDD dataset from the case catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from paths_setup import ARTIFACTS_DIR, CASES_DIR, CONFIGS_DIR, ensure_imports
from physics import load_yaml
from run_case import build_and_run


MAJOR_CATEGORIES = [
    "single_loop",
    "double_loop",
    "triple_loop",
    "six_loops",
    "twelve_loops",
    "line_loop",
    "glissile_junction",
    "fov_variant",
]


def expand_catalog(catalog: dict, representatives_only: bool = False) -> list[dict]:
    defaults = catalog.get("defaults", {})
    jobs = []
    for entry in catalog["cases"]:
        case_type = entry["case_type"]
        seeds = list(entry.get("seeds", [101]))
        stress_factors = list(entry.get("stress_factors", [1.0]))
        if representatives_only:
            seeds = seeds[:1]
            stress_factors = stress_factors[:1]
        for seed in seeds:
            for sf in stress_factors:
                jobs.append(
                    {
                        "case_type": case_type,
                        "n_loops": int(entry.get("n_loops", 1)),
                        "seed": int(seed),
                        "stress_factor": float(sf),
                        "box": entry.get("box_size"),
                        "fov": entry.get("fov"),
                        "max_step": entry.get("max_step", defaults.get("max_step")),
                        "write_freq": entry.get("write_freq", defaults.get("write_freq")),
                        "print_freq": entry.get("print_freq", defaults.get("print_freq")),
                    }
                )
    return jobs


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--catalog",
        type=Path,
        default=CONFIGS_DIR / "case_catalog.yaml",
        help="Case catalog YAML",
    )
    p.add_argument(
        "--representatives-only",
        action="store_true",
        help="Run one seed/stress per major case type",
    )
    p.add_argument(
        "--case-type",
        action="append",
        default=None,
        help="Filter to one or more case types (repeatable)",
    )
    p.add_argument("--cases-root", type=Path, default=CASES_DIR)
    p.add_argument("--skip-viz", action="store_true")
    p.add_argument("--continue-on-error", action="store_true")
    args = p.parse_args(argv)

    ensure_imports()
    catalog = load_yaml(args.catalog)
    jobs = expand_catalog(catalog, representatives_only=args.representatives_only)
    if args.case_type:
        allow = set(args.case_type)
        jobs = [j for j in jobs if j["case_type"] in allow]

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    failures = []
    for i, job in enumerate(jobs, 1):
        print(f"\n=== [{i}/{len(jobs)}] {job} ===", flush=True)
        try:
            case_dir = build_and_run(
                case_type=job["case_type"],
                n_loops=job["n_loops"],
                seed=job["seed"],
                stress_factor=job["stress_factor"],
                box=job.get("box"),
                fov=job.get("fov"),
                max_step=job.get("max_step"),
                write_freq=job.get("write_freq"),
                print_freq=job.get("print_freq"),
                cases_root=args.cases_root,
                skip_viz=args.skip_viz,
            )
            results.append({"job": job, "case_dir": str(case_dir), "status": "success"})
            print(f"SUCCESS {case_dir}", flush=True)
        except Exception as exc:
            failures.append({"job": job, "error": str(exc)})
            results.append({"job": job, "status": "failed", "error": str(exc)})
            print(f"FAILED {job}: {exc}", flush=True)
            if not args.continue_on_error:
                break

    summary = {
        "n_jobs": len(jobs),
        "n_success": sum(1 for r in results if r["status"] == "success"),
        "n_failed": len(failures),
        "results": results,
        "major_categories_covered": sorted(
            {r["job"]["case_type"] for r in results if r["status"] == "success"}
        ),
    }
    out = ARTIFACTS_DIR / "generation_summary.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {out}")
    print(
        f"Success {summary['n_success']}/{summary['n_jobs']}; "
        f"categories: {summary['major_categories_covered']}"
    )
    # Require every major category if running representatives
    if args.representatives_only and not args.case_type:
        missing = [c for c in MAJOR_CATEGORIES if c not in summary["major_categories_covered"]]
        if missing:
            print(f"Missing major categories: {missing}", file=sys.stderr)
            return 2
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
