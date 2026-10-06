"""A rod in a clear tank casts a geometric shadow of width ``2a``."""

from __future__ import annotations

import numpy as np

from turbid.mc.run import run_simulation


def test_clear_medium_shadow_has_width_2a(make_config) -> None:
    """With ``μ_a = μ_s = 0``, bins fully inside the rod are dark.

    The source is a wide collimated beam, so the shadow on the exit face is
    a strip of width ``2a`` independent of depth. Bins that straddle the
    geometric edge are excluded. Bins fully outside the rod and inside the
    beam carry weight.
    """
    radius_mm = 2.0
    half_width_mm = 10.0
    config = make_config(
        medium={"mu_a": 0.0, "mu_s": 0.0},
        source={
            "type": "wide",
            "x_mm": 0.0,
            "y_mm": 0.0,
            "x_half_width_mm": half_width_mm,
            "y_half_height_mm": half_width_mm,
        },
        rod={"enabled": True, "radius_mm": radius_mm, "x_mm": 0.0, "z_mm": 20.0},
        detector={
            "lateral_x_min_mm": -half_width_mm,
            "lateral_x_max_mm": half_width_mm,
            "lateral_n_bins": 40,
        },
    )
    assert config["tank"]["n_medium"] == config["tank"]["n_outside"]

    result = run_simulation(config)

    position_mm = result.lateral_x_mm
    weight = result.lateral_weight_mean
    bin_width_mm = float(position_mm[1] - position_mm[0])
    inside = np.abs(position_mm) <= radius_mm - bin_width_mm
    outside = (np.abs(position_mm) >= radius_mm + bin_width_mm) & (
        np.abs(position_mm) <= half_width_mm - bin_width_mm
    )
    assert inside.any()
    assert outside.any()
    np.testing.assert_allclose(weight[inside], 0.0, atol=1e-12)
    assert np.all(weight[outside] > 0.0)
