"""Turn a camera frame into a lateral exit profile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from turbid.analysis.profiles import lateral_profile_from_image, load_image
from turbid.io.results import ensure_output_path_allowed


def main(argv: list[str] | None = None) -> int:
    """Dark-subtract a frame and write ``x_mm, intensity`` as CSV.

    The default destination is ``data/processed``. ``data/raw`` is rejected
    as an output.
    """
    parser = argparse.ArgumentParser(description="Average a rod image into a 1D profile.")
    parser.add_argument("image", type=Path, help="Camera frame. Read only.")
    parser.add_argument("--dark", type=Path, default=None, help="Dark frame at the same exposure.")
    parser.add_argument("--pixel-size-mm", type=float, required=True, help="Millimetres per pixel.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="CSV path. Default: data/processed/<image stem>_profile.csv.",
    )
    args = parser.parse_args(argv)
    output = args.output or Path("data") / "processed" / f"{args.image.stem}_profile.csv"
    ensure_output_path_allowed(output)
    image = load_image(args.image)
    dark = load_image(args.dark) if args.dark is not None else None
    position_mm, intensity = lateral_profile_from_image(image, args.pixel_size_mm, dark)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"x_mm": position_mm, "intensity": intensity}).to_csv(output, index=False)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
