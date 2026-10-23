# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-23 (Session 8, Step B in progress)
**Phase:** Phase 4 started as one owner-approved experiment: **kaggle400** (400 videos, real training on
Kaggle), folder `kaggle/`. Proposal 05 as a whole is still not approved.

## Where we are right now
- Step A done in the AI's cloud workspace (no desktop shell this session): `kaggle/` folder, code, notebooks
  00–09, tests, guide, PowerShell script. Files written into `D:\sign_avatar_cse498r`. Nothing copied,
  committed, uploaded or run on the desktop or on Kaggle yet.
- Split chosen (measured from manifest_v1 + S1 v0): 320 / 40 / 40 clips, 398 leakage groups, val OOV 20.7%,
  test OOV 12.1% of word tokens; leakage checks 1–7 PASS; checks 8–10 need the copies.
- Workspace test run (Linux, Python 3.12.3): 209 passed. The desktop run happens inside the script.
- Technical choices are **PROPOSED ADR-0028** (decisions.md) — owner confirmation pending.
- Desktop run 1 (2026-10-23 12:07): steps 1–4 PASS (selection identical on the desktop, 400/400 copies
  byte-identical, 5.94 GB, 10/10 split checks); step 5 failed 1 of 209 tests (Windows path separator in
  `k400.setup.restore`, fixed in the workspace); steps 6–7 not run. Details: test_log.md.
- Desktop run 2 (12:26): steps 1–4 PASS again (400 copies re-hashed, 10/10); step 5 failed 1 of 209
  (timing value inside the quality metrics made an exact resume comparison depend on luck; fixed in the
  workspace, 209 passed); steps 6–7 not run.

## The one thing we are doing next
👉 **Step B (re-run) — the owner runs the same command again in PowerShell:**
`powershell -ExecutionPolicy Bypass -File D:\sign_avatar_cse498r\kaggle\tools\run_local_steps.ps1`
and pastes the summary. Expected: 7 PASS lines; step 3 now says "already present: 400" (re-hashed, not
copied again); 209 tests pass; one local commit — not pushed; upload zip ≈ 5.95 GB. Then the AI checks it.

## After that
- Step C: Kaggle account, phone verification, GPU quota (record numbers → G3), private dataset `bdsl-k400`
  (GUIDE sections 1–4).
- Step D: notebooks 00 → 09, one at a time, the owner pastes each notebook's PASS/FAIL list.
- After Step D: download outputs, verify hashes, copy small results into `kaggle/outputs/`, update
  test_log with the real Kaggle numbers, commit locally (owner decides about push).

## Evidence rules
- kaggle400 results: small-scale, signer-dependent; test used once (FINAL_TEST_LOCK.json); measured vs
  estimated labels; low coordinate error ≠ correct BdSL; G0 = pseudo-gloss; Model A = agreement with the
  rule glosser; no human/expert validation.
- Pilot numbers stay "pipeline test". `TEST_…` runs (ADR-0025) are never results; `NFP_…` and `DRYRUN_…`
  runs are never results.

## Locked decisions — do NOT re-open without the owner
- ADR-0003, 0006, 0007, 0008, 0012; ADR-0004/0005/0009/0010/0011/0013 as amended;
  ADR-0014–0021 (owner bullets Accepted; technical specifics Accepted in principle); ADR-0022–0027.
- ADR-0028 is only PROPOSED.

## Important environment / gotchas
- Run everything through `uv run …`. Notebooks for Kaggle are in `kaggle/notebooks/` (import them on Kaggle).
- No `git push` (owner, 2026-10-23). The repo is public: a push is a publication (ADR-0017).
- Never `git add` kaggle/data videos, features, checkpoints, `kaggle/work/`, `kaggle.json`.
- Line endings: `core.autocrlf=true` (G12 open); kaggle400 lock hashes ignore line endings by design.
- On Windows (PowerShell 5.1), multi-line commit messages: `git commit -F <file>` (the script does this).
- Notebook 07 must run only once; a new version without the earlier output attached cannot see the lock (G15).
