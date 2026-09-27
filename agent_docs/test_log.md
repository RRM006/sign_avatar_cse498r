# test_log.md — What Was Tested + Results

> Records what we tested or verified, how, and the result, including failures. This makes progress
> verifiable.
>
> Template for each entry:
> ```
> ## YYYY-MM-DD — <area/module> — <what was tested>
> - Setup: <how it was tested; tools/versions; environment; data used>
> - Metric(s) / checks: <what was measured or verified>
> - Result: <the numbers / pass-fail / observations>
> - Notes: <what helped or hurt; errors; next idea>
> ```

---

## What we care about (per area)
**(TBD — decide with owner.)** The evaluation method is not chosen yet (ADR-0002). Options found in the
literature are listed in `open_questions.md` C5. They are candidates, not decisions.

## Planned test cases
None yet. There is no system to test. Add test cases once the design is chosen.

---

## 2026-09-27 — Repository — Real-folder verification + worktree removal (Session 1)
- Setup: `git rev-parse`, `git worktree list`, `git status`, `git diff --cached -M --name-status`,
  `find`, `grep` in `C:/Workspace/NSU/sign_avatar_cse498r` on branch `main`.
- Metric(s) / checks: session location; dataset files unchanged; analyses cleaned (D3); references to
  the old worktree; worktree removal.
- Result: Session ran in the real folder (`.git` is the main git dir). Dataset: 53 files are 100%
  renames (3 sheets + 50 videos), `videos.txt` deleted, `dataset/README.md` added. Analyses 01–07 were
  edited to remove the medical/dialect context (similarity 87–99%); 08 is a 100% rename. Remaining
  medical/dialect mentions are paper findings, except two "Medical" table rows in 07 (flagged, E3).
  No symlinks, and no project file depends on the worktree. Worktree folder was already empty; its
  branch had no commits beyond `main`. `git worktree prune -v` removed the stale metadata;
  `git worktree list` now shows only the real folder. `rmdir` of the empty folder failed ("Device or
  resource busy").
- Notes: The empty folder can be deleted once the process holding it (likely the old Claude session)
  is closed.

## 2026-09-27 — Repository — Bootstrap reorganization check
- Setup: `git status` / `find` on branch `claude/bangla-sign-avatar-setup-699b03` after the `git mv`
  moves; spreadsheets read with Python's standard library (zipfile + XML).
- Metric(s) / checks: every moved file shows as a rename; file counts per folder; no leftover files in
  the old folders; sheet row counts and video ↔ Index alignment.
- Result: 70 files were moved (6 PDFs + notice README, 8 analyses, reading form, 3 sheets, 50 videos +
  `videos.txt`). 69 are byte-identical renames; the only content edit was the reading form (3 lines
  removed, ADR-0003). The 17 `templates/` files were deleted (git shows one of them as "renamed" to
  `session_protocol.md` only because the content is similar).
  `FinalSheet.xlsx` 3,491 rows; `FinalSheet2.xlsx` 5,010 rows (superset); all 50 videos match an Index
  in `FinalSheet2.xlsx`.
- Notes: The first `git mv` failed with "Permission denied" because the shell's working directory was
  inside the folder being moved. Retrying from the repo root worked.
