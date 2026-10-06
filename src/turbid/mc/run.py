"""Run a configured simulation in independent batches.

Batch means and their standard errors are the uncertainty the rest of the
project uses. Lengths in the returned histograms are millimetres. Optical
coefficients echoed on the result are mm^-1. Weights and reported fractions
are dimensionless.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray

from turbid.io.config import validate_config


class SimulationResult:
    """Tallies from a full run, with one standard error from the batch spread.

    Fractions (``transmission_mean`` and its siblings) are batch totals
    divided by ``photons_per_batch``, then averaged over batches. The
    matching ``*_stderr`` is the sample standard deviation of those batch
    fractions divided by ``sqrt(n_batches)`` (``ddof=1``).

    Histogram centres are millimetres. Histogram means are the same
    per-photon fractions: bin weight divided by ``photons_per_batch``,
    averaged over batches. Accepted-exit photons are the only ones in the
    histograms.

    ``escaped_sides`` is weight that leaves through a lateral wall. It is
    part of the energy sum

    ``transmitted + reflected + escaped_sides + absorbed + object_absorbed``.

    Attributes
    ----------
    seed, n_photons, n_batches, photons_per_batch :
        Bookkeeping. ``photons_per_batch * n_batches == n_photons``.
    g, mu_a, mu_s, mu_s_prime :
        Optical inputs actually used. ``g`` is dimensionless. The three
        coefficients are mm^-1.
    transmitted, reflected, escaped_sides, absorbed, object_absorbed,
    ballistic_transmitted :
        Per-batch sums of weight, each of shape ``(n_batches,)``.
    transmission_mean, transmission_stderr, reflection_mean, reflection_stderr,
    escape_mean, escape_stderr, absorption_mean, absorption_stderr,
    object_mean, object_stderr, ballistic_mean, ballistic_stderr :
        Per-photon fractions and their standard errors, dimensionless.
    lateral_x_mm, lateral_weight_mean, lateral_weight_stderr :
        Exit-face profile along ``x``.
    radial_rho_mm, radial_weight_mean, radial_weight_stderr :
        Exit-face radial profile.
    """

    def __init__(
        self,
        seed: int,
        n_photons: int,
        n_batches: int,
        photons_per_batch: int,
        g: float,
        mu_a: float,
        mu_s: float,
        mu_s_prime: float,
        transmitted: NDArray[np.float64],
        reflected: NDArray[np.float64],
        escaped_sides: NDArray[np.float64],
        absorbed: NDArray[np.float64],
        object_absorbed: NDArray[np.float64],
        ballistic_transmitted: NDArray[np.float64],
        transmission_mean: float,
        transmission_stderr: float,
        reflection_mean: float,
        reflection_stderr: float,
        escape_mean: float,
        escape_stderr: float,
        absorption_mean: float,
        absorption_stderr: float,
        object_mean: float,
        object_stderr: float,
        ballistic_mean: float,
        ballistic_stderr: float,
        lateral_x_mm: NDArray[np.float64],
        lateral_weight_mean: NDArray[np.float64],
        lateral_weight_stderr: NDArray[np.float64],
        radial_rho_mm: NDArray[np.float64],
        radial_weight_mean: NDArray[np.float64],
        radial_weight_stderr: NDArray[np.float64],
    ) -> None:
        self.seed = seed
        self.n_photons = n_photons
        self.n_batches = n_batches
        self.photons_per_batch = photons_per_batch
        self.g = g
        self.mu_a = mu_a
        self.mu_s = mu_s
        self.mu_s_prime = mu_s_prime
        self.transmitted = transmitted
        self.reflected = reflected
        self.escaped_sides = escaped_sides
        self.absorbed = absorbed
        self.object_absorbed = object_absorbed
        self.ballistic_transmitted = ballistic_transmitted
        self.transmission_mean = transmission_mean
        self.transmission_stderr = transmission_stderr
        self.reflection_mean = reflection_mean
        self.reflection_stderr = reflection_stderr
        self.escape_mean = escape_mean
        self.escape_stderr = escape_stderr
        self.absorption_mean = absorption_mean
        self.absorption_stderr = absorption_stderr
        self.object_mean = object_mean
        self.object_stderr = object_stderr
        self.ballistic_mean = ballistic_mean
        self.ballistic_stderr = ballistic_stderr
        self.lateral_x_mm = lateral_x_mm
        self.lateral_weight_mean = lateral_weight_mean
        self.lateral_weight_stderr = lateral_weight_stderr
        self.radial_rho_mm = radial_rho_mm
        self.radial_weight_mean = radial_weight_mean
        self.radial_weight_stderr = radial_weight_stderr


def run_simulation(config: Mapping[str, Any]) -> SimulationResult:
    """Run the Monte Carlo described by ``config``.

    Parameters
    ----------
    config :
        Mapping with the blocks documented on
        :func:`turbid.io.config.load_config`. Lengths in millimetres,
        coefficients in mm^-1, acceptance angle in radians.

    Returns
    -------
    SimulationResult
        Batch totals, per-photon means, and standard errors.

    Notes
    -----
    Photons are split into ``simulation.n_batches`` equal batches. Batch
    ``i`` is seeded from ``numpy.random.SeedSequence(simulation.seed).spawn(n_batches)[i]``,
    so the batches are independent and the whole run repeats when the seed
    is fixed. A progress bar over batches belongs here (``tqdm``).

    The standard error is the batch-to-batch scatter of the per-photon
    fraction, divided by ``sqrt(n_batches)``.
    """
    validate_config(config)
    raise NotImplementedError("run_simulation physics is not implemented")
