"""Common first cell of every kaggle400 notebook: find the data and code, set paths, carry state forward.

On Kaggle:
  dataset root  the folder of the private dataset that holds UPLOAD_MANIFEST.csv (data/, code/)
  code root     <dataset root>/code (read-only `git archive` of a clean commit)
  state root    /kaggle/working/k400 — everything a notebook writes (processed/, outputs/); Kaggle saves
                /kaggle/working as the notebook's Output when you use "Save Version → Save & Run All".
  carry-over    the Output of an earlier notebook, added with "Add Input", appears under /kaggle/input/;
                its k400/ folder is copied into /kaggle/working/k400 (never overwriting) so results
                accumulate notebook by notebook.
On the desktop: dataset root = state root = <project>/kaggle, code root = <project>.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

KAGGLE_INPUT = Path("/kaggle/input")
KAGGLE_WORKING = Path("/kaggle/working")
STATE_MARKER = "STATE.json"
NOISE = ("inference_feedback_manager", "XNNPACK delegate", "absl::InitializeLog", "gl_context", "landmark_projection_calculator")


def on_kaggle() -> bool:
    return "KAGGLE_KERNEL_RUN_TYPE" in os.environ or KAGGLE_WORKING.is_dir()


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def find_previous_states(base: Path = KAGGLE_INPUT, max_depth: int = 6) -> list[Path]:
    """k400/ folders (with STATE.json) inside attached notebook outputs (video and code folders skipped)."""
    found = []
    if not base.is_dir():
        return found
    for dirpath, dirnames, filenames in os.walk(base):
        here = Path(dirpath)
        if here.name == "k400" and STATE_MARKER in filenames:
            found.append(here)
            dirnames[:] = []
            continue
        depth = len(here.relative_to(base).parts)
        dirnames[:] = [] if depth >= max_depth else [d for d in dirnames if d not in ("videos", "code")]
    return sorted(found)


def restore(states: list[Path], state_root: Path, log=print) -> dict:
    """Copy earlier outputs into the state root without overwriting; report conflicts."""
    copied, same, conflicts = 0, 0, []
    for src_root in states:
        for f in src_root.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(src_root)
            dst = state_root / rel
            if dst.exists():
                if dst.stat().st_size == f.stat().st_size and _sha(dst) == _sha(f):
                    same += 1
                else:
                    conflicts.append(rel.as_posix())   # same text on Windows and Linux
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            copied += 1
    if conflicts:
        log(f"WARNING: {len(conflicts)} files differ between attached outputs; the first copy was kept: {conflicts[:5]}")
    return {"from": [str(s) for s in states], "copied": copied, "identical": same, "conflicts": conflicts}


class Setup:
    def __init__(self, dataset_root: Path, code_root: Path, notebook: str, log=print):
        self.notebook = notebook
        self.kaggle = on_kaggle()
        self.dataset_root = Path(dataset_root)
        self.code_root = Path(code_root)
        if self.kaggle:
            self.data_root = self.dataset_root
            self.state_root = KAGGLE_WORKING / "k400"
        else:
            self.data_root = self.code_root / "kaggle"
            self.state_root = Path(os.environ.get("K400_STATE_ROOT", self.code_root / "kaggle"))
        self.state_root.mkdir(parents=True, exist_ok=True)
        env = {"BDSL_PROJECT_ROOT": str(self.code_root), "K400_DATA_ROOT": str(self.data_root),
               "K400_STATE_ROOT": str(self.state_root), "PYTHONIOENCODING": "utf-8",
               "BDSL_ENV": "kaggle" if self.kaggle else os.environ.get("BDSL_ENV", "local")}
        if self.kaggle:
            env["BDSL_WORK_DIR"] = str(self.state_root / "work")
        os.environ.update(env)
        for p in (self.code_root / "kaggle" / "src", self.code_root / "src"):
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
        self.restored = restore(find_previous_states(), self.state_root, log) if self.kaggle else {"copied": 0}
        self.code_version = self._code_version()
        self._mark("started")
        log(self.describe())

    def _code_version(self) -> dict:
        f = self.code_root / "CODE_VERSION.json"
        if f.is_file():
            cv = json.loads(f.read_text(encoding="utf-8"))
            return {"source": "package", "commit": cv.get("commit"), "created_utc": cv.get("created_utc")}
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.code_root, capture_output=True, text=True,
                                    check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            commit = None
        return {"source": "git" if commit else "unknown", "commit": commit}

    def _mark(self, status: str) -> None:
        f = self.state_root / STATE_MARKER
        state = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {"label": "kaggle400 state", "runs": []}
        state["runs"].append({"notebook": self.notebook, "status": status,
                              "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                              "code_commit": self.code_version.get("commit"), "kaggle": self.kaggle})
        f.write_text(json.dumps(state, indent=1), encoding="utf-8")

    def describe(self) -> str:
        return "\n".join([
            f"notebook      : {self.notebook}",
            f"platform      : {'Kaggle' if self.kaggle else 'desktop / local'}  (Python {sys.version.split()[0]})",
            f"dataset root  : {self.dataset_root}",
            f"code          : {self.code_root}  (commit {str(self.code_version.get('commit'))[:12]}, {self.code_version.get('source')})",
            f"data (videos) : {self.data_root / 'data'}",
            f"outputs       : {self.state_root}",
            f"carried over  : {self.restored.get('copied', 0)} files from earlier notebooks"
            + (f" ({len(self.restored.get('from', []))} attached output(s))" if self.kaggle else ""),
        ])

    # ---- running commands, output shown live in the notebook (and saved inside the .ipynb)
    def _stream(self, cmd: list[str], python: str | None = None) -> int:
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(self.code_root / "src"), str(self.code_root / "kaggle" / "src")]
                                            + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        full = [python or sys.executable, *cmd]
        print("$ " + " ".join(full[1:]), flush=True)
        env["MPLBACKEND"] = "Agg"                      # Jupyter's inline backend does not exist in child Pythons
        env.setdefault("GLOG_minloglevel", "2")        # MediaPipe / TensorFlow Lite C++ log noise
        env.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
        p = subprocess.Popen(full, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                             errors="replace", env=env, cwd=str(self.state_root))
        hidden = 0
        for line in p.stdout:
            if any(n in line for n in NOISE):
                hidden += 1
                continue
            print(line, end="", flush=True)
        code = p.wait()
        print(f"[exit code {code}]" + (f" ({hidden} MediaPipe/TFLite log lines hidden)" if hidden else ""), flush=True)
        return code

    def pip_install(self, *pins: str) -> int:
        """pip install pinned packages into this notebook's Python (Kaggle: needs Internet On)."""
        missing = []
        for pin in pins:
            name, _, ver = pin.partition("==")
            try:
                from importlib.metadata import version

                if version(name) == ver:
                    continue
            except Exception:  # noqa: BLE001 — not installed
                pass
            missing.append(pin)
        if not missing:
            print("already installed:", ", ".join(pins))
            return 0
        return self._stream(["-m", "pip", "install", "-q", *missing])

    def bdsl(self, *args: str, python: str | None = None) -> int:
        extra = json.loads(os.environ.get("K400_EXTRA_SETS", "[]"))
        if extra and args and args[0].startswith("train-"):
            # Only for the workspace smoke test (tiny epochs); leave K400_EXTRA_SETS unset on Kaggle.
            # The overrides are recorded in run.json like any --set.
            args = (*args, *[a for s in extra for a in ("--set", s)])
        return self._stream(["-m", "bdsl.cli", *args], python)

    def k400(self, *args: str, python: str | None = None) -> int:
        return self._stream([str(self.code_root / "kaggle" / "src" / "k400_run.py"), *args], python)

    def finish(self, checks: list[tuple[str, bool]] | None = None) -> None:
        """Hash list of every output file (for checking downloads) + the "what to check" verdict."""
        rows = []
        for f in sorted(self.state_root.rglob("*")):
            if f.is_file() and f.name != "OUTPUT_HASHES.csv":
                rows.append({"path": f.relative_to(self.state_root).as_posix(), "bytes": f.stat().st_size, "sha256": _sha(f)})
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=["path", "bytes", "sha256"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        (self.state_root / "OUTPUT_HASHES.csv").write_text(buf.getvalue(), encoding="utf-8")
        self._mark("finished")
        total = sum(r["bytes"] for r in rows)
        print(f"Saved {len(rows)} output files ({total / 1e6:.1f} MB) under {self.state_root}; hash list OUTPUT_HASHES.csv")
        if checks:
            ok = all(c for _, c in checks)
            for name, c in checks:
                print(f"{'PASS' if c else 'FAIL'}  {name}")
            print("NOTEBOOK RESULT:", "PASS" if ok else "FAIL — read the messages above before going on")


def setup(dataset_root, code_root, notebook: str) -> Setup:
    return Setup(Path(dataset_root), Path(code_root), notebook)
