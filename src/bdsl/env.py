"""Environment check for Day 1 Step 1 (notebooks/00_env_check.ipynb).

Each check returns {"status": "pass" | "fail" | "skip", ...details}. Nothing here installs or
downloads anything, and dataset files are only read. The report holds counts, shapes and timings —
never landmark coordinates or image data.
"""

from __future__ import annotations

import dataclasses
import importlib.metadata as md
import importlib.util
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .io import atomic_write_json, sha256_file
from .paths import cfg_path, ensure_dir

# Distributions whose versions are reported. Both OpenCV wheels are listed so a clash is visible.
TRACKED_PACKAGES = (
    "numpy", "PyYAML", "mediapipe", "opencv-contrib-python", "opencv-python", "torch",
    "torch-directml", "matplotlib", "pytest", "ipykernel", "nbclient", "nbformat",
)
HOLISTIC_FIELDS = (
    "pose_landmarks", "pose_world_landmarks",
    "left_hand_landmarks", "left_hand_world_landmarks",
    "right_hand_landmarks", "right_hand_world_landmarks",
    "face_landmarks", "face_blendshapes",
)


def _guarded(fn: Callable[[], dict]) -> dict:
    """Run one check; an unexpected exception becomes a recorded failure, not a crash."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 — the report must capture every failure
        return {"status": "fail", "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(limit=3)}


def _version(dist: str) -> str | None:
    try:
        return md.version(dist)
    except md.PackageNotFoundError:
        return None


# ---------------------------------------------------------------- individual checks

def check_python(cfg: dict) -> dict:
    expected = str(cfg["env_check"]["expected_python"])
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    return {
        "status": "pass" if actual == expected else "fail",
        "expected": expected,
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
        "in_virtualenv": sys.prefix != sys.base_prefix,
        "os": platform.platform(),
    }


def check_packages(cfg: dict) -> dict:
    versions = {d: _version(d) for d in TRACKED_PACKAGES}
    expected_mp = str(cfg["mediapipe"]["version"])
    problems = []
    if versions["mediapipe"] != expected_mp:
        problems.append(f"mediapipe is {versions['mediapipe']}, expected {expected_mp}")
    if versions["opencv-python"] and versions["opencv-contrib-python"]:
        problems.append("both opencv-python and opencv-contrib-python are installed (they clash)")
    for needed in ("numpy", "PyYAML", "torch"):
        if not versions[needed]:
            problems.append(f"{needed} is not installed")
    return {"status": "fail" if problems else "pass", "versions": versions, "problems": problems}


def _open_capture(path: Path, auto_rotate: bool):
    import cv2

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV cannot open {path.name}")
    cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1 if auto_rotate else 0)
    return cap


def _read_frame(path: Path, index: int = 0, auto_rotate: bool = True):
    import cv2

    cap = _open_capture(path, auto_rotate)
    try:
        if index:
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"Could not decode frame {index} of {path.name}")
        meta = {
            "orientation_meta": int(cap.get(cv2.CAP_PROP_ORIENTATION_META)),
            "orientation_auto": int(cap.get(cv2.CAP_PROP_ORIENTATION_AUTO)),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "fps": round(float(cap.get(cv2.CAP_PROP_FPS)), 3),
        }
        return frame, meta
    finally:
        cap.release()


def rotation_consistent(orientation_meta: int, quarter_turns: int | None) -> bool:
    """Does the rotation OpenCV applied (in quarter turns) match the file's rotation flag?"""
    if quarter_turns is None:
        return False
    if orientation_meta in (90, 270):
        return quarter_turns in (1, 3)
    if orientation_meta == 180:
        return quarter_turns == 2
    return quarter_turns == 0


def check_opencv_rotation(cfg: dict) -> dict:
    import numpy as np

    sample_dir = Path(cfg["data"]["sample_dir"])
    clips = []
    for name in cfg["env_check"]["rotation_clips"]:
        path = sample_dir / name
        if not path.is_file():
            clips.append({"clip": name, "status": "fail", "error": "file not found"})
            continue
        sha_before = sha256_file(path)
        auto, meta = _read_frame(path, auto_rotate=True)
        raw, raw_meta = _read_frame(path, auto_rotate=False)
        # Which rotation turns the raw (stored) frame into the auto-rotated one?
        turns = next((k for k in range(4)
                      if np.rot90(raw, k).shape == auto.shape and np.array_equal(np.rot90(raw, k), auto)), None)
        sha_after = sha256_file(path)
        ok = rotation_consistent(meta["orientation_meta"], turns) and sha_before == sha_after
        clips.append({
            "clip": name,
            "status": "pass" if ok else "fail",
            "orientation_meta": meta["orientation_meta"],
            "auto_rotate_setting": meta["orientation_auto"],
            "raw_frame_hw": list(raw.shape[:2]),
            "auto_frame_hw": list(auto.shape[:2]),
            "display": "portrait" if auto.shape[0] > auto.shape[1] else "landscape",
            "quarter_turns_applied": turns,
            "raw_auto_setting": raw_meta["orientation_auto"],
            "sha256_unchanged": sha_before == sha_after,
            "sha256": sha_before,
        })
    status = "pass" if clips and all(c["status"] == "pass" for c in clips) else "fail"
    return {"status": status, "clips": clips}


