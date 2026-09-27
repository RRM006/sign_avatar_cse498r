# codebase_map.md — Where Everything Lives

**Last updated:** 2026-09-27

There is **no code** in this repo yet. It holds research material, data and project docs.

---

## Current structure (real, verified 2026-09-27)

```
sign_avatar_cse498r/
├── CLAUDE.md                        # Short root guide; AI reads it first every session
├── README.md                        # Project summary: confirmed scope, confirmed decisions, open items
├── agent_docs/                      # Living project docs (the "shared brain")
│   ├── session_protocol.md          # Start/end-of-session prompts
│   ├── current_task.md              # What we're doing now + the next step (overwritten each session)
│   ├── changelog.md                 # Session history, newest first
│   ├── milestone_log.md             # Milestones, phases, status
│   ├── constitution.md              # Stable purpose, rules, constraints, what's hard
│   ├── decisions.md                 # Owner-confirmed decisions (ADRs)
│   ├── open_questions.md            # Undecided questions + candidate options
│   ├── codebase_map.md              # This file
│   └── test_log.md                  # What was checked/tested + results
├── research/
│   ├── paper_reading_template.md    # The form used to analyse each paper
│   ├── papers/                      # 6 source PDFs — AI must NOT read these
│   │   └── README.md                # "Do not read" notice (ADR-0006) + PDF ↔ analysis index
│   ├── paper_analyses/              # Filled paper forms 01–06 + comparisons 07–08 (cleaned, ADR-0012)
│   └── design_proposals/            # AI-written design PROPOSALS, not decisions
│       ├── 01_Beginners_Research_Guide_and_Initial_Project_Design.md   # older; partly superseded by 02
│       └── 02_BdSL_Text-to-Sign_Research_and_Build_Guide.md            # newer
└── dataset/
    ├── README.md                    # Dataset facts, status of each file, known/unknown
    └── initial_dataset/
        ├── FinalSheet2.xlsx         # CURRENT (ADR-0008). "Names" (Bangla sentence) + "Index"; 5,010 rows, Index 0–5460
        ├── FinalSheet_DuplicateGroups.xlsx  # 82 duplicate groups (178 rows); computed over FinalSheet.xlsx's 3,491 rows only
        ├── superseded/
        │   └── FinalSheet.xlsx      # Superseded (ADR-0008). 3,491 rows = first 3,491 rows of FinalSheet2.xlsx
        └── videos/                  # 50-clip sample, <Index>.mp4 (~767 MB). Full set is on desktop / Drive (ADR-0009)
```

Not on disk: `new_project_intake/` (the inbox named in `CLAUDE.md` and `README.md`). See
`open_questions.md` E2. `BOOTSTRAP_PROJECT_PROMPT.md`, `misc/` and `templates/` were removed (staged
deletions; recoverable from commit `15c9496`).

### Verified dataset facts
- Video filenames present: `0–3`, `328–332`, `784–794`, `3931–3950`, `5451–5460` (50 files). All 50 appear
  in `FinalSheet2.xlsx`.
- The 3 sheets and 50 videos are byte-identical to the originals in commit `15c9496` (git shows them
  as 100% renames).
- One signer per clip; distinct-signer count unverified (ADR-0008, `open_questions.md` B7).

### Paper ↔ analysis map
See `research/papers/README.md`.

---

## Planned structure (where we're growing toward)

**(TBD — decide with owner.)** No pipeline has been chosen (ADR-0010), so no code folders are planned
yet. `research/design_proposals/02_…` sketches a code layout; that is a proposal only. Until the owner
decides:
- New papers → `research/papers/`, and their analysis → `research/paper_analyses/09-…` (and onward).
- New design proposals → `research/design_proposals/`.
- Folders for code are created only when the owner asks for implementation.

---

## Important file rules
- **Don't read `research/papers/*.pdf`**. Use the analyses (ADR-0006).
- **Keep `videos/<Index>.mp4` aligned with the `Index` column** in the sheets. Don't rename videos.
- **Don't modify the dataset files.** The spelling is intentional (ADR-0008).
- **Don't add the full video set to git.** It stays on the desktop / Drive (ADR-0009). The 50-clip
  sample is already committed directly (no Git LFS).
- Several file and folder names contain spaces (e.g. analysis 05, most PDFs). Quote paths in shell
  commands.
