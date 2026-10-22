# decisions.md — Decision Record (ADR style)

> A dated record of real design choices: what we chose, why, and what we rejected, so decisions
> aren't silently re-opened later. **Only the owner confirms a decision.** Undecided items live in
> `open_questions.md`.
>
> Template:
> ```
> ## ADR-NNNN — YYYY-MM-DD — <title>
> - Decision: <what we will do>
> - Why: <the reason>
> - Rejected: <the main alternative(s) and why not>
> - Status: Accepted | Accepted in principle | Superseded by ADR-XXXX
> ```
>
> **Accepted** = the owner stated or confirmed it. **Accepted in principle** = the owner approved the
> direction; the listed technical specifics are working choices that may be revised from evidence,
> only with the owner's OK. Bullets inside an ADR are tagged **(owner)** or **(in principle)**.

---

## ADR-0001 — 2026-09-27 — Use a markdown project-memory system (CLAUDE.md + agent_docs/)
- Decision: Keep a short `CLAUDE.md` at the root and living docs in `agent_docs/`, updated every
  session (see `session_protocol.md`).
- Why: The owner asked for the project to be set up following `BOOTSTRAP_PROJECT_PROMPT.md`. Its
  stated purpose is to let any AI assistant resume the project session after session without
  re-explaining it.
- Rejected: None recorded.
- Status: Accepted

## ADR-0002 — 2026-09-27 — The design stays open during the research phase
- Decision: No translation pipeline, ML/NLP architecture, dataset strategy, sign representation, 3D
  avatar technology, model, training method or evaluation method is chosen yet. Options are collected
  in `open_questions.md` and decided later with the owner.
- Why: Owner statement. The project is in idea generation and research, and the owner will provide
  ideas and requirements in future sessions.
- Rejected: Adopting a pipeline suggested in the paper analyses now. The owner explicitly deferred these
  decisions.
- Status: Accepted. Items settled by ADR-0014–0021 (2026-10-22); still applies to anything they do not cover.

## ADR-0003 — 2026-09-27 — Not a medical project; no dialect focus
- Decision: The project has no medical-domain focus, no medical audio recordings, no medical entity
  extraction (symptoms, diseases, medications, duration, allergies) and no dialect focus (Dhaka,
  Sylhet, Chittagong, Barishal). Those lines were removed from `research/paper_reading_template.md`.
- Why: Owner correction: "this not medical project this is new project". The lines had been in the
  paper-reading form's context block by mistake, and several analyses already flagged them as a possible
  leftover.
- Rejected: Keeping them as possible scope.
- Status: Accepted

## ADR-0004 — 2026-09-27 — Zero budget; Colab + one local machine
- Decision: Work within zero budget, using Google Colab (T4 GPU, ~15 GB VRAM, ~12 h session limit)
  and a local machine with 24 GB RAM and an AMD Radeon RX 570.
- Why: Owner-confirmed as true for this project. The underlying reason is not stated (TBD).
- Rejected: None recorded.
- Status: Accepted; compute roles amended by ADR-0016 (2026-10-22).

## ADR-0005 — 2026-09-27 — Folder layout: research/ + dataset/ + inbox
- Decision: Papers → `research/papers/`, paper analyses → `research/paper_analyses/`, reading form →
  `research/paper_reading_template.md`, data → `dataset/initial_dataset/`. `new_project_intake/` stays
  as the inbox for new owner material. The generic `templates/` folder was deleted after use. Analysis
  08 was renamed so it no longer shares its name with 07.
- Why: The owner chose the reorganization for clarity. Files were moved with `git mv` (history kept);
  no file contents changed except the reading-form edit in ADR-0003.
- Rejected: Keeping files in their original `misc/` + `new_project_intake/` locations (the other option
  offered). No reason recorded beyond the owner's choice.
- Status: Accepted; the inbox part is superseded by ADR-0021 (2026-10-22).

## ADR-0006 — 2026-09-27 — AI does not read the paper PDFs
- Decision: The notice in `research/papers/README.md` (formerly `misc/README.md`) stays. AI assistants
  use `research/paper_analyses/` instead of reading the PDFs.
- Why: Owner confirmed the notice is intentional. The reason is not stated (TBD).
- Rejected: Removing the notice.
- Status: Accepted

