# open_questions.md — Undecided Questions + Candidate Options

> Everything still **unclear, missing or undecided**. An AI must **ask rather than guess** on any of
> these. When the owner answers one, record the decision in `decisions.md` (ADR) and move the item to
> "Answered" at the bottom with the ADR id.
>
> "Candidate options" are ideas found in the paper analyses (`research/paper_analyses/NN`) and the
> design proposals (`research/design_proposals/`). They are **proposals, not decisions**.

**Last updated:** 2026-09-27

---

## Scope (settled — ADR-0007)
Text sentence → BdSL avatar only; sentence-level translation with BdSL grammar/word order; deliverable
is report + literature review + trained model + results, aimed at a publishable paper.

---

## B. The initial dataset — still open

### B7. How many distinct signers? (from B3)
- **Evidence:** One signer per clip (owner, ADR-0008). The total number of distinct signers is
  unverified.
- **Why it matters:** A signer-independent split is only possible if signer identities are known.
- **Status:** Open.

### B8. How is the held-out evaluation split defined?
- **Evidence:** A held-out evaluation split must be reserved (owner, ADR-0008). It has not been
  created, and how it is grouped (by sentence, duplicate group, signer, …) is not decided.
- **Status:** Open. Part of the design phase.

---

## C. Design questions (undecided — candidate options from the literature)

### C1. Sign representation and avatar technology
- **Owner (ADR-0010):** Not decided. MediaPipe Holistic is only the interim landmark-extraction step.
- Candidate options seen:
  - **Notation-based:** HamNoSys → SiGML → JASigning / SiGML Player avatar (01, 05).
  - **Animation clips:** 3D character (Blender / Mixamo rig) animated by motion capture from sign
    videos, then retargeted and smoothed (04).
  - **Browser 3D:** Three.js avatar with Bezier interpolation + inverse kinematics (06).
  - **Learned pose/motion generation** from extracted landmarks (e.g. Ham2Pose, SignAvatar in 05 §10;
    further options in `research/design_proposals/`).
- **Status:** Open.

### C2. Text → sign mapping
- **Owner (ADR-0010):** Not decided. Must be sentence-level with BdSL grammar/word order (ADR-0007).
- Candidate options seen:
  - Lemmatise + dictionary lookup (01, BiLSTM seq2seq lemmatiser, 79.22% reported).
  - Rule-based parsing + BdSL reordering rules + fingerspelling fallback (05; rules not listed).
  - Contextual-model restructuring into sign-language word order before lookup (06).
  - Learned text → pose/motion model trained on the team's videos (`research/design_proposals/`).
- **Status:** Open.

### C3. Sign lexicon / data source
- **Owner (ADR-0010):** Not decided. The team's videos are primarily training data (ADR-0008).
- Candidate options seen:
  - **IsharaKotha** corpus: 3,823 BdSL signs as SiGML (01). Public availability **unconfirmed**.
  - **Zenodo BdSL SiGML set:** ~90–94 classes (letters, numerals, 41 words), public; licence
    unverified (05).
  - **BDSL-49:** 49 BdSL character images, public (02). Characters only, images not motion.
  - This repo's `dataset/initial_dataset/` (team-owned, ADR-0008).
- **Status:** Open.

### C4. Handling words that have no sign
- **Owner (ADR-0010):** Fingerspelling is the recommended fallback, still to be validated.
- Other options seen: a placeholder, or other strategies discussed in 01 §9. Known issue: Bangla
  compound letters (যুক্তাক্ষর) animated incorrectly in 05.
- **Status:** Open (direction given, not validated).

### C5. Evaluation method — details
- **Owner (ADR-0011):** Human evaluation (experts / deaf signers / interpreters) plus an automatic
  metric.
- Still open: which automatic metric(s); who the human evaluators are and how many; the protocol.
- Candidate options seen: human 1–4 rating (01); expert pass/fail + accuracy (05); gloss BLEU, lemma
  accuracy, sign-sequence exact match (01 §6, 06 §12); pose-distance and back-translation metrics
  (`research/design_proposals/`); scenario-based stress tests (04).
- **Status:** Open.

---

## E. Housekeeping found on 2026-09-27 (low priority)

### E1. Which local machine has 24 GB RAM + RX 570?
- ADR-0004 names "one local machine (24 GB RAM, AMD Radeon RX 570)". ADR-0009 names two local
  machines (desktop, laptop). Which one is which is not stated. **Status:** Open.

### E2. `new_project_intake/` is missing
- The folder no longer exists on disk (its `README.md` is staged as modified but deleted in the working
  tree). `README.md` and `CLAUDE.md` still point to it as the inbox. Restore it, or change the inbox
  convention? **Status:** Open. Nothing was changed.

### E3. Analysis 07 still has two "Medical" comparison rows
- `07` table rows "Medical-domain signs" (line 21) and "Medical coverage" (line 80): IsharaKotha's 84
  "Disease & Treatment" signs vs 0 vs 0. The number is a genuine paper finding; the row exists because of the old
  medical context. Keep or remove (D3)? **Status:** Open. Nothing was changed.

### E4. Conservative rule on sharing videos
- `CLAUDE.md` rule 7 / `constitution.md` §2.8 say "until origin, licence and consent are known". B1 now
  answers that, but D4 keeps the defaults unchanged, so the rule stays as written. Should the wording
  change? **Status:** Open.

---

## Answered

- **2026-09-27** — Is this a medical project / are dialects in scope? → **No** (ADR-0003).
- **2026-09-27** — Are the budget & hardware constraints real? → **Yes** (ADR-0004).
- **2026-09-27** — Reorganize the folders? → **Yes**, into `research/` + `dataset/` (ADR-0005).
- **2026-09-27** — Is the "don't read" notice on the papers intentional? → **Yes** (ADR-0006).
- **2026-09-27** — A1 Deliverable → report + literature review + trained model + results, aimed at a
  publishable paper (ADR-0007).
- **2026-09-27** — A2 Direction → text sentence → sign avatar only; speech input and sign → text out of
  scope (ADR-0007).
- **2026-09-27** — A3 Translation depth → sentence-level with BdSL grammar/word order (ADR-0007).
- **2026-09-27** — B1 Origin/licence/consent → collected by the team, fully owned, permissions in place
  (ADR-0008).
- **2026-09-27** — B2 Current sheet → `FinalSheet2.xlsx`; `FinalSheet.xlsx` superseded (ADR-0008).
- **2026-09-27** — B3 Video content → one signer per clip; distinct-signer count still open as B7
  (ADR-0008).
- **2026-09-27** — B4 Storage → full dataset on desktop or Drive → Colab; laptop code/small samples
  only (ADR-0009).
- **2026-09-27** — B5 Purpose → primarily training data; extracted pose/landmarks feed the
  sign-generation model; reserve a held-out evaluation split (ADR-0008; split definition open as B8).
- **2026-09-27** — B6 Data observations → spelling is intentional, leave unchanged; `videos.txt`
  unnecessary (ADR-0008). Duplicate groups and `Index` gaps are documented in `dataset/README.md`; no
  action requested.
- **2026-09-27** — C6 What runs where → Colab training; desktop full data; laptop code/small samples
  (ADR-0009).
- **2026-09-27** — D1 IsharaKotha citation → arXiv:2511.16896 (2025) (ADR-0012).
- **2026-09-27** — D2 Literature review → complete; next phase is pipeline/system design (ADR-0012).
- **2026-09-27** — D3 Wrong context in analyses → removed from 01–08, genuine findings kept (ADR-0012).
- **2026-09-27** — D4 Conservative defaults / working style → unchanged (ADR-0013).
