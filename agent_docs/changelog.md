# changelog.md — Session-by-Session History

> The running memory of the project. **Newest entry at the top.** One short entry per session.
>
> Template for each entry:
> ```
> ## Session N — YYYY-MM-DD — <short title>
> - Did: <what we actually did or changed>
> - Decided: <any decision; also add it to decisions.md>
> - Broke / problem: <anything that failed or is fragile>
> - Deferred: <what we chose NOT to do yet, and why>
> - Next: <the one thing to do next — also update current_task.md>
> ```

---

## Session 9 — 2026-10-23 — kaggle400 on Kaggle: upload, notebooks 00–09, final test, results downloaded
- Did: Owner did everything on Kaggle, step by step; the AI checked each result and recorded it (test_log):
  - C1 account + phone verified; C2 limits recorded (G3: T4 x2, 30 GPU h/week, 12 h per run; disk 20.9 GB
    measured by notebook 00); C3/C4 PRIVATE dataset `bdsl-k400` Version 1 (535 files, 5.94 GB, unzipped — G17).
  - Notebooks 00–09 all PASS (Python 3.13, MediaPipe main route; 01 upload 532/532 identical + 10/10 split
    checks; 02 400/400 clips in 56.8 min, feat_ver = pilot; 03 glosses identical; 04–06 trained on T4;
    07 Version 2 froze 04/05/06 and ran the single TEST evaluation; 08 12 tables + 8 figures; 09 avatar export).
  - Outputs downloaded through a helper zip notebook, verified (2,447/2,448; STATE.json mismatch explained and
    proven harmless), small results copied into `kaggle/outputs/` + `kaggle/processed/qc/`, privacy scan
    (only `env/mediapipe_route.json` holds the Kaggle username → kept out of Git), `RUN1_NOTES.md` written.
  - Safety stop added to notebook 07 (+ generator + test; 210 tests in the workspace).
- Decided (owner): freeze and test now (G19); re-run 07 once after the failed first attempt and report it
  (option a); keep `mediapipe_route.json` out of Git; one local commit, no push → ADR-0029.
- Results (measured, 40 test clips): Model B beats B0 and B1 on every position/DTW metric (CIs exclude 0;
  DTW body 0.181 vs 0.199 / 0.198) but its motion is strongly damped (velocity 0.14–0.18, hand energy
  0.03–0.05 of real) and over-fits early; G0 gloss input = Bangla word input. Model A test WER vs G0 19.7
  (agreement with the rule glosser only).
- Broke / problem: notebook 07 Version 1 ran without Internet and reached the test code before crashing (no
  result); progress logs silent until a step ends; skeleton videos not browser-playable (`mp4v`); STATE.json
  hashed before its last update; Kaggle has no "download all outputs" button (G18 items 4–8).
- Deferred: push (owner); G18 fixes (need a new commit + package); G16 (ADR-0028); paper write-up.
- Next: the owner runs the commit block (tests first, then one local commit, no push) and pastes the output.

## Session 8 (part 2) — 2026-10-23 — kaggle400 Step B: desktop script passes, upload zip ready
- Did: Wrote the 91 Step A files into `D:\sign_avatar_cse498r`. The owner ran
  `kaggle/tools/run_local_steps.ps1` three times (logs in `kaggle/work/`, gitignored):
  - Run 1 (12:07): selection reproduced identically on the desktop; **400/400 copies byte-identical**
    (5.94 GB, sources unchanged); `verify_split --require-videos` **10/10 PASS**; tests 208/209.
  - Run 2 (12:26): steps 1–4 PASS again (copies re-hashed, not re-copied); tests 208/209 (another test).
  - Run 3 (12:34): **all 7 steps PASS** — 209 tests; local commit **`933e903`** (93 files, not pushed);
    upload zip `kaggle/work/upload/bdsl-k400-933e9032.zip`, 5,938,005,200 bytes (Windows shows 5.53 GB),
    535 files, re-hashed PASS.
  - Fixes between runs (all tests pass in the workspace after each): `k400.setup.restore` reports paths with
    `/` on every OS; a re-run of the copy step replaces its SPLIT_REPORT section and adds a dated
    "Re-check" line to the DATASET_WORK_LOG entry; training time moved out of the per-seed quality
    metrics into `metrics["train_seconds"]` (both trainers, report T3, notebooks 04/05 one line each);
    new regression assertions in `test_k400_split.py` / `test_k400_training.py`; older tests unchanged.
  - Found the zip's `code/` has CRLF text files (desktop git `core.autocrlf` + `git archive`); a workspace
    smoke run of all notebooks on a package built the same way gave identical PASS/FAIL lines → harmless.
  - Started Step C: gave the owner the C1 instructions (Kaggle account + phone verification, GUIDE §1).
