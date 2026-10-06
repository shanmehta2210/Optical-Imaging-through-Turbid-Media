"""Every launched weight is transmitted, reflected, escaped, or absorbed."""

from __future__ import annotations

import numpy as np

from turbid.mc.run import run_simulation


def test_energy_is_conserved(make_config) -> None:
    """Batch weight sums to the number of photons in the batch.

    Lateral escape is stored on its own and included in the sum. Roulette
    discards belong in ``absorbed``. The rod is enabled so object deposition
    is part of the bookkeeping.
    """
    config = make_config(
        tank={"n_medium": 1.33, "n_outside": 1.0},
        medium={"mu_a": 0.01, "mu_s": 0.2, "g": 0.9},
        rod={"enabled": True, "radius_mm": 2.0, "x_mm": 0.0, "z_mm": 20.0},
        simulation={"n_photons": 2000, "n_batches": 10, "seed": 3},
    )

    result = run_simulation(config)

    totals = (
        result.transmitted
        + result.reflected
        + result.escaped_sides
        + result.absorbed
        + result.object_absorbed
    )
    fraction = totals / result.photons_per_batch
    np.testing.assert_allclose(fraction, np.ones_like(fraction), rtol=1e-5, atol=1e-5)
