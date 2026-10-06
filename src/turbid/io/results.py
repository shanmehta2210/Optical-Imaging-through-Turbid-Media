"""Save a run next to the config and seed that produced it.

``results.npz`` holds the tallies. ``config.yaml`` is a copy of the mapping
that was executed. ``seed.txt`` repeats ``simulation.seed`` so it can be
read without opening the archive. Outputs under ``data/raw`` are refused.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import yaml

from turbid.analysis.lookup import LookupTable
from turbid.mc.run import SimulationResult

_INT_FIELDS = ("seed", "n_photons", "n_batches", "photons_per_batch")
_ARRAY_FIELDS = (
    "transmitted",
    "reflected",
    "escaped_sides",
    "absorbed",
    "object_absorbed",
    "ballistic_transmitted",
    "lateral_x_mm",
    "lateral_weight_mean",
    "lateral_weight_stderr",
    "radial_rho_mm",
    "radial_weight_mean",
    "radial_weight_stderr",
)


def ensure_output_path_allowed(path: Path) -> None:
    """Refuse any path inside ``data/raw``.

    Parameters
    ----------
    path :
        File or directory about to be created.

    Raises
    ------
    ValueError
        ``path`` is ``data/raw`` or a file inside it. Raw frames are never
        modified.
    """
    resolved = path.resolve()
    for candidate in (resolved, *resolved.parents):
        if candidate.name == "raw" and candidate.parent.name == "data":
            raise ValueError(f"Refusing to write {path}: data/raw is never modified")


def save_results(
    directory: Path,
    result: SimulationResult,
    config: Mapping[str, Any],
) -> Path:
    """Write ``results.npz``, ``config.yaml``, and ``seed.txt``.

    Parameters
    ----------
    directory :
        Output directory, created if needed. A path inside ``data/raw`` is
        rejected.
    result :
        Tallies from :func:`turbid.mc.run.run_simulation`. Histogram
        coordinates in the archive are millimetres and coefficients are
        mm^-1.
    config :
        The mapping that was executed, including ``simulation.seed``.

    Returns
    -------
    pathlib.Path
        ``directory``.
    """
    ensure_output_path_allowed(directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload = {key: np.asarray(value) for key, value in vars(result).items()}
    np.savez_compressed(directory / "results.npz", **payload)
    with (directory / "config.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(dict(config), handle, sort_keys=False)
    (directory / "seed.txt").write_text(f"{result.seed}\n", encoding="utf-8")
    return directory


def load_results(directory: Path) -> tuple[SimulationResult, dict[str, Any]]:
    """Read a directory written by :func:`save_results`.

    Parameters
    ----------
    directory :
        Directory containing ``results.npz`` and ``config.yaml``.

    Returns
    -------
    tuple
        The simulation result and the config mapping.
    """
    archive = np.load(directory / "results.npz")
    code = SimulationResult.__init__.__code__
    parameter_names = code.co_varnames[1 : code.co_argcount]
    kwargs: dict[str, Any] = {}
    for key in parameter_names:
        value = archive[key]
        if key in _INT_FIELDS:
            kwargs[key] = int(np.asarray(value).item())
        elif key in _ARRAY_FIELDS:
            kwargs[key] = np.asarray(value, dtype=np.float64)
        else:
            kwargs[key] = float(np.asarray(value).item())
    with (directory / "config.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    return SimulationResult(**kwargs), config


def save_lookup(path: Path, table: LookupTable) -> None:
    """Write a lookup table as a compressed ``.npz``.

    Parameters
    ----------
    path :
        Destination file. A ``.npz`` suffix is added when it is missing.
        Paths inside ``data/raw`` are rejected.
    table :
        Profiles normalised to ``I_bg``. ``depth_mm``, ``diameter_mm``, and
        ``lateral_x_mm`` are millimetres.
    """
    ensure_output_path_allowed(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        depth_mm=np.asarray(table.depth_mm, dtype=np.float64),
        diameter_mm=np.asarray(table.diameter_mm, dtype=np.float64),
        lateral_x_mm=np.asarray(table.lateral_x_mm, dtype=np.float64),
        profiles=np.asarray(table.profiles, dtype=np.float64),
    )
