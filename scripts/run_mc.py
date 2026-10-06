"""Run a photon-transport simulation from a YAML config."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from turbid.io.config import load_config
from turbid.io.results import save_results
from turbid.mc.run import run_simulation


def main(argv: list[str] | None = None) -> int:
    """Load a config, run the Monte Carlo, and write a directory under ``runs``.

    The photon loop is still a stub, so a valid config currently raises
    ``NotImplementedError`` after it has been checked.
    """
    parser = argparse.ArgumentParser(description="Run a Monte Carlo photon-transport simulation.")
    parser.add_argument("config", type=Path, help="YAML config. Lengths are mm, coefficients are mm^-1.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory. Default: runs/<config stem>_seed<seed>.",
    )
    args = parser.parse_args(argv)
    config = load_config(args.config)
    seed = int(config["simulation"]["seed"])
    output = args.output or Path("runs") / f"{args.config.stem}_seed{seed}"
    result = run_simulation(config)
    save_results(output, result, config)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
