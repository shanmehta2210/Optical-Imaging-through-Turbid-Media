"""Build a depth–diameter lookup table of simulated rod profiles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from turbid.analysis.lookup import build_lookup
from turbid.io.config import load_config
from turbid.io.results import save_lookup


def main(argv: list[str] | None = None) -> int:
    """Simulate the lookup table and write it as an ``.npz`` file."""
    parser = argparse.ArgumentParser(description="Build a rod-profile lookup table.")
    parser.add_argument("config", type=Path, help="Base YAML config.")
    parser.add_argument(
        "--depths-mm",
        type=float,
        nargs="+",
        required=True,
        help="Rod-centre depths along z, in millimetres.",
    )
    parser.add_argument(
        "--diameters-mm",
        type=float,
        nargs="+",
        required=True,
        help="Rod diameters, in millimetres.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Destination .npz path.")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    table = build_lookup(
        config,
        np.asarray(args.depths_mm, dtype=np.float64),
        np.asarray(args.diameters_mm, dtype=np.float64),
    )
    save_lookup(args.output, table)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
