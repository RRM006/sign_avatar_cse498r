# kaggle/src — code used by the kaggle400 notebooks

The notebooks **import** the project code instead of copying it: `src/bdsl` (training, evaluation,
features) plus the helpers here. On Kaggle both come from the `code/` folder of the upload, which is a
`git archive` of a clean commit (`code/CODE_VERSION.json` lists the commit and the SHA-256 of every file).

| File | What it does |
|---|---|
| `k400_run.py` | entry point: `python kaggle/src/k400_run.py <command>` (`--help` lists them) |
| `verify_split.py` | anyone can re-check the split: 10 PASS/FAIL checks (`--require-videos` for the full check) |
| `k400/select.py` | chooses the 400 clips (rules in its docstring and in `data/SPLIT_REPORT.md`) |
| `k400/splitio.py` | writes the manifests, `SPLIT_REPORT.md`, `SPLIT_SUMMARY.png`, `SELECTION_META.json` |
| `k400/copyvid.py` | copies the videos with SHA-256 checks, writes `SPLIT_LOCK.json` and the work-log entry |
| `k400/lock.py` | line-ending-independent hashes for the lock |
| `k400/verify.py` | the leakage / consistency checks |
| `k400/package.py` | builds and re-checks the private-dataset zip (allow-list, clean commit) |
| `k400/setup.py` | first cell of every notebook: paths, carry-over of earlier outputs, live command output |
| `k400/mp_env.py` | MediaPipe 0.10.35 install + real-frame probe + pinned fallback (uv Python 3.12) |
| `k400/extract.py` | per-split, resume-safe MediaPipe extraction with a time budget, QC, rotation and privacy checks |
| `k400/gloss.py` | G0 pseudo-glosses for the 400 sentences, TRAIN-only vocabularies |
| `k400/report.py`, `tables.py`, `figstyle.py` | paper tables (CSV / Markdown / LaTeX), figures, `RESULTS_SUMMARY.md` |
| `k400/avatar.py` | motion JSON + skeleton videos for test sentences (after the test lock) |

Training and evaluation are in `src/bdsl`: `data/kaggle400.py` (layout, split lock, test guard),
`models/train_gloss2motion.py`, `models/train_text2gloss.py` (device, `--max-steps`, B1 exclusions, G0
references), `eval/kaggle400_eval.py` (freeze, val / final test evaluation, lock), `eval/bootstrap.py`,
`provenance.py` (clean-code rule, `env.json`, registry), `device.py`.
