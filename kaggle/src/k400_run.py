"""Entry point: `python kaggle/src/k400_run.py <command>` (see `k400/cli.py` or `--help`)."""

import os
import sys
from pathlib import Path

# A Jupyter kernel exports MPLBACKEND=module://matplotlib_inline...; another Python (e.g. the MediaPipe
# fallback environment) cannot import it, and mediapipe imports matplotlib. Use the file backend instead.
if os.environ.get("MPLBACKEND", "").startswith("module://"):
    os.environ["MPLBACKEND"] = "Agg"

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent.parent / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from k400.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
