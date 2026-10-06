"""Exit-face tallies and the lens acceptance filter.

Positions and bin edges are millimetres. Direction cosines are
dimensionless. Histogram values are sums of photon weight (dimensionless).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def direction_accepted(
    ux: float,
    uy: float,
    uz: float,
    acceptance_half_angle_rad: float,
) -> bool:
    """Whether an exit direction falls inside the camera cone.

    Parameters
    ----------
    ux, uy, uz :
        Unit direction, dimensionless. The optical axis is ``+z``.
    acceptance_half_angle_rad :
        Half-angle of the lens cone in radians, approximately
        ``arctan(aperture radius / working distance)``. Measure this from
        the real aperture and working distance.

    Returns
    -------
    bool
        True when the angle between the direction and ``+z`` is smaller
        than ``acceptance_half_angle_rad``.
    """
    raise NotImplementedError("direction_accepted is not implemented")


def lateral_histogram(
    x_mm: NDArray[np.float64],
    weights: NDArray[np.float64],
    x_min_mm: float,
    x_max_mm: float,
    n_bins: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Bin accepted exit photons along ``x``.

    Parameters
    ----------
    x_mm :
        Exit ``x`` positions in millimetres, one per accepted photon.
    weights :
        Photon weights, dimensionless, same length as ``x_mm``.
    x_min_mm, x_max_mm :
        Histogram range in millimetres.
    n_bins :
        Number of equal bins.

    Returns
    -------
    tuple of numpy.ndarray
        Bin centres in millimetres, shape ``(n_bins,)``, and the total
        weight in each bin, shape ``(n_bins,)``.
    """
    raise NotImplementedError("lateral_histogram is not implemented")


def radial_histogram(
    x_mm: NDArray[np.float64],
    y_mm: NDArray[np.float64],
    weights: NDArray[np.float64],
    origin_x_mm: float,
    origin_y_mm: float,
    rho_max_mm: float,
    n_bins: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Azimuthally averaged exit profile about the beam centre.

    Parameters
    ----------
    x_mm, y_mm :
        Exit positions in millimetres.
    weights :
        Photon weights, dimensionless.
    origin_x_mm, origin_y_mm :
        Beam centre on the exit face, in millimetres. For a pencil beam
        this is the launch ``(x, y)``.
    rho_max_mm :
        Outer radius of the histogram in millimetres.
    n_bins :
        Number of equal bins in ``ρ``.

    Returns
    -------
    tuple of numpy.ndarray
        Bin centres of ``ρ = hypot(x − x0, y − y0)`` in millimetres, and
        the total weight in each bin.
    """
    raise NotImplementedError("radial_histogram is not implemented")


def filter_accepted_exits(
    positions_mm: NDArray[np.float64],
    directions: NDArray[np.float64],
    weights: NDArray[np.float64],
    n_scatters: NDArray[np.int64],
    acceptance_half_angle_rad: float,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.int64],
]:
    """Keep exit photons whose direction lies inside the lens cone.

    Parameters
    ----------
    positions_mm :
        Exit positions, shape ``(n, 3)``, millimetres.
    directions :
        Exit directions, shape ``(n, 3)``, dimensionless unit vectors.
    weights :
        Photon weights, shape ``(n,)``, dimensionless.
    n_scatters :
        Scatter counts, shape ``(n,)``. A zero marks a ballistic exit.
    acceptance_half_angle_rad :
        Lens half-angle in radians. The optical axis is ``+z``.

    Returns
    -------
    tuple of numpy.ndarray
        The accepted positions, directions, weights, and scatter counts,
        in that order, with the same units as the inputs.
    """
    raise NotImplementedError("filter_accepted_exits is not implemented")
