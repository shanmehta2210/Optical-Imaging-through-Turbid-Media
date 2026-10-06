"""Rectangular tank and an opaque cylinder infinite along ``y``.

Lengths are millimetres. Direction cosines and face normals are
dimensionless. Keep the numeric functions free of dataclasses so a Numba
loop in :mod:`turbid.mc.transport` can call them.

Coordinate system, matching the lab plan:

- ``z = 0`` is the entry face and ``z = length`` is the exit face.
- ``x`` spans ``[-width/2, width/2]``.
- ``y`` spans ``[-height/2, height/2]``.
- The rod is an infinite cylinder along ``y``, centred at ``(x, z)``.
"""

from __future__ import annotations

CYLINDER_FACE_ID: int = 6

_FACE_NORMALS: dict[int, tuple[float, float, float]] = {
    0: (0.0, 0.0, -1.0),
    1: (0.0, 0.0, 1.0),
    2: (-1.0, 0.0, 0.0),
    3: (1.0, 0.0, 0.0),
    4: (0.0, -1.0, 0.0),
    5: (0.0, 1.0, 0.0),
}


def face_outward_normal(face_id: int) -> tuple[float, float, float]:
    """Outward unit normal of a tank face.

    Parameters
    ----------
    face_id :
        ``0`` entry (``z = 0``), ``1`` exit (``z = L``), ``2`` ``−x``,
        ``3`` ``+x``, ``4`` ``−y``, ``5`` ``+y``. The cylinder uses
        :data:`CYLINDER_FACE_ID` and :func:`cylinder_outward_normal`.

    Returns
    -------
    tuple of float
        ``(nx, ny, nz)``, dimensionless and of unit length.
    """
    try:
        return _FACE_NORMALS[face_id]
    except KeyError as exc:
        raise ValueError(f"Unknown tank face id {face_id}") from exc


def tank_intersection_mm(
    x_mm: float,
    y_mm: float,
    z_mm: float,
    ux: float,
    uy: float,
    uz: float,
    length_mm: float,
    width_mm: float,
    height_mm: float,
) -> tuple[float, int]:
    """Distance from a point inside the tank to the next wall.

    Parameters
    ----------
    x_mm, y_mm, z_mm :
        Ray origin in millimetres.
    ux, uy, uz :
        Unit direction, dimensionless.
    length_mm, width_mm, height_mm :
        Tank size along ``z``, ``x``, and ``y``, in millimetres.

    Returns
    -------
    tuple
        ``(distance_mm, face_id)``. ``distance_mm`` is positive. Face ids
        are the ones accepted by :func:`face_outward_normal`.

    Notes
    -----
    Ignore hits at or behind the origin. A photon that has just reflected
    sits on a wall; the caller is responsible for nudging it off that wall
    before the next query so the same face is not hit at distance zero.
    """
    raise NotImplementedError("tank_intersection_mm is not implemented")


def cylinder_intersection_mm(
    x_mm: float,
    y_mm: float,
    z_mm: float,
    ux: float,
    uy: float,
    uz: float,
    radius_mm: float,
    center_x_mm: float,
    center_z_mm: float,
) -> float:
    """Distance to the opaque rod, or ``inf`` on a miss.

    Parameters
    ----------
    x_mm, y_mm, z_mm :
        Ray origin in millimetres. ``y_mm`` does not enter the hit test.
    ux, uy, uz :
        Unit direction, dimensionless. ``uy`` does not enter the hit test.
    radius_mm :
        Rod radius in millimetres.
    center_x_mm, center_z_mm :
        Axis position in millimetres. The axis is parallel to ``y``.

    Returns
    -------
    float
        Smallest positive distance in millimetres, or ``math.inf`` when the
        ray misses the cylinder or starts inside it.

    Notes
    -----
    Solve the quadratic in the path length ``s`` (millimetres)

    .. math::

        (x - x_0 + s\\, u_x)^2 + (z - z_0 + s\\, u_z)^2 = a^2.

    The rod is opaque: the caller deposits the photon's remaining weight
    and ends the photon. There is no refraction at the rod surface.
    """
    raise NotImplementedError("cylinder_intersection_mm is not implemented")


def cylinder_outward_normal(
    x_mm: float,
    z_mm: float,
    center_x_mm: float,
    center_z_mm: float,
) -> tuple[float, float, float]:
    """Unit normal pointing out of the rod at a surface point.

    Parameters
    ----------
    x_mm, z_mm :
        Hit position in millimetres.
    center_x_mm, center_z_mm :
        Axis position in millimetres.

    Returns
    -------
    tuple of float
        ``(nx, 0, nz)``, dimensionless. The ``y`` component is zero because
        the cylinder is invariant along ``y``.
    """
    raise NotImplementedError("cylinder_outward_normal is not implemented")


def next_surface_mm(
    x_mm: float,
    y_mm: float,
    z_mm: float,
    ux: float,
    uy: float,
    uz: float,
    length_mm: float,
    width_mm: float,
    height_mm: float,
    rod_enabled: bool,
    rod_radius_mm: float,
    rod_x_mm: float,
    rod_z_mm: float,
) -> tuple[float, int]:
    """Nearest forward surface: a tank wall, or the rod when it is closer.

    Parameters
    ----------
    x_mm, y_mm, z_mm :
        Ray origin in millimetres.
    ux, uy, uz :
        Unit direction, dimensionless.
    length_mm, width_mm, height_mm :
        Tank size in millimetres.
    rod_enabled :
        When false, the cylinder is ignored.
    rod_radius_mm, rod_x_mm, rod_z_mm :
        Cylinder radius and axis position in millimetres.

    Returns
    -------
    tuple
        ``(distance_mm, face_id)``. A cylinder hit uses
        :data:`CYLINDER_FACE_ID`.
    """
    raise NotImplementedError("next_surface_mm is not implemented")
