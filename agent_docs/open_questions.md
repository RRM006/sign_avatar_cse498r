# open_questions.md — Undecided Questions + Candidate Options

> Everything still **unclear, missing or undecided**. An AI must **ask rather than guess** on any of
> these. When the owner answers one, record the decision in `decisions.md` (ADR) and move the item to
> "Answered" at the bottom with the ADR id.
>
> "Candidate options" are ideas found in the paper analyses (`research/paper_analyses/NN`) and the
> design proposals (`research/design_proposals/`). They are **proposals, not decisions**.

**Last updated:** 2026-10-22 (Session 3: B, C, E, F answered → ADR-0014–0021; open items now in §G)

---

## Scope (settled — ADR-0007)
Text sentence → BdSL avatar only; sentence-level translation with BdSL grammar/word order; deliverable
is report + literature review + trained model + results, aimed at a publishable paper.

---

## B. The initial dataset — answered 2026-10-22

### B7. How many distinct signers? (from B3)
- **Evidence:** One signer per clip (owner, ADR-0008). The total number of distinct signers is
  unverified.
- **Why it matters:** A signer-independent split is only possible if signer identities are known.
- **2026-10-21:** No signer field exists in any sheet or filename. The old SESSION_LOG's "~5–7 signers"
  is a visual estimate from 100 thumbnails, so it is unverified. Index blocks differ in orientation and
  resolution (e.g. all 350 low-res clips are in Index 3675–5415), but blocks are **not** signers. See F4.
- **Status:** Answered 2026-10-22 — not determinable from the data and not pursued; no identity or demographic inference; results are signer-dependent (ADR-0018).

### B8. How is the held-out evaluation split defined?
- **Evidence:** A held-out evaluation split must be reserved (owner, ADR-0008). It has not been
  created, and how it is grouped (by sentence, duplicate group, signer, …) is not decided.
- **2026-10-21 evidence:** 1,424 of the 1,516 exact-duplicate groups have their second copy at
  Index ≥ 4000, so a random split leaks. Proposal (plan 03 §F/§J): group by normalised sentence ∪
  duplicate group ∪ near-duplicate cluster. Splits: S1 sentence-grouped, S2 unseen combination,
  S3 index-block stress test. The old "80/10/10 sentence-grouped" simulation is not adopted.
- **Status:** Answered 2026-10-22 — split S1, accepted in principle (ADR-0018).

---

## C. Design questions — answered 2026-10-22 (candidate options kept for history)

> **2026-10-22:** Settled by ADR-0014, ADR-0015, ADR-0019 and ADR-0020 (technical specifics accepted
> in principle). The options below are kept as history.

### C1. Sign representation and avatar technology
- **Owner (ADR-0010):** Not decided. MediaPipe Holistic is only the interim landmark-extraction step.
- Candidate options seen:
  - **Notation-based:** HamNoSys → SiGML → JASigning / SiGML Player avatar (01, 05).
  - **Animation clips:** 3D character (Blender / Mixamo rig) animated by motion capture from sign
    videos, then retargeted and smoothed (04).
  - **Browser 3D:** Three.js avatar with Bezier interpolation + inverse kinematics (06).
  - **Learned pose/motion generation** from extracted landmarks (e.g. Ham2Pose, SignAvatar in 05 §10;
    further options in `research/design_proposals/`).
- **Status:** Answered 2026-10-22 → ADR-0019.

### C2. Text → sign mapping
- **Owner (ADR-0010):** Not decided. Must be sentence-level with BdSL grammar/word order (ADR-0007).
- Candidate options seen:
  - Lemmatise + dictionary lookup (01, BiLSTM seq2seq lemmatiser, 79.22% reported).
  - Rule-based parsing + BdSL reordering rules + fingerspelling fallback (05; rules not listed).
  - Contextual-model restructuring into sign-language word order before lookup (06).
  - Learned text → pose/motion model trained on the team's videos (`research/design_proposals/`).
- **Status:** Answered 2026-10-22 → ADR-0014, ADR-0015.

### C3. Sign lexicon / data source
- **Owner (ADR-0010):** Not decided. The team's videos are primarily training data (ADR-0008).
- Candidate options seen:
  - **IsharaKotha** corpus: 3,823 BdSL signs as SiGML (01). Public availability **unconfirmed**.
  - **Zenodo BdSL SiGML set:** ~90–94 classes (letters, numerals, 41 words), public; licence
    unverified (05).
  - **BDSL-49:** 49 BdSL character images, public (02). Characters only, images not motion.
  - This repo's `dataset/initial_dataset/` (team-owned, ADR-0008).
- **Status:** Answered 2026-10-22 → ADR-0014 (gloss vocabulary table, not sign clips).