def _count(value: Any) -> int | None:
    """Number of landmarks/categories in a result field (handles flat and nested lists)."""
    if value is None:
        return None
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return len(value[0])
        return len(value)
    return None


def check_mediapipe_holistic(cfg: dict) -> dict:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    model = cfg_path(cfg, "models_dir") / cfg["mediapipe"]["model_file"]
    if not model.is_file():
        return {"status": "fail", "error": f"model file missing: {model.name} (download needs owner approval)",
                "model_path": model.as_posix()}
    info: dict[str, Any] = {"model_file": model.name, "model_sha256": sha256_file(model),
                            "model_bytes": model.stat().st_size,
                            "has_HolisticLandmarker": hasattr(vision, "HolisticLandmarker")}

    clip = Path(cfg["data"]["sample_dir"]) / cfg["env_check"]["rotation_clips"][0]
    _, meta = _read_frame(clip)
    frame, _ = _read_frame(clip, index=meta["frame_count"] // 2)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    def options(mode):
        return vision.HolisticLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model)),
            running_mode=mode, output_face_blendshapes=True)

    t0 = time.perf_counter()
    with vision.HolisticLandmarker.create_from_options(options(vision.RunningMode.IMAGE)) as lm:
        info["create_seconds"] = round(time.perf_counter() - t0, 3)
        result = lm.detect(image)
    if dataclasses.is_dataclass(result):
        fields = [f.name for f in dataclasses.fields(result)]
    else:
        fields = sorted(k for k in vars(result) if not k.startswith("_"))
    info["result_fields"] = fields
    info["missing_expected_fields"] = [f for f in HOLISTIC_FIELDS if f not in fields]
    info["counts_on_test_frame"] = {f: _count(getattr(result, f, None)) for f in HOLISTIC_FIELDS}

    with vision.HolisticLandmarker.create_from_options(options(vision.RunningMode.VIDEO)) as lm:
        lm.detect_for_video(image, 0)
        info["video_mode_ok"] = True

    expected_sha = cfg["mediapipe"].get("model_sha256")
    info["model_sha256_matches_config"] = expected_sha is None or info["model_sha256"] == expected_sha
    ok = info["has_HolisticLandmarker"] and not info["missing_expected_fields"] and info["model_sha256_matches_config"]
    info["status"] = "pass" if ok else "fail"
    info["test_frame"] = f"{clip.name} frame {meta['frame_count'] // 2}"
    return info


def check_torch(cfg: dict) -> dict:
    import numpy as np
    import torch

    xn = np.arange(6, dtype=np.float32).reshape(2, 3)
    x = torch.from_numpy(xn)
    cpu_ok = bool(np.allclose((x @ x.T).numpy(), xn @ xn.T))
    cuda = torch.cuda.is_available()
    mps = getattr(torch.backends, "mps", None)
    return {
        "status": "pass" if cpu_ok else "fail",
        "version": torch.__version__,
        "cpu_tensor_ok": cpu_ok,
        "num_threads": torch.get_num_threads(),
        "cuda_available": cuda,
        "cuda_devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if cuda else [],
        "cuda_build": torch.version.cuda,
        "mps_available": bool(mps and mps.is_available()),
        "directml_installed": importlib.util.find_spec("torch_directml") is not None,
        "configured_device": cfg.get("env", {}).get("device"),
    }


def check_write_permission(cfg: dict) -> dict:
    reports = ensure_dir(cfg_path(cfg, "reports_dir"))
    probe = reports / ".write_test.json"
    payload = {"written_at": datetime.now(timezone.utc).isoformat()}
    atomic_write_json(probe, payload)
    import json

    read_back = json.loads(probe.read_text(encoding="utf-8"))
    probe.unlink()
    leftovers = [p.name for p in reports.glob(".*.tmp")]
    ok = read_back == payload and not probe.exists() and not leftovers
    return {"status": "pass" if ok else "fail", "dir": reports.as_posix(), "round_trip_ok": read_back == payload,
            "probe_removed": not probe.exists(), "tmp_leftovers": leftovers}


