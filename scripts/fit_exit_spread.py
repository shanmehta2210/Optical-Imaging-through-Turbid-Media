"""Fit μ_s′ to a measured pencil-beam exit profile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from turbid.analysis.fitting import fit_exit_spread
from turbid.io.config import load_config
from turbid.io.results import ensure_output_path_allowed


def main(argv: list[str] | None = None) -> int:
    """Grid-search ``μ_s′`` and write the best value plus the ``χ²`` curve.

    The measured profile CSV has columns ``rho_mm``, ``intensity``, and
    ``sigma``. ``μ_s′`` is in mm^-1.
    """
    parser = argparse.ArgumentParser(description="Fit reduced scattering to an exit-face profile.")
    parser.add_argument("config", type=Path, help="Base YAML config. mu_a stays fixed.")
    parser.add_argument("profile", type=Path, help="CSV with rho_mm, intensity, sigma.")
    parser.add_argument(
        "--mu-s-prime",
        type=float,
        nargs="+",
        required=True,
        help="Grid of mu_s_prime values, in mm^-1.",
    )
    parser.add_argument(
        "--normalise-at-mm",
        type=float,
        required=True,
        help="Radius at which measured and simulated profiles are scaled to 1.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Directory for the fit outputs.")
    args = parser.parse_args(argv)
    ensure_output_path_allowed(args.output)
    config = load_config(args.config)
    frame = pd.read_csv(args.profile)
    fit = fit_exit_spread(
        frame["rho_mm"].to_numpy(dtype=np.float64),
        frame["intensity"].to_numpy(dtype=np.float64),
        frame["sigma"].to_numpy(dtype=np.float64),
        config,
        np.asarray(args.mu_s_prime, dtype=np.float64),
        args.normalise_at_mm,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"mu_s_prime_per_mm": fit.grid_per_mm, "chi2": fit.chi2}).to_csv(
        args.output / "chi2_grid.csv",
        index=False,
    )
    (args.output / "fit.txt").write_text(
        (
            f"mu_s_prime_per_mm {fit.mu_s_prime_per_mm}\n"
            f"uncertainty_per_mm {fit.mu_s_prime_uncertainty_per_mm}\n"
            f"chi2_per_dof {fit.chi2_per_dof}\n"
        ),
        encoding="utf-8",
    )
    print(
        f"mu_s_prime = {fit.mu_s_prime_per_mm} ± {fit.mu_s_prime_uncertainty_per_mm} mm^-1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