## ADR-0007 — 2026-09-27 — Scope and deliverable (answers A1–A3)
- Decision: The deliverable is a report, a literature review, a trained model and results, aimed at a
  publishable research paper (A1). The direction is Bangla text sentence → BdSL on a 3D avatar only
  (A2). Translation is sentence-level and must handle BdSL grammar/word order (A3).
- Why: Owner answers to `open_questions.md` A1–A3.
- Rejected: Speech input and sign → text (out of scope, A2). Word-by-word lookup as the translation
  approach (A3).
- Status: Accepted. Target end users: not stated (TBD — decide with owner).

## ADR-0008 — 2026-09-27 — The initial dataset (answers B1, B2, B3, B5, B6)
- Decision:
  - B1: The dataset was collected by the team and is fully team-owned. Permissions are in place.
  - B2: `FinalSheet2.xlsx` is the current sheet. `FinalSheet.xlsx` is obsolete/superseded (kept in
    `dataset/initial_dataset/superseded/`).
  - B3: One signer per clip. The total number of distinct signers is still unverified.
  - B5: The videos are primarily training data. Pose/landmarks extracted from them feed the
    sign-generation model. A held-out evaluation split must be reserved.
  - B6: The non-standard spelling is intentional and stays unchanged. `videos/videos.txt` was
    unnecessary (no longer in the folder).
- Why: Owner answers to `open_questions.md` B1–B3, B5, B6.
- Rejected: Correcting the spelling in the sheets (B6).
- Status: Accepted. Still open: number of distinct signers; how the split is defined.

## ADR-0009 — 2026-09-27 — Data storage and what runs where (answers B4, C6)
- Decision: The full dataset stays on the desktop or goes Google Drive → Colab. Only the 50-clip
  sample is in this repo. Colab is for training, the desktop for full-dataset work, the laptop for code
  and small samples only.
- Why: Owner answers to `open_questions.md` B4 and C6.
- Rejected: None recorded.
- Status: Accepted. Refines ADR-0004. Data-location wording superseded by ADR-0017; compute roles
  amended by ADR-0016; the RX 570 machine is the desktop (ADR-0016). All 2026-10-22.

## ADR-0010 — 2026-09-27 — Sign representation, mapping and lexicon stay open (answers C1–C4)
- Decision:
  - C1: The final sign representation and avatar technology are **not decided**. MediaPipe Holistic
    is only the interim landmark-extraction step.
  - C2: The text → sign mapping is **not decided**.
  - C3: The sign lexicon / data source is **not decided**.
  - C4: Fingerspelling is the recommended fallback for words without a sign, but this still has to
    be validated as a research/design decision.
- Why: Owner answers to `open_questions.md` C1–C4. ADR-0002 stays in force for these items.
- Rejected: None recorded.
- Status: Accepted; C1–C4 settled by ADR-0014 and ADR-0019 (2026-10-22, technical specifics in
  principle). MediaPipe Holistic remains the extraction step.

## ADR-0011 — 2026-09-27 — Evaluation combines human and automatic evaluation (answer C5)
- Decision: Evaluation combines human evaluation (BdSL experts, deaf signers, interpreters) with an
  automatic metric. Which metric, who the evaluators are and the exact protocol are (TBD — decide with
  owner).
- Why: Owner answer to `open_questions.md` C5.
- Rejected: None recorded.
- Status: Accepted (direction); refined by ADR-0020 (2026-10-22).

## ADR-0012 — 2026-09-27 — Literature review closed; IsharaKotha citation; analyses cleaned (answers D1–D3)
- Decision:
  - D1: Cite IsharaKotha as **arXiv:2511.16896 (2025)**. The "Rahman et al. 2023, Heliyon" reference
    in analysis 05 is not the project citation.
  - D2: The literature review is complete. The next phase is pipeline/system design.
  - D3: Remove the unrelated medical/dialect context blocks from analyses 01–08 and keep the genuine
    research-paper findings. Done by the owner; verified on 2026-09-27 (see `test_log.md`).
- Why: Owner answers to `open_questions.md` D1–D3.
- Rejected: Keeping the wrong context blocks with a warning (the earlier interim approach).
- Status: Accepted. ADR-0003 (not medical, no dialect focus) still applies.

