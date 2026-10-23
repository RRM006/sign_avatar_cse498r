# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-23 (Session 9; kaggle400 run 1 finished on Kaggle; local commit pending)
**Phase:** Phase 4 started as one owner-approved experiment: **kaggle400** (400 videos, real training on
Kaggle), folder `kaggle/`. Proposal 05 as a whole is still not approved.

## Where we are right now
- **Milestone 11a done** (2026-10-23): Steps A–D complete. PRIVATE Kaggle dataset `bdsl-k400` Version 1
  (code = commit `933e903`, not pushed); notebooks 00–09 all PASS on Kaggle; notebook 07 passed on its
  second attempt — the first crashed after reading the test split in memory, with no result (ADR-0029,
  reported in `kaggle/outputs/RUN1_NOTES.md`).
- Final TEST (40 clips, measured): Model B beats B0/B1 on every position/DTW metric (CIs exclude 0), but its
  motion is strongly damped (velocity 0.14–0.18, hand energy 0.03–0.05 of real) and over-fits early;
  G0 gloss input = Bangla word input; Model A test WER vs G0 19.7 (agreement with the rule glosser only).
  Details: `test_log.md`, `kaggle/outputs/tables/`, `RESULTS_SUMMARY.md`, `RUN1_NOTES.md`.
- All run outputs are on the desktop in `kaggle/work/downloads/run1/k400/` (gitignored; verified). The small
  results are copied into `kaggle/outputs/` and `kaggle/processed/qc/` (privacy-checked).
- **Not committed yet** (after `933e903`): run-1 results (`kaggle/outputs/`, `kaggle/processed/qc/`),
  notebook-07 safety stop (`kaggle/notebooks/07_baselines_eval.ipynb`, `kaggle/tools/build_notebooks.py`,
  `tests/test_k400_misc.py`; 210 tests pass in the workspace), `agent_docs/*`, `DATASET_WORK_LOG.md`.
  Keep `kaggle/outputs/env/mediapipe_route.json` out of Git (owner's Kaggle username; ADR-0029).

## The one thing we are doing next
👉 **Local commit (owner's OK given 2026-10-23; no push):** the owner runs the commit block from the chat
(run the tests; `git add` only the listed paths, excluding `kaggle/outputs/env/mediapipe_route.json`; stop
if any `.pt/.npz/.mp4/.zip`, `motion_real`, `motion_B1` or `kaggle.json` is staged; commit) and pastes the
output. Then the AI records the commit hash in `test_log.md`.

## After that (owner decides the order)
- Push to GitHub or not (repo is public; the kaggle400 instruction was "no push").
- Write up the results for the paper, including the failed first attempt of notebook 07 and the damped-motion
  limitation; BdSL-competent human evaluation does not exist.
- G16: confirm or change the proposed ADR-0028. G18: small fixes (need a new commit + package). G12 line
  endings. Older open items: G1, G2, G6–G10.

## Evidence rules
- kaggle400 results: small-scale, signer-dependent; test used once (FINAL_TEST_LOCK.json) — plus the
  documented crashed attempt without result; measured vs estimated labels; low coordinate error ≠ correct
  BdSL; G0 = pseudo-gloss; Model A = "agreement with the rule glosser (G0 pseudo-gloss)"; no human/expert
  validation. Never re-run notebook 07.
- Pilot numbers stay "pipeline test". `TEST_…`, `NFP_…`, `DRYRUN_…` and overfit runs are never results.
  Workspace smoke runs are never results.

## Locked decisions — do NOT re-open without the owner
- ADR-0003, 0006, 0007, 0008, 0012; ADR-0004/0005/0009/0010/0011/0013 as amended;
  ADR-0014–0021 (owner bullets Accepted; technical specifics Accepted in principle); ADR-0022–0027; ADR-0029.
- ADR-0028 is only PROPOSED.
