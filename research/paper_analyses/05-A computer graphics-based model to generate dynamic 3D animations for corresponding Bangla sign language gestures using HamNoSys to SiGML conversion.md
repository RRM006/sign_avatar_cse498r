# Paper Review Form — BdSL 3D Animation via HamNoSys→SiGML

> Reader note: form filled strictly from the paper. Links were additionally verified live on 2026-09-25 (marked **[verified]**). Anything not stated in the paper is flagged, never guessed.

---

## 1. Basic Information

- **Title:** A computer graphics-based model to generate dynamic 3D animations for corresponding Bangla sign language gestures using HamNoSys to SiGML conversion
- **Authors:** Ahsanul Karim; Muhammad Aminur Rahaman; Md. Ariful Islam; Md. Ariful Islam (two distinct authors sharing this name); Anichur Rahman; Tanoy Debnath; Utpol Kanti Das
- **Year:** 2026 (journal issue); published online 25 Nov 2025 (received 28 Oct 2024, accepted 26 Aug 2025)
- **Venue / Journal:** Artificial Intelligence Review (Springer), Vol. 59, Article 25
- **Paper link:** https://doi.org/10.1007/s10462-025-11370-z
- **Code / Model / Dataset link:**
  - Code: https://gitlab.com/devarifkhan/bdsl-3d-animation **[verified live]** — note: abstract calls it "GitHub" but URL is GitLab; it is a **Laravel/PHP web app** (last commit Jun 2024), not Python/ML code
  - Dataset (SiGML): https://doi.org/10.5281/zenodo.12152444 **[verified live]** — ~45 kB total, one small `.sigml` file per Bangla letter/word/numeral, published 23 Jun 2024
  - Testing-input spreadsheet: Google Sheets link given in Sect. 4.4 of the paper
- **License note:** paper text is CC BY-NC-ND 4.0 (non-commercial, **no derivatives**) — check before reusing/adapting their material.

**Why this matters for our project:** This is a very recent, fully open (code + data) Bangla text/voice → 3D BdSL avatar system — the closest prior work to our project's goal.

---

## 2. Relevance to Our Project

**Primary area(s):**
- ☑ Bangla / Low-resource NLP
- ☑ Text-to-Sign Language (Sign Language Production)
- ☑ 3D Avatar / Sign Animation
- ☑ NLP / Grammar Processing (rule-based Bangla parsing)
- ☑ Motion Generation (notation-driven, not learned)
- ☐ Sign Language Recognition
- ☐ Other

| Aspect | Score /5 | Reason |
|---|---|---|
| Bangla relevance | 5 | Entirely Bangla: text, voice, numerals, dialects (Dhaka/Chittagong/Sylhet tested) |
| Sign-language relevance | 5 | Core task is Bangla Sign Language (BdSL) production |
| Text-to-sign translation | 4 | Complete text→sign pipeline, but rule-based lookup with only ~90 sign classes + fingerspelling fallback; no learned translation |
| NLP / grammar | 3 | Rule-based parsing, root-word extraction, composite-numeral decomposition, BdSL word-order rewriting — but rules are not fully specified in the paper |
| Sign/motion generation | 3 | Motion = pre-made HamNoSys→SiGML files concatenated; no motion synthesis/smoothing of their own |
| 3D avatar / animation | 4 | Uses JASigning / UEA avatar engine driven by SiGML; proven to work, but avatar/rig/render details are thin (they reuse an existing engine) |
| Dataset usefulness | 4 | Public SiGML dataset (36 letters + 13 numerals + 41 words) directly reusable as seed + format template |
| Feasibility for our project | 5 | Zero training, no GPU (ran on i5 + MX350 2GB laptop); well inside our zero-budget Colab/local constraints |

**Overall relevance: High**
**Why:** It is essentially a working blueprint of our target system (Bangla text → BdSL → 3D avatar) that runs on consumer hardware with open code and data; its gaps (small vocabulary, no non-manual signals, rule-only NLP) are exactly where our project can add value.

**Why this matters for our project:** High-relevance anchor paper for our literature review and a candidate base architecture for our avatar stage.

---

## 3. Problem & Proposed Solution

**A. Problem:**
- Deaf–hearing communication gap in Bangladesh (~2.6M people affected); very few people know BdSL.
- No existing system automatically produces *flexible* BdSL 3D animations from Bangla text or voice; prior work covered only numerals or other sign languages (ISL/PSL/ArSL/ASL).
- BdSL resources/datasets are scarce; regional dialect variation complicates things.

