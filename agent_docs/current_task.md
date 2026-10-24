# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-24 (end of Session 10; kaggle400 commits pushed, project-memory update committed)
**Phase:** Phase 4 started as one owner-approved experiment: **kaggle400** (400 videos, real training on
Kaggle), folder `kaggle/`. Proposal 05 as a whole is still not approved. Phase 3 still has milestone 8
open (Model A on really reviewed glosses; waits for G10).

## Where we are right now
- **Milestone 11a done** (2026-10-23): Steps A–D complete. PRIVATE Kaggle dataset `bdsl-k400` Version 1
  (code = commit `933e903`); notebooks 00–09 all PASS on Kaggle; notebook 07 passed on its second
  attempt — the first crashed after reading the test split in memory, with no result (ADR-0029, reported in
  `kaggle/outputs/RUN1_NOTES.md`).
- **The owner requested commit and push on 2026-10-24.** The kaggle400 commits `933e903` and `b705768`,
  plus the Session 10 project-memory update, are published to the public GitHub repository.
- Final TEST (40 clips, measured): Model B beats B0/B1 on every position/DTW metric (CIs exclude 0), but its
  motion is strongly damped (velocity 0.14–0.18, hand energy 0.03–0.05 of real) and over-fits early;
  G0 gloss input = Bangla word input; Model A test WER vs G0 19.7 (agreement with the rule glosser only).
  Details: `test_log.md`, `kaggle/outputs/tables/`, `RESULTS_SUMMARY.md`, `RUN1_NOTES.md`.
- **Run-1 report** (2026-10-23): a 2-page Claude Doc in the owner's claude.ai account, "kaggle400 Run 1 —
  Bangla Text to BdSL Avatar: Experiment Report" (findings, method, test table, skeleton videos, meaning,
  improvement proposals, output provenance). Not in the repo.
- Desktop only (gitignored): `kaggle/work/downloads/run1/k400/` (all 2,448 output files, incl. checkpoints,
  features, skeleton videos, `motion_real.json` / `motion_B1.json`).

## The one thing we are doing next
👉 **The owner decides the next direction; nothing runs before that.** G20 is answered: the owner requested
the push on 2026-10-24. Ask which work item comes next (list below). Every improvement in the report is a
**proposal**, not a decision.

## After that (owner decides the order)
- Paper write-up of run 1 (use the report + `RUN1_NOTES.md`; include the failed first attempt of notebook 07,
  the damped motion and the small, signer-dependent test set).
- Improvement proposals from the report (not decided): motion/velocity losses and higher hand weight; a
  retrieval + generation hybrid; more data (proposal 05); real glosses (G10); BdSL-competent raters; hand-side
  check (G8). A changed model must be tested on the **437 unused S1-test clips**, never on the kaggle400 test
  split again.
- G18 fixes (need a new commit + a new package), incl. browser-playable H.264 skeleton videos.
- G16 (ADR-0028), G12 line endings, G15 general rule; older open items G1, G2, G6–G10.
- Optional (owner's OK): export the run-1 report (Markdown or PDF) into `research/reports/`.

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
