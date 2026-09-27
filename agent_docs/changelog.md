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
