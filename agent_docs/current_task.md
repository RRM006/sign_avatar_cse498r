# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-21
**Phase:** Phase 2 — Design & pipeline decision. A full design plan is **proposed** (Session 2) and
waits for owner approval. After approval: the 5-day prototype (Phase 3).

## Where we are right now
- Scope unchanged (ADR-0007): Bangla sentence → BdSL on a 3D avatar, sentence-level.
- Read-only audit done 2026-10-21. Measured facts are in `test_log.md` (2026-10-21):
  - 5,010 videos (66.3 GiB) in `dataset/initial_dataset/SIGN_LANGUAGE_DATA/` (gitignored), 1:1 with
    `FinalSheet2.xlsx`.
  - 3,456 unique videos after exact dedup; 3,378 unique normalised sentences, 98.4% with one video.
  - 85.9% portrait after rotation; 5 of 80 sampled clips have irregular timestamps.
- Found: earlier project `D:\CSE498R\Sign_Language\CSE498R_v2\` (sign→voice; different scope). It has
  reusable MediaPipe code, model `.task` files and the duplicate CSVs. **No landmark features exist
  anywhere.**
- No gloss annotations, models, avatar or pipeline exist.
- Proposed design (NOT an ADR): `research/design_proposals/03_Stage1_Audit_and_Design_Plan_2026-10-21.md`.
  - Model A: Bangla → gloss (GRU; BanglaT5 later).
  - Model B: gloss → motion (GRU) on MediaPipe features, with pseudo-glosses on the full set.
  - Retrieval and mean baselines; the avatar as a display layer.

## The one thing we are doing next
👉 **Owner answers the blocking questions F1–F6 in `open_questions.md`:**
- F1 approve the direction;
- F2 gloss reviewer;
- F3 data copy/upload + repo visibility;
- F4 signer metadata;
- F5 avatar route;
- F6 Kaggle.

Record confirmed answers as ADRs (proposed ADR-0014–0018 in the plan, section L). Then, on the owner's
"go", do **Day 1 step 1 ONLY: environment check + configuration system.** Use the exact prompt in plan
section N. Ask before installing anything. Don't touch dataset files, build the manifest or select
videos in that step.

## Proposed 5-day prototype (not adopted until F1 is answered)
| Day | Milestone | Status | Done means |
|---|---|---|---|
| 1 | Env + config + manifest + pilot50 | ⬜ | env check 0 fail; manifest 5,010 rows; 50 copies hash-verified; sources unchanged |
| 2 | Gloss v0.1 + pilot features | ⬜ | 50/50 annotated with status; 50/50 extracted or failures logged; resume test passes |
| 3 | Splits + Model A | ⬜ | leakage tests pass; curves + metrics saved; resume works |
| 4 | Model B + baselines | ⬜ | masked-loss test passes; table vs B0/B1; hand energy reported |
| 5 | Avatar + end-to-end | ⬜ | sentence → video with versioned log; limitations written |

## Evidence rules
- Pilot numbers are labelled "pipeline test", never "generalisation".
- Gloss status is auto-draft / team-reviewed / expert-validated. Only the last counts as validated.
- Old logs (SESSION_LOG, CSE498R_v2 test_log) are "reported", not "measured", until re-run.

## Locked decisions — do NOT re-open
- ADR-0002 / ADR-0010 — the design stays open until the owner decides each item.
- ADR-0003 — not medical; no dialect focus.
- ADR-0004 / ADR-0009 — zero budget; compute roles (amendment proposed: F6).
- ADR-0005 — folder layout. ADR-0006 — AI does not read the paper PDFs.
- ADR-0007 — scope and deliverable. ADR-0008 — dataset facts. ADR-0011 — evaluation direction.
- ADR-0012 — literature review closed. ADR-0013 — conservative defaults and working style.

## Small open items
- E1: this desktop (DESKTOP-4NDR99B) has the RX 570 (8 GB) + 24 GB RAM. Owner to confirm.
- E2 inbox missing; E3; E4.
- F7–F11 in `open_questions.md`: colour-cluster labels, the old project, Bangla-SGP release,
  data-location wording in ADR-0009 / constitution, empty `misc/pdf/` folder.

## Important environment / gotchas
- Don't read `research/papers/*.pdf` (or the PDFs in the old project's `Paper sign/`).
- Don't add `SIGN_LANGUAGE_DATA/` or pilot copies to git.
- OpenCV 5.0 auto-applies the rotation flag. PyAV did not report it — test rotation explicitly.
- mediapipe pinned at 0.10.35 (1.1.1 exists; don't upgrade mid-project). PyAV segfaulted in one long
  loop; run it one file per process. No ffmpeg/ffprobe or torch installed yet.
- Many paths contain spaces; quote them.

## Reminders (the non-negotiables)
- Don't invent project facts; mark unknowns "(TBD — decide with owner)" or ask.
- The owner makes design decisions; record them only after an explicit yes.
- Keep evidence, owner requirements, proposals and future work labelled separately.
