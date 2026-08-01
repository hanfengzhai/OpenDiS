#!/usr/bin/env python3
"""Render the evolution video and initial/final snapshots for one case.

Usage:
    python3 visualize_case.py CASE_DIR
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ddd_dataset.visualize import visualize_case


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case_dir")
    args = ap.parse_args()
    out = visualize_case(args.case_dir)
    for k, v in out.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