## ADR-0013 — 2026-09-27 — Conservative defaults and working style kept (answer D4)
- Decision: These stay unchanged: never commit secrets; don't share dataset videos outside the
  repo/team; no implementation code unless the owner asks; explain things simply.
- Why: Owner answer to `open_questions.md` D4.
- Rejected: None recorded.
- Status: Accepted; the video-sharing default is re-worded by ADR-0017 (owner's public-release
  permission, 2026-10-22). The other defaults are unchanged.

## ADR-0014 — 2026-10-22 — Research direction and pipeline (answers F1; C2–C4)
- Decision:
  - (owner) This is text → sign generation, not recognition. Direction: Bangla sentence → gloss
    sequence → generated motion → 3D avatar. Two trained models: Model A (Bangla → gloss) and
    Model B (gloss → motion, on MediaPipe-derived features). A direct Bangla text → motion model is
    a comparison (ablation). Learned models are always compared with simple baselines. The team's own
    videos are the primary training source; no external dataset becomes a required dependency
    without the owner's OK.
  - (in principle) Model A: rule glosser G0 (baseline); BiGRU-attention seq2seq; BanglaT5
    fine-tuning once ≥ 300 reviewed pairs exist. Model B: non-autoregressive Transformer with a
    length predictor (primary); autoregressive GRU optional. Model B baselines: mean motion (B0) and
    nearest-sentence retrieval of a real training motion (B1).
  - (in principle) Full-set Model B training uses G0 pseudo-glosses, always labelled
    "pseudo-gloss". No word-level timestamps or sign-level clips are created or claimed; each video is
    one complete sentence.
  - (in principle) Lexicon (C3): a gloss vocabulary table built from reviewed annotations — not a
    library of per-sign motion clips.
  - (in principle) Unknown words (C4): `UNK(word)` = neutral hold + on-screen caption + log entry.
    `FS()`/`NUM()` tokens are kept in glosses and rendered as UNK until reviewed assets exist.
    Fingerspelling is future work.
- Why: Owner direction 2026-10-22; design review `research/design_proposals/04_…` approved in
  principle 2026-10-22. Measured: 646 of 1,417 tokens occur in only one sentence (2026-10-22);
  98.4% of normalised sentences have one video (2026-10-21).
- Rejected: Notation avatars (HamNoSys/SiGML/JASigning): our videos cannot produce notation.
  Per-word clip concatenation: no per-sign clips exist. Diffusion/VQ motion models: too data- and
  time-hungry for the timeline. Treating pseudo-glosses as BdSL annotations.
- Status: Accepted (owner bullets); Accepted in principle (technical specifics). Refines ADR-0010
  for C2–C4; ADR-0002 applies to anything not covered here.

## ADR-0015 — 2026-10-22 — Annotation layers, statuses and review (answers F2)
- Decision:
  - (owner) Normal Bangla sentences are not assumed to be BdSL glosses. Provisional gloss drafts use
    a defined convention and review process. The four statuses `auto_draft`, `team_reviewed`,
    `expert_validated` and `rejected` stay distinct. A BdSL-competent person is available for later
    validation; the initial test uses provisional annotations and claims no linguistic validation.
    No human review, expert identity or expert approval is ever fabricated. Mock or simulated cases
    are explicitly marked (`is_mock=true`, reviewer `MOCK`) and excluded from real training and
    evaluation. No word-level timestamps are invented.
  - (in principle) Gloss convention v0.1 as in `research/design_proposals/03_…` §F (provisional).
    Review: a team member checks each draft against the video (`team_reviewed`); a second member
    spot-checks 20%; disagreements are logged; the BdSL-competent person reviews a stratified
    sample. `expert_validated` is set only from a review record carrying a reviewer code assigned by
    the owner. No reviewer names are stored in git.
- Why: Owner requirements 2026-10-22.
- Rejected: Treating Bangla text as gloss; marking AI drafts as reviewed.
- Status: Accepted (owner bullets); Accepted in principle (convention v0.1 and review details).

