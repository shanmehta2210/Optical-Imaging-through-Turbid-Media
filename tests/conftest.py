"""Shared config factory for the validation tests."""

from __future__ import annotations

import copy
from typing import Any

import pytest

BASELINE: dict[str, Any] = {
    "tank": {
        "length_mm": 40.0,
        "width_mm": 80.0,
        "height_mm": 80.0,
        "n_medium": 1.0,
        "n_outside": 1.0,
    },
    "medium": {
        "mu_a": 0.05,
        "mu_s": 0.0,
    },
    "source": {
        "type": "pencil",
        "x_mm": 0.0,
        "y_mm": 0.0,
    },
    "rod": {
        "enabled": False,
        "radius_mm": 2.0,
        "x_mm": 0.0,
        "z_mm": 20.0,
    },
    "detector": {
        "acceptance_half_angle_rad": 0.2,
        "lateral_x_min_mm": -20.0,
        "lateral_x_max_mm": 20.0,
        "lateral_n_bins": 80,
        "radial_rho_max_mm": 20.0,
        "radial_n_bins": 40,
    },
    "simulation": {
        "n_photons": 20000,
        "n_batches": 10,
        "seed": 12345,
        "weight_threshold": 1.0e-4,
        "roulette_survival": 0.1,
    },
}


def _merge(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@pytest.fixture
def make_config():
    """Return a config dict, with ``BASELINE`` updated by keyword blocks."""

    def factory(**overrides: Any) -> dict[str, Any]:
        return _merge(BASELINE, overrides)

    return factory
