"""``χ²`` comparisons between measured profiles and Monte Carlo runs.

Profile coordinates are millimetres. ``μ_s′`` is mm^-1. ``χ²`` is
dimensionless.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray


class ChiSquared:
    """A ``χ²`` value and its degrees of freedom.

    Attributes
    ----------
    chi2 :
        Sum of squared residuals over the variance, dimensionless.
    dof :
        Number of points minus the number of fitted parameters.
    chi2_per_dof :
        ``chi2 / dof``, dimensionless.
    """

    def __init__(self, chi2: float, dof: int, chi2_per_dof: float) -> None:
        self.chi2 = chi2
        self.dof = dof
        self.chi2_per_dof = chi2_per_dof


class SpreadFit:
    """Grid fit of ``μ_s′`` to an exit-face radial profile.

    Attributes
    ----------
    mu_s_prime_per_mm :
        Best ``μ_s′`` in mm^-1.
    mu_s_prime_uncertainty_per_mm :
        Half-width of the region where ``χ²`` is within 1 of its minimum,
        in mm^-1.
    chi2_per_dof :
        ``χ²`` per degree of freedom at the minimum.
    grid_per_mm :
        ``μ_s′`` values that were simulated, in mm^-1.
    chi2 :
        ``χ²`` at each grid point, dimensionless, same length as the grid.
    """

    def __init__(
        self,
        mu_s_prime_per_mm: float,
        mu_s_prime_uncertainty_per_mm: float,
        chi2_per_dof: float,
        grid_per_mm: NDArray[np.float64],
        chi2: NDArray[np.float64],
    ) -> None:
        self.mu_s_prime_per_mm = mu_s_prime_per_mm
        self.mu_s_prime_uncertainty_per_mm = mu_s_prime_uncertainty_per_mm
        self.chi2_per_dof = chi2_per_dof
        self.grid_per_mm = grid_per_mm
        self.chi2 = chi2


def normalise_to_background(
    position_mm: NDArray[np.float64],
    intensity: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Divide a lateral profile by its far-from-rod background.

    Parameters
    ----------
    position_mm :
        Coordinate in millimetres.
    intensity :
        Counts or weight.

    Returns
    -------
    numpy.ndarray
        ``intensity / I_bg``, dimensionless. ``I_bg`` is the mean of the
        outer quarters of the span, as in :func:`turbid.analysis.metrics.shadow_contrast`.
    """
    raise NotImplementedError("normalise_to_background is not implemented")


def chi_squared(
    measured: NDArray[np.float64],
    predicted: NDArray[np.float64],
    sigma: NDArray[np.float64],
    n_parameters: int = 0,
) -> ChiSquared:
    """``χ²`` between two profiles that share a coordinate grid.

    Parameters
    ----------
    measured, predicted :
        Dimensionless profiles, already normalised to their own backgrounds
        when the comparison is a rod image. Same shape.
    sigma :
        One-standard-deviation uncertainty on ``measured``, same shape.
    n_parameters :
        Fitted parameters to subtract from the number of points. A pure
        comparison with no free parameters uses ``0``.

    Returns
    -------
    ChiSquared
        ``χ²``, degrees of freedom, and ``χ²`` per degree of freedom.
    """
    raise NotImplementedError("chi_squared is not implemented")


def fit_exit_spread(
    rho_mm: NDArray[np.float64],
    intensity: NDArray[np.float64],
    intensity_sigma: NDArray[np.float64],
    config: Mapping[str, Any],
    mu_s_prime_grid_per_mm: NDArray[np.float64],
    normalise_at_mm: float,
) -> SpreadFit:
    """Fit ``μ_s′`` to a measured pencil-beam exit profile.

    Parameters
    ----------
    rho_mm :
        Radial coordinate in millimetres.
    intensity :
        Measured azimuthal average, in counts.
    intensity_sigma :
        Uncertainty on ``intensity``, in counts.
    config :
        Simulation config used as the base. ``medium.mu_a`` stays fixed.
        Each grid point overwrites ``μ_s′`` and the ``g`` consistent with
        the already measured ``μ_s``.
    mu_s_prime_grid_per_mm :
        Trial values of ``μ_s′``, in mm^-1.
    normalise_at_mm :
        Radius, in millimetres, at which both the measured profile and each
        simulated profile are divided by their own value. The fit then sees
        the shape rather than the absolute power.

    Returns
    -------
    SpreadFit
        The minimising ``μ_s′``, its ``χ²``-rise uncertainty, and the curve
        of ``χ²`` on the grid. Refine the grid near the minimum before
        quoting the result.
    """
    raise NotImplementedError("fit_exit_spread is not implemented")


def fit_rod_profile(
    position_mm: NDArray[np.float64],
    measured: NDArray[np.float64],
    measured_sigma: NDArray[np.float64],
    predicted: NDArray[np.float64],
) -> ChiSquared:
    """``χ²`` between one measured rod profile and one prediction.

    Parameters
    ----------
    position_mm :
        Shared lateral coordinate in millimetres. Present so the caller
        records which grid was compared; the sum itself uses the arrays.
    measured, predicted :
        Profiles in counts and in weight. Each is normalised to its own
        background inside this function.
    measured_sigma :
        Uncertainty on the measured profile in counts, scaled by the same
        background factor as ``measured``.

    Returns
    -------
    ChiSquared
        Comparison with no free parameters (``n_parameters = 0``).
    """
    raise NotImplementedError("fit_rod_profile is not implemented")