**B. Approach:**
- Rule-based (non-ML) computer-graphics pipeline: Bangla text or voice input → Microsoft Speech API (voice→text) → rule-based Bangla parser (strip punctuation, get root words, decompose composite numerals into place-value tokens like কোটি/লক্ষ/হাজার/শত) → dictionary lookup of pre-built **HamNoSys → SiGML** files → sequence generator orders signs using BdSL grammar rewriting rules → JASigning/UEA 3D avatar plays the SiGML stream.
- **Fallback ("Bangla Word Spelling System"):** any word not in the dataset is split into letters and fingerspelled, so *any* Bangla word/phrase can be animated.
- Dataset built by mining ~6,000 existing English HamNoSys notations; ~20% matched BdSL (adapted), ~80% authored manually for BdSL, then converted to SiGML.

**C. Connection to our project:**
- **Directly useful:** the whole pipeline architecture; the public SiGML dataset; the spelling-fallback trick; the dialect-stratified evaluation protocol (Dhaka/Chittagong/Sylhet).
- **Technique we can adapt:** notation-based avatar stage (HamNoSys→SiGML→JASigning) as a training-free baseline; numeral/quantity decomposition; expert pass/fail validation with a BdSL expert.
- **Different from our project:** no ML/NLP model at all (our deliverable includes a trained model); tiny general-domain vocabulary; they also support voice input via live ASR, which is out of our scope.

**Why this matters for our project:** Gives us a zero-budget, no-training path to a working 3D avatar demo, while showing the vocabulary and NLP gaps our project must fill.

---

## 4. Methodology

### 4A. NLP / Text Processing
- **Input language:** Bangla (text or voice; voice converted by Microsoft Speech Recognition API).
- **Tokenization:** whitespace splitting; punctuation/whitespace removal; sentence → words → (if unmatched) letters; composite numerals → digit + place-value tokens.
- **Grammar / linguistic processing:** rule-based parser using "Bangla Linguistic rules"; BdSL grammar rewriting rules used by the sequence generator to fix sign order. Rules are *not* enumerated in the paper.
- **Translation method:** rule-based dictionary lookup (word → its SiGML file) via asynchronous API; fingerspelling fallback for out-of-vocabulary items.
- **Output representation:** ordered sequence of SiGML (XML) files sent to the animation server.

### 4B. Sign Language
- **Sign language:** Bangla Sign Language (BdSL), standard gestures.
- **Sign representation:** HamNoSys notation (hand shape, orientation, location, movement, non-manual framework) converted to SiGML markup.
- **Sign vocabulary:** 90 data classes per Sect. 4.2 (13 numerals + 36 letters + 41 words). ⚠️ Abstract and Zenodo description say **94 classes** — internal inconsistency (see Sect. 13).
- **Text-to-sign mapping:** exact-match file lookup in dataset folder; miss → spell word letter-by-letter.
- **Sign sequence generation:** "sequence generator" module arranges SiGML files in BdSL-correct order per grammar rewriting rules.

### 4C. ML / Deep Learning
- **Model:** None — no ML/DL model; rule-based lookup + string parsing system.
- **Pre-trained model:** None of their own (Microsoft Speech Recognition API used off-the-shelf for ASR).
- **Training data:** Not applicable — "trained dataset" in the paper means the pre-built HamNoSys→SiGML file collection, not model training.
- **Fine-tuning:** Not applicable.
- **Important hyperparameters:** Not applicable (only UI control: avatar speed, scale +3 to −3, default 0).
- **Training method:** Not applicable. Dataset construction method: mined ~6,000 English HamNoSys entries → kept/adapted the ~20% resembling BdSL → hand-authored the remaining ~80% → converted all to SiGML.

### 4D. 3D Avatar / Animation
- **Avatar type:** 3D signing avatar from the JASigning application; UEA (University of East Anglia) avatar animation engine. Avatar character name/identity: Not stated in the paper.
- **Rigging / skeleton:** Not stated in the paper (handled internally by JASigning; SiGML drives articulators).
- **Motion representation:** SiGML XML tags per sign (hand shape, orientation, location, movement); non-manual elements exist in the HamNoSys/SiGML framework but the expert review found them **absent** in the actual animations.
- **Animation method:** playback of stored per-sign SiGML files, concatenated in sequence by the animation server; no procedural/learned motion synthesis.
- **Motion smoothing / interpolation:** Not stated in the paper (left to the avatar engine; authors only claim "temporal consistency" qualitatively).
- **Rendering method:** Web GUI (6 pages: word, digit, alphabet, voice/text options, speed control) interfaced with the UEA engine; underlying rendering technology (e.g., WebGL) Not stated in the paper for their system.

