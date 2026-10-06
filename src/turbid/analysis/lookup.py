"""Lookup table of rod profiles over depth and diameter.

Depths, diameters, and the lateral coordinate are millimetres. Stored
profiles are normalised to the background ``I_bg`` and are dimensionless.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray


class LookupTable:
    """Simulated lateral profiles on a depth–diameter grid.

    Attributes
    ----------
    depth_mm :
        Rod-centre depths, shape ``(n_depth,)``, millimetres, increasing.
    diameter_mm :
        Rod diameters, shape ``(n_diameter,)``, millimetres, increasing.
    lateral_x_mm :
        Shared profile coordinate, shape ``(n_bins,)``, millimetres.
    profiles :
        Normalised profiles, shape ``(n_depth, n_diameter, n_bins)``.
        Each profile is divided by its own far-field background.
    """

    def __init__(
        self,
        depth_mm: NDArray[np.float64],
        diameter_mm: NDArray[np.float64],
        lateral_x_mm: NDArray[np.float64],
        profiles: NDArray[np.float64],
    ) -> None:
        self.depth_mm = depth_mm
        self.diameter_mm = diameter_mm
        self.lateral_x_mm = lateral_x_mm
        self.profiles = profiles


class DepthInference:
    """Depth and diameter that minimise ``χ²``, with a ``χ² + 1`` range.

    Attributes
    ----------
    depth_mm, diameter_mm :
        Best estimates, in millimetres.
    depth_low_mm, depth_high_mm :
        Ends of the depth interval where ``χ²`` stays within 1 of the
        minimum, in millimetres. A front/back degeneracy shows up as a wide
        interval rather than as a small symmetric error bar.
    diameter_low_mm, diameter_high_mm :
        The same interval for diameter, in millimetres.
    chi2, chi2_per_dof :
        Fit quality at the minimum, dimensionless.
    """

    def __init__(
        self,
        depth_mm: float,
        depth_low_mm: float,
        depth_high_mm: float,
        diameter_mm: float,
        diameter_low_mm: float,
        diameter_high_mm: float,
        chi2: float,
        chi2_per_dof: float,
    ) -> None:
        self.depth_mm = depth_mm
        self.depth_low_mm = depth_low_mm
        self.depth_high_mm = depth_high_mm
        self.diameter_mm = diameter_mm
        self.diameter_low_mm = diameter_low_mm
        self.diameter_high_mm = diameter_high_mm
        self.chi2 = chi2
        self.chi2_per_dof = chi2_per_dof


def build_lookup(
    config: Mapping[str, Any],
    depth_mm: NDArray[np.float64],
    diameter_mm: NDArray[np.float64],
) -> LookupTable:
    """Simulate a normalised rod profile at every depth and diameter.

    Parameters
    ----------
    config :
        Base simulation config. Each run overwrites the rod depth, the rod
        diameter (twice the radius), and enables the rod. Other optical
        inputs stay at the Part A values.
    depth_mm :
        Centre depths along ``z``, in millimetres.
    diameter_mm :
        Diameters, in millimetres.

    Returns
    -------
    LookupTable
        Profiles normalised to ``I_bg``. Linear interpolation in
        :func:`interpolate_profile` is only trustworthy after a few extra
        direct runs, off the grid, agree with the interpolated curve.
    """
    raise NotImplementedError("build_lookup is not implemented")


def interpolate_profile(
    table: LookupTable,
    depth_mm: float,
    diameter_mm: float,
) -> NDArray[np.float64]:
    """Linearly interpolate a normalised profile between grid nodes.

    Parameters
    ----------
    table :
        Table from :func:`build_lookup`.
    depth_mm :
        Query depth in millimetres. Must lie inside the table's depth range.
    diameter_mm :
        Query diameter in millimetres. Must lie inside the table's diameter
        range.

    Returns
    -------
    numpy.ndarray
        Interpolated profile, shape ``(n_bins,)``, dimensionless.
    """
    raise NotImplementedError("interpolate_profile is not implemented")


def infer_depth(
    table: LookupTable,
    position_mm: NDArray[np.float64],
    measured: NDArray[np.float64],
    measured_sigma: NDArray[np.float64],
    opposite_measured: NDArray[np.float64] | None = None,
    opposite_sigma: NDArray[np.float64] | None = None,
) -> DepthInference:
    """Infer rod depth and diameter by minimising ``χ²`` on the table.

    Parameters
    ----------
    table :
        Lookup table. Its ``lateral_x_mm`` grid is the coordinate the
        measured profile is compared on; resample ``measured`` onto it
        before the sum.
    position_mm :
        Coordinate of ``measured``, in millimetres.
    measured :
        Measured lateral profile in counts, not yet normalised.
    measured_sigma :
        One-standard-deviation uncertainty on ``measured``, in counts.
    opposite_measured, opposite_sigma :
        Optional second profile taken after rotating the tank by 180°.
        When they are present, ``χ²`` is the sum of the two views. That is
        the measurement that breaks a front/back degeneracy.

    Returns
    -------
    DepthInference
        The minimising depth and diameter, and the interval on which ``χ²``
        rises by 1 above that minimum.
    """
    raise NotImplementedError("infer_depth is not implemented")
