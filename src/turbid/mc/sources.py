"""Pencil and wide collimated sources on the entry face.

Positions are millimetres. Directions are dimensionless unit vectors.
Weights start at 1.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray


class Launch:
    """Initial states of a photon batch.

    Attributes
    ----------
    positions_mm :
        Shape ``(n_photons, 3)``, millimetres. Every photon starts at
        ``z = 0``.
    directions :
        Shape ``(n_photons, 3)``, dimensionless unit vectors. Collimated
        sources point along ``+z``, so each row is ``(0, 0, 1)``.
    weights :
        Shape ``(n_photons,)``, dimensionless, all ones.
    """

    def __init__(
        self,
        positions_mm: NDArray[np.float64],
        directions: NDArray[np.float64],
        weights: NDArray[np.float64],
    ) -> None:
        self.positions_mm = positions_mm
        self.directions = directions
        self.weights = weights


def pencil_beam(x_mm: float, y_mm: float, n_photons: int) -> Launch:
    """Launch a pencil beam along ``+z``.

    Parameters
    ----------
    x_mm, y_mm :
        Entry position in millimetres.
    n_photons :
        Number of photons. Each is an independent packet of weight 1.

    Returns
    -------
    Launch
        ``n_photons`` copies of the same position and direction.
    """
    raise NotImplementedError("pencil_beam is not implemented")


def wide_collimated_beam(
    x_mm: float,
    y_mm: float,
    x_half_width_mm: float,
    y_half_height_mm: float,
    n_photons: int,
    seed: int,
) -> Launch:
    """Launch a collimated beam uniform over a rectangle on ``z = 0``.

    Parameters
    ----------
    x_mm, y_mm :
        Centre of the rectangle in millimetres.
    x_half_width_mm, y_half_height_mm :
        Half-widths of the illuminated rectangle in millimetres. A photon's
        ``x`` is uniform on ``[x − Δx, x + Δx]``, and likewise for ``y``.
    n_photons :
        Number of photons.
    seed :
        Seed for the positions. Directions are all ``+z`` and are not random.

    Returns
    -------
    Launch
        Positions, ``+z`` directions, and unit weights.
    """
    raise NotImplementedError("wide_collimated_beam is not implemented")


def launch_from_config(source: dict[str, Any], n_photons: int, seed: int) -> Launch:
    """Build the launch described by a ``source`` config block.

    Parameters
    ----------
    source :
        The ``source`` mapping from a simulation config. ``type`` is
        ``"pencil"`` or ``"wide"``.
    n_photons :
        Photons in this batch, not in the whole run.
    seed :
        Used by the wide beam. The pencil beam ignores it.

    Returns
    -------
    Launch
        Initial photon states. Positions are in millimetres.
    """
    raise NotImplementedError("launch_from_config is not implemented")
