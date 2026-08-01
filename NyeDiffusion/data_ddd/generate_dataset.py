#!/usr/bin/env python3
"""Generate elasticity-enabled DDD glissile-loop datasets."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from NyeDiffusion.data_ddd.reference import make_case_config, save_case_config


def _case_dir_name(cfg: Dict[str, Any]) -> str:
    g = cfg["geometry"]
    s = cfg["loading"]["applied_stress"]
    stress_tag = f"sig{int(abs(s[5])/1e6)}MPa" if s[5] != 0 else "nostress"
    return (
        f"{g['case_type']}_n{g['num_loops']}_box{int(g['box_size'])}"
        f"_fov{int(g['field_of_view'])}_{stress_tag}_seed{g['seed']}"
    )


def load_manifest(path: Path) -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


def build_cases_from_manifest(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    cases = []
    for entry in manifest.get("representative_cases", []):
        cfg = make_case_config(
            case_type=entry["case_type"],
            num_loops=entry["num_loops"],
            seed=entry["seed"],
            stress_scale=entry.get("stress_scale", 1.0),
            fov=entry.get("field_of_view"),
            box_size=entry.get("box_size"),
            max_step=entry.get("max_step"),
        )
        cases.append(cfg)

    for entry in manifest.get("stress_perturbations", []):
        cfg = make_case_config("single_loop", 1, seed=entry["seed"],
                               stress_scale=entry["stress_scale"])
        cases.append(cfg)

    for entry in manifest.get("fov_variants", []):
        cfg = make_case_config("single_loop", 1, seed=entry["seed"],
                               fov=entry["field_of_view"])
        cases.append(cfg)

    return cases


def main():
    parser = argparse.ArgumentParser(description="Generate DDD glissile-loop datasets")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "dataset" / "glissile_loops" / "generated")
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).parent / "configs" / "representative_cases.yaml")
    parser.add_argument("--run", action="store_true", help="Run simulations")
    parser.add_argument("--visualize", action="store_true", help="Create videos")
    parser.add_argument("--case", type=str, default=None, help="Run single case type only")
    parser.add_argument("--max-step", type=int, default=None, help="Override max steps")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    cases = build_cases_from_manifest(manifest)
    if args.case:
        cases = [c for c in cases if c["geometry"]["case_type"] == args.case]
    if args.max_step:
        for c in cases:
            c["simulation"]["max_step"] = args.max_step

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = []

    for cfg in cases:
        name = _case_dir_name(cfg)
        case_dir = args.output_dir / name
        save_case_config(cfg, case_dir / "config.yaml")
        entry = {"name": name, "case_dir": str(case_dir), "generated": True}

        if args.run:
            print(f"\n=== Running {name} ===")
            cmd = [
                sys.executable,
                str(Path(__file__).parent / "run_single_case.py"),
                str(case_dir),
            ]
            if args.visualize:
                cmd.append("--visualize")
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.stdout.strip():
                try:
                    entry["run_output"] = json.loads(proc.stdout)
                    entry["simulation"] = entry["run_output"].get("simulation", {})
                    entry["visualization"] = entry["run_output"].get("visualization")
                except json.JSONDecodeError:
                    entry["stdout"] = proc.stdout
            if proc.returncode != 0:
                entry["simulation"] = {"success": False, "errors": [proc.stderr or proc.stdout]}
                print(proc.stderr or proc.stdout)

        summary.append(entry)

    summary_path = args.output_dir / "generation_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWrote {len(summary)} case configs to {args.output_dir}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