### C4. Handling words that have no sign
- **Owner (ADR-0010):** Fingerspelling is the recommended fallback, still to be validated.
- Other options seen: a placeholder, or other strategies discussed in 01 §9. Known issue: Bangla
  compound letters (যুক্তাক্ষর) animated incorrectly in 05.
- **Status:** Answered 2026-10-22 → ADR-0014 (UNK policy now; fingerspelling future).

### C5. Evaluation method — details
- **Owner (ADR-0011):** Human evaluation (experts / deaf signers / interpreters) plus an automatic
  metric.
- Still open: which automatic metric(s); who the human evaluators are and how many; the protocol.
- Candidate options seen: human 1–4 rating (01); expert pass/fail + accuracy (05); gloss BLEU, lemma
  accuracy, sign-sequence exact match (01 §6, 06 §12); pose-distance and back-translation metrics
  (`research/design_proposals/`); scenario-based stress tests (04).
- **Status:** Answered 2026-10-22 → ADR-0020.

---

## E. Housekeeping found on 2026-09-27 — answered 2026-10-22

### E1. Which local machine has 24 GB RAM + RX 570?
- ADR-0004 names "one local machine (24 GB RAM, AMD Radeon RX 570)". ADR-0009 names two local
  machines (desktop, laptop). Which one is which is not stated.
- **2026-10-21 evidence:** The machine holding the full dataset is `DESKTOP-4NDR99B`: Radeon RX 570 with
  8 GB (registry), 23.9 GB RAM, Ryzen 5 3500X. `DATASET_WORK_LOG.md` (2026-09-28) says "Computer:
  Desktop". So the desktop is very likely the RX 570 machine. **Status:** Answered 2026-10-22 — yes, the desktop (owner; ADR-0016).

### E2. `new_project_intake/` is missing
- The folder no longer exists on disk (its `README.md` is staged as modified but deleted in the working
  tree). `README.md` and `CLAUDE.md` still point to it as the inbox. Restore it, or change the inbox
  convention? **Status:** Answered 2026-10-22 — inbox retired (ADR-0021).

### E3. Analysis 07 still has two "Medical" comparison rows
- `07` table rows "Medical-domain signs" (line 21) and "Medical coverage" (line 80): IsharaKotha's 84
  "Disease & Treatment" signs vs 0 vs 0. The number is a genuine paper finding; the row exists because of the old
  medical context. Keep or remove (D3)? **Status:** Answered 2026-10-22 — removed (ADR-0021).

### E4. Conservative rule on sharing videos
- `CLAUDE.md` rule 7 / `constitution.md` §2.8 say "until origin, licence and consent are known". B1 now
  answers that, but D4 keeps the defaults unchanged, so the rule stays as written. Should the wording
  change? **Status:** Answered 2026-10-22 — re-worded per the owner's public-release permission (ADR-0017).

---

## F. Raised by the 2026-10-21 audit + design plan — answered 2026-10-22

**Blocking (needed before implementation):**

### F1. Approve the proposed overall direction?
- Model A (Bangla → gloss) + Model B (gloss → MediaPipe motion), pseudo-glosses for the full set,
  retrieval/mean baselines, avatar as a display layer (plan 03 §C–§E).
- Alternative: direct text → motion (simpler; weaker gloss/grammar story).
- **AI recommendation:** approve; keep text → motion as an ablation. **Status:** Answered 2026-10-22 (ADR-0014).

### F2. Is a BdSL-competent gloss reviewer available?
- A team member, a signer from the recordings, or the RA.
- Without one, glosses stay "team-reviewed" and every grammar claim is provisional.
- **Recommendation:** name one person, even for a 20-item check. **Status:** Answered 2026-10-22 — a BdSL-competent person is available later; provisional annotations now (ADR-0015).

### F3. Data permissions + repo visibility
- (a) May 50 videos be **copied** into `dataset/pilot50_v1/` (gitignored)?
- (b) May derived features (which include face landmarks) be uploaded as a **private** Kaggle dataset
  (no videos)?
- (c) Is `github.com/RRM006/sign_avatar_cse498r` public? The 50 sample videos with identifiable faces
  are pushed there.
- Relates to E4. **Recommendation:** yes to (a), yes to (b) for features only. **Status:** Answered 2026-10-22 — (a) yes; (b) yes, features only, no raw face mesh; (c) public on purpose, with permission (ADR-0017). Reuse licence: G1.

### F4. Can the team say who recorded which Index ranges?
- This is the only route to a signer-independent test. Record it as "team-reported".
- **Status:** Answered 2026-10-22 — unknown; not pursued (ADR-0018).

### F5. Avatar route for the prototype?
- Browser VRM (three-vrm + Kalidokit-style solver; fastest, older library).
- Or Blender + MPFB2 (robust offline renders; more retargeting work).
- **Recommendation:** browser VRM first, Blender as fallback. **Status:** Answered 2026-10-22 (ADR-0019; feasibility pending Day 5).

