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


---

## Latest active task — 2026-11-11 — Session 11, Gates 1–6

এই append-only dated block এখন active handoff। উপরের 2026-10-24 next-step text historical; owner পুরোনো entries অপরিবর্তিত রাখতে বলেছেন।

- Gate 1 audit/plan শেষ। Gate 2-এ `demo --data` (default pilot50), `--out-root`, config-selected full k400 state, resolver/checks ও tests লিখিত। Runtime **not run**; Python এই assistant session-এ unavailable।
- Gates 3–4 শেষ: `versions/pilot50/` ও `versions/k400/`-তে 1,899 selected data/output file copy; 907,101,104 bytes; সব SHA-256 identical, mismatch 0। Original `work/`/`kaggle/` অক্ষত।
- Gate 5 শেষ: overview ও version READMEs, `HOW_TO_ADD_NEW_VERSION.md`, `RUN_AND_SHOW.md` তৈরি; মোট পাঁচটি new doc। k600 folder/config/data নেই।
- Gate 6: preview করা text শুধু memory files-এর শেষে append; ADR-0030 **Proposed**। `/versions/` ignore line owner-কে প্রস্তাব করা হয়েছে; `.gitignore` বদলানো হয়নি। AGENTS.md অপরিবর্তিত/untracked; git add/commit/push হয়নি।

### পরের একমাত্র step — Gate 7 runtime acceptance

Owner-এর Gate 7 go ও PC outputs-এর জন্য অপেক্ষা করুন। Assistant Python/pytest/demo চালাবে না। Owner-কে `versions/RUN_AND_SHOW.md`-এর existing-environment commands ব্যবহার করতে হবে: pytest; pilot “আমি স্কুল যাই”, seed 42; তারপর k400 validation Index 912 “আমার নানা অনেক ভালো”, seed 42; viewer ও actual output folders।

Owner-এর output ছাড়া success, regression pass, config-hash test pass বা local compatibility দাবি করবেন না। Current runtime status সব **not run**। Error এ exact output ধরে diagnosis করুন; install/download/retrain বা final test rerun নয়। নতুন outputs `--out-root` দিয়ে রাখুন; original outputs overwrite নয়।

Data/config নাম: display folder `k400`, CLI `kaggle400`। Full k400 state `kaggle/work/downloads/run1/k400/`; `kaggle/outputs/runs/` শুধু small summaries। k600 শুধু future guide; training workflow এখনো নির্ধারিত নয়।

Pilot fake review/Model A blocker (G10), signer-dependent সীমা, damped motion, expert-validation gap এবং final TEST lock আগের মতো বহাল। Session 11-এর নতুন entries append-only নিয়মে memory files-এর শেষে আছে।


---

## Latest active handoff — 2026-11-11 — Gate 7 pending

Gate 7 go পাওয়া গেছে। Assistant Python/pytest/demo চালায়নি। Saved TEMP pilot50/k400 outputs পাওয়া গেছে; hashes ও pilot JSON regression মেলে; দুইটির avatar viewer browser-এ দেখা গেছে। বিস্তারিত test_log.md-এর Gate 7 entry-তে।

পরের একমাত্র step: owner PC-তে existing environment দিয়ে `uv run pytest -q` চালিয়ে সম্পূর্ণ output দেবেন। Demo command transcripts থাকলে সেগুলোও দেবেন; না থাকলে RUN_AND_SHOW.md-এর commands নতুন --out-root-এ চালাবেন। কোনো install/download/final-test rerun নয়।

নতুন saved demos এখনও TEMP-এ; versions/-এ copy করা হয়নি। Overview-তে Gate 4-এর copies ও Gate 5-এর docs আছে। Viewer-এর পুরোনো pilot captions একটি known issue; ঠিক করার জন্য owner approval দরকার। ADR-0030 Proposed; /versions/ ignore line এখনও শুধু proposal। Gate 7 পুরোপুরি closed নয়।


---

2026-11-11 — Active goal changed by owner: copies নয়; canonical version folders, duplicate cleanup ও version-specific notebooks চান। Read-only migration plan প্রস্তুত; source/config/notebook edit বা move/delete হয়নি। পরের gate: reviewed plan অনুযায়ী path fixes ও unique-file moves; owner PC tests-এর পরে hash-verified redundant copies সরানো। Exact plan: C:/Users/User/AppData/Local/Temp/bdsl_restructure_plan_5e02d2e6-9d35-4997-b40e-e4206df30025/RESTRUCTURE_PLAN.md। Raw videos/ZIP ও k600 অপরিবর্তিত থাকবে। Python/tests not run।


---

## Latest active handoff — 2026-11-11 — Canonical migration implemented; PC acceptance pending

Owner-approved move/path-fix gate শেষ। 1,388 unique/variant file move হয়েছে, 1,227,494,033 bytes; immediate SHA-256 mismatch 0। pilot50 notebooks/state এখন versions/pilot50/; k400 notebooks/helpers/state versions/k400/; shared assets/index shared/-এ। Shared src/configs/web root-এ থাকে।

