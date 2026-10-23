"""k400 — helpers for the 400-video Kaggle experiment (folder `kaggle/`, owner-approved 2026-10-23).

Selection, copying, verification and packaging run on the desktop (PowerShell script
`kaggle/tools/run_local_steps.ps1`); setup, MediaPipe installation, extraction, G0 glosses, reports
and the avatar export run in the Kaggle notebooks. Training and evaluation live in `bdsl` (the
`--data kaggle400` options of `python -m bdsl.cli`).
"""

K400_VERSION = "k400-v1"
