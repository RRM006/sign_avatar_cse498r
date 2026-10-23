"""Re-check the kaggle400 split: anyone can run this.

    python kaggle/src/verify_split.py                    # without videos: checks 1-7 (+10 if the lock exists)
    python kaggle/src/verify_split.py --require-videos   # full check incl. the SHA-256 of all 400 copies

Checks (PASS/FAIL each): manifests agree; counts; no leakage group, SHA-256, normalised sentence or known
shared-segment link crosses splits; every clip kept its S1 v0 partition; each videos/ folder holds exactly
its manifest's files with equal SHA-256; no file in two folders; SPLIT_LOCK.json matches the manifests.
Exit code 0 = all passed.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent.parent / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from k400.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["verify", *sys.argv[1:]]))
