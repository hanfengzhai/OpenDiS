#!/usr/bin/env python3
"""Generate, run and visualize the full dataset suite (or a subset).

Usage:
    python3 run_suite.py [--out DIR] [--only NAME_SUBSTR] [--skip-vis]
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ddd_dataset.suite import build_suite
from ddd_dataset.runner import run_case, _dump_json
from ddd_dataset.visualize import visualize_case

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "dataset", "glissile_loops")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", default=None)
    ap.add_argument("--skip-vis", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    # 1) generate
    gen_cmd = [sys.executable,
               os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "generate_cases.py"), "--out", args.out]
    if args.only:
        gen_cmd += ["--only", args.only]
    subprocess.run(gen_cmd, check=True)

    cases = build_suite()
    if args.only:
        cases = [c for c in cases if args.only in c.name]

    # 2) run + 3) visualize
    results = {}
    for cfg in cases:
        case_dir = os.path.join(args.out, cfg.name)
        status = run_case(case_dir, force=args.force)
        results[cfg.name] = {"success": status["success"],
                             "steps": status["steps_completed"],
                             "wall_s": status["wall_time_s"],
                             "reason": status.get("termination_reason",
                                                  status.get("error"))}
        if status["success"] and not args.skip_vis:
            vis = visualize_case(case_dir)
            results[cfg.name]["video"] = vis["video"]

    # 4) summary
    summary_path = os.path.join(args.out, "suite_summary.json")
    _dump_json(results, summary_path)
    print("\n===== suite summary =====")
    for name, r in results.items():
        flag = "OK  " if r["success"] else "FAIL"
        print(f"[{flag}] {name}: steps={r['steps']} wall={r['wall_s']}s "
              f"({r['reason']})")
    print(f"summary written to {summary_path}")
    n_fail = sum(1 for r in results.values() if not r["success"])
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