### F6. Kaggle as the main training platform?
- Kaggle primary, Colab fallback, local CPU for MediaPipe extraction. Amends ADR-0004/0009.
- **Recommendation:** yes. **Status:** Answered 2026-10-22 (ADR-0016).

**Not blocking:**

### F7. Colour-label cluster
- Index 3456/3457/3458/5096/5100/5102: visually identical (old pHash), but labelled white/red/black.
- Wrong labels, or subtly different videos? Proposed: exclude from training and the pilot.
- **Status:** Answered 2026-10-22 — retained as one "edited minimal pair" group; labels provisional (ADR-0018).

### F8. The earlier project `D:\CSE498R\Sign_Language\CSE498R_v2\`
- Sign→voice scope; remote `RRM006/sign-language-to-voice`.
- May its code and `.task` model files be reused (copied, not moved)? Should it be referenced in docs?
- Also: a 70 GB `D:\CSE498R\Sign_Language.zip` exists (not opened). **Status:** Answered 2026-10-22 — read-only reference, no code copied (ADR-0021).

### F9. Is Bangla-SGP (LREC 2026, 1,000 sentence–gloss pairs) released?
- The paper says GitHub, CC BY 4.0, "upon publication". **Status:** Answered 2026-10-22 — not a dependency; not investigated (ADR-0021).

### F10. Data-location wording
- ADR-0009 and `constitution.md` §3 say only the 50-clip sample is in the repo and the full set is on
  the desktop/Drive.
- Fact: the full set is inside this repo folder (gitignored) on the desktop.
- Amend the wording (proposed ADR-0017)? `CLAUDE.md` and `dataset/README.md` were corrected on
  2026-10-21. **Status:** Answered 2026-10-22 (ADR-0017).

### F11. Empty folder `misc/pdf/`
- It exists on disk (untracked, empty). Keep or remove? **Status:** Answered 2026-10-22 — left alone (ADR-0021).

---

## G. Open after the 2026-10-22 design review

### G1. Reuse licence and attribution for the public dataset
- The repo is public and the owner has permission to make the dataset public (ADR-0017). The repo has
  no LICENSE file, so the terms for reuse by others are not stated. Which licence (if any), which
  attribution text, and whether it covers videos, annotations, derived features and models:
  (TBD — decide with owner). Not blocking Day 1. **Status:** Open (owner input).

### G2. How common are edited "shared-segment" clips?
- The colour cluster shares identical opening frames across differently labelled clips. The full
  scan (Week 2) decides split S1 v1. S1 v0 (2026-10-22) links only the known colour cluster.
  **Status:** Open (measurement).

### G3. Kaggle limits
- Weekly GPU hours, session length and disk: record the numbers shown in the owner's account.
  **Status:** Open (measurement at account setup).

### G4. Python 3.12 + mediapipe 0.10.35
- The wheel lists 3.12; not installed or tested yet. Day 1 Step 1 checks it (ADR-0016).
  **Status:** Answered 2026-10-22 — works: Python 3.12.13 + mediapipe 0.10.35 in `.venv`;
  HolisticLandmarker in IMAGE and VIDEO mode with all 8 expected result fields (`test_log.md`,
  Day 1 Step 1). The ADR-0016 condition is met.

### G5. Avatar model details
- Whether the chosen CC0 VRM model has finger bones; VRM 0.x handling in three-vrm. Checked on Day 5.
  **Status:** Answered 2026-10-22 — `Base_Female.vrm` has 54 humanoid bones, including 30 finger bones.
  three-vrm 3.5.5 loads it as VRM 0.x; with `rotateVRM0` and x/z-negated quaternions, the round-trip
  error is ≤ 3.4° (`test_log.md`).

### G6. Deadline of the one-month deliverable
- Plan 03 assumed a buffer to 2026-11-20; not confirmed. **Status:** Open (owner input).

### G7. End users of the system
- Not stated (ADR-0007). **Status:** Open, not blocking.

### G8. Hand sides and mirroring
- Pilot QC (VIDEO mode, 2026-10-22): MediaPipe "left hand" coverage is 69.7% vs "right hand" 35.7%;
  left > right in 40 of 50 clips. By recording type:
  - portrait (38 clips): left 0.76 vs right 0.25;
  - landscape (9): left 0.59 vs right 0.73;
  - low-res (3): left 0.23 vs right 0.60.
  MediaPipe's hand labels agree with its own body-wrist labels (median 0.90), so the labels are
  consistent with each other.
- Unknown: whether some clips (or recording batches) are mirrored, e.g. by a front camera. If so,
  MediaPipe's "left" is the signer's real right hand. This matters for the avatar (Day 5) and for any
  statement about the dominant hand. Not inferred from the data.
