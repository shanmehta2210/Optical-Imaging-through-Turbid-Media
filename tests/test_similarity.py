"""Equal ``μ_s′`` gives equal diffuse transmission deep in the slab."""

from __future__ import annotations

import math

from turbid.mc.run import run_simulation


def test_similarity_relation_at_equal_mu_s_prime(make_config) -> None:
    """``g = 0`` and ``g = 0.9`` agree when ``μ_s′`` and the thickness match.

    ``μ_a = 0``, so the transport mean free path is ``1 / μ_s′``. The tank is
    index-matched and at least 10 transport mean free paths long. Agreement
    is judged on total exit-face transmission, within three standard errors
    of the two batch estimates combined.
    """
    length_mm = 20.0
    mu_s_prime = 0.5
    assert length_mm * mu_s_prime >= 10.0

    isotropic = make_config(
        tank={"length_mm": length_mm},
        medium={"mu_a": 0.0, "mu_s": mu_s_prime, "g": 0.0},
    )
    forward = make_config(
        tank={"length_mm": length_mm},
        medium={"mu_a": 0.0, "mu_s": mu_s_prime / (1.0 - 0.9), "g": 0.9},
    )
    assert isotropic["tank"]["n_medium"] == isotropic["tank"]["n_outside"]

    slow = run_simulation(isotropic)
    fast = run_simulation(forward)

    tolerance = 3.0 * math.hypot(slow.transmission_stderr, fast.transmission_stderr)
    assert abs(slow.transmission_mean - fast.transmission_mean) <= tolerance
    assert slow.transmission_mean > slow.ballistic_mean
    assert fast.ballistic_mean < 1e-6
