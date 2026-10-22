# current_task.md — What We Are Doing RIGHT NOW

**Date:** 2026-10-22 (end of Session 6)
**Phase:** Phase 3 — 5-day prototype done as a pipeline test (milestones 5–7, 9, 10 ✅; milestone 8
🟨, Day 3 run only in TEST mode on fake review data, ADR-0025). Phase 4 (full dataset) is planned as
**proposal 05 — not approved**. Implementation runs one owner-approved step at a time.

## Where we are right now
- Session 6 was a read-only audit plus two documents (owner-approved):
  - `research/reports/PILOT_TEST_VERSION_COMPLETE_REPORT.{md,pdf}` — evidence-based record of the pilot.
  - `research/design_proposals/05_FULL_DATASET_EXECUTION_PLAN.md` + `research/reports/FULL_DATASET_EXECUTION_PLAN.pdf`
    — step-by-step plan (Phases A–P), a PROPOSAL.
  - Figures in `research/reports/figures/`; rebuild the PDFs with `python research/reports/build_reports.py`
    (system Python with markdown-it-py; headless Chrome).
- The reports and Session 6 doc updates are **not committed**. `main` is 6 commits ahead of
  `origin/main` and not pushed.
- Audit findings needing owner decisions: G12 line endings (`.gitattributes`), G13 GPU device support
  in the training code, G14 clean-commit rule for result runs; `README.md` status is out of date.
- Annotations: 50 pilot rows, all fake on purpose (`is_mock=true`); 0 real reviews (G10).
- 140 tests pass.

## Start of the next session (after the standard start-of-session reading)
1. `git status` / `git log --oneline -5`: `main` ahead of `origin/main` by 6 or more; the reports and
   Session 6 doc edits present but uncommitted. If not, stop and tell the owner.
2. `uv run pytest` → expected 140 passed.

## The one thing we are doing next
👉 **Owner reviews both reports and answers the Phase A decision register (proposal 05, Appendix C):
G6 deadline, G10 reviewers, G3 Kaggle account, push policy, G12 `.gitattributes`, G13 device support,
G14 clean-commit rule.**

No implementation step is authorised. Committing the reports (the repository is public) also needs the
owner's go.

## Evidence rules
- Pilot numbers are "pipeline test", never "generalisation". All results are signer-dependent.
- `TEST_…` runs (ADR-0025) are never reported as results.
- Gloss statuses: auto_draft / team_reviewed / expert_validated / rejected. Only a registered reviewer
  sets a reviewed status; the AI never does. Mock rows are refused by default.
- G0 output is a pseudo-gloss, never a BdSL annotation.
- Proposal 05 is a plan, not a decision; its estimates are labelled [ESTIMATE].

## Locked decisions — do NOT re-open without the owner
- ADR-0003, 0006, 0007, 0008, 0012; ADR-0004/0005/0009/0010/0011/0013 as amended;
  ADR-0014–0021 (owner bullets Accepted; technical specifics Accepted in principle); ADR-0022–0027.

## Important environment / gotchas
- Run everything through `uv run …` (CLAUDE.md COMMANDS). Notebooks: the `.venv` kernel.
- Don't read research/papers/*.pdf. Don't add SIGN_LANGUAGE_DATA/, pilot copies or work/ to git.
- The repo is public: a push is a publication (ADR-0017). Reviewer names never go into git.
- Line endings: `core.autocrlf=true` changes tracked-CSV byte hashes on checkout (G12).
- A PDF open in Acrobat Reader blocks the report rebuild; quit Acrobat fully first.
- On Windows (PowerShell 5.1), pass multi-line git commit messages with `git commit -F <file>`.
- Log dataset inspections in dataset/initial_dataset/DATASET_WORK_LOG.md.
