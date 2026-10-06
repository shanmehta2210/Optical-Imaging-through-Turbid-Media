"""Shadow contrast and edge-blur width of a rod profile.

Positions are millimetres. Intensities may be camera counts or Monte Carlo
weights; both metrics are scale-free apart from the blur width.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def shadow_contrast(
    position_mm: NDArray[np.float64],
    intensity: NDArray[np.float64],
) -> float:
    """Contrast ``C = (I_bg − I_min) / I_bg``.

    Parameters
    ----------
    position_mm :
        Profile coordinate in millimetres, shape ``(n,)``. Used to decide
        which samples sit far from the shadow.
    intensity :
        Profile values, same length as ``position_mm``. Counts or weight.

    Returns
    -------
    float
        Dimensionless contrast in ``[0, 1]`` for a dark shadow on a bright
        background.

    Notes
    -----
    ``I_min`` is the minimum of ``intensity``. ``I_bg`` is the mean of the
    samples in the outer quarters of the ``position_mm`` span, which is the
    level far from a centred rod. The caller normalises nothing first.
    """
    raise NotImplementedError("shadow_contrast is not implemented")


def rise_distance_10_90_mm(
    position_mm: NDArray[np.float64],
    intensity: NDArray[np.float64],
) -> float:
    """Mean 10–90% edge width of a rod shadow.

    Parameters
    ----------
    position_mm :
        Profile coordinate in millimetres.
    intensity :
        Profile values, counts or weight.

    Returns
    -------
    float
        Mean of the two edges' 10–90% rise distances, in millimetres.
        Each edge is the span between the positions where the profile
        crosses ``I_min + 0.1 (I_bg − I_min)`` and
        ``I_min + 0.9 (I_bg − I_min)``. ``I_bg`` is defined as in
        :func:`shadow_contrast`.
    """
    raise NotImplementedError("rise_distance_10_90_mm is not implemented")


def edge_blur_sigma_mm(
    position_mm: NDArray[np.float64],
    intensity: NDArray[np.float64],
) -> float:
    """Gaussian ``σ`` of a step, fitted independently to each edge.

    Parameters
    ----------
    position_mm :
        Profile coordinate in millimetres.
    intensity :
        Profile values, counts or weight.

    Returns
    -------
    float
        Mean of the two edges' ``σ``, in millimetres. The model on one edge
        is a step from ``I_min`` to ``I_bg`` convolved with a normal
        distribution of width ``σ``.
    """
    raise NotImplementedError("edge_blur_sigma_mm is not implemented")