## ADR-0016 — 2026-10-22 — Compute and environment (answers F6, E1; amends ADR-0004, ADR-0009)
- Decision:
  - (owner) The desktop (Ryzen 5 3500X, ~24 GB RAM, AMD Radeon RX 570 8 GB) holds the full dataset.
    Local CPU is used for data inspection and MediaPipe feature extraction. Kaggle is the primary
    training platform; Google Colab is the fallback. The laptop is for code and small samples.
  - (owner, conditional) Python 3.12 with mediapipe 0.10.35, adopted only if the Day-1 environment
    check confirms that the combination works. If it fails, the owner chooses the alternative.
  - (in principle) A pinned `uv` virtual environment in the project. The RX 570 is not on the
    critical path (torch-directml is a 2024 pre-release).
- Why: Owner answers 2026-10-22. Hardware verified 2026-10-21. The mediapipe 0.10.35 wheel lists
  Python 3.12 as supported (checked 2026-10-22; not installed or tested yet).
- Rejected: Colab as primary (owner preference); upgrading mediapipe mid-project.
- Status: Accepted (roles); the Python/mediapipe pin is conditional on the Day-1 check — passed 2026-10-22 (test_log), so the pin is in effect. Amends the
  compute roles of ADR-0004 and ADR-0009.

## ADR-0017 — 2026-10-22 — Data location, sharing and handling (answers F3, F10, E4)
- Decision:
  - (owner) The full 5,010-video set is inside the project folder on the desktop, at
    `dataset/initial_dataset/SIGN_LANGUAGE_DATA/`, and is gitignored; it is never added to git. The
    50-clip sample in `dataset/initial_dataset/videos/` is committed. The Drive → Colab route of
    ADR-0009 remains allowed.
  - (owner) The GitHub repository is public by the owner's choice, and the owner has permission to
    make the dataset publicly available. Permission for one use does not cover every use: each new
    distribution channel or redistribution (for example a public Kaggle dataset, a paper supplement or
    another platform) needs the owner's explicit OK, and consent, privacy, licence and attribution
    requirements are kept. A formal licence for reuse by others is (TBD — decide with owner).
  - (owner) 50 pilot videos may be copied into `dataset/pilot50_v1/videos/` (gitignored); the
    originals stay untouched.
  - (owner, subject to checks) Derived features — never the original videos — may be uploaded to a
    private Kaggle dataset shared with team members only. Check done 2026-10-22: no project rule
    forbids this.
  - (in principle) Upload minimisation: no video frames or images and no raw 478-point face mesh
    (only body and hand landmarks, 52 face blendshapes, head rotation and masks); an upload manifest
    with SHA-256; an automatic pre-upload check.
  - (in principle) Because the repo is public, a commit is a publication: derived features,
    checkpoints, `work/`, credentials and reviewers' personal data are never committed.
- Why: Owner statements 2026-10-22. Verified: the full set is inside the folder and gitignored
  (2026-10-21); the repo is public (2026-10-22).
- Rejected: Uploading original videos to Kaggle; uploading the raw face mesh.
- Status: Accepted (owner bullets); Accepted in principle (minimisation and commit controls).
  Supersedes ADR-0009's "only the 50-clip sample is in this repo" wording and the video-sharing
  wording kept by ADR-0013.

## ADR-0018 — 2026-10-22 — Split and leakage policy (answers B7, B8, F4; rule for F7)
- Decision:
  - (owner) One visible signer per video. About 4–6 distinct signers, estimated by the owner and
    unverified. Which signer recorded which Index is unknown. No signer identity, gender or other
    demographic attribute is predicted or assumed. No random video split without duplicate and
    sentence-overlap checks.
  - (in principle) One fixed split S1: group-disjoint 80/10/10 by leakage group (same normalised
    sentence ∪ same SHA-256 ∪ shared recorded segments), assigned deterministically by a hash of the
    group key. The test set is reported for in-vocabulary vs OOV items, and for items with vs without
    a minimal-pair sibling in train. The test set is locked and used once for final numbers.
    Leakage tests are automated; a run refuses to start on a split-hash mismatch. The pilot is drawn
    from S1's partitions. S1 is `v0` until the full shared-segment scan, then frozen as `v1`.
  - (in principle) Near-duplicates with different labels: an "edited minimal pair" (retained, one
    group, flagged) if a differing segment exists; a "label conflict" (excluded until resolved) if
    not. Colour cluster: 3456, 3457 and 3458 are retained as one group, with labels provisional until
    the BdSL-competent person checks the endings; 5096, 5100 and 5102 are exact duplicates of them.
  - (owner consequence) All results are reported as signer-dependent. Index blocks are recording
    batches, not signers.
