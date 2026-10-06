"""Pure absorber: transmitted fraction matches the Beer–Lambert law."""

from __future__ import annotations

import math

from turbid.mc.run import run_simulation


def test_pure_absorber_matches_beer_lambert(make_config) -> None:
    """Index-matched slab with ``μ_s = 0`` transmits ``exp(-μ_a L)``.

    Fresnel factors are 1 because the refractive indices match. Every
    transmitted photon is unscattered, so the ballistic fraction equals the
    transmitted fraction.
    """
    mu_a = 0.05
    config = make_config(medium={"mu_a": mu_a, "mu_s": 0.0})
    assert config["tank"]["n_medium"] == config["tank"]["n_outside"]
    length_mm = float(config["tank"]["length_mm"])
    expected = math.exp(-mu_a * length_mm)

    result = run_simulation(config)

    assert result.transmission_stderr > 0.0
    assert abs(result.transmission_mean - expected) <= 3.0 * result.transmission_stderr
    assert abs(result.ballistic_mean - result.transmission_mean) <= 1e-9
