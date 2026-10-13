"""Capture a stack of frames using settings from a YAML file.

Usage (from the project root):
    python scripts/capture_yaml.py                      # uses configs/capture.yaml
    python scripts/capture_yaml.py configs/other.yaml   # any other settings file

Edit the YAML, run, repeat. Each run saves:
    data/raw/YYYYMMDD/<timestamp>_<name>.tif   uint16 stack (frames, H, W)
    data/raw/YYYYMMDD/<timestamp>_<name>.json  camera settings + your YAML
and appends one row to data/lab_log.csv.
Close the camera in Vimba X Viewer before running.
"""
import csv
import json
import queue
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import tifffile
import yaml
from vmbpy import FrameStatus, PixelFormat, VmbSystem
from vmbpy.camera import Camera
from vmbpy.frame import Frame
from vmbpy.stream import Stream

RAW_ROOT = Path("data/raw")
LOG = Path("data/lab_log.csv")
LOG_COLS = ["date", "time", "filename", "name", "sample", "concentration",
            "rod_depth_mm", "mode", "exposure_us", "frames", "nd_filters",
            "iris_mm", "temperature_C", "peak_counts", "saturated_fraction",
            "dark", "notes"]
FULL_SCALE = {"Mono8": 255, "Mono10": 1023, "Mono12": 4095, "Mono16": 65535}
REQUIRED = ["name", "exposure_us", "frames"]


def load_config(path):
    cfg = yaml.safe_load(Path(path).read_text()) or {}
    missing = [k for k in REQUIRED if cfg.get(k) in (None, "")]
    if missing:
        sys.exit(f"Config {path} is missing: {', '.join(missing)}")
    cfg.setdefault("pixel_format", "Mono12")
    cfg.setdefault("dark", False)
    return cfg


def try_set(cam, name, value, quiet=False):
    """Set a camera feature if it exists and is writable. Returns True on success."""
    try:
        cam.get_feature_by_name(name).set(value)
        return True
    except Exception as err:
        if not quiet:
            print(f"  note: could not set {name} ({err})")
        return False


def configure(cam, cfg):
    fmt_name = cfg["pixel_format"]
    fmt = getattr(PixelFormat, fmt_name, None)
    if fmt is None or fmt not in cam.get_pixel_formats():
        sys.exit(f"Pixel format {fmt_name} is not available on this camera.")
    cam.set_pixel_format(fmt)
    try_set(cam, "ExposureAuto", "Off")
    try_set(cam, "GainAuto", "Off")
    try_set(cam, "Gain", 0.0)
    try_set(cam, "LUTEnable", False)
    try_set(cam, "Gamma", 1.0)
    if cfg.get("black_level") is not None:
        try_set(cam, "BlackLevel", float(cfg["black_level"]))

    exp = cam.get_feature_by_name("ExposureTime")
    lo, hi = exp.get_range()
    if not lo <= float(cfg["exposure_us"]) <= hi:
        sys.exit(f"exposure_us {cfg['exposure_us']} outside camera range {lo:.1f}-{hi:.0f} us")
    exp.set(float(cfg["exposure_us"]))


def acquire(cam, n, exposure_us, attempts=3):
    """Grab n complete frames with one continuous stream.

    The camera is started once, frames arrive through a callback, and it is
    stopped once at the end. (get_frame and get_frame_generator both start and
    stop acquisition for every frame, which fails with InternalFault at long
    exposures.) MultiFrame mode makes the camera finish on its own before we
    stop it, so the stop never lands in the middle of an exposure.
    """
    wait_s = exposure_us / 1e6 + 5.0
    for attempt in range(1, attempts + 1):
        q, skipped = queue.Queue(), [0]

        # vmbpy type-checks the handler, so it needs exactly this signature
        def handler(c: Camera, stream: Stream, frame: Frame) -> None:
            if frame.get_status() == FrameStatus.Complete:
                q.put(frame.as_numpy_ndarray().squeeze().copy())
            else:
                skipped[0] += 1
            c.queue_frame(frame)

        extra = 3
        multi = try_set(cam, "AcquisitionMode", "MultiFrame", quiet=True) and \
            try_set(cam, "AcquisitionFrameCount", n + extra, quiet=True)
        frames = []
        try:
            cam.start_streaming(handler=handler, buffer_count=min(n + extra, 10))
            try:
                while len(frames) < n:
                    frames.append(q.get(timeout=wait_s))
                    print(f"\r  frame {len(frames)}/{n}", end="")
                print()
                if multi:  # let the camera finish its remaining frames by itself
                    time.sleep(extra * exposure_us / 1e6 + 0.3)
            finally:
                try:
                    cam.stop_streaming()
                except Exception as err:
                    print(f"\n  note: camera complained on stop ({err})")
        except queue.Empty:
            print(f"\n  timed out waiting for a frame (got {len(frames)}/{n})")
        except TypeError as err:  # a bug in this script, not a camera problem
            sys.exit(f"Script error (not the camera): {err}")
        except Exception as err:
            print(f"\n  camera error on attempt {attempt}/{attempts}: {err}")
        finally:
            try_set(cam, "AcquisitionMode", "Continuous", quiet=True)  # leave Viewer-friendly

        if skipped[0]:
            print(f"  note: skipped {skipped[0]} incomplete frame(s)")
        if len(frames) == n:
            return frames
        time.sleep(1.0)
    sys.exit("Acquisition failed repeatedly. Unplug and replug the camera, then rerun.")