- Decided: Nothing new by the owner. (Running the script, the local commit and the zip were already
  approved in Step A.) ADR-0028 is still PROPOSED.
- Broke / problem: Two desktop test failures, both bugs from Session 8, fixed: a Windows path separator in a
  report message; a wall-clock value inside metrics that the older resume tests compare exactly (they
  passed only by luck). Also: one file write to the desktop reported success but left the previous
  content of `test_log.md` and `current_task.md`; found at the end of the session and rewritten, with every
  saved file read back and compared. The guide still says "about 5.95 GB" (Windows shows 5.53 GB for the same
  5.94 GB zip) — left as is, so code paths keep matching `933e903` (G18).
- Deferred: The guide size text and a `core.autocrlf=false` archive for later packages (G18; need a new
  commit + package); committing the agent_docs / DATASET_WORK_LOG edits made after `933e903` (next local
  commit, owner's OK); push (owner decides).
- Next: Step C1 — the owner creates or logs into the Kaggle account and verifies the phone (GUIDE §1), then
  reports "C1 done"; then C2 (GPU quota numbers → G3), C3 (PRIVATE dataset `bdsl-k400` from the zip), C4.

## Session 8 — 2026-10-23 — kaggle400: the 400-video Kaggle experiment folder (Step A)
- Did: Built `kaggle/` (README, beginner Kaggle guide, pinned requirements, data/processed/notebooks/
  src/tools/outputs with READMEs) and the code behind it, in the AI's cloud workspace (no shell on the
  desktop this session; files were written into the project folder):
  - 400-clip selection from manifest_v1 + S1 v0 (seed 20261023): 320/40/40, every clip in its S1
    partition, colour cluster kept together in train, 10 + 10 minimal-pair held-out clips with train
    siblings, stratified fill; manifests with a reason per clip, SPLIT_REPORT.md, SPLIT_SUMMARY.png.
  - `kaggle/src/verify_split.py` (10 PASS/FAIL checks), SHA-256-verified copy step, line-ending-
    independent SPLIT_LOCK.json, private-dataset package (git archive of a clean commit + allow-list).
  - bdsl: CUDA device support in both training loops, `--data kaggle400`, `--max-steps`, `--set`,
    `--device`, `--not-for-paper`, test-split guard, `freeze` / `evaluate --split val` /
    `evaluate --final` with FINAL_TEST_LOCK.json, bootstrap 95% CIs, run registry, env.json,
    clean-code rule, B1 excludes exact copies and shared-segment partners, Model A on G0 references.
  - Notebooks 00–09 (Kaggle), report (tables CSV/MD/LaTeX, figures, RESULTS_SUMMARY.md), avatar export.
  - `kaggle/tools/run_local_steps.ps1` for the owner: selection check → copy 400 videos → verify →
    tests → one local commit (no push) → upload zip.
- Decided: Owner instructions in chat (2026-10-23), recorded as stated: copy 400 videos into
  `kaggle/data/`; upload videos + features + metadata + code (`code/` from a clean commit) to a PRIVATE
  Kaggle dataset, this experiment only; do everything on Kaggle incl. MediaPipe extraction (local
  extraction only as a backup); GPU support; refuse dirty result runs or mark NOT FOR PAPER; no push;
  Model A labelled "agreement with the rule glosser (G0 pseudo-gloss)"; notebook 09 only after the test
  lock; known split limits in SPLIT_REPORT.md; line-ending-independent lock hashes. Technical design
  choices by the AI are written as **PROPOSED ADR-0028** in decisions.md (not accepted yet).
