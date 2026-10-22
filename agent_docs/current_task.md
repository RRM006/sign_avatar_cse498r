# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-22 (end of Session 5)
**Phase:** Phase 3 — 5-day prototype, in progress. Days 1–2 are done (milestones 5–7). Day 3 code is
done and was run in TEST mode only, on fake review data (milestone 8 🟨, ADR-0025). Day 4 (Model B) is
done (milestone 9 ✅, ADR-0026). The design was approved in principle on 2026-10-22 (ADR-0014–0026). Implementation runs one owner-approved step at a time.

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
- 125 tests pass. No avatar yet.
- Open owner inputs: G1 licence, G6 deadline, G8 hand sides / mirroring, G9 QC thresholds,
  G10 real team review, **G11 motion source for the Day 5 demo**. Open measurements: G2, G3, G5 (`open_questions.md`).

## Start of the next session (after the standard start-of-session reading)
1. `git status` / `git log --oneline -5`: `main` is ahead of `origin/main` with the Session 5
   commits and has no uncommitted changes. If not, stop and tell the owner.
2. `uv run pytest` → expected 125 passed.
3. If T1 has done the real video review: `uv run python -m bdsl.cli gloss-validate` (no option) and
   report the result. Never fix reviewed rows yourself.

## The one thing we are doing next
👉 **Day 5 (milestone 10): show the owner the plan and wait for the go. Ask G11 first.**

Day 5 (design doc 04 §F-12, ADR-0019):
- Post-process predicted motion (de-normalise, smoothing, bone lengths, masked hands → rest pose).
- Own direction-based retargeter → `motion_<run>.json`; a skeleton viewer (always) and a three.js +
  three-vrm viewer with a CC0 VRM model (G5).
- One sentence → video, with a versioned log; limitations written.
- Owner inputs first: G11 (Model B, B1 or both, labelled), and G8 (hand sides) for retargeting.
- Ask before installing or downloading anything (three.js / three-vrm versions, the VRM model).

Still owed: the real Day 3 run, after a real video review (`gloss-validate` without the test option
→ 0 problems → `train-text2gloss`).

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
  ADR-0014–0021 (owner bullets Accepted; technical specifics Accepted in principle); ADR-0022–0026.

## Important environment / gotchas
- Run everything through `uv run …` (CLAUDE.md COMMANDS). Notebooks: the `.venv` kernel.
- Don't read research/papers/*.pdf. Don't add SIGN_LANGUAGE_DATA/, pilot copies or work/ to git.
- The repo is public: a push is a publication (ADR-0017). Reviewer names never go into git.
- Annotation CSVs are UTF-8 with BOM; in Excel save as "CSV UTF-8" (REVIEW_GUIDE.md).
- `gloss-draft` refuses to overwrite a file with reviewed rows; never bypass this.
- On Windows (PowerShell 5.1), pass multi-line git commit messages with `git commit -F <file>`.
- Use a fresh HolisticLandmarker per video; Windows multiprocessing code under `if __name__ == "__main__"`.
- Log dataset inspections in dataset/initial_dataset/DATASET_WORK_LOG.md.
