# constitution.md — The Project Constitution

> This is the stable core of the project. It changes very rarely. If something here needs to change,
> record it as a decision in `decisions.md`. Everything else must obey this file.

---

## 1. Purpose (one paragraph)

The project **"Bangla Text-to-Bangla Sign Language (BdSL) Translation Using a 3D Avatar"** investigates
how Bangla text can be converted into Bangla Sign Language and shown through a 3D avatar. It is an
initial, research-based project by a beginner ML/NLP team. The deliverable is a report, a literature
review, a trained model and results, aimed at a publishable research paper (ADR-0007). The literature
review is complete; the current phase is pipeline/system design (ADR-0012). Who the end users are is
**(TBD — decide with owner)**.
The project must always stay grounded in evidence and owner decisions. It must never present guesses,
proposals or future plans as facts or completed work.

## 2. Non-negotiable rules

1. **No invented facts.** Only the repo and the owner are sources of project facts. Unknowns are marked
   "(TBD — decide with owner)" or asked about. *Why:* the owner requires accuracy over speed, and a
   wrong "fact" in these docs spreads into every later session.
2. **The owner makes the design decisions.** The AI may research, compare and recommend, but it never
   locks in the pipeline, model, dataset strategy, sign representation, avatar technology, training or
   evaluation method. *Why:* the design is intentionally open during the research phase (ADR-0002).
   *Enforced by:* nothing goes into `decisions.md` as Accepted without the owner's explicit yes.
3. **Evidence, owner requirements, proposals and future work stay labelled and separate.** *Why:* the
   paper analyses contain many AI-written recommendations that could be mistaken for decisions.
4. **Not a medical project; no dialect focus** (ADR-0003). The wrong medical/dialect context blocks
   were removed from analyses 01–08 (ADR-0012); remaining mentions are genuine paper findings.
5. **AI does not read `research/papers/*.pdf`** (ADR-0006). Use `research/paper_analyses/`.
6. **Uncertain file operations need the owner's go.** No moving, renaming or deleting files when the
   reason is uncertain.
7. **Never commit secrets or credentials.** *(Conservative default — kept by owner, ADR-0013.)*
8. **Dataset videos stay inside the repo/team** until origin, licence and consent are confirmed.
   *(Conservative default — kept unchanged by owner, ADR-0013; see `open_questions.md` E4.)* *Why:*
   the clips show real, identifiable people. (Origin/permissions: team-owned, permissions in place —
   ADR-0008.)

## 3. Scope & major pieces (how it fits together)

**Owner-confirmed (ADR-0007):**
- **Input:** a Bangla text sentence. Speech input is out of scope.
- **Output:** BdSL, shown by a 3D avatar. Sign → text is out of scope.
- **Translation:** sentence-level, handling BdSL grammar/word order — not word-by-word lookup.
- **Data role (ADR-0008):** the team's videos are primarily training data; extracted pose/landmarks feed
  the sign-generation model; a held-out evaluation split is reserved.
- **Interim step (ADR-0010):** MediaPipe Holistic for landmark extraction only.

**Everything else in between is (TBD — decide with owner):** sign representation, text → sign
mapping, sign lexicon, avatar technology, model and training, and the build order (ADR-0010). Options
are listed in `open_questions.md` and `research/design_proposals/`; none has been chosen.

**What exists today (evidence):**
- A completed literature base: 6 papers, 6 per-paper analyses and 2 comparisons (`research/`), plus
  2 design proposals (`research/design_proposals/`, proposals only).
- A team-owned dataset (ADR-0008): Bangla sentence sheets plus a 50-clip video sample in
  `dataset/initial_dataset/`. The full video set is on the desktop / Drive (ADR-0009).

**Build order:** (TBD — defined after the design is chosen).

## 4. Hard constraints (the box we build inside)

- **Zero budget.** Free tools, data and services only. *(Owner-confirmed 2026-09-27; reason not
  stated.)*
- **Compute:** Google Colab (T4 GPU, ~15 GB VRAM, ~12 h session limit) and a local machine (24 GB RAM,
  AMD Radeon RX 570). *(Owner-confirmed 2026-09-27.)* Roles (ADR-0009): Colab for training, desktop
  for full-dataset work, laptop for code and small samples. Which machine has the RX 570: (TBD —
  confirm with owner).
  - *Unverified notes from the paper analyses (not facts yet):* Colab has no display, so desktop GUI
    tools cannot render there, and the RX 570 may have poor GPU-compute (ROCm) support. Verify these
    before relying on them.
- **Language:** Bangla (primary). The sign language is BdSL.

## 5. Realistic expectations (so we don't fool ourselves)

Points the paper analyses raise repeatedly (evidence from the literature, not project results):
- **BdSL resources are scarce.** The largest BdSL sign corpus found so far (IsharaKotha, 3,823 signs)
  is not confirmed to be publicly available. The public SiGML set found is small (~90–94 classes).
- **Word-by-word lookup is not full translation.** No analysed paper spells out BdSL grammar or
  word-order rules (paper 05 says it uses some but never lists them). Sentence-level quality was lower
  than word-level quality where both were measured (`07` §8).
- **Evaluation is weak across the field.** None of the analysed papers used an automatic or objective
  metric for signed output; results were human-judged. Credible evaluation likely needs BdSL-fluent
  people, which takes time to arrange.
- **Non-manual signals** (facial expressions and similar grammatical cues) were missing, unused, or not
  BdSL-specific in the analysed systems (`07` §8).
- Evaluation will combine human evaluation (experts / deaf signers / interpreters) with an automatic
  metric (ADR-0011). The exact metric and protocol are **(TBD — decide with owner)**. "It runs" is not
  success.