def check_cpu_benchmark(cfg: dict, mediapipe_ok: bool) -> dict:
    import numpy as np

    bench = cfg["env_check"]["benchmark"]
    n, reps = int(bench["matmul_size"]), int(bench["matmul_repeats"])
    rng = np.random.default_rng(int(cfg["project"]["seed"]))
    a = rng.standard_normal((n, n), dtype=np.float32)
    b = rng.standard_normal((n, n), dtype=np.float32)
    a @ b  # warm-up
    t0 = time.perf_counter()
    for _ in range(reps):
        a @ b
    dt = time.perf_counter() - t0
    out: dict[str, Any] = {
        "cpu_count_logical": os.cpu_count(),
        "processor": platform.processor(),
        "numpy_matmul": {"size": n, "repeats": reps, "seconds": round(dt, 4),
                         "gflops": round(2 * n ** 3 * reps / dt / 1e9, 2)},
    }
    if not mediapipe_ok:
        out["mediapipe_holistic"] = {"status": "skip", "reason": "MediaPipe check did not pass"}
        out["status"] = "pass"
        return out

    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    k = int(bench["mediapipe_frames"])
    clip = Path(cfg["data"]["sample_dir"]) / cfg["env_check"]["rotation_clips"][0]
    _, meta = _read_frame(clip)
    idx = [int(i) for i in np.linspace(0, meta["frame_count"] - 1, k)]
    frames = [cv2.cvtColor(_read_frame(clip, index=i)[0], cv2.COLOR_BGR2RGB) for i in idx]
    model = cfg_path(cfg, "models_dir") / cfg["mediapipe"]["model_file"]
    opts = vision.HolisticLandmarkerOptions(base_options=mp_python.BaseOptions(model_asset_path=str(model)),
                                            running_mode=vision.RunningMode.IMAGE, output_face_blendshapes=True)
    times = []
    with vision.HolisticLandmarker.create_from_options(opts) as lm:
        for rgb in frames:
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            t0 = time.perf_counter()
            lm.detect(image)
            times.append(time.perf_counter() - t0)
    out["mediapipe_holistic"] = {
        "status": "pass", "clip": clip.name, "frame_hw": list(frames[0].shape[:2]), "frames": k,
        "ms_per_frame_mean": round(1000 * sum(times) / k, 1),
        "ms_per_frame_first": round(1000 * times[0], 1),
        "ms_per_frame_rest_mean": round(1000 * sum(times[1:]) / max(k - 1, 1), 1),
        "note": "single process, IMAGE mode, incl. first-call warm-up; not a full-dataset estimate",
    }
    out["status"] = "pass"
    return out


def check_paths(cfg: dict) -> dict:
    root = Path(cfg["_meta"]["project_root"])
    resolved = {k: v for k, v in cfg["paths"].items()}
    resolved["sample_dir"] = cfg["data"]["sample_dir"]
    exists = {k: Path(v).exists() for k, v in resolved.items()}
    ok = (root / "pyproject.toml").is_file() and exists["data_root"] and exists["sample_dir"]
    return {"status": "pass" if ok else "fail", "project_root": root.as_posix(), "resolved": resolved,
            "exists": exists, "env": cfg["_meta"]["env"], "env_var_overrides": cfg["_meta"]["env_var_overrides"],
            "layers": cfg["_meta"]["layers"]}


def _git_state(root: Path) -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True,
                                    check=True).stdout.strip())
        return {"commit": commit, "dirty": dirty}
    except Exception as exc:  # noqa: BLE001 — git may be absent on Kaggle/Colab
        return {"commit": None, "dirty": None, "error": str(exc)}


# ---------------------------------------------------------------- runner

def run_env_check(cfg: dict, write: bool = True) -> dict:
    """Run every check, write work/reports/<report_file> atomically, and return the report."""
    started = datetime.now(timezone.utc)
    checks: dict[str, dict] = {}
    checks["paths"] = _guarded(lambda: check_paths(cfg))
    checks["python"] = _guarded(lambda: check_python(cfg))
    checks["packages"] = _guarded(lambda: check_packages(cfg))
    checks["opencv_rotation"] = _guarded(lambda: check_opencv_rotation(cfg))
    checks["mediapipe_holistic"] = _guarded(lambda: check_mediapipe_holistic(cfg))
    checks["torch_devices"] = _guarded(lambda: check_torch(cfg))
    checks["write_permission"] = _guarded(lambda: check_write_permission(cfg))
    mp_ok = checks["mediapipe_holistic"].get("status") == "pass"
    checks["cpu_benchmark"] = _guarded(lambda: check_cpu_benchmark(cfg, mp_ok))

    statuses = {name: c.get("status", "fail") for name, c in checks.items()}
    overall = "pass" if all(s == "pass" for s in statuses.values()) else (
        "fail" if any(s == "fail" for s in statuses.values()) else "incomplete")
    report = {
        "report": "env_check",
        "generated_at_utc": started.isoformat(timespec="seconds"),
        "duration_seconds": round((datetime.now(timezone.utc) - started).total_seconds(), 2),
        "overall": overall,
        "summary": statuses,
        "config_hash": cfg["_meta"]["config_hash"],
        "config_layers": cfg["_meta"]["layers"],
        "git": _git_state(Path(cfg["_meta"]["project_root"])),
        "checks": checks,
    }
    if write:
        out = cfg_path(cfg, "reports_dir") / cfg["env_check"]["report_file"]
        atomic_write_json(out, report)
        report["written_to"] = out.as_posix()
    return report
