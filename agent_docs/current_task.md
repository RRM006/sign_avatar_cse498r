# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-22 (end of Session 5)
**Phase:** Phase 3 — 5-day prototype, in progress. Days 1–2 are done (milestones 5–7). Day 3 code is
done and was run in TEST mode only, on fake review data (milestone 8 🟨, ADR-0025). Days 4–5 (Model B,
avatar demo) are done (milestones 9–10 ✅, ADR-0026/0027). The design was approved in principle on 2026-10-22 (ADR-0014–0027). Implementation runs one owner-approved step at a time.

## Where we are right now
- Day 1: `.venv`, configs, env check 8/8; manifest v1 (5,010 rows); split S1 v0; pilot50_v1 copied
  (40/5/5, option B, ADR-0022).
- Day 2: pilot MediaPipe features, VIDEO mode, feat_ver `fa89892d4908` (ADR-0023), in `work/features/`.
  Hands are the weak point (left 69.7%, right 35.7%, both 25.9%). G0 drafts + convention v0.1.
- Day 3 (TEST mode, ADR-0025):
  - `annotations/pilot50_v1_gloss_v01.csv` holds FAKE review rows: `is_mock=true`, notes "TEST
    DATA … not video-verified", reviewer T1 (role team).
  - `gloss-validate` and `train-text2gloss` refuse these rows by default. Only `--allow-test-data`
    accepts them, and its outputs are `TEST_…`.
  - Results: `test_log.md` 2026-10-22. G0 beats A-GRU on val/test; the A-GRU memorises its train
    sentences. Not a Model A result.
- `main` = local merge `0eef7c6` (practice branch `test-run-fake-review` + Day 3 code), plus the
  Session 5 docs commit. **Not pushed**: a push publishes the fake-labelled annotation rows.
- Day 4: `train-gloss2motion` (Model B NAR, ablation T, B0/B1). Model B ≈ B0 on held-out clips and
  moves at ~20–30% of real speed; B1 moves realistically (`test_log.md` 2026-10-22, open question
  G11). Predictions for all 50 clips: `work/runs/gloss2motion_gloss_pilot50_20261022T133822Z/seed42/predictions/`.
- Day 5: `bdsl.cli demo` + `web/avatar_viewer/`. Sentence 3246 → Model B and B1 side by side (ADR-0027),
  `work/demo/demo_20261022T141520Z/` (skeleton MP4, motion JSON, log, LIMITATIONS.md). Round-trip on the
  real avatar ≤ 3.4°. Not reviewed by a BdSL-competent person.
- 140 tests pass.
- Open owner inputs: G1 licence, G6 deadline, G8 hand sides / mirroring, G9 QC thresholds,
  G10 real team review. Open measurements: G2, G3 (`open_questions.md`). G5 and G11 answered.

## Start of the next session (after the standard start-of-session reading)
1. `git status` / `git log --oneline -5`: `main` is ahead of `origin/main` with the Session 5
   commits and has no uncommitted changes. If not, stop and tell the owner.
2. `uv run pytest` → expected 140 passed.
3. If T1 has done the real video review: `uv run python -m bdsl.cli gloss-validate` (no option) and
   report the result. Never fix reviewed rows yourself.

## The one thing we are doing next
👉 **The 5-day prototype (Phase 3) is complete as a pipeline test. Owner: review the demo, then decide the
Phase 4 / Week 2 plan (design doc 04 §G). No implementation before the owner's go.**

How to view the demo: `uv run python -m http.server 8765 --bind 127.0.0.1`, then open
`http://127.0.0.1:8765/web/avatar_viewer/?demo=/work/demo/demo_20261022T141520Z/` (or play
`skeleton_side_by_side.mp4` in that folder).

Candidate next steps (proposals, not decisions; see design doc 04 §G):
- The real Day 3 run: T1's real video review of the 50 pilot glosses → `gloss-validate` (no option) →
  `train-text2gloss`.
- Week 2: full-set extraction (owner's go), the shared-segment scan (G2) → split S1 v1, Kaggle setup (G3).
- More training data for Model B (the pilot result is close to the mean motion).
- Owner inputs still open: G1, G6, G8, G9; a BdSL-competent reviewer for the demo.
- Pushing: `main` is ahead of `origin` and contains the fake-labelled Day 3 rows (ADR-0025); a push publishes them.

## Evidence rules
- Pilot numbers are "pipeline test", never "generalisation". All results are signer-dependent.
- `TEST_…` runs (ADR-0025) are never reported as results.
- Gloss statuses: auto_draft / team_reviewed / expert_validated / rejected. Only a registered reviewer
  sets a reviewed status; the AI never does. Mock rows are flagged and refused by default.
- G0 output is a pseudo-gloss, never a BdSL annotation.
- `sample50` (committed videos/) ≠ `pilot50_v1` (dataset/pilot50_v1/, selected from split S1).
- MediaPipe "left/right hand" may not be the signer's real left/right (G8).

## Locked decisions — do NOT re-open without the owner
- ADR-0003, 0006, 0007, 0008, 0012; ADR-0004/0005/0009/0010/0011/0013 as amended;
  ADR-0014–0021 (owner bullets Accepted; technical specifics Accepted in principle); ADR-0022–0027.

## Important environment / gotchas
- Run everything through `uv run …` (CLAUDE.md COMMANDS). Notebooks: the `.venv` kernel.
- Don't read research/papers/*.pdf. Don't add SIGN_LANGUAGE_DATA/, pilot copies or work/ to git.
- The repo is public: a push is a publication (ADR-0017). Reviewer names never go into git.
- Annotation CSVs are UTF-8 with BOM; in Excel save as "CSV UTF-8" (REVIEW_GUIDE.md).
- `gloss-draft` refuses to overwrite a file with reviewed rows; never bypass this.
- On Windows (PowerShell 5.1), pass multi-line git commit messages with `git commit -F <file>`.
- Use a fresh HolisticLandmarker per video; Windows multiprocessing code under `if __name__ == "__main__"`.
- Log dataset inspections in dataset/initial_dataset/DATASET_WORK_LOG.md.
