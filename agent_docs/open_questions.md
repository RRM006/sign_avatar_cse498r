# open_questions.md — Undecided Questions + Candidate Options

> Everything still **unclear, missing or undecided**. An AI must **ask rather than guess** on any of
> these. When the owner answers one, record the decision in `decisions.md` (ADR) and move the item to
> "Answered" at the bottom with the ADR id.
>
> "Candidate options" are ideas found in the paper analyses (`research/paper_analyses/NN`) and the
> design proposals (`research/design_proposals/`). They are **proposals, not decisions**.

**Last updated:** 2026-10-21 (Session 2: evidence added to B7, B8, C1–C5, E1; new section F)

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
- **2026-10-21:** No signer field exists in any sheet or filename. The old SESSION_LOG's "~5–7 signers"
  is a visual estimate from 100 thumbnails, so it is unverified. Index blocks differ in orientation and
  resolution (e.g. all 350 low-res clips are in Index 3675–5415), but blocks are **not** signers. See F4.
- **Status:** Open.

### B8. How is the held-out evaluation split defined?
- **Evidence:** A held-out evaluation split must be reserved (owner, ADR-0008). It has not been
  created, and how it is grouped (by sentence, duplicate group, signer, …) is not decided.
- **2026-10-21 evidence:** 1,424 of the 1,516 exact-duplicate groups have their second copy at
  Index ≥ 4000, so a random split leaks. Proposal (plan 03 §F/§J): group by normalised sentence ∪
  duplicate group ∪ near-duplicate cluster. Splits: S1 sentence-grouped, S2 unseen combination,
  S3 index-block stress test. The old "80/10/10 sentence-grouped" simulation is not adopted.
- **Status:** Open. Part of the design phase (proposed ADR-0018).

---

## C. Design questions (undecided — candidate options from the literature)

> **2026-10-21:** A recommendation for each of C1–C5 is in
> `research/design_proposals/03_Stage1_Audit_and_Design_Plan_2026-10-21.md` §D. It is a **proposal**;
> the items stay open until the owner answers F1 and F5.

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
  machines (desktop, laptop). Which one is which is not stated.
- **2026-10-21 evidence:** The machine holding the full dataset is `DESKTOP-4NDR99B`: Radeon RX 570 with
  8 GB (registry), 23.9 GB RAM, Ryzen 5 3500X. `DATASET_WORK_LOG.md` (2026-09-28) says "Computer:
  Desktop". So the desktop is very likely the RX 570 machine. **Status:** Open — owner to confirm.

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

## F. Raised by the 2026-10-21 audit + design plan

**Blocking (needed before implementation):**

### F1. Approve the proposed overall direction?
- Model A (Bangla → gloss) + Model B (gloss → MediaPipe motion), pseudo-glosses for the full set,
  retrieval/mean baselines, avatar as a display layer (plan 03 §C–§E).
- Alternative: direct text → motion (simpler; weaker gloss/grammar story).
- **AI recommendation:** approve; keep text → motion as an ablation. **Status:** Open (proposed ADR-0014).

### F2. Is a BdSL-competent gloss reviewer available?
- A team member, a signer from the recordings, or the RA.
- Without one, glosses stay "team-reviewed" and every grammar claim is provisional.
- **Recommendation:** name one person, even for a 20-item check. **Status:** Open.

### F3. Data permissions + repo visibility
- (a) May 50 videos be **copied** into `dataset/pilot50_v1/` (gitignored)?
- (b) May derived features (which include face landmarks) be uploaded as a **private** Kaggle dataset
  (no videos)?
- (c) Is `github.com/RRM006/sign_avatar_cse498r` public? The 50 sample videos with identifiable faces
  are pushed there.
- Relates to E4. **Recommendation:** yes to (a), yes to (b) for features only. **Status:** Open.

### F4. Can the team say who recorded which Index ranges?
- This is the only route to a signer-independent test. Record it as "team-reported".
- **Status:** Open (relates to B7).

### F5. Avatar route for the prototype?
- Browser VRM (three-vrm + Kalidokit-style solver; fastest, older library).
- Or Blender + MPFB2 (robust offline renders; more retargeting work).
- **Recommendation:** browser VRM first, Blender as fallback. **Status:** Open (C1).

### F6. Kaggle as the main training platform?
- Kaggle primary, Colab fallback, local CPU for MediaPipe extraction. Amends ADR-0004/0009.
- **Recommendation:** yes. **Status:** Open (proposed ADR-0016).

**Not blocking:**

### F7. Colour-label cluster
- Index 3456/3457/3458/5096/5100/5102: visually identical (old pHash), but labelled white/red/black.
- Wrong labels, or subtly different videos? Proposed: exclude from training and the pilot.
- **Status:** Open.

### F8. The earlier project `D:\CSE498R\Sign_Language\CSE498R_v2\`
- Sign→voice scope; remote `RRM006/sign-language-to-voice`.
- May its code and `.task` model files be reused (copied, not moved)? Should it be referenced in docs?
- Also: a 70 GB `D:\CSE498R\Sign_Language.zip` exists (not opened). **Status:** Open.

### F9. Is Bangla-SGP (LREC 2026, 1,000 sentence–gloss pairs) released?
- The paper says GitHub, CC BY 4.0, "upon publication". Check on Day 1. **Status:** Open.

### F10. Data-location wording
- ADR-0009 and `constitution.md` §3 say only the 50-clip sample is in the repo and the full set is on
  the desktop/Drive.
- Fact: the full set is inside this repo folder (gitignored) on the desktop.
- Amend the wording (proposed ADR-0017)? `CLAUDE.md` and `dataset/README.md` were corrected on
  2026-10-21. **Status:** Open.

### F11. Empty folder `misc/pdf/`
- It exists on disk (untracked, empty). Keep or remove? Nothing was changed. **Status:** Open.

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
