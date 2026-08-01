#!/usr/bin/env python3
"""Run the DDD simulation for one generated case directory.

Usage:
    python3 run_case.py CASE_DIR [--force]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ddd_dataset.runner import run_case


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case_dir")
    ap.add_argument("--force", action="store_true",
                    help="re-run even if the case already succeeded")
    args = ap.parse_args()

    status = run_case(args.case_dir, force=args.force)
    print(f"{status['name']}: success={status['success']} "
          f"steps={status['steps_completed']} "
          f"wall={status['wall_time_s']}s "
          f"reason={status.get('termination_reason', status.get('error'))}")
    sys.exit(0 if status["success"] else 1)


if __name__ == "__main__":
    main()