### 4E. System Pipeline
Bangla text **or** voice → [ASR: Microsoft Speech API (voice only)] → [Rule-based Bangla parsing: strip punctuation, root words, composite-numeral decomposition] → [Async-API lookup of matching SiGML file; **miss → re-parse into letters → fingerspelling**] → [Sequence generator: BdSL grammar ordering] → [Animation server plays SiGML on JASigning/UEA 3D avatar] → BdSL 3D animation (+ user-adjustable speed).

**Why this matters for our project:** A concrete, trainable-model-free reference architecture we can copy for our avatar stage and extend (drop the ASR stage, since speech input is out of our scope; grow the SiGML dictionary).

---

## 5. Dataset

- **Dataset name:** BdSL SiGML dataset (Zenodo record titled "A Computer Graphics Approach to Creating New Method for Generating 3D Gesture Animations in Bangla Sign Language via HamNoSys to SiGML Conversion")
- **Language:** Bangla (text side)
- **Sign language:** Bangla Sign Language (BdSL)
- **Size:** 90 data classes (13 numeral + 36 alphabet + 41 word) per paper body; abstract/Zenodo say 94 — inconsistent. Total deposit ≈45 kB **[verified]**
- **Number of classes/signs:** 90 (or 94 as claimed elsewhere; see Sect. 13)
- **Text/sign pairs:** sign-level only — one SiGML file per letter/word/numeral; **0 sentence-level data classes** (sentences are composed at runtime)
- **Video / image / motion data:** motion-notation data only (SiGML files); no videos; paper figures show avatar stills
- **2D or 3D:** 3D (SiGML drives a 3D avatar)
- **Publicly available:** Yes **[verified live]**
- **Link:** https://doi.org/10.5281/zenodo.12152444 (files include Bangla letters, vowel signs া/ি/ু/ে/ো, ং, ঃ, ড়, য়, numerals, and words like আমি, নাম, খাবার, দুধ, গাড়ী)
- **Collection method:** mined from existing English HamNoSys datasets (~6,000 data points); ~20% similar to BdSL were adapted, ~80% manually created by authors for BdSL
- **Annotation method:** manual HamNoSys notation authoring → conversion to SiGML tags (hand shape / orientation / movement / notations per class)
- **Can we use it? Partial**
- **Why:**
  - ✔ Reusable as-is for Bangla letters/digits/basic words — instantly gives our avatar a fingerspelling + numeral capability.
  - ✔ Great format template: we can author additional signs the same way (HamNoSys → SiGML).
  - ✘ Only ~41 words; we would author our own SiGML entries.
  - ⚠️ Data quality check needed: one file (ই.sigml) is only 9 bytes **[verified]** — likely broken/empty.
  - ⚠️ License of the Zenodo record not stated in the paper and not visible in our fetch — verify before redistributing derivatives (paper text itself is CC BY-NC-ND 4.0).

**Why this matters for our project:** It's the only public BdSL SiGML resource found so far — a free seed dataset and a proven recipe for building our own sign dictionary.

---

## 6. Evaluation

