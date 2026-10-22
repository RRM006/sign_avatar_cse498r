# codebase_map.md — Where Everything Lives

**Last updated:** 2026-10-22

It holds research material, data, project docs, annotations and the code so far (2026-10-22): configuration, environment check, dataset manifest, leakage groups, split S1, pilot selection, MediaPipe feature extraction + QC, and gloss drafting + validation.

---

## Current structure (real, verified 2026-10-22)

```
sign_avatar_cse498r/
├── CLAUDE.md                        # Short root guide; AI reads it first every session
├── README.md                        # Project summary: confirmed scope, confirmed decisions, open items
├── pyproject.toml                   # Package `bdsl`; pinned deps (extras: extract, train; group: dev)
├── uv.lock                          # Exact resolved versions (91 packages); `uv sync` rebuilds .venv
├── configs/                         # Layered YAML: base.yaml ← env/{local,kaggle,colab}.yaml ← data/{pilot50,full}.yaml
├── src/bdsl/                        # config.py (layers, ${…} refs, hash) · paths.py (project root) · io.py (atomic writes, SHA-256) · env.py (environment checks) · cli.py (manifest / split / pilot-select / pilot-copy / extract / gloss-draft / gloss-validate)
│   ├── text/                        # normalize.py (norm_v1) · tags.py (indicative word lists) · gloss_rules.py (G0 v0.1) · annotations.py (schema, validator, overwrite guard)
│   ├── data/                        # video.py (probe) · manifest.py · groups.py (leakage groups) · split.py (S1, leakage checks) · pilot.py (selection + copy)
│   └── features/                    # layout.py (npz contents, feat_ver, privacy check) · extract.py (MediaPipe, 15 fps grid) · qc.py (QC + mode comparison)
├── tests/                           # pytest: config, paths, io, normalize, groups_split, pilot, features, gloss (93 tests)
├── notebooks/
│   ├── 00_env_check.ipynb           # Writes work/reports/env_report.json; stored without outputs (run on Day 1)
│   ├── 01_manifest.ipynb            # = bdsl.cli manifest / split / pilot-select (pilot-copy behind the approval note)
│   ├── 02_extract.ipynb             # = bdsl.cli extract --data pilot50 --mode video + QC summary
│   └── 03_gloss.ipynb               # = bdsl.cli gloss-draft / gloss-validate (01–03: no outputs, not yet executed)
├── work/                            # GITIGNORED generated outputs: models/, reports/, manifests/ (manifest_v1), splits/ (S1_v0), pilot/ (selection), features/<feat_ver>/ (VIDEO fa89892d4908 = chosen, IMAGE 395e878f9861), features_resume_test/
├── .venv/                           # GITIGNORED: Python 3.12.13 environment (uv)
├── annotations/                     # TRACKED (public): GLOSS_CONVENTION_v0.1.md (provisional) · REVIEW_GUIDE.md · REVIEWERS.csv (owner-maintained codes) · pilot50_v1_gloss_v01.csv (ADR-0015/0024)
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
│       ├── 02_BdSL_Text-to-Sign_Research_and_Build_Guide.md            # newer
│       ├── 03_Stage1_Audit_and_Design_Plan_2026-10-21.md               # Session 2 plan; partly superseded by 04
│       └── 04_Phase1_Design_Review_2026-10-22.md                       # Design review, approved in principle (ADR-0014–0021)
├── .gitignore                       # Ignores SIGN_LANGUAGE_DATA/, work/, dataset/pilot50_v1/videos/, .venv/, __pycache__/, .ipynb_checkpoints/
├── misc/pdf/                        # EMPTY, untracked folder on disk; left alone (ADR-0021)
└── dataset/
    ├── README.md                    # Dataset facts, status of each file, known/unknown
    ├── initial_dataset/
    │   ├── README.md                # Directory guide + AI rules for dataset work (2026-09-28)
    │   ├── DATASET_WORK_LOG.md      # Log of every dataset inspection/operation
    │   ├── FinalSheet2.xlsx         # CURRENT (ADR-0008). "Names" (Bangla sentence) + "Index"; 5,010 rows, Index 0–5460
    │   ├── FinalSheet_DuplicateGroups.xlsx  # 82 duplicate groups (178 rows); computed over FinalSheet.xlsx's 3,491 rows only
    │   ├── superseded/
    │   │   └── FinalSheet.xlsx      # Superseded (ADR-0008). 3,491 rows = first 3,491 rows of FinalSheet2.xlsx
    │   ├── SIGN_LANGUAGE_DATA/      # FULL SET: 5,010 <Index>.mp4 (66.3 GiB) + SESSION_LOG.md + copy of FinalSheet2.xlsx (identical). GITIGNORED — never add to git
    │   └── videos/                  # 50-clip sample (sample50), <Index>.mp4 (~767 MB), committed; byte-identical to SIGN_LANGUAGE_DATA copies
    └── pilot50_v1/                  # Pilot set (ADR-0017/0018/0022): README.md, SELECTION_PROTOCOL.md, pilot50_manifest.csv; videos/ = 50 copies (723 MB), GITIGNORED
```