def read_settings(cam):
    def get(name):
        try:
            return cam.get_feature_by_name(name).get()
        except Exception:
            return None
    return {
        "model": cam.get_model(), "serial": cam.get_serial(),
        "pixel_format": str(cam.get_pixel_format()),
        "exposure_us_actual": get("ExposureTime"), "gain_db": get("Gain"),
        "black_level": get("BlackLevel"), "device_temperature_C": get("DeviceTemperature"),
    }


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "configs/CapYaml.yaml"
    cfg = load_config(cfg_path)
    now = datetime.now()
    out_dir = RAW_ROOT / now.strftime("%Y%m%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{now.strftime('%Y%m%d_%H%M%S')}_{cfg['name']}.tif"

    if cfg["dark"]:
        input("DARK FRAME: block the beam right after the laser, then press Enter...")

    with VmbSystem.get_instance() as vmb:
        cams = vmb.get_all_cameras()
        if not cams:
            sys.exit("No camera found. Is it plugged in and closed in Vimba X Viewer?")
        with cams[0] as cam:
            configure(cam, cfg)
            frames = acquire(cam, int(cfg["frames"]), float(cfg["exposure_us"]))
            settings = read_settings(cam)

    stack = np.stack(frames).astype(np.uint16)
    full = FULL_SCALE.get(cfg["pixel_format"], int(stack.max()))
    peak = int(stack.max())
    sat = float(np.mean(stack >= full))
    mean_img = stack.mean(axis=0)
    py, px = np.unravel_index(np.argmax(mean_img), mean_img.shape)

    tifffile.imwrite(out, stack)
    meta = {"config_file": str(cfg_path), "config": cfg, "camera": settings,
            "timestamp": now.isoformat(timespec="seconds"),
            "peak_counts": peak, "full_scale": full, "saturated_fraction": sat,
            "peak_position_xy": [int(px), int(py)]}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2, default=str))

    log = LOG
    if log.exists():
        with log.open(newline="") as f:
            header = next(csv.reader(f), [])
        if header != LOG_COLS:  # an older log with different columns
            log = LOG.with_name("lab_log_capture.csv")
            print(f"  note: {LOG} has different columns; logging to {log} instead")
    new_log = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(LOG_COLS)
        w.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), out.name,
                    cfg["name"], cfg.get("sample", ""), cfg.get("concentration", ""),
                    cfg.get("rod_depth_mm", ""), cfg.get("mode", ""), cfg["exposure_us"],
                    cfg["frames"], cfg.get("nd_filters", ""), cfg.get("iris_mm", ""),
                    cfg.get("temperature_C", ""), peak, f"{sat:.6f}", cfg["dark"],
                    cfg.get("notes", "")])

    print(f"Saved {out}")
    print(f"  stack {stack.shape}, peak {peak}/{full} ({100 * peak / full:.0f}% of full scale), "
          f"mean {stack.mean():.1f}, brightest pixel at x={px}, y={py}")
    if sat > 0 and not cfg["dark"]:
        print(f"  WARNING: {100 * sat:.4f}% of pixels saturated. Shorten exposure or add ND.")
    if cfg["dark"]:
        input("Unblock the beam if needed, then press Enter...")


if __name__ == "__main__":
    main()