- Needs: someone who knows how the videos were recorded, or a team member looking at a few clips per
  recording type. **Status:** Open (owner input). Day 4 used the labels as given (ADR-0026); the
  answer matters for Day 5 retargeting.

### G9. QC thresholds for weak clips
- Pilot QC reports values only. For example:
  - 792: right hand missing for up to 11.9 s;
  - 1829 (val): any-hand coverage 0.34;
  - 3802: no left hand at all.
- Whether and how weak clips are excluded or down-weighted is (TBD — decide with owner) before
  full-set training. **Status:** Open (owner input).

### G10. Team reviewer(s) for the pilot drafts
- The 50 drafts in `annotations/pilot50_v1_gloss_v01.csv` need a registered team reviewer
  (`annotations/REVIEWERS.csv`, `annotations/REVIEW_GUIDE.md`) before Model A can be trained on them
  (ADR-0024). Who reviews, and when: (TBD — decide with owner). Blocks Day 3 as planned; the
  alternatives are listed in `current_task.md`.
- 2026-10-22: T1 is registered (role `team`). The current rows are fake on purpose: no clip
  watched, `is_mock=true` (ADR-0025). Day 3 ran only as a labelled TEST run. **Status:** Open — a
  real video review by T1 is still needed for the real Model A run.

### G11. Which motion drives the Day 5 avatar demo?
- Day 4 pilot (`test_log.md`, 2026-10-22): Model B is close to the mean-motion baseline B0 on val/test.
  It moves at about 20–30% of the real speed (velocity ratio 0.20–0.30; hand-energy ratio
  0.05–0.09); diversity ratio 0.27–0.39.
- B1 (retrieval of a real training clip) has realistic motion amounts (velocity ratio ≈ 1.0), but it
  only replays a different sentence.
- Design doc 04 (D4 risk row): "Model does not fit → report it, keep B1 output for the demo".
- Options: Model B output, B1 output, or both side by side, each clearly labelled.
  **Status:** Answered 2026-10-22 — both side by side, labelled (ADR-0027).

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
- **2026-10-22** — B7 Signer count → unknown (~4–6 estimated by the owner, unverified); not inferred;
  results are signer-dependent (ADR-0018).
- **2026-10-22** — B8 Held-out split → S1 group-disjoint, deterministic, locked test (ADR-0018, in principle).
- **2026-10-22** — C1 Representation/avatar → 3D landmarks + blendshapes + masks; three-vrm + own
  retargeter; Blender fallback (ADR-0019).
- **2026-10-22** — C2 Text → gloss → G0 + Model A with review layers (ADR-0014, ADR-0015).
- **2026-10-22** — C3 Lexicon → gloss vocabulary table from reviewed data (ADR-0014).
- **2026-10-22** — C4 Unknown words → UNK hold + caption + log; fingerspelling future (ADR-0014).
- **2026-10-22** — C5 Evaluation → per-stage metrics + human evaluation when available (ADR-0020).
- **2026-10-22** — E1 RX 570 machine → the desktop (ADR-0016).
- **2026-10-22** — E2 Inbox → retired (ADR-0021).
- **2026-10-22** — E3 Medical rows in 07 → removed (ADR-0021).
- **2026-10-22** — E4 Video-sharing rule → re-worded: public release permitted, new channels need the
  owner's OK (ADR-0017).
- **2026-10-22** — F1 Direction → Model A + Model B + text → motion ablation + baselines (ADR-0014).
- **2026-10-22** — F2 Reviewer → BdSL-competent person later; provisional annotations now (ADR-0015).
- **2026-10-22** — F3 Pilot copy / private Kaggle features / public repo → yes / yes, features only /
  public on purpose with permission (ADR-0017). Reuse licence → G1.
- **2026-10-22** — F4 Signer per range → unknown; not pursued (ADR-0018).
- **2026-10-22** — F5 Avatar route → three-vrm first, Blender fallback (ADR-0019).
- **2026-10-22** — F6 Kaggle → primary; Colab fallback; local CPU extraction (ADR-0016).
- **2026-10-22** — F7 Colour cluster → retained as one edited-minimal-pair group (ADR-0018).
- **2026-10-22** — F8 Earlier project → read-only reference, no code copied (ADR-0021).
- **2026-10-22** — F9 Bangla-SGP → not a dependency (ADR-0021).
- **2026-10-22** — F10 Data-location wording → corrected (ADR-0017).
- **2026-10-22** — F11 `misc/pdf/` → left alone (ADR-0021).
- **2026-10-22** — G4 Python 3.12 + mediapipe 0.10.35 → works (Day 1 Step 1; `test_log.md`).
