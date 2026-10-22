# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-22 (end of Session 4)
**Phase:** Phase 3 — 5-day prototype, in progress. Days 1–2 are done (milestones 5–7). The design was
approved in principle on 2026-10-22 (ADR-0014–0024). Implementation runs one owner-approved step at a time.

## Where we are right now
- Day 1: `.venv`, configs, env check 8/8; manifest v1 (5,010 rows, 3,378 sentences, 3,376 groups,
  0 conflicts); split S1 v0 (no leakage found); pilot50_v1 copied (40/5/5, option B, ADR-0022).
- Day 2 Step 1: pilot MediaPipe features, **VIDEO mode, feat_ver `fa89892d4908`** (ADR-0023), in
  `work/features/` (gitignored). QC: hands are the weak point (left 69.7%, right 35.7%, both 25.9%).
- Day 2 Step 2: `annotations/` has the provisional gloss convention v0.1, the review guide, an empty
  reviewer register and 50 G0 drafts. All are `auto_draft` (ADR-0024); 0 rows are usable for training.
- Notebooks `00_env_check` (run on Day 1) and `01_manifest`, `02_extract`, `03_gloss` exist. The last
  three are thin wrappers of the same `bdsl` CLI code; they are saved without outputs and have not
  been executed.
- The owner authorized publication. All work since commit `1809048`, including `annotations/`, is
  being committed and pushed to the public repository.
- No models or avatar exist yet.
- Open owner inputs: G1 reuse licence, G6 deadline, G8 hand sides / mirroring, G9 QC thresholds,
  **G10 team reviewer**. Open measurements: G2, G3, G5 (`open_questions.md`).

## Start of the next session (after the standard start-of-session reading)
1. Run `git status` and confirm the uncommitted work is still there: modified agent_docs/README/dataset
   docs, plus untracked `annotations/`, `configs/`, `dataset/pilot50_v1/`, `notebooks/`, `src/`,
   `tests/`, `pyproject.toml`, `uv.lock` and design doc 04. If anything is missing, stop and tell the
   owner.
2. Run `uv run pytest`. Expected: 93 passed.
3. If the owner has registered reviewer codes and reviews were done, run
   `uv run python -m bdsl.cli gloss-validate` and report its result. Never fix reviewed rows yourself.
4. Ask the owner for the Day 3 route (below). Ask whether to propose a commit first.

## The one thing we are doing next
👉 **Owner decision on how Day 3 proceeds (G10). Nothing below is authorised before the owner's go.**

Day 3 (Model A) trains only on `team_reviewed` / `expert_validated` rows (ADR-0024). Options:
1. **Review first (planned route):** the owner registers reviewer code(s) in
   `annotations/REVIEWERS.csv` and a team member reviews the 50 drafts (`annotations/REVIEW_GUIDE.md`).
   `uv run python -m bdsl.cli gloss-validate` must then report 0 problems. Then "go Day 3 Step 1".
2. **Swap Day 3 and Day 4 while the review runs:** Model B (gloss → motion) uses G0 pseudo-glosses
   (ADR-0014), so it does not need the review. Needs the owner's go for the new order.
3. **Labelled pipeline test:** run Day 3 on auto drafts, reported only as "auto-draft pipeline test",
   never as Model A results. Needs the owner's explicit decision.

Day 3 Step 1 (when authorised) — Model A pilot ONLY:
- On the go, first show the exact plan, model sizes, metrics and acceptance tests; **ask before**
  installing anything. sacreBLEU, for BLEU/chrF per ADR-0020, is not installed yet.
- G0 baseline vs BiGRU-attention seq2seq on the pilot (train 40 / val 5 / test 5, from S1).
  Per-item tables, gloss WER, BLEU/chrF, exact match — labelled "pipeline test".
- Checkpoints with resume (model, optimizer, RNG, config/vocab/split hashes) + a kill-and-resume test.
- A notebook `04_train_text2gloss` as a thin wrapper of the same code.
- No upload. A Kaggle dry run happens only if the owner has set up the account (G3) and approves it.

## Plan and status
The 5-day milestones and their status live in `milestone_log.md` (the single status board). The
month plan is in design doc 04 §G.

## Evidence rules
- Pilot numbers are "pipeline test", never "generalisation". All results are signer-dependent.
- Gloss statuses: auto_draft / team_reviewed / expert_validated / rejected. Only a registered
  reviewer sets a reviewed status; the AI never does. Mock rows are flagged and refused.
- G0 output is a pseudo-gloss, never a BdSL annotation.
- `sample50` (committed videos/) ≠ `pilot50_v1` (dataset/pilot50_v1/, selected from split S1).
- Indicative tags (question/negation/number) are word lists, not annotation.
- MediaPipe "left/right hand" may not be the signer's real left/right (G8).
- Old logs are "reported" until re-run.

## Locked decisions — do NOT re-open without the owner
- ADR-0003, 0006, 0007, 0008, 0012; ADR-0004/0005/0009/0010/0011/0013 as amended;
  ADR-0014–0021 (owner bullets Accepted; technical specifics Accepted in principle); ADR-0022–0024.

## Important environment / gotchas
- Run everything through the project environment: `uv run …` (see CLAUDE.md COMMANDS). Notebooks:
  choose the `.venv` kernel.
- Don't read research/papers/*.pdf. Don't add SIGN_LANGUAGE_DATA/, pilot copies or work/ to git.
- The repo is public: a commit is a publication (ADR-0017). Reviewer names never go into git.
- Annotation CSVs are UTF-8 with BOM; in Excel save as "CSV UTF-8" (REVIEW_GUIDE.md).
- `gloss-draft` refuses to overwrite a file with reviewed rows; never bypass this.
- OpenCV applies the rotation flag (verified 2026-10-22); PyAV does not report it (reported).
- Use a fresh HolisticLandmarker per video (earlier project: reuse crashed; reported).
- On Windows, multiprocessing code must sit under `if __name__ == "__main__"` (bdsl.cli does this);
  notebooks call `bdsl.cli.main`, whose worker functions live in importable modules.
- Quote paths with spaces. Log dataset inspections in dataset/initial_dataset/DATASET_WORK_LOG.md.