`new_project_intake/` was retired (ADR-0021). `BOOTSTRAP_PROJECT_PROMPT.md` and `templates/` were
removed in commit `43598be` (recoverable from `15c9496`).

### Related material OUTSIDE this repo (read-only reference; found 2026-10-21)
- `D:\CSE498R\Sign_Language\CSE498R_v2\`: the earlier project (sign→voice recognition; git remote
  `RRM006/sign-language-to-voice`). It contains:
  - `src/`: `features.py`, `extract_landmarks.py`, `paths.py`, …
  - `tests/`, `analysis/`, `notebooks/` (never executed), `models/*.task` (holistic, hand, face, pose_lite);
  - `Sign_Language/{scripts,outputs,mediapipe_models,reports,SESSION_LOG.md}`: the July 2026 analysis
    scripts and their JSON/CSV outputs, including `duplicate_groups.csv`;
  - its own `agent_docs/`;
  - `Paper sign/` PDFs (not read).

  Different scope. Read-only reference: lessons only, no code copied (ADR-0021).
- `D:\CSE498R\Sign_Language.zip` (70 GB, not opened).

### Verified dataset facts
- Video filenames present: `0–3`, `328–332`, `784–794`, `3931–3950`, `5451–5460` (50 files). All 50 appear
  in `FinalSheet2.xlsx`.
- The 3 sheets and 50 videos are byte-identical to the originals in commit `15c9496` (git shows them
  as 100% renames).
- One signer per clip; distinct-signer count unverified (ADR-0008, `open_questions.md` B7).

### Paper ↔ analysis map
See `research/papers/README.md`.

---

## Planned structure (approved in principle, ADR-0014–0021)

Created step by step, only after the owner's go for each step. **Exists now (Days 1–2, 2026-10-22):** the configs base/env/data layers, src/bdsl/{config,paths,env,io,cli}.py, src/bdsl/{text,data,features}/, tests/, notebooks/00_env_check … 03_gloss.ipynb, dataset/pilot50_v1/, annotations/, pyproject.toml + uv.lock. Everything else below is not created yet:
```
configs/ base.yaml · env/{local,kaggle,colab}.yaml · data/{pilot50,full}.yaml · model/*.yaml
src/bdsl/ config · paths · env · io · data/ · text/ · features/ · models/ · train/ · eval/ · avatar/ · cli
notebooks/ 00_env_check … 07_avatar_demo     tests/     web/avatar_viewer/
pyproject.toml + uv.lock
work/ (gitignored)     dataset/pilot50_v1/ (videos/ gitignored)
```
Details: research/design_proposals/04_… §F-13. New papers → research/papers/ + research/paper_analyses/09-…

---

## Important file rules
- **Don't read `research/papers/*.pdf`**. Use the analyses (ADR-0006).
- **Keep `videos/<Index>.mp4` aligned with the `Index` column** in the sheets. Don't rename videos.
- **Don't modify the dataset files.** The spelling is intentional (ADR-0008).
- **Don't add the full video set to git.** It sits in `SIGN_LANGUAGE_DATA/` on the desktop and is
  gitignored (ADR-0017). The 50-clip sample is already
  committed directly (no Git LFS).
- Several file and folder names contain spaces (e.g. analysis 05, most PDFs). Quote paths in shell
  commands.
