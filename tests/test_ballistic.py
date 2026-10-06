"""Unscattered transmission equals ``exp(-μ_t L)``."""

from __future__ import annotations

import math

from turbid.mc.run import run_simulation


def test_ballistic_fraction_matches_beer_lambert(make_config) -> None:
    """The weight that exits with zero scatters is ``exp(-(μ_a + μ_s) L)``.

    The tank is index-matched, so a Fresnel reflection does not remove
    ballistic photons. Scattered light may still leave the exit face; that
    weight is transmission and is not part of the ballistic tally.
    """
    mu_a = 0.01
    mu_s = 0.1
    config = make_config(medium={"mu_a": mu_a, "mu_s": mu_s, "g": 0.9})
    assert config["tank"]["n_medium"] == config["tank"]["n_outside"]
    length_mm = float(config["tank"]["length_mm"])
    expected = math.exp(-(mu_a + mu_s) * length_mm)

    result = run_simulation(config)

    assert result.ballistic_stderr > 0.0
    assert abs(result.ballistic_mean - expected) <= 3.0 * result.ballistic_stderr
