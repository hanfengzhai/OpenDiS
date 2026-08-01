#!/usr/bin/env python3
"""Run a single case (invoked as subprocess by generate_dataset.py)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from NyeDiffusion.data_ddd.simulator import run_case


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--visualize", action="store_true")
    args = parser.parse_args()

    with open(args.case_dir / "config.yaml") as f:
        cfg = yaml.safe_load(f)

    result = run_case(cfg, args.case_dir)
    out = {"simulation": result}

    if result.get("success") and args.visualize:
        # Visualize in a fresh subprocess (Kokkos cannot re-initialize after finalize)
        import subprocess
        viz_cmd = [
            sys.executable, "-c",
            f"import sys; sys.path.insert(0, '{ROOT}'); "
            "from NyeDiffusion.data_ddd.visualize import visualize_case; "
            f"print(visualize_case('{args.case_dir}'))",
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = ":".join([
            str(ROOT / "core" / "exadis" / "python"),
            str(ROOT / "core" / "pydis" / "python"),
            str(ROOT / "python"),
            str(ROOT),
            env.get("PYTHONPATH", ""),
        ])
        viz_proc = subprocess.run(viz_cmd, capture_output=True, text=True, env=env)
        if viz_proc.returncode == 0:
            out["visualization"] = viz_proc.stdout.strip()
        else:
            out["visualization_error"] = viz_proc.stderr or viz_proc.stdout

    print(json.dumps(out, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
