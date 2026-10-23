"""MediaPipe 0.10.35 on Kaggle: install, probe, and the pinned fallback (owner request, 2026-10-23).

Main route: `pip install mediapipe==0.10.35 opencv-contrib-python==5.0.0.93` into the notebook's Python.
Both are generic Linux wheels (mediapipe: py3-none-manylinux_2_28_x86_64; OpenCV: cp37-abi3), checked
on 2026-10-23 to exist for Python 3.10–3.14, so the Python version alone should not block them.
Fallback route (used automatically if the main route fails): a separate Python 3.12 environment made
with `uv` (downloads a standalone CPython 3.12), with the desktop's exact pins (numpy 2.4.6, PyYAML 6.0.3,
pandas 3.0.3, mediapipe 0.10.35, OpenCV 5.0.0.93). Extraction then runs in that Python as a subprocess.

Every probe creates a real HolisticLandmarker in VIDEO mode and runs it on one real frame of a
dataset video (rotation applied by OpenCV), so "OK" means extraction can really start.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

MP_VERSION = "0.10.35"
MAIN_PINS = [f"mediapipe=={MP_VERSION}", "opencv-contrib-python==5.0.0.93"]
FALLBACK_PINS = MAIN_PINS + ["numpy==2.4.6", "pyyaml==6.0.3", "pandas==3.0.3"]

PROBE = r'''
import json, sys
out = {"python": sys.version.split()[0], "executable": sys.executable}
try:
    import numpy as np, cv2, mediapipe as mp
    out.update(numpy=np.__version__, cv2=cv2.__version__, mediapipe=mp.__version__)
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    model, video = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
    if video:
        cap = cv2.VideoCapture(video)
        ok, frame = cap.read()
        out["orientation_meta"] = cap.get(cv2.CAP_PROP_ORIENTATION_META)
        cap.release()
        if not ok:
            raise RuntimeError("OpenCV could not decode the first frame of " + video)
    else:
        frame = np.full((480, 640, 3), 128, np.uint8)
    out["frame_hw"] = list(frame.shape[:2])
    opts = vision.HolisticLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=model),
                                            running_mode=vision.RunningMode.VIDEO, output_face_blendshapes=True)
    with vision.HolisticLandmarker.create_from_options(opts) as lm:
        rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), 0)
    pose = res.pose_landmarks[0] if res.pose_landmarks and isinstance(res.pose_landmarks[0], list) else res.pose_landmarks
    out["pose_points_found"] = len(pose or [])
    out["ok"] = mp.__version__ == "%s"
    if not out["ok"]:
        out["error"] = "mediapipe " + mp.__version__ + " is not the pinned %s"
except Exception as exc:
    out["ok"] = False
    out["error"] = type(exc).__name__ + ": " + str(exc)
print("K400PROBE " + json.dumps(out))
''' % (MP_VERSION, MP_VERSION)


def clean_env(env: dict | None = None) -> dict:
    """Environment for child Pythons. Jupyter sets MPLBACKEND to its inline backend, which a separate
    Python (the fallback) does not have; mediapipe imports matplotlib and would crash on it."""
    out = dict(os.environ if env is None else env)
    out["MPLBACKEND"] = "Agg"
    out.setdefault("GLOG_minloglevel", "2")
    out.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    return out


def _run(cmd: list[str], timeout: int = 1800, env: dict | None = None) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=clean_env(env))
    return r.returncode, (r.stdout + r.stderr)[-4000:]


def probe(python: str, model_path: Path, video: Path | None = None) -> dict:
    code, out = _run([python, "-c", PROBE, str(model_path), str(video or "")], timeout=600)
    for line in out.splitlines():
        if line.startswith("K400PROBE "):
            return json.loads(line[len("K400PROBE "):])
    return {"ok": False, "error": f"probe crashed (exit {code}): {out[-800:]}"}


def download_model(url: str, dest: Path, sha256: str) -> dict:
    """Download the HolisticLandmarker model (needs Internet) and check its pinned SHA-256."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.is_file():
        tmp = dest.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(dest)
    h = hashlib.sha256(dest.read_bytes()).hexdigest()
    return {"path": str(dest), "sha256": h, "ok": h == sha256, "expected": sha256, "bytes": dest.stat().st_size}


def install_main(log=print) -> dict:
    log(f"[main route] pip install {' '.join(MAIN_PINS)} into {sys.executable}")
    code, out = _run([sys.executable, "-m", "pip", "install", "-q", *MAIN_PINS])
    return {"route": "main", "returncode": code, "output_tail": out[-1500:], "python": sys.executable}


def install_fallback(env_dir: Path, log=print) -> dict:
    """uv-managed CPython 3.12 + the desktop's exact pins (no change to the notebook's own Python)."""
    py = env_dir / "bin" / "python"
    steps = []
    if not py.is_file():
        log("[fallback] installing uv, then a standalone Python 3.12 environment")
        steps.append(_run([sys.executable, "-m", "pip", "install", "-q", "uv"]))
        uv = [sys.executable, "-m", "uv"]
        steps.append(_run(uv + ["venv", str(env_dir), "--python", "3.12"]))
    else:
        uv = [sys.executable, "-m", "uv"]
    log(f"[fallback] uv pip install {' '.join(FALLBACK_PINS)}")
    steps.append(_run(uv + ["pip", "install", "--python", str(py), *FALLBACK_PINS]))
    return {"route": "fallback", "returncode": max(c for c, _ in steps), "output_tail": steps[-1][1][-1500:],
            "python": str(py)}


def ensure(model_path: Path, video: Path | None, fallback_dir: Path, allow_fallback: bool = True, log=print) -> dict:
    """Make a Python that can run MediaPipe 0.10.35 on a real frame. Returns the route and its probe."""
    report = {"model": str(model_path), "video": str(video) if video else None, "attempts": []}
    first = probe(sys.executable, model_path, video)
    report["attempts"].append({"route": "already installed", "probe": first})
    if first.get("ok"):
        return report | {"route": "main (already installed)", "python": sys.executable, "probe": first, "ok": True}
    inst = install_main(log)
    p = probe(sys.executable, model_path, video)
    report["attempts"].append({**inst, "probe": p})
    if p.get("ok"):
        return report | {"route": "main", "python": sys.executable, "probe": p, "ok": True}
    log(f"[main route] FAILED: {p.get('error')}")
    if not allow_fallback:
        return report | {"route": "failed", "python": None, "probe": p, "ok": False}
    fb = install_fallback(fallback_dir, log)
    p2 = probe(fb["python"], model_path, video) if Path(fb["python"]).is_file() else {"ok": False, "error": fb["output_tail"]}
    report["attempts"].append({**fb, "probe": p2})
    if p2.get("ok"):
        return report | {"route": "fallback (uv Python 3.12)", "python": fb["python"], "probe": p2, "ok": True}
    return report | {"route": "failed", "python": None, "probe": p2, "ok": False}


def worker_env(code_root: Path) -> dict:
    """Environment for a subprocess that must import bdsl and k400 from the uploaded code folder."""
    env = clean_env()
    paths = [str(code_root / "src"), str(code_root / "kaggle" / "src")]
    env["PYTHONPATH"] = os.pathsep.join(paths + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env
