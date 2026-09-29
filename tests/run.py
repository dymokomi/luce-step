#!/usr/bin/env python3
"""luce-step's gate: the Luce regressions in tests/, native and through the C backend.
They run in a scratch directory holding tests/fixtures and any generated ones."""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXE = ".exe" if os.name == "nt" else ""


def prepare(work):
    fixtures = work / "tests/fixtures"
    if (ROOT / "tests/fixtures").is_dir():
        shutil.copytree(ROOT / "tests/fixtures", fixtures)
    fixtures.mkdir(parents=True, exist_ok=True)
    generator = ROOT / "tests/generate_fixtures.py"
    if generator.exists():
        spec = importlib.util.spec_from_file_location("generate_fixtures", generator)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.write_fixtures(fixtures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(os.environ.get("LUCE_BASE", ROOT.parent / f"luce-base/build/luce-base{EXE}")))
    parser.add_argument("--luce", type=Path, default=Path(os.environ.get("LUCE", ROOT.parent / f"luce/build/luce{EXE}")))
    parser.add_argument("--opt", choices=["0", "1", "2", "3"], default="0")
    parser.add_argument("--backend", choices=["native", "c", "both"], default="both")
    args = parser.parse_args()
    backends = ["native", "c"] if args.backend == "both" else [args.backend]
    with tempfile.TemporaryDirectory(prefix="luce-step-tests-") as temporary:
        work = Path(temporary)
        prepare(work)
        env = dict(os.environ, LUCE_BASE=str(args.base.resolve()), LUCE_CACHE=str(work / "cache"))
        for backend in backends:
            flags = ["--native", "--opt", args.opt] if backend == "native" else ["--backend=c"] + (["--release"] if int(args.opt) >= 2 else [])
            print(f"TEST regressions {backend}", flush=True)
            binary = work / f"regressions{EXE}"
            subprocess.run([str(args.luce.resolve()), "build", str(ROOT / "tests/main.luc"), *flags, "-o", str(binary)],
                           check=True, env=env, timeout=600)
            subprocess.run([str(binary)], check=True, timeout=300, cwd=work)
    print("PASS luce-step", flush=True)


if __name__ == "__main__":
    main()
