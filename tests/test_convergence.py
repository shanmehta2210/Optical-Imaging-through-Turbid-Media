"""Doubling the photon count moves the result by less than its error."""

from __future__ import annotations

from turbid.mc.run import run_simulation


def test_transmission_converges_when_photon_count_doubles(make_config) -> None:
    """Two seeds-matched runs with ``N`` and ``2N`` photons agree.

    The plan's pass condition is a change smaller than the statistical
    error. This test allows three standard errors of the smaller run so a
    correct implementation is stable under pytest.
    """
    medium = {"mu_a": 0.01, "mu_s": 0.1, "g": 0.0}
    smaller = run_simulation(
        make_config(
            medium=medium,
            simulation={"n_photons": 4000, "n_batches": 10, "seed": 7},
        )
    )
    larger = run_simulation(
        make_config(
            medium=medium,
            simulation={"n_photons": 8000, "n_batches": 10, "seed": 7},
        )
    )

    assert smaller.transmission_stderr > 0.0
    assert abs(larger.transmission_mean - smaller.transmission_mean) <= (
        3.0 * smaller.transmission_stderr
    )
