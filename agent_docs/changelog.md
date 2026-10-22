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
