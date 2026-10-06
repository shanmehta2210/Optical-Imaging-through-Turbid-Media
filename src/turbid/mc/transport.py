"""One batch of the weighted photon walk.

The functions in this module are the ones to compile with ``numba.njit``
once the physics is in place. They take plain floats and arrays so the
compiled loop does not have to handle dataclasses.

Lengths are millimetres. Optical coefficients are mm^-1. Directions,
refractive indices, and weights are dimensionless. Angles passed as
``cosines`` are dimensionless; angles passed as angles are radians.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

DEFAULT_WEIGHT_THRESHOLD: float = 1e-4
DEFAULT_ROULETTE_SURVIVAL: float = 0.1


class BatchTallies:
    """Weight tallies for a single batch.

    Every total is a sum of photon weights, on the scale of the number of
    photons launched in the batch. Histogram arrays follow the binning in
    the detector config: centres in millimetres, values as weight per bin.

    Attributes
    ----------
    transmitted :
        Weight that leaves through the exit face (``+z``), before the
        acceptance-angle cut.
    reflected :
        Weight that leaves through the entry face (``−z``).
    escaped_sides :
        Weight that leaves through the four lateral faces.
    absorbed :
        Weight deposited in the medium, plus weight discarded by roulette.
    object_absorbed :
        Weight deposited in the rod.
    ballistic_transmitted :
        Subset of ``transmitted`` that crossed the tank with zero scatters.
    lateral_x_mm, lateral_weight :
        Accepted-exit histogram along ``x``. Centres in millimetres, weight
        per bin. The acceptance cut is applied only to histograms; rejected
        photons remain inside ``transmitted`` so the energy sum still closes.
    radial_rho_mm, radial_weight :
        Accepted-exit radial histogram. Centres in millimetres, weight per bin.
    """

    def __init__(
        self,
        transmitted: float,
        reflected: float,
        escaped_sides: float,
        absorbed: float,
        object_absorbed: float,
        ballistic_transmitted: float,
        lateral_x_mm: NDArray[np.float64],
        lateral_weight: NDArray[np.float64],
        radial_rho_mm: NDArray[np.float64],
        radial_weight: NDArray[np.float64],
    ) -> None:
        self.transmitted = transmitted
        self.reflected = reflected
        self.escaped_sides = escaped_sides
        self.absorbed = absorbed
        self.object_absorbed = object_absorbed
        self.ballistic_transmitted = ballistic_transmitted
        self.lateral_x_mm = lateral_x_mm
        self.lateral_weight = lateral_weight
        self.radial_rho_mm = radial_rho_mm
        self.radial_weight = radial_weight


def sample_step_mm(mu_t_per_mm: float, xi: float) -> float:
    """Free-path length ``s = −ln(ξ) / μ_t``.

    Parameters
    ----------
    mu_t_per_mm :
        Extinction coefficient ``μ_a + μ_s``, in mm^-1. Must be positive.
        The clear-medium case ``μ_t = 0`` is handled in
        :func:`simulate_batch`, not here.
    xi :
        Uniform random number on (0, 1]. A draw of 0 is undefined; replace
        it and draw again.

    Returns
    -------
    float
        Step length in millimetres. The mean of many draws is ``1 / μ_t``.
    """
    raise NotImplementedError("sample_step_mm is not implemented")


def fresnel_reflectance(
    cos_incident: float,
    n_incident: float,
    n_transmitted: float,
) -> float:
    """Unpolarised Fresnel reflectance of a wall.

    Parameters
    ----------
    cos_incident :
        Cosine of the angle between the photon direction and the outward
        wall normal. Dimensionless. Use the absolute value so a signed
        cosine is acceptable.
    n_incident :
        Refractive index of the medium the photon is in (the milk).
    n_transmitted :
        Refractive index beyond the wall (air). Glass walls are omitted.

    Returns
    -------
    float
        Reflectance in ``[0, 1]``, the average of the s and p Fresnel
        coefficients. Above the critical angle the reflectance is 1.

    Notes
    -----
    The walk keeps a single packet. Draw ``ξ`` uniform on (0, 1). Reflect
    specularly when ``ξ < R``; otherwise the packet crosses the wall and is
    tallied. The weight is unchanged. That sampling is unbiased for ``R``
    and keeps ``reflected + transmitted + escaped_sides + absorbed +
    object_absorbed`` equal to the launched weight.
    """
    raise NotImplementedError("fresnel_reflectance is not implemented")


def reflect_direction(
    ux: float,
    uy: float,
    uz: float,
    nx: float,
    ny: float,
    nz: float,
) -> tuple[float, float, float]:
    """Specular reflection of a unit direction in an outward unit normal.

    Parameters
    ----------
    ux, uy, uz :
        Incoming unit direction, dimensionless.
    nx, ny, nz :
        Outward unit normal, dimensionless.

    Returns
    -------
    tuple of float
        Reflected unit direction, dimensionless.
    """
    raise NotImplementedError("reflect_direction is not implemented")


def apply_roulette(
    weight: float,
    threshold: float,
    survival_probability: float,
    xi: float,
) -> float:
    """Apply Russian roulette to a low-weight packet.

    Parameters
    ----------
    weight :
        Current packet weight, dimensionless.
    threshold :
        Roulette starts when ``weight < threshold``. The plan uses ``1e-4``.
    survival_probability :
        Probability of keeping the packet. The plan uses ``0.1``. A survivor
        is multiplied by ``1 / survival_probability`` so the expected weight
        is unchanged.
    xi :
        Uniform random number on (0, 1), used only when the weight is below
        the threshold.

    Returns
    -------
    float
        The updated weight. ``0`` means the packet was terminated. The caller
        adds the pre-roulette weight to the absorbed tally in that case.
        A packet at or above the threshold is returned unchanged.
    """
    raise NotImplementedError("apply_roulette is not implemented")


def simulate_batch(
    positions_mm: NDArray[np.float64],
    directions: NDArray[np.float64],
    weights: NDArray[np.float64],
    mu_a_per_mm: float,
    mu_s_per_mm: float,
    g: float,
    tank_length_mm: float,
    tank_width_mm: float,
    tank_height_mm: float,
    n_medium: float,
    n_outside: float,
    rod_enabled: bool,
    rod_radius_mm: float,
    rod_x_mm: float,
    rod_z_mm: float,
    acceptance_half_angle_rad: float,
    lateral_x_min_mm: float,
    lateral_x_max_mm: float,
    lateral_n_bins: int,
    radial_origin_x_mm: float,
    radial_origin_y_mm: float,
    radial_rho_max_mm: float,
    radial_n_bins: int,
    weight_threshold: float,
    roulette_survival: float,
    seed: int,
) -> BatchTallies:
    """Propagate one batch and return its tallies.

    Parameters
    ----------
    positions_mm :
        Shape ``(n, 3)``, launch positions in millimetres.
    directions :
        Shape ``(n, 3)``, unit directions, dimensionless.
    weights :
        Shape ``(n,)``, dimensionless launch weights.
    mu_a_per_mm, mu_s_per_mm :
        Absorption and scattering coefficients, mm^-1.
    g :
        Anisotropy, dimensionless, in ``(-1, 1)``. Unused when ``μ_s = 0``.
    tank_length_mm, tank_width_mm, tank_height_mm :
        Tank size in millimetres.
    n_medium, n_outside :
        Refractive indices, dimensionless.
    rod_enabled, rod_radius_mm, rod_x_mm, rod_z_mm :
        Opaque cylinder along ``y``. Lengths in millimetres.
    acceptance_half_angle_rad :
        Camera cone half-angle in radians. Applied only when filling
        histograms.
    lateral_x_min_mm, lateral_x_max_mm, lateral_n_bins :
        Lateral histogram, millimetres and a bin count.
    radial_origin_x_mm, radial_origin_y_mm, radial_rho_max_mm, radial_n_bins :
        Radial histogram about the beam centre. Lengths in millimetres.
    weight_threshold, roulette_survival :
        Russian-roulette settings. See :func:`apply_roulette`.
    seed :
        Seed for this batch only.

    Returns
    -------
    BatchTallies
        Weight sums and histograms. The five leaving channels
        (transmitted, reflected, escaped sides, absorbed, object) sum to
        the sum of the launch weights.

    Notes
    -----
    Per photon, in this order:

    1. Draw ``s = −ln(ξ) / μ_t`` with ``μ_t = μ_a + μ_s`` in mm^-1 and
       ``s`` in millimetres. When ``μ_t = 0`` there is no interaction:
       fly in a straight line to the next surface.
    2. Find the next tank wall or rod. If that distance is shorter than
       ``s``, the surface wins and the interaction in step 3 does not
       happen.
    3. Otherwise step ``s``, deposit ``w · μ_a / μ_t`` as absorbed, set
       ``w ← w · μ_s / μ_t``, and scatter with Henyey–Greenstein.
    4. A rod hit ends the photon. Add the remaining weight to
       ``object_absorbed``.
    5. A wall hit draws Fresnel reflection or transmission. Transmission
       tallies the weight and ends the photon. Reflection continues the
       walk. Count an exit through ``+z`` with zero scatters toward
       ``ballistic_transmitted``.
    6. When ``w < weight_threshold``, apply roulette.

    Compile the loop with Numba after the pure-Python version matches the
    validation tests. Histograms include only exit-face photons inside the
    acceptance cone.
    """
    raise NotImplementedError("simulate_batch is not implemented")
