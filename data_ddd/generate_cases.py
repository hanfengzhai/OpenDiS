#!/usr/bin/env python3
"""Generate the dataset case directories (config + initial geometry +
pre-run validation) without running the simulations.

Usage:
    python3 generate_cases.py [--out DIR] [--only NAME_SUBSTR]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ddd_dataset.suite import build_suite
from ddd_dataset.geometry import build_network
from ddd_dataset.validate import validate_case
from ddd_dataset.runner import _dump_json

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "dataset", "glissile_loops")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", default=None,
                    help="only generate cases whose name contains this string")
    args = ap.parse_args()

    cases = build_suite()
    if args.only:
        cases = [c for c in cases if args.only in c.name]

    print(f"generating {len(cases)} cases under {args.out}")
    n_fail = 0
    for cfg in cases:
        case_dir = os.path.join(args.out, cfg.name)
        os.makedirs(case_dir, exist_ok=True)
        cfg.save(os.path.join(case_dir, "config.json"))
        net = build_network(cfg)
        net.write_json(os.path.join(case_dir, "initial_network.json"))
        report = validate_case(net, cfg)
        _dump_json(report, os.path.join(case_dir, "validation.json"))
        ok = "OK " if report["passed"] else "FAIL"
        if not report["passed"]:
            n_fail += 1
            failed = [k for k, v in report["checks"].items()
                      if not v["passed"]]
            print(f"  [{ok}] {cfg.name}  failed checks: {failed}")
        else:
            print(f"  [{ok}] {cfg.name}  "
                  f"({len(cfg.loops)} loops, {len(cfg.lines)} lines)")
    if n_fail:
        print(f"{n_fail} cases failed pre-run validation")
        sys.exit(1)
    print("all cases valid")


if __name__ == "__main__":
    main()
