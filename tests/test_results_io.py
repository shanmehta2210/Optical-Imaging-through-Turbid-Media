"""Round-trip of a simulation directory, and the raw-data guard."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from turbid.io.results import ensure_output_path_allowed, load_results, save_results
from turbid.mc.run import SimulationResult


def _result(seed: int = 7) -> SimulationResult:
    batches = np.array([10.0, 12.0], dtype=np.float64)
    lateral = np.linspace(-1.0, 1.0, 4)
    radial = np.linspace(0.25, 1.75, 4)
    zeros = np.zeros(4, dtype=np.float64)
    return SimulationResult(
        seed=seed,
        n_photons=20,
        n_batches=2,
        photons_per_batch=10,
        g=0.9,
        mu_a=1.0e-4,
        mu_s=0.5,
        mu_s_prime=0.05,
        transmitted=batches,
        reflected=np.zeros(2),
        escaped_sides=np.zeros(2),
        absorbed=np.array([10.0, 8.0]),
        object_absorbed=np.zeros(2),
        ballistic_transmitted=batches,
        transmission_mean=1.1,
        transmission_stderr=0.1,
        reflection_mean=0.0,
        reflection_stderr=0.0,
        escape_mean=0.0,
        escape_stderr=0.0,
        absorption_mean=0.9,
        absorption_stderr=0.1,
        object_mean=0.0,
        object_stderr=0.0,
        ballistic_mean=1.1,
        ballistic_stderr=0.1,
        lateral_x_mm=lateral,
        lateral_weight_mean=zeros,
        lateral_weight_stderr=zeros,
        radial_rho_mm=radial,
        radial_weight_mean=zeros,
        radial_weight_stderr=zeros,
    )


def test_results_round_trip(tmp_path: Path) -> None:
    config = {"simulation": {"seed": 7}, "medium": {"mu_s": 0.5}}
    save_results(tmp_path, _result(), config)
    loaded, loaded_config = load_results(tmp_path)
    assert loaded.seed == 7
    assert loaded.g == pytest.approx(0.9)
    assert loaded.mu_s_prime == pytest.approx(0.05)
    np.testing.assert_allclose(loaded.transmitted, [10.0, 12.0])
    np.testing.assert_allclose(loaded.lateral_x_mm, np.linspace(-1.0, 1.0, 4))
    assert loaded_config["simulation"]["seed"] == 7
    assert (tmp_path / "seed.txt").read_text(encoding="utf-8").strip() == "7"
    assert (tmp_path / "config.yaml").is_file()


def test_raw_directory_is_not_writable() -> None:
    with pytest.raises(ValueError, match="data/raw"):
        ensure_output_path_allowed(Path("data") / "raw" / "frame.tif")
