# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-09-27
**Phase:** Phase 2 — Design & pipeline decision (design not decided)

## Where we are right now
- Scope is settled (ADR-0007): Bangla text sentence → BdSL on a 3D avatar; sentence-level translation
  with BdSL grammar/word order; no speech input, no sign → text. Deliverable: report + literature review
  + trained model + results, aimed at a publishable paper.
- Dataset is settled (ADR-0008, ADR-0009): team-owned; `FinalSheet2.xlsx` current; one signer per clip;
  videos are primarily training data (pose/landmarks → sign-generation model); a held-out evaluation
  split must be reserved; full set on desktop / Drive → Colab.
- Literature review is complete (ADR-0012). The analyses are cleaned of the wrong medical/dialect
  context.
- Still **not decided** (ADR-0010): sign representation, avatar technology, text → sign mapping, sign
  lexicon. MediaPipe Holistic is only the interim landmark-extraction step. Fingerspelling is the
  recommended fallback for unknown words, still to be validated.
- Evaluation direction: human (experts / deaf signers / interpreters) + an automatic metric (ADR-0011);
  details open.

## The one thing we are doing next
👉 **End-to-end pipeline/system design research based on the confirmed project scope and dataset.**
Compare options for C1–C5 in `open_questions.md` (using the paper analyses and
`research/design_proposals/`, which are proposals only). Present trade-offs and a recommendation;
the owner decides. No implementation code.

## Locked decisions — do NOT re-open
- ADR-0002 / ADR-0010 — the design stays open until the owner decides each item.
- ADR-0003 — not medical; no dialect focus.
- ADR-0004 / ADR-0009 — zero budget; Colab training, desktop full data, laptop code/small samples.
- ADR-0005 — folder layout. ADR-0006 — AI does not read the paper PDFs.
- ADR-0007 — scope and deliverable. ADR-0008 — dataset facts. ADR-0011 — evaluation direction.
- ADR-0012 — literature review closed; cite IsharaKotha as arXiv:2511.16896 (2025).
- ADR-0013 — conservative defaults and working style kept.

## Small open items to raise with the owner when convenient
- `open_questions.md` E1–E4: which machine has the RX 570; the missing `new_project_intake/` folder;
  two leftover "Medical" rows in analysis 07; wording of the video-sharing rule.
- Leftover git branch `claude/bangla-sign-avatar-setup-699b03` (same commit as `main`) and the empty,
  locked folder `.claude/worktrees/bangla-sign-avatar-setup-699b03` (see `changelog.md`, Session 1).

## Important environment / gotchas
- Don't read `research/papers/*.pdf`. Use `research/paper_analyses/`.
- Don't add the full video set to git. Only the 50-clip sample is in the repo.
- Many paths contain spaces. Quote them in shell commands. On Windows, a folder can't be renamed or
  removed while a process has it as its working directory.
- The reorganization (moves/deletions) is staged but **not committed** yet; `CLAUDE.md` and
  `agent_docs/` are untracked.

## Reminders (the non-negotiables)
- Don't invent project facts; mark unknowns "(TBD — decide with owner)" or ask.
- The owner makes design decisions; record them only after an explicit yes.
- Keep evidence, owner requirements, proposals and future work labelled separately.