- Why: Measured 2026-10-22: the colour-cluster clips share identical frames for ~70% of their
  length. 1,424 of 1,516 exact-duplicate second copies sit at Index ≥ 4000 (2026-10-21).
- Rejected: Random video split; grouping whole minimal-pair families (removes compositional tests);
  treating Index blocks as signers; clustering signers by face.
- Status: Accepted (owner bullets); Accepted in principle (split mechanics and the F7 rule).

## ADR-0019 — 2026-10-22 — Motion representation and avatar route (answers C1, F5)
- Decision:
  - (owner) MediaPipe Holistic is the landmark-extraction step. A browser VRM avatar (three.js +
    three-vrm) is the route to investigate; Blender is the fallback.
  - (in principle) Motion target: MediaPipe 3D world landmarks (upper body + both hands),
    body-normalised, plus 52 face blendshapes and head rotation, with validity masks, resampled to
    15 fps (configurable). The project writes its own direction-based retargeter; the avatar is a
    CC0 VRM model; a skeleton viewer is always produced. Kalidokit is not a dependency.
- Why: three-vrm 3.5.5 is maintained (2026-07-09, MIT). Kalidokit is deprecated (last release
  2022-02-05) and tied to the legacy MediaPipe API (both checked 2026-10-22). Feasibility counts as
  confirmed only when the Day-5 prototype runs.
- Rejected: Notation avatars (no notation data); SMPL-X fitting (too heavy for the timeline).
- Status: Accepted (owner bullets); Accepted in principle (representation, solver), feasibility
  pending Day 5. Refines ADR-0010 C1.

## ADR-0020 — 2026-10-22 — Evaluation protocol (answers C5; refines ADR-0011)
- Decision:
  - (owner) Text → gloss, gloss → motion and the rendered avatar are evaluated separately; expert
    evaluation where feasible. Never claim correct BdSL grammar or natural signing from low landmark
    error alone. Never claim statistical significance from a handful of pilot items. Never report
    synthetic or mock examples as observations.
  - (in principle) Model A: gloss WER, BLEU-4, chrF (sacreBLEU), exact match, tag accuracy.
    Model B: masked MPJPE and DTW-MJE per body part, duration error, velocity/jerk statistics,
    hand-motion energy ratio, output diversity, compared with B0/B1. Avatar: round-trip angular
    error, FPS, latency, visual checklist. Human (when the BdSL-competent person is available):
    comprehension within minimal-pair families, 1–4 naturalness, gloss correctness. 50-video pilot
    results are labelled "pipeline test". Reported results use 3 seeds and bootstrap confidence
    intervals on the S1 test set.
- Why: Owner requirements 2026-10-22; ADR-0011 direction.
- Rejected: A single automatic score as proof of quality; back-translation with a recogniser trained
  on the same data (circular).
- Status: Accepted (owner bullets); Accepted in principle (metric set).