| Task | Metric | Result |
|---|---|---|
| Translation (text→sign) | Accuracy = correctly generated animations / total inputs (Eq. 1, q=100), judged by a BdSL expert + BdSL dictionary | **97.50%** avg (text) — digits-only 100%, digits+text 100%, text-only numerals 95%, sentence 94%, word 96%, alphabet 100% |
| Translation (voice→sign) | Same accuracy after ASR | **94.75%** avg — digits 96%, sentence 91%, word 94%, alphabet 98%; by dialect: Dhaka 96.50%, Chittagong 93.50%, Sylhet 92.00%; −3–5% under loud noise |
| Sign recognition | — | Not covered in paper (system produces, doesn't recognize) |
| Sign generation | BdSL expert pass/fail on syntax, clarity, BdSL-rule conformance | 7 input types × 10 inputs → all "Pass"; expert noted missing non-manual signals and trouble with compound letters / complex words |
| Motion quality | No objective motion metric used | Qualitative claim of temporal consistency/fluency only; user-adjustable speed (−3…+3) |
| Avatar evaluation | User-based testing | 90 native Bangla speakers (30 each from Dhaka, Chittagong, Sylhet; 3 age groups 15–25/26–40/41–55; mixed gender; 10 voice inputs each) |
| Other (efficiency) | Avg computational cost per input via JS `performance.now()` (network ~2 Mbps) | **79.57 ms** avg — alphabet 9.45, word 11.11, sentence 47.61, digit-only 42.10, text-only numeral 99.52, digit+text numeral 267.65 |

- **Train / Validation / Test split:** Not applicable (no training). Test inputs per Table 3: text 150 sentences / 230 words / 45 alphabets / 95 numerals; voice 300 / 370 / 76 / 155. (⚠️ prose says "500 text tests" and "10 per voice input" — inconsistent with Table 3; see Sect. 13.)
- **Baselines:** No experimental baselines run. Table 6 = *qualitative* feature comparison vs. Caballero-Morales & Trujillo-Romero 2013; Nawshin 2020 (Protik); Sugandhi & Kaur 2020; Sanaullah 2022; Aliwy 2021; Rahaman 2020; Rahman 2023 (IsharaKotha); Dong 2024 (SignAvatar). Only numeric cross-comparison: 79.57 ms vs Sanaullah's 88.3 ms.
- **Hardware:** Asus VivoBook S15 S533EQ — Intel Core i5 11th Gen CPU + NVIDIA MX350 **2 GB** GPU; Plextone G30 headset mic. No dedicated GPU/training needed.
- **Framework:** Visual Studio Code (IDE); web application (repo shows Laravel/PHP + JS **[verified]**); Microsoft Speech Recognition API; JASigning/UEA avatar animation engine.

**Why this matters for our project:** Defines a cheap, copyable evaluation recipe (expert pass/fail + per-type accuracy + dialect-stratified user tests) and proves the avatar stage runs on hardware weaker than ours.

---

## 7. Results & Findings

- **Best result:** 100% text accuracy for alphabets and digit-form composite numerals; 79.57 ms average processing per input (faster than the 88.3 ms of Sanaullah et al.).
- **Compared with:** qualitative Table 6 comparison against 8 prior systems (ISL/PSL/ArSL/ASL/Mexican SL/BdSL); unique claimed features: all input types (sentence/word/alphabet/digit/composite numerals), Bangla voice + text, spelling capability, flexible async API.
- **Main finding:** a notation-driven (HamNoSys→SiGML) lookup system + fingerspelling fallback can animate *any* Bangla word/phrase without training per-word models, at interactive speed on a laptop.
- **What worked:** composite-numeral decomposition into place-value tokens; spelling fallback for unknown words; SiGML files tiny enough to stream over the web; dialect-diverse voice testing (Dhaka best, Sylhet worst).
- **Failure cases:** some Bangla compound letters (যুক্তাক্ষর) and complex words animated incorrectly; idioms/metaphors/context-dependent gestures unsupported; voice accuracy drops with background noise (−3–5%), accents, and non-Dhaka dialects.
- **Limitations stated by authors:** no non-manual signals (facial expressions, head tilts) in output; limited to standard BdSL gestures (no regional signing variance); narrow vocabulary needing expansion; needs advanced NLP for contextual meaning; future work: multimodal input (gaze), avatar personalization, community-driven dataset validation.

**Why this matters for our project:** Confirms the notation-lookup approach's ceiling (fast, robust for known signs; weak for open vocabulary & expressiveness) — our vocabulary coverage and any learned components must address exactly these gaps.

---

## 8. Reproducibility & Feasibility

- **Code available:** Yes — GitLab repo **[verified]** (Laravel/PHP web app; folders: app, routes, database, public, resources; includes `bdsl.zip`; last commit Jun 2024). Not a Python/ML codebase.
- **Dataset available:** Yes — Zenodo **[verified]** (~45 kB of `.sigml` files) + Google Sheets of test inputs.
- **Pre-trained model:** None (no learned model exists in this system).
- **GPU requirement:** None — paper ran everything on an i5 laptop with a 2 GB MX350. Our Colab T4 is unnecessary; local RX 570 machine is more than enough.
- **Free Colab feasible:** Yes, trivially (CPU-only workload). Caveat: it's a PHP/Laravel web app, so on Colab you'd need to install PHP or reimplement parsing in Python; JASigning avatar playback is the part that may not run inside Colab — likely better run locally/in a browser.
- **Missing resources:** JASigning/UEA animation-server setup instructions (not in paper); exact BdSL grammar rewriting rules (not enumerated); Microsoft Speech API configuration for Bangla; HamNoSys→SiGML converter tool itself is referenced as "a separate system … open to all" but not linked.
- **Estimated reproduction time:** Demo (text→animation with their dataset): ~2–5 days. Full paper replication incl. voice pipeline: 1–2 weeks. Full user study (90 participants + BdSL expert): weeks to months.
- **Feasibility: Partial** (Demo: fully feasible; voice input and avatar-server integration carry setup risk due to undocumented details).

**Why this matters for our project:** We can stand up a working BdSL avatar demo within a week at zero cost — a strong fallback/baseline while we research the vocabulary and NLP layers.

---

## 9. Direct Takeaways for Our Project

**Can adapt:**
1. **Notation-based avatar stage:** HamNoSys → SiGML → JASigning gives training-free 3D BdSL animation that fits our zero-budget, weak-GPU constraints.
2. **Fingerspelling fallback:** out-of-vocabulary words spelled letter-by-letter — directly applicable to names and terms outside our sign vocabulary; their 36-letter SiGML set covers this immediately.
3. **Numeral/quantity decomposition:** composite-numeral parsing (কোটি/লক্ষ/হাজার/শত + digits ০–৯) transfers to quantities in input text — e.g. "৩ বার", "৫ দিন", counts.
4. **Dataset-extension recipe:** mine existing HamNoSys → adapt/create BdSL notations → convert to SiGML; we can extend a BdSL SiGML dictionary the same way (starting from their 90 classes).
5. **Evaluation protocol:** expert pass/fail review + accuracy = correct animations/inputs + dialect-stratified testing (Dhaka/Chittagong/Sylhet) with age/gender balance.

**Not applicable:**
1. No ML/DL model to reuse — nothing for Colab T4 training; our translation layer must add its own approach.
2. Microsoft Speech Recognition API (voice input) — details are undocumented, and speech input is out of our scope.
3. Their general-domain 41-word vocabulary is too small to serve as our sign lexicon — usable only as seed + format.

**Open questions:**
1. Under what license do JASigning/UEA avatar engine and their SiGML dataset permit academic reuse and modification? (Paper text is CC BY-NC-ND.)
2. What exactly are the "BdSL grammar rewriting rules" (word-order changes Bangla→BdSL)? Not enumerated — needed before we trust sentence-level output.
3. How comprehensible is fingerspelling for long terms to real BdSL users (10+ letters)? Their expert flagged compound-letter errors.

**Useful project phase:**
- ☑ Literature review
- ☑ Bangla text processing
- ☑ Sign-language translation
- ☑ Dataset collection
- ☐ Model development (no models in paper)
- ☑ Sign sequence generation
- ☑ 3D avatar development
- ☑ Evaluation
- ☑ System integration

**Why this matters for our project:** This paper alone supplies our avatar-stage architecture, seed dataset, spelling fallback, and evaluation blueprint — roughly half of our pipeline design questions.

---

## 10. Action Items

1. Clone the GitLab repo; read the parser + sequence-generator code to extract the actual Bangla/BdSL rewriting rules (paper doesn't list them).
2. Download the Zenodo SiGML set; validate all files (ই.sigml is 9 bytes — likely broken) and inspect the SiGML schema/tags.
3. Install JASigning locally; play one of their `.sigml` files end-to-end to confirm the avatar stage works on our RX 570 machine.
4. Verify licenses (Zenodo record + JASigning/UEA engine) before deriving our dataset from theirs.
5. Read the referenced **IsharaKotha** corpus (Rahman et al. 2023, Heliyon — ~3,823 BdSL words, HamNoSys-based, avatar rating 3.32/4.00) — likely a much bigger vocabulary resource for us. *(Project citation for IsharaKotha: arXiv:2511.16896 (2025) — owner decision, ADR-0012.)*
6. Decide avatar stack for our project: JASigning/SiGML (proven here) vs. alternatives (e.g., Ham2Pose → 3D poses, cited in this paper) — compare in a short write-up.

**Why this matters for our project:** Turns this paper into concrete next steps: verify tooling and licences, and pick our avatar stack.

---

## 11. Questions for Supervisor / Team

**Supervisor:**
1. Should our avatar stage adopt this paper's SiGML/JASigning route (fast, proven, limited expressiveness) or invest in a learned 3D motion route (e.g., SignAvatar/Ham2Pose — heavier, needs GPU)?
2. Is a rule-based lookup + fingerspelling translation acceptable as our baseline, given CC BY-NC-ND licensing on this paper — do we need to reimplement rather than reuse their code?
3. How do we get BdSL expert validation for our signs (they used one qualified expert + dictionary comparison)? Any contacts at deaf organizations/schools?

**Team:**
1. Who sets up the Laravel repo + JASigning demo this week, and who audits the Zenodo SiGML files for broken entries?
2. How do we handle Bangla compound letters (যুক্তাক্ষর) in spelling — the paper reports failures here.

**Why this matters for our project:** Forces the key architecture, licensing, and validation decisions early, before we commit implementation effort.

---

## 12. Keywords & Concepts

**Relevant keywords:**
1. HamNoSys (Hamburg Notation System)
2. SiGML (Signing Gesture Markup Language)
3. Bangla Sign Language (BdSL) production / text-to-sign
4. JASigning / UEA avatar animation engine
5. Fingerspelling fallback + rule-based Bangla parsing (composite numerals)

**Terms we need to learn:**
1. HamNoSys symbol set (hand shape / orientation / location / movement / non-manuals) and how it maps to SiGML XML tags
2. SiGML schema + how signing-avatar players consume it (vs. BVH/SMPL-X motion formats)
3. BdSL linguistics: grammar rewriting rules, যুক্তাক্ষর (compound letters), regional dialect variation
4. (If reusing code) Laravel/PHP basics for their web app

**Why this matters for our project:** These are the exact concepts our avatar and sign-dictionary work will live in; HamNoSys/SiGML literacy is the entry ticket.

---

## 13. AI Reader Confidence Note

Everything below was **not clearly/explicitly stated** by the paper or is internally inconsistent — do not treat as fact:

- **Section 2 / 5:** Class-count contradiction — abstract & Zenodo description say **94 classes**, but Sect. 4.2 and Table 3 say **90** (13+36+41=90). Cannot determine the true count from the paper.
- **Section 6:** Test-count contradiction — prose says "tested **500** times for text input and **10** times for each voice input", but Table 3 totals 520 text and 901 voice tests, and Table 4 reports voice accuracy for sentences too. Cannot reconcile.
- **Section 6:** Accuracy Eq. 1 says q = 100, but per-type test counts differ; how p/q were computed per category is Not stated clearly.
- **Section 6:** The criterion for counting an animation as "correct" (expert judgment + dictionary comparison) has no formal rubric — subjective; Not stated in detail.
- **Section 4D:** Avatar character identity/name, rigging/skeleton spec, rendering technology, and any motion smoothing/interpolation — Not stated in the paper (delegated to JASigning/UEA engine).
- **Section 4A/4B:** The BdSL "grammar rewriting rules" and Bangla linguistic rules are referenced but never enumerated — Information unavailable.
- **Section 4A:** Which Microsoft Speech Recognition API/product, its Bangla language support, and dialect handling — Not stated in the paper.
- **Section 3B/8:** The "separate system … open to all" that converts HamNoSys→SiGML is mentioned but never named or linked — Cannot determine what tool to use for conversion.
- **Section 4E:** Whether lookup uses a real database or plain file folders — paper describes file/folder lookup; the repo contains a Laravel `database/` folder. Implementation may differ from the description. Unsure.
- **Section 5:** License of the Zenodo dataset — Not stated in the paper; not visible in our fetch of the record page. **Unsure: must check the Zenodo "Rights" field before reuse.**
- **Section 5:** Whether all 90/94 SiGML files are valid — we verified one 9-byte file (ই.sigml) that appears broken; full audit not done.
- **Section 1:** Abstract says "GitHub repository" but provides a GitLab URL — minor inconsistency, noted.
- **Paper metadata oddities (not form fields, but worth knowing):** Author-contribution section names "Neeraj Kumar" and "Lama Almogren", who are absent from the author list; the Conclusion references "The Visual Computer" journal goals although the paper appears in Artificial Intelligence Review (likely a leftover from a prior submission). Cannot determine cause from the paper.
- **Section 4.2:** Claims to address "user diversity and biases" during dataset creation/testing, but no methodology for this is described — Information unavailable.