- Broke / problem: found and fixed while testing — the training lock check opened the test manifest;
  two runs started in the same second shared a folder (the second would have resumed the first);
  `--not-for-paper` did not mark runs from clean code; prediction needed targets; MediaPipe log noise;
  big scratch files would have been saved as Kaggle output. Not possible this session: any run on the
  desktop (no shell) or on Kaggle (owner's account).
- Deferred: Kaggle runs (owner), real gloss review (G10), shared-segment scan (G2), Colab.
- Next: Owner runs `kaggle/tools/run_local_steps.ps1` and pastes the output (Step B); then Kaggle
  account / GPU quota / private dataset (Step C); then notebooks 00 → 09 (Step D).

## Session 7 — 2026-10-22 — Publish audit reports and prototype work
- Did: At the owner's request, committed the Session 6 reports and documentation as `62e719e`, then
  pushed `main` to `origin/main` (`edadec9..62e719e`). This also published the six commits already
  ahead of origin, including the Day 3 TEST run and mock annotation rows; the rows are explicitly
  marked `is_mock=true` and "TEST DATA: ... not video-verified".
- Decided: No standing push-policy decision or ADR; this push was explicitly requested by the owner.
- Broke / problem: None during commit or push. `git diff --check` passed; no test suite was run for
  the documentation-only commit (the prior audit recorded 140 passing tests).
- Deferred: Owner review of the reports and Phase A decision register; push policy, G12, G13 and G14
  remain open.
- Next: Owner reviews both reports and answers the Phase A decision register in proposal 05,
  Appendix C.

## Session 6 — 2026-10-22 — Read-only audit; pilot report and full-dataset plan (Markdown + PDF)
- Did: Stage 1 read-only audit (repo, work/ artifacts, git, hardware, PDF tools): manifest/split/pilot
  hashes match their meta; 50/50 pilot copies match; leakage re-check 0/0/0 on S1 v0; all 60
  checkpoints load; pytest 140 passed; gloss-validate exits 1 (normal) / 0 (--allow-test-data).
  Stage 2 (owner-approved): research/reports/ with PILOT_TEST_VERSION_COMPLETE_REPORT.{md,pdf},
  FULL_DATASET_EXECUTION_PLAN.pdf, figures/ (7 SVG), build_reports.py; research/design_proposals/
  05_FULL_DATASET_EXECUTION_PLAN.md (PROPOSAL). PDFs: system Python markdown-it-py 4.2.0 + headless
  Chrome; checked with pdf.js in the browser pane.
- Decided: No design decision (the owner approved the report files and toolchain: process only, no ADR).
- Broke / problem: Found — core.autocrlf=true without .gitattributes changes tracked-CSV hashes
  (annotation CSV: working copy 9cd37d3d…, committed a0be4e91…); every run.json has dirty=True; the
  training code has no GPU device support; notebooks 01–06 never executed; README.md status stale.
  Fixed in my own build script: image paths, cached figures, chart font.
- Deferred: All implementation in proposal 05; committing the reports (public repo); README,
  .gitattributes, device support (owner decisions).
- Next: Owner reviews both reports and answers the Phase A decision register (proposal 05, Appendix C).

## Session 5 (continued) — 2026-10-22 — Day 5: retargeting + avatar viewer + end-to-end demo
- Did: On the owner's go (Steps 1 and 2, defaults; G11 = Model B and B1 side by side):
  - added `src/bdsl/avatar/` (`postprocess` One-Euro + hand rest blend; `retarget` rt-v1 direction-
    based solver; `export` motion JSON + skeleton video; `demo` end-to-end) and
    `bdsl.cli demo --sentence`;
  - added `web/avatar_viewer/` (three 0.186.1 + three-vrm 3.5.5 via jsDelivr; side-by-side
    avatars, labels, mirror toggle, record to .webm), `.claude/launch.json` (local preview server),
    notebook 06 and 15 tests (140 pass);
  - downloaded the approved CC0 `base_female.zip` (13,149,860 bytes) → `work/models/vrm/Base_Female.vrm`
    (gitignored);
  - ran the demo for sentence 3246 and checked the viewer in the built-in browser (`test_log.md`).
- Decided: ADR-0027 (owner): G11 = both motions side by side, labelled; the Day 5 defaults.
- Broke / problem: Four bugs in my own new code were found and fixed during the run (`test_log.md`).
- Deferred:
  - A BdSL-competent review of the demo.
  - The real Day 3 run (G10).
  - Pushing (`main` holds the fake-labelled Day 3 rows).
  - Phase 4 planning.
- Next: Owner reviews the demo; decide the Phase 4 / Week 2 plan (design doc 04 §G).

## Session 5 (continued) — 2026-10-22 — Day 4: Model B pilot (gloss → motion) + ablation T + B0/B1
- Did: On the owner's go (Steps 1 and 2, with my recommendations):
  - added `src/bdsl/features/normalize.py`: 208-value frames, part masks, hand gaps ≤ 5 frames
    interpolated, standardiser;
  - added `src/bdsl/eval/motion_metrics.py` (MPJPE, DTW-MJE, duration, velocity/jerk, hand energy,
    diversity) and B0/B1 in `models/baselines.py`;
  - added the NAR Transformer `models/gloss2motion.py` (2,663,441 parameters) with a masked loss, and
    `models/train_gloss2motion.py`;
  - added `bdsl.cli train-gloss2motion [--input gloss|text]`, notebook 05 and 14 tests (125 pass).
  Ran overfit 1 and 40, 3 seeds × {gloss, text} and a real kill-and-resume test (`test_log.md`). No
  installs.
- Decided: ADR-0026 (owner): 9 named upper-body points; MediaPipe hand labels as given (G8); no clip
  excluded (G9); loss weights hands ×2, λ_v 0.5, λ_len 0.1.
- Broke / problem: Found and fixed during the run:
  - the decoder's time code was too coarse to tell neighbouring frames apart;
  - MediaPipe Holistic hand "world" points are not hand-centred: the wrist is ≈ 0.55 m from their
    origin. The Day 2 layout note was wrong; hands are now made wrist-relative.
  The runs from before the hand fix are in `work/runs/_superseded_day4_hand_offset/`.
- Deferred: Day 5 (retarget + viewer + demo). Which motion drives the demo is new open question G11.
- Next: Day 5 plan — show it and wait for the owner's go.

## Session 5 — 2026-10-22 — Day 3 Step 1 as a labelled TEST run; merged into main
- Did: Checked the pilot review twice; both versions failed `gloss-validate`.
  - First version: role `reviewer` was not allowed, and the notes said "video not checked".
  - Second version: all 50 rows had `is_mock=true` and the notes "TEST DATA … not video-verified".
  On the owner's request, a local practice run on branch `test-run-fake-review`:
  - added `--allow-test-data` (off by default) to `gloss-validate`. `validate()` now also refuses
    reviewed rows whose notes say "not video-verified";
  - installed sacreBLEU 2.6.0 (+5 small dependencies; pinned in the `train` extra);
  - built Day 3 Step 1: `bdsl.cli train-text2gloss` (G0 vs A-GRU, tag prefix tokens, 3 seeds, early
    stopping, beam 4, checkpoints with resume, guard), `src/bdsl/{models,eval}/` and notebook 04;
  - ran the guard, the overfit tests, the 3-seed TEST run and a real kill-and-resume test
    (`test_log.md`); 111 tests pass.
  The owner then had the branch merged into `main` (merge `0eef7c6`, not pushed).
- Decided: ADR-0025. The practice run, including the fake annotation rows, is merged into `main`. The
  test option stays off by default; nothing trained with it is a Model A result.
- Broke / problem: Two bugs in my own Day 3 code were found by the run and fixed:
  - the overfit stop used greedy decoding, while the final score uses beam search;
  - resume ignored the run's original seeds.
  The superseded TEST run folders stay in `work/runs/` (gitignored).
- Deferred:
  - A real team review of the 50 pilot glosses (G10) and the real Model A run.
  - Pushing (a push would publish the fake-labelled annotation rows).
  - agent_docs updates for anything beyond Day 3.
- Next: Day 4 (Model B) plan — show it and wait for the owner's go.

## Session 4 — 2026-10-22 — Publish the approved Day 1–2 work
- Did: Ran `uv run pytest` (93 passed). Committed and pushed the implementation, pilot metadata,
  annotations, design/docs and session memory authorized by the owner.
- Decided: The owner authorized committing and pushing the current work.
- Broke / problem: None during validation or publication.
- Deferred: Day 3 and all other work remain subject to the owner's next-step decision in
  `current_task.md`.
- Next: Owner decision on how Day 3 proceeds (current_task.md: review first, swap Day 3/4, or a
  labelled auto-draft pipeline test), then the matching "go".

## Session 3 — 2026-10-22 — Phase 1 design review; docs recorded; Days 1–2 done
- Did: Read-only review of all agent_docs, ADRs, plan 03, the dataset READMEs and the work log.
  Re-checked:
  - git and the GitHub visibility (public);
  - `SIGN_LANGUAGE_DATA/` (5,010 MP4 + SESSION_LOG.md + a byte-identical copy of FinalSheet2.xlsx);
  - the Python setup (3.14 only; no 3.12);
  - the colour cluster (SHA-256 + frame-difference profile);
  - sentence/token statistics;
  - the 50 sample-clip headers;
  - the earlier project's model files and notes.
  Web-checked mediapipe 0.10.35 wheels, the Holistic API outputs, three-vrm, Kalidokit, VRoid CC0
  models, BanglaT5 and (secondary sources only) Kaggle limits. Wrote design review 04 and the
  documentation change set; the owner approved both, and the doc edits were applied.
  Day 1 Step 1 (on the owner's go and install approval):
  - installed CPython 3.12.13 and the pinned packages into `.venv` (uv, `uv.lock`);
  - downloaded the official `holistic_landmarker.task` (SHA-256 pinned);
  - added `pyproject.toml`, `configs/`, `src/bdsl/{config,paths,io,env}.py`, `tests/` (30 tests),
    `notebooks/00_env_check.ipynb`, and 5 `.gitignore` entries.
  Env check: 8/8 pass (`test_log.md`).
  Day 1 Step 2 (on the owner's go, plan and install approval):
  - added pandas/openpyxl, `src/bdsl/{text,data}/` and `src/bdsl/cli.py` (54 tests);
  - built manifest v1 (5,010 rows, 3,456 unique files, 3,378 sentences, 3,376 groups, 0 conflicts);
  - built split S1 v0 (no leakage found);
  - selected pilot50_v1 (option B) and copied it (50/50 SHA-256 OK) to `dataset/pilot50_v1/`.
  Sources unchanged.
  Day 2 Step 1 (on the owner's go and plan approval; no new packages):
  - added `src/bdsl/features/` and `bdsl.cli extract` (67 tests);
  - extracted MediaPipe features for the 50 pilot copies in VIDEO and IMAGE mode (50/50 each,
    0 failures; no face mesh or image data stored);
  - wrote the QC and the mode comparison; the kill-and-resume test passed (array-identical).
  Day 2 Step 2 (on the owner's go and plan approval, with R5; no new packages):
  - added `src/bdsl/text/{gloss_rules,annotations}.py`, `bdsl.cli gloss-draft | gloss-validate`
    and `annotations/` (convention v0.1, review guide, empty reviewer register);
  - wrote 50 G0 auto-drafts (deterministic, validation clean, 93 tests).
  End of session: added thin notebooks `01_manifest`, `02_extract`, `03_gloss` (the same `bdsl` code
  as the CLI; saved without outputs; structurally checked, not executed).
- Decided: ADR-0014–0021. Owner bullets Accepted; technical specifics Accepted in principle. The
  public repo is intentional, with permission to make the dataset public (ADR-0017). G4 answered:
  Python 3.12 + mediapipe 0.10.35 works. ADR-0022: pilot held-out rule, option B. ADR-0023: VIDEO
  mode for extraction (feat_ver fa89892d4908). ADR-0024: G0 v0.1 with R5; annotations in `annotations/`.
- Broke / problem:
  - The first env-check run failed `torch_devices` because of a wrong constant in the check (fixed;
    torch was fine).
  - Step 2: three bugs in my own code, caught by tests or review before the real run (fixed).
  - Day 2 Step 2: one bug in my own tests (fixed).
  - The first pilot rule gave 1/10 held-out clips with seen words only (superseded by option B).
  - Found: edited "shared-segment" clips are a leakage risk; Kalidokit is deprecated; hands are
    often missing (right hand 35.7% of frames); MediaPipe's left/right may be mirrored (G8).
- Deferred: Day 3 and later, until the owner's go. The team review of the 50 drafts (G10, owner).
  Commit/push (owner decides): all work since commit 1809048 is uncommitted, including `annotations/`
  (a push publishes it). Reuse licence (G1), deadline (G6), hand sides (G8) and QC thresholds
  (G9) need owner input. Kaggle/Colab environment checks. Full shared-segment scan (G2, Week 2).
  Full-set extraction.
- Next: Owner decides how Day 3 proceeds (current_task.md: review first, swap Day 3/4, or a labelled
  auto-draft pipeline test), then the matching "go".

## Session 2 — 2026-10-21 — Read-only audit + Stage-1 research design plan
- Did: Read all agent_docs, ADRs, analyses 01 and 07, design proposal 02, the dataset logs, and the
  earlier project `D:\CSE498R\Sign_Language\CSE498R_v2\` (found this session; sign→voice scope). Re-measured
  dataset facts read-only:
  - the sheet and the video ID mapping;
  - duplicate CSV consistency, plus SHA-256 spot-checks;
  - header metadata of all 5,010 files;
  - rotation via OpenCV;
  - packet timestamps on 80 clips.

  Results are in `test_log.md`. Checked hardware and software read-only, and verified Bangla-SGP, the
  mBART text-to-gloss paper, MediaPipe Holistic, torch-directml and avatar tools on the web. Wrote the
  plan `research/design_proposals/03_Stage1_Audit_and_Design_Plan_2026-10-21.md` (PROPOSAL). Corrected
  the wrong "only the 50-clip sample is in the repo" line in `CLAUDE.md` and `dataset/README.md`. Added
  the `DATASET_WORK_LOG.md` entry.
- Decided: Nothing. No owner decision was given. The proposed ADR-0014–0018 wait for F1–F6.
- Broke / problem:
  - PyAV 17.1 segfaulted during a long in-process packet-demux loop; it worked one file per process.
  - PyAV did not report rotation, so OpenCV was used.
  - Old claims are contradicted: "all VFR" and "0 badly VFR" (5/80 irregular), and stale docs
    (reorganisation is committed, no leftover branch/worktree, the full set is inside the repo folder).
  - The 50 sample videos (identifiable faces) are pushed to GitHub; repo visibility unknown.
- Deferred: All implementation (owner rule: wait for "go"). Full SHA-256 re-hash, pHash re-run,
  MediaPipe re-runs, signer inspection. ADR-0009 / constitution wording fixes (need an owner decision).
- Next: Owner answers F1–F6, then "go" for Day 1 step 1 (environment check + config only).

## Session 1 — 2026-09-27 — Finalize setup: record owner answers, retire old worktree
- Did: Confirmed the session runs in the real folder (not a worktree). Verified the owner's manual
  fixes: dataset files are byte-identical moves, `FinalSheet.xlsx` is in `superseded/`, `videos.txt`
  is gone, `README.md` / `dataset/README.md` / `research/papers/README.md` match the answers, and the
  wrong medical/dialect context is removed from analyses 01–07 (08 needed none). Recorded answers
  A1–D4 in `decisions.md` and `open_questions.md`. Updated stale facts in `CLAUDE.md`,
  `constitution.md`, `codebase_map.md`, `milestone_log.md`. Added a one-line D1 citation note to
  analysis 05 (original text kept). Ran `git worktree prune`: git no longer tracks the old worktree.
- Decided: ADR-0007 (scope/deliverable), ADR-0008 (dataset), ADR-0009 (storage/compute roles),
  ADR-0010 (C1–C4 stay open; MediaPipe Holistic interim only), ADR-0011 (evaluation direction),
  ADR-0012 (literature closed; IsharaKotha citation; analyses cleaned), ADR-0013 (defaults kept).
- Broke / problem: The empty folder `.claude/worktrees/bangla-sign-avatar-setup-699b03` could not be
  removed ("Device or resource busy"), probably held by the old Claude session. Not forced. The branch
  `claude/bangla-sign-avatar-setup-699b03` (same commit as `main`) was left in place.
- Deferred: `open_questions.md` E1–E4 (RX 570 machine, missing `new_project_intake/`, two "Medical"
  rows in analysis 07, video-sharing rule wording). Nothing committed.
- Next: End-to-end pipeline/system design research based on the confirmed scope and dataset.

## Session 0 — 2026-09-27 — Project bootstrap and folder organization
- Did: Inspected every folder. Read `BOOTSTRAP_PROJECT_PROMPT.md`, all templates, all 8 paper analyses,
  the paper-reading form and the dataset sheets. Only a first-page identity check was done on the PDFs.
  Created `CLAUDE.md` + `agent_docs/` (constitution, session_protocol, current_task, changelog,
  milestone_log, decisions, codebase_map, test_log, plus `open_questions.md`). Moved papers, analyses,
  the reading form and the dataset into `research/` and `dataset/` with `git mv`. Renamed analysis 08
  (it had the same name as 07 but different content). Removed the medical and dialect lines from the
  paper-reading form. Added `research/paper_analyses/README.md` (index + scope warning). Deleted the
  generic `templates/` folder.
- Decided: ADR-0001 (memory system), ADR-0002 (design stays open), ADR-0003 (not medical, no dialects),
  ADR-0004 (zero budget; Colab + local machine), ADR-0005 (folder layout), ADR-0006 (AI doesn't read the
  PDFs).
- Broke / problem: Nothing broke. Fragile: 50 videos (~767 MB) are committed straight to git. The
  existing analyses still contain wrong medical/dialect context.
- Deferred: All design decisions (pipeline, model, data strategy, sign representation, avatar,
  evaluation), per the owner. Also deferred: cleaning the analyses (D3) and deciding which dataset sheet
  is current (B2).
- Next: First research/design session. The owner gives first ideas and answers A1, B1 and B5 in
  `open_questions.md`.