## ADR-0021 — 2026-10-22 — Housekeeping (answers E2, E3, F8, F9, F11)
- Decision:
  - (owner) The `new_project_intake/` inbox is retired; new owner material is given in chat and
    recorded in `agent_docs/`.
  - (owner) The two "Medical" comparison rows in analysis 07 are removed.
  - (owner) The earlier project `D:\CSE498R\Sign_Language\CSE498R_v2\` is a read-only reference:
    lessons only, no code copied.
  - (owner) Bangla-SGP is not a required dependency.
  - (owner) The empty `misc/pdf/` folder is left alone.
- Why: Owner answers 2026-10-22.
- Rejected: None.
- Status: Accepted. Amends ADR-0005 (inbox part only).

## ADR-0022 — 2026-10-22 — pilot50_v1 held-out selection rule (option B)
- Decision: (owner) Pilot held-out (val/test) clips are chosen after the 40 train clips, preferring
  sentences made only of pilot-train words. A core held-out family sibling that contains unseen
  words is swapped for a free same-split sentence made only of pilot-train words when one exists
  (config `pilot.heldout_prefer_in_vocab: true`, `pilot.heldout_fallback_pool: true`). Each held-out
  clip's unseen words are listed (`unseen_in_pilot_train`). Result for pilot50_v1: 6/10 held-out
  clips use only pilot-train words; 4 keep unseen words.
- Why: Owner choice on 2026-10-22 after seeing both lists. With family siblings only, 1/10 held-out
  clips used only seen words (15 of 676 val/test sentences are covered by the pilot-train
  vocabulary), so the pilot test would mostly measure unknown-word handling.
- Rejected: Option A (family siblings only); a fixed val/test alternation per family (it left some
  families with no eligible sibling).
- Status: Accepted. Refines design doc 04 §F-6 for pilot50_v1; ADR-0018 is unchanged. Pilot
  results remain "pipeline tests".

## ADR-0023 — 2026-10-22 — Feature-extraction mode: MediaPipe VIDEO mode
- Decision: (owner) MediaPipe Holistic runs in VIDEO mode (tracking across the 15 fps grid) for
  feature extraction. The pilot feature set is feat_ver `fa89892d4908`:
  - layout `feat_layout_v1`, 15 fps;
  - the documented default confidence thresholds;
  - mediapipe 0.10.35;
  - model SHA-256 e2dab611…c3f8.
  Full-set extraction will use the same settings when the owner authorises it. The IMAGE-mode pilot
  features (`395e878f9861`) are kept only as the record of the comparison.
- Why: Pilot comparison on 2026-10-22 (50 clips, 4,806 frames per mode). Hand coverage was
  practically equal: any hand 79.5% (VIDEO) vs 79.2% (IMAGE); 18 clips higher, 17 lower, 15 equal.
  Wrist jitter was lower in VIDEO mode: left 15.8 vs 19.6 m/s², right 19.0 vs 24.8 m/s² (`test_log.md`).
- Rejected: IMAGE mode (same coverage, more jitter).
- Status: Accepted. Settles the mode choice left open in design doc 04 §F-8.

## ADR-0024 — 2026-10-22 — G0 v0.1 drafter and the annotation files
- Decision: (owner) Pilot gloss drafts are written by G0 v0.1 with rules R0–R6, including R5: a
  genitive ending is stripped only when the stem is itself a word in the sheet, and the result is
  marked `~`. G0 never reorders words and never guesses a lemma (`?`).
  - Annotation files live in the tracked top-level `annotations/` folder: a commit publishes them,
    and reviewers appear only as codes.
  - Reviewer codes are registered by the owner in `annotations/REVIEWERS.csv` (roles team / expert).
  - `bdsl.cli gloss-validate` accepts a reviewed row only from a registered reviewer, and
    `gloss-draft` never overwrites human-reviewed rows.
  - Model A trains only on reviewed, non-mock rows. If no review is done, the Day 3 options in
    `current_task.md` apply.
- Why: Owner approval of the Day 2 Step 2 plan and its three scope details (2026-10-22); ADR-0015.
- Rejected: G0 without R5 (offered as an option, not chosen).
- Status: Accepted. Implements ADR-0015 for pilot50_v1; the convention itself stays provisional.

## ADR-0025 — 2026-10-22 — Day 3 practice run on fake review data, merged into main
- Decision:
  - (owner) The current `annotations/pilot50_v1_gloss_v01.csv` is test data on purpose: glosses
    derived from the sentence text, no clip watched, `is_mock=true`, notes "TEST DATA … not
    video-verified". It is kept as is; the notes are never rewritten to claim a video check.
  - (owner) A test-only option `--allow-test-data` on `gloss-validate` and `train-text2gloss`
    accepts such rows. It is off by default; without it both commands refuse the data. With it,
    every output is named `TEST_…` and carries `TEST_RUN: true`.
  - (owner) Day 3 Step 1 was run in this TEST mode on branch `test-run-fake-review`. On the owner's
    request, the branch was merged into `main` (merge commit `0eef7c6`, local; not pushed).
  - (owner, rule kept) TEST numbers are never reported as Model A results. The real Model A run
    needs a real video review by a registered reviewer, `is_mock=false`, honest notes, and no test
    option (ADR-0024 unchanged).
- Why: The owner wanted to learn the annotation → validation → training process before the real
  review (owner, 2026-10-22).
- Rejected: Rewriting the notes to say the videos were checked; turning the test option on by default.
- Status: Accepted. Milestone 8 stays open until the real run.