পরের একমাত্র step: owner PC-তে versions/RUN_AND_SHOW.md-এর pytest ও দুইটি seed-42 validation demo চালিয়ে সম্পূর্ণ outputs দেবেন। Assistant Python/pytest/demo চালাবে না। Default demo output এখন version-specific; --out-root explicit override। নতুন paths-এর runtime acceptance **not run**।

2,053 reviewed redundant source instances এখনও আছে; কিছু মুছিনি। Tests/validation গ্রহণযোগ্য হলে original proposed manifest অনুযায়ী প্রতিটি source/retained hash আবার মেলাতে হবে, তারপর cleanup gate। Move plan আবার চালাবেন না: source files ইতিমধ্যে সরানো হয়েছে; execution logs ব্যবহার করুন।

Execution reports: C:/Users/User/AppData/Local/Temp/bdsl_restructure_plan_5e02d2e6-9d35-4997-b40e-e4206df30025/execution_1648dc03bc5f4f48857f621630f95f58/ । Full diff পরে এই report folder-এ থাকবে। Raw videos/ZIP, AGENTS.md, .gitignore অপরিবর্তিত; k600 নেই। ভবিষ্যৎ compatible demo-এর default outputs আর pilot50 inherit করে না; full k600 training CLI এখনও প্রস্তুত নয়।


---

## Latest active handoff — 2026-11-11 — Retest after stale-test-path fix

Owner PC reported 5 failed / 203 passed / 3 skipped (53.55s). The five failures were stale kaggle/ path references in test_k400_misc.py. Fixed those plus related pilot/shared-index paths in two test files, and aligned the script safety assertion with its validation-only behavior. Runtime retest **not run**; do not claim success.

Next: owner reruns uv run pytest -q with the same offline/no-sync environment and sends the complete output. Then validation demos; only after acceptance may the duplicate cleanup gate proceed. No more moves or duplicate removal yet.


---

## Latest active handoff — 2026-11-11 — Pytest accepted; pilot demo next

Owner PC retest: 238 passed in 46.03s. Next: owner runs pilot50 sentence "আমি স্কুল যাই", seed 42, run gloss2motion_gloss_pilot50_20261022T133822Z, with --out-root ./versions/pilot50/demo_validation and shares the full output. Assistant must not run Python.

Then inspect the actual outputs/regression and proceed to k400 validation Index 912 and viewers. Duplicate cleanup is still pending; no further moves/deletes are authorized by the pytest result alone.


---

## Latest active handoff — 2026-11-11 — k400 PC demo next; cleanup conditionally authorized

Pilot50 real-checkpoint PC demo received and files verified: versions/pilot50/demo_validation/demo_20261111T150500Z/. Both motion JSONs exactly match the old reference. Owner pytest already reported 238 passed.

Owner explicitly requested k400 demo, then duplicate cleanup. Assistant must not run Python; next owner PC command uses kaggle400 validation Index 912 "আমার নানা অনেক ভালো", run gloss2motion_gloss_kaggle400_20261023T135437Z, seed 42, --out-root ./versions/k400/demo_validation. No post-migration k400 output exists yet.

After successful k400 artifact/viewer acceptance, proceed with the already authorized, reviewed cleanup scope; do not ask for the same cleanup permission again. Revalidate retained/source hashes and absolute paths immediately before removal, then critical hashes/counts. Current read-only preflight matches all 2,053 pairs / 911,823,762 bytes; zero files deleted. Retain protected raw data/ZIP and the non-identical corpus variant.


---

## Latest active handoff — 2026-11-11 — Local consolidation and reviewed cleanup complete

Completed: canonical pilot50/k400 folders, version notebooks/helpers, shared engine/assets/index, configs/output routing, owner PC pytest 238 passed, both real-checkpoint validation demos and browser viewers, reviewed duplicate cleanup. Removed 2,053 redundant files / 911,823,762 bytes and 194 empty directories; retained hashes/counts match, including 127 critical files. No raw videos/ZIP, checkpoints/settings/final-test lock, AGENTS.md or .gitignore changed. Root work/ and notebooks/ are gone; do not use their old paths.

Current demos:
- versions/pilot50/demo_validation/demo_20261111T150500Z/
- versions/k400/demo_validation/demo_20261111T151556Z/
Current commands/viewer URLs: versions/RUN_AND_SHOW.md. Assistant did not run Python; full pytest was not repeated after cleanup.

Next useful owner check: uv run pytest -q once after cleanup to catch any surviving legacy-path dependency. Do not rerun migration/removal scripts: their reviewed sources are already gone. Publishing/ignore policy still needs owner review because notebooks/helpers now live inside versions/. No git mutations; no k600 folder/config/data. Future full k600 training workflow remains separate work.


---

## Latest active handoff — 2026-11-11 — Scoped public commit/push authorized

The owner approved a safe scoped commit/push to the configured remote. `.gitignore` now excludes version-local data/features/checkpoints/run and demo state, the full dataset index, and model assets; source, docs, notebooks, tests, and safe aggregate results remain publishable. The large version state and local model assets are not staged. Workspace `AGENTS.md` is also excluded.

Post-cleanup Python/pytest/demo were not run by the assistant; the owner-reported 238 passed occurred before cleanup. No k600 folder/config/data exists.

Next: finish the staged-path safety audit, then commit and push to `origin/main`.
