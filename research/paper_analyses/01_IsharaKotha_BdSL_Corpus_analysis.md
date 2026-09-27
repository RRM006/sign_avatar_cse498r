# Paper Analysis — IsharaKotha: A Comprehensive Avatar-based Bangla Sign Language Corpus

> Filled for: Bangla Text-to-BdSL Translation using a 3D Avatar (beginner team, zero budget, Colab T4 + local RX 570).
> Source: `uploads/IsharaKotha A Comprehensive Avatar-based Bangla Sign Language Corpus.pdf` (20 pp., fully parsed).
> Convention used below: **"Not stated in the paper"** = the authors never mention it. **"Unsure: …"** = ambiguous.

---

## 1. Basic Information

- **Title:** IsharaKotha: A Comprehensive Avatar-based Bangla Sign Language Corpus
- **Authors:** MD. Ashikul Islam, Prato Dewan, Md Fuadul Islam, Md. Ataullha, M. Shahidur Rahman (corresponding) — Shahjalal University of Science & Technology, Sylhet, Bangladesh
- **Year:** 2025 (arXiv v1 dated 21 Nov 2025)
- **Venue / Journal / Conference:** arXiv preprint, `arXiv:2511.16896v1 [cs.HC]`. Layout is an Elsevier-style journal template, but the target journal is **not stated in the paper** (no DOI, no journal name, no acceptance note).
- **Paper link:** https://arxiv.org/abs/2511.16896
- **Code / Model / Dataset link:**
  - Evaluation web interface (the only link given): http://bdsl-isharakotha.ap-1.evennode.com
  - Code: **Not stated in the paper** (no repository linked)
  - Lemmatizer model: **Not stated in the paper** (no weights/checkpoint linked)
  - Corpus files (3,823 SiGML): **Not stated in the paper** (no download link, no licence, no data-availability statement)
  - Third-party tools named (external, not authored by them): HamNoSys editor (Univ. Hamburg, DGS-Korpus), SiS-Builder, SiGML Player, JASigning (`vhg.cmp.uea.ac.uk/tech/jas/vhg2023`)

**Why this matters for our project:** This is the single closest match to our goal that exists in Bangla — same language, same output modality (3D avatar), same zero-cost toolchain. But the absence of a corpus/code link is the #1 blocker to resolve before we plan anything around it.

---

## 2. Relevance to Our Project

**Primary area(s):**
- [x] Bangla / Low-resource NLP
- [x] Sign Language Generation (primary — this is a generation *resource*, not a recognition paper)
- [x] Text-to-Sign Language (partial — word-level lookup, not a translation model)
- [x] 3D Avatar / Sign Animation
- [x] NLP / Grammar Processing (only lemmatization)
- [ ] Sign Language Recognition — not covered
- [ ] Motion Generation (no learned motion synthesis) — not covered
- [ ] Other: Sign-language *corpus/dictionary construction* + *human evaluation protocol* (both directly reusable by us)

| Aspect | Score /5 | Reason |
|---|---|---|
| Bangla relevance | **5** | Entirely Bangla; built on the BSTI-standardised national BdSL sign set (~4,000 signs); Bangla morphological inflection handled by their lemmatizer. |
| Sign-language relevance | **5** | 3,823 real BdSL signs across 36 semantic categories, transcribed in HamNoSys. |
| Text-to-sign translation | **3** | There *is* an end-to-end Bangla sentence → animation pipeline, but "translation" is lemma → dictionary lookup. No gloss translation model, no syntax/word-order handling, no OOV fallback. Authors explicitly say the dynamic system is unfinished. |
| NLP / grammar | **2** | Only lemmatization (79.22% accuracy). No POS tagging, no parsing, no Bangla→BdSL grammar rules, no handling of tense/aspect/negation/question structure. |
| Sign / motion generation | **3** | Motion is *authored* (hand-written HamNoSys) then *rendered* (SiGML→JASigning). Nothing is learned or synthesised; no inter-sign transitions or coarticulation discussed. |
| 3D avatar / animation | **4** | Concrete, free, working toolchain: HamNoSys editor → SiS-Builder → SiGML Player / JASigning; 5 standard avatars; real-time and web-deployable. Docked 1 point because rigging, skeleton and rendering internals are never described. |
| Dataset usefulness | **4** | If obtainable, this replaces months of manual sign-notation work for us and gives a ready BdSL lexicon + a human-evaluation benchmark. Docked 1 point because availability/licence is unconfirmed. |
| Feasibility for our project | **4** | Everything runs on free/CPU-level tools; the lemmatizer is a tiny BiLSTM seq2seq that trains fine on a Colab T4. The infeasible part is *re-creating* 3,823 notations by hand — so our plan must be reuse, not reproduction. |

**Overall relevance: HIGH**

**Why:** It is the first and (per the paper) only HamNoSys-based BdSL corpus, it uses exactly the free avatar pipeline we can afford, and it supplies three things we need and cannot easily build ourselves: (1) a validated BdSL sign inventory in a machine-readable notation, (2) a working Bangla lemma→sign lookup architecture, and (3) a published human-evaluation protocol with deaf-user ratings we can copy for our own system. Its weaknesses (no grammar, no OOV handling, no learned motion) are precisely the research gaps our project can claim.

**Why this matters for our project:** Treat this as our **foundational citation and our baseline architecture**, and simultaneously as the source of our project's novelty claim — the paper stops where a real translation system begins.

---

## 3. Problem & Proposed Solution

**A. Problem**
- Deaf/hard-of-hearing Bangladeshis (~13.7M with ≥40 dB loss per 2011 census, cited in paper) lack access to interpreters, who are scarce.
- Existing Bangla SL tools are video-clip based → large storage, costly to produce, slow; and prior work covers only alphabets/numerals/a few words.
- **Root blocker:** no BdSL *corpus* exists. Without a corpus, no text-to-sign generation system can be built. Prior BdSL datasets are tiny or non-avatar (13 numerals; 6,000 videos/200 words; 29,490 images/49 alphabets).

**B. Approach**
1. Take the BSTI-standardised BdSL dictionary (~4,000 signs, adopted after workshops with the Deaf community, guided by BCC).
2. Manually author a **HamNoSys** notation for each word using the open-source HamNoSys editor (handshape, orientation, location, movement, two-hand/symmetry operators, non-manual features).
3. Convert each notation to a **SiGML** (XML) file with the public **SiS-Builder** web tool.
4. Validate the animation in **SiGML Player / JASigning** (3D avatar, real-time); only correct animations enter the corpus → **3,823 signs**.
5. Add a **BiLSTM seq2seq + attention lemmatizer** (trained on a self-built corpus of 94,781 unique inflected Bangla words, 79.22% accuracy) to reduce full sentences to root words.
6. Build a **web evaluation interface** (Alphabets / Numbers / Words / Sentences) and collect 3,828 ratings from 2 professional interpreters + 1 deaf sign-language user on a 1–4 categorical scale → pooled mean **3.14/4**.

**C. Connection to our project**
- **Directly useful:**
  - The **whole avatar toolchain** (HamNoSys editor → SiS-Builder → SiGML/JASigning) — free, no GPU, and it is the fastest legal route to a 3D BdSL avatar for us.
  - The **3,823-sign corpus** itself, if released (must be confirmed by email to the corresponding author).
  - Their **evaluation protocol** (4-point Bad/Average/Good/Excellent, separate sections, interpreters + deaf user, score formula) — we can adopt it verbatim for our demo.
  - Their **limitations list** = our project's contribution space.
- **Technique we can adapt:**
  - Lemma-based dictionary lookup as the *first* version of our text→sign mapper (simple, explainable, zero-budget).
  - Seq2seq BiLSTM+attention as a lightweight Bangla morphological normaliser that fits a T4 easily.
  - Category-wise sign organisation (36 categories) as our vocabulary schema.
- **Different from our project:**
  - No *translation* model: they never map Bangla syntax to BdSL gloss order; we must add that.
  - No learned/continuous **motion generation**: signs are isolated, hand-authored clips; concatenation quality between signs is not addressed.
  - Their lemmatizer accuracy (79.22%) is a bottleneck they did not try to improve; modern Bangla morphological tools / transformers would likely beat it.

**Why this matters for our project:** We should position our work as *"IsharaKotha + grammar + OOV handling + a modern Bangla NLP front-end"* rather than rebuilding the corpus — that keeps the project achievable inside a Colab-only, zero-budget constraint.

---

## 4. Methodology

### 4A. NLP / Text Processing
- **Input language:** Bangla (full sentences).
- **Tokenization:** Not stated in the paper. **Unsure:** the decoder "produces the output sequence token by token" over inflected *words*, but whether tokens are characters, subwords or words is never specified.
- **Grammar / linguistic processing:** Lemmatization only (inflected word → root word). No POS tagging, no dependency/syntactic parsing, no Bangla→BdSL word-order or grammar transformation, no handling of non-manual grammar markers (negation, questions).
- **Translation method:** Not a learned translation. Pipeline is: Bangla sentence → lemmatize → **retrieve** the pre-stored SiGML file for each root word → concatenate animations. Authors state the system only works when *every* root word exists in the sign dictionary.
- **Output representation:** Root words (lemmas) → HamNoSys notation → SiGML (XML) → avatar animation.

### 4B. Sign Language
- **Sign language:** Bangla Sign Language (BdSL), using the BSTI-standardised national sign set (~4,000 signs) documented from the CDD manuals and the BCC "Specification of Bangla Sign Language (first version)" user guideline (obtained personally from the standardisation committee).
- **Sign representation:** HamNoSys (Hamburg Notation System, ~200 symbols: handshape, orientation, >30 location symbols, straight/circular movement, repetition, two-hand symbols, non-manual head/face/lip/eye features) encoded as SiGML XML with `<hamnosys_manual>` and `<hamnosys_nonmanual>` blocks and a `gloss` attribute.
- **Sign vocabulary:** 3,823 words total — 49 alphabets, 10 numbers, and 3,764 word signs across 36 categories (largest: Others 776, Human Characteristics 470, Household Items 342, Education 269, Food & Drinks 234; **Disease & Treatment only 84**).
- **Text-to-sign mapping:** One Bangla word ↔ one HamNoSys notation ↔ one SiGML file (a static lexicon / lookup table). No many-to-one disambiguation, no sense selection, no multi-word signs discussed.
- **Sign sequence generation:** Sequential retrieval and playback of per-word SiGML animations in input order. No transition blending, no timing model, no grammar-driven reordering. Non-manual features are *representable* in the notation but sentence-level use is not described.

### 4C. ML / Deep Learning
- **Model:** Seq2Seq lemmatizer — **BiLSTM encoder** (bidirectional hidden states + concatenated context vectors) → **attention** → **unidirectional LSTM decoder** (initialised from encoder context) → **dense layer with softmax** for next-token prediction.
- **Pre-trained model:** Not stated in the paper (no mention of Bangla embeddings, pretrained LMs, or transfer learning).
- **Training data:** Self-developed corpus of **94,781 unique inflected Bangla words** (inflected form → lemma pairs). Construction method, source text, and whether it is public: **Not stated in the paper**.
- **Fine-tuning:** N/A (no pretrained base model reported).
- **Important hyperparameters:** **Not stated in the paper** — no embedding dim, hidden size, layers, dropout, optimizer, learning rate, batch size, epochs, or sequence-length limits.
- **Training method:** **Not stated in the paper.** Only outcome reported: **79.22% accuracy**; no loss curve, no train/val/test split, no BLEU/exact-match definition, no error analysis.

### 4D. 3D Avatar / Animation
- **Avatar type:** Standard JASigning virtual humans — the paper says JASigning offers **a choice of five distinct standard avatars**; a 3D avatar from SiGML Player was used to visually check animations. Which specific avatar(s) were used for the corpus/evaluation: **Not stated in the paper**.
- **Rigging / skeleton:** Not stated in the paper (JASigning's skeleton/BVH layer is only referenced via citation, never described).
- **Motion representation:** HamNoSys parameter set (handshape, orientation, location, movement, symmetry/two-hand operators, hand-replace operator, repetition) serialised to SiGML XML; manual and non-manual channels separated.
- **Animation method:** Real-time synthesis from SiGML by JASigning (Java, desktop + web) / SiGML Player (Windows, Mac, Linux). No keyframing, mocap, or learned motion model.
- **Motion smoothing / interpolation:** **Not stated in the paper.** Nothing about blending between consecutive signs or transition artefacts.
- **Rendering method:** Not stated in the paper (no renderer, engine, frame rate, resolution, or web-vs-desktop rendering detail). The evaluation system is a hosted Node web app.

### 4E. System Pipeline
```
Bangla sentence
  → [1] Lemmatization: BiLSTM seq2seq + attention decoder (79.22% acc)
  → [2] Root words (lemmas)
  → [3] Lexicon lookup: lemma → stored HamNoSys notation → corresponding SiGML file
  → [4] Avatar animation: SiGML played by JASigning / SiGML Player (3D avatar, real-time)
  → Output: sequential animated BdSL signing of the sentence
```
Corpus-construction pipeline (offline, separate):
```
BSTI BdSL dictionary word → manual HamNoSys notation (HamNoSys editor)
  → SiGML file (SiS-Builder) → animation check (SiGML Player) → sign validation
  → IsharaKotha corpus (3,823 SiGML files)
```
Hard constraint: fails/stops if any root word is missing from the 3,823-sign dictionary.

**Why this matters for our project:** This 4-step pipeline is directly copyable as our v0.1 demo — every component is free and CPU-friendly — and steps 1 and 3 are exactly where our project must improve (better Bangla normalisation, OOV fallback, gloss-order grammar).

---

## 5. Dataset

- **Dataset name:** **IsharaKotha** (BdSL sign corpus). Secondary asset: an unnamed **Bangla inflected-word/lemma corpus of 94,781 unique words**.
- **Language:** Bangla (spoken/written text side).
- **Sign language:** Bangla Sign Language (BdSL), BSTI-standardised.
- **Size:** 3,823 word-level sign entries (49 alphabets + 10 numbers + 3,764 category words) in Table 1. Plus 94,781 inflected Bangla words for the lemmatizer.
- **Number of classes/signs:** 3,823 distinct signs, grouped into 36 semantic categories.
- **Text/sign pairs:** 3,823 (Bangla word ↔ HamNoSys/SiGML). Sentence-level pairs: **Not stated in the paper** — the evaluation used 17 + 19 + 20 sentence instances rated by the three evaluators, but no sentence dataset is described or sized.
- **Video / image / motion data:** **Motion description files only (SiGML/XML)** — no human video, no images, no skeletal mocap data. Animations are synthesised on demand by the avatar.
- **2D or 3D:** **3D** (avatar animation driven by SiGML).
- **Publicly available:** **Unsure:** the paper never states that the corpus is released. Only the evaluation *interface* is linked; there is no download URL, repository, DOI, or licence, and no data-availability statement in the PDF. The corpus must be assumed **not yet public** until confirmed with the authors.
- **Link:** Evaluation interface: http://bdsl-isharakotha.ap-1.evennode.com (corpus download link: not given).
- **Collection method:** Manual authoring by the researchers. HamNoSys notations were created with the open-source HamNoSys editor following the BSTI-standardised BdSL dictionary and the BCC "Specification of Bangla Sign Language" guideline; SiGML generated via the public SiS-Builder web platform; each animation visually verified in SiGML Player before inclusion. No crowdsourcing, no sensors, no cameras. The 94,781-word inflected corpus's collection method: **Not stated in the paper**.
- **Annotation method:** Author-created HamNoSys transcription (handshape / orientation / location / movement / two-hand operators), with a Bangla natural-language "sign description" per word (see Table 2 examples). Quality was then judged by 2 professional interpreters and 1 deaf sign-language user (a hearing-impaired athlete) through 3,828 categorical ratings (1=Bad … 4=Excellent) plus an optional free-text comment box. Inter-annotator agreement statistics: **Not stated in the paper**.
- **Can we use it?** **Partial**
- **Why:**
  - *Yes-side:* It is the only machine-readable BdSL lexicon of this size; SiGML is an open standard playable by free JASigning tooling; categories map cleanly onto a vocabulary schema; the evaluation protocol is reusable.
  - *No/blocker-side:* Availability and licence unconfirmed → must email the corresponding author (rahmanms@sust.edu / ashibul03abir@gmail.com). Even if released: word-level only, no sentence/gloss annotations, no Bangla→BdSL word-order data, some signs admittedly unfinished, and alphabets scored worst (2.48/4 from the deaf user) — so raw reuse would inherit those quality gaps.

**Why this matters for our project:** Our single highest-value action is to establish whether we can legally obtain these 3,823 SiGML files; that answer decides whether our project is "build a translation layer on an existing corpus" (feasible in a semester) or "author our own small domain-specific corpus" (feasible only for ~100–300 signs).

---

## 6. Evaluation

Only metrics actually reported in the paper:

| Task | Metric | Result |
|---|---|---|
| Translation (Bangla → root word) | Accuracy of the lemmatizer | **79.22%** on their self-developed 94,781-word corpus |
| Avatar / corpus quality — pooled | Mean categorical human rating (1=Bad, 2=Average, 3=Good, 4=Excellent); Score = (B·1 + A·2 + G·3 + E·4) / N | **3.14 / 4** over 3,828 ratings (116 Bad, 294 Average, 2,346 Good, 1,072 Excellent) |
| — Interpreter 1 (30 alphabets, 10 numbers, 205 words, 17 sentences) | Same | **3.32 / 4** (Alphabets 2.83, Numbers 3.60, Words 3.40, Sentences 3.06) |
| — Interpreter 2 | Same | **3.17 / 4** (Alphabets 2.66, Numbers 3.60, Words 3.09, Sentences 3.32) |
| — Deaf sign-language user (hearing-impaired athlete) | Same | **3.13 / 4** (Alphabets 2.48, Numbers 4.00, Words 3.14, Sentences 3.05); 3,223 of the 3,828 ratings came from this one user |
| Sign recognition | — | N/A (not addressed) |
| Sign generation (objective: BLEU/WER/motion error) | — | **Not covered in paper** — no automatic metric is used anywhere |
| Motion quality (objective) | — | **Not covered in paper** — judged only subjectively by humans |

- **Train / Validation / Test split:** **Not stated in the paper** for the lemmatizer (only "trained and tested on a self-developed corpus of 94,781 unique inflected Bangla words"). For the human evaluation: items were **randomly selected** per section; no held-out split concept applies.
- **Baselines:** No quantitative baseline system. Only a **qualitative scope comparison** (Table 7) against three prior BdSL datasets: Islam et al. 2022 (13 numeral gestures, HamNoSys+SiGML), Sams et al. 2023 (6,000 sign videos, 200 unique words), Hasib et al. 2022 (BDSL49: 29,490 images, 49 alphabets).
- **Hardware:** **Not stated in the paper** (no GPU/CPU/RAM/training-time information at all).
- **Framework:** **Not stated in the paper** for the deep-learning model (no PyTorch/TensorFlow/Keras mention). Named software tools: HamNoSys editor, SiS-Builder, SiGML Player, JASigning; the evaluation system is a hosted Node.js web app (inferred from the `evennode.com` URL, **not stated in the paper**).

**Why this matters for our project:** Their evaluation is 100% human-subjective with no automatic metric — so if we add any objective evaluation (gloss BLEU, lemma accuracy, sign-sequence exact match, timing/transition error), we immediately have a measurable contribution over this paper. We should also reuse their 1–4 scale and their interpreter + deaf-user setup for credibility.

---

## 7. Results & Findings

- **Best result:** Numbers section rated **4.00/4** by the deaf sign-language user (perfect); pooled corpus score **3.14/4** ("Good"→"Excellent" band); Words sections 3.09–3.40 across evaluators.
- **Compared with:** Prior BdSL resources in *scope only* — 13 numerals (Islam 2022), 200 words/6,000 videos (Sams 2023), 49 alphabets/29,490 images (Hasib 2022). IsharaKotha is presented as the largest HamNoSys-based BdSL resource (3,823 word animations). No model-vs-model comparison.
- **Main finding:** A large, usable BdSL sign corpus can be built **without video recording, without hiring volunteers, and with modest storage**, using standardised dictionary + HamNoSys + SiGML + free avatar tools — and deaf users/interpreters rate the resulting animations as largely intelligible and good quality. Avatar-based generation is argued to be preferable to pre-recorded video for memory, cost and speed.
- **What worked:**
  - Starting from an officially standardised sign set (BSTI/BCC) instead of inventing signs.
  - HamNoSys as the intermediate representation — flexible enough to encode two-handed signs via symmetry and hand-replace operators.
  - Free public conversion tools (SiS-Builder) and a real-time player (JASigning/SiGML Player) for instant validation loops.
  - Including an actual deaf user, not only hearing interpreters, in evaluation.
  - Numbers/numerals animate best (4.00/4).
- **Failure cases:**
  - **Alphabets are the weakest section** (2.48/4 from the deaf user; 11 "Bad" ratings; also 2.66 and 2.83 from the interpreters).
  - **Directional / body-contact signs** could not be represented properly: touching lower body parts, touching the back side of body parts, pointing along the spine.
  - **Scenario-based real-time facial expressions** were hard to encode.
  - Some dictionary signs remain **unfinished** (Figure 17 shows examples).
  - Sentence-level scores (3.05–3.32) are **lower than word-level** for two of three evaluators → concatenation/sequence quality is weaker than isolated signs.
  - The system **breaks on any out-of-vocabulary root word**.
- **Limitations stated by authors:**
  - Bangla is low-resource and morphologically complex, making resource development and benchmarking hard.
  - BdSL itself is "equally complicated and diverse"; certain directional signs need special handling.
  - The system **assumes all root words exist in the sign dictionary**; mapping the entire Bangla vocabulary to the 3,823 signs is **not yet accomplished**, so it is not a dynamic translation system.
  - Future work named by authors: a dynamic text→sign translation system, and integration with speech recognition.

**Why this matters for our project:** Their failure list is our to-do list. Alphabets, directional/body-contact signs, facial expressions, sentence-level transitions and OOV words are all open, and each is a defensible sub-goal for a beginner research project.

---

## 8. Reproducibility & Feasibility

- **Code available:** **No** — nothing is linked. Only the evaluation web interface is public.
- **Dataset available:** **Unsure** — no corpus link, licence, or data-availability statement in the paper. Must be requested from the authors.
- **Pre-trained model:** **No** — no lemmatizer checkpoint released; hyperparameters also unstated, so exact re-implementation is impossible from the paper alone.
- **GPU requirement:** **Not stated in the paper.** Practical inference (ours, not the paper's): the BiLSTM seq2seq lemmatizer over ~95k short word sequences is very small — a Colab T4 (or even CPU) is more than enough; the HamNoSys/SiGML/JASigning avatar side is CPU/Java and needs **no GPU at all**.
- **Free Colab feasible:** **Partial.**
  - Feasible on Colab T4: replicating/improving the lemmatizer *if* we build our own inflected-word→lemma data (Bangla morphology resources exist); training any text→gloss model we design.
  - **Not feasible inside Colab:** JASigning / SiGML Player are desktop Java GUI apps — Colab has no display server, so avatar rendering must happen on the **local machine (RX 570 / CPU)** or via JASigning's web variant in a browser. Colab is for the NLP half only.
  - Local machine note: 24 GB RAM + RX 570 is fine for JASigning (CPU/OpenGL) and for small LSTM training, but ROCm support for an RX 570 (Polaris/gfx803) is poor — plan on **CPU locally, GPU on Colab**.
- **Missing resources:** the 3,823 SiGML files; the HamNoSys notations; the 94,781-word inflected corpus; lemmatizer code, hyperparameters and train/test split; the evaluation interface's source; licence terms; any sentence-level gold data.
- **Estimated reproduction time:** **Not stated in the paper.** Our own rough estimate (inference, flagged as such): re-authoring 3,823 HamNoSys notations manually is on the order of **person-months** and is not realistic for us; re-implementing the lemmatizer, given data, is **hours** on a T4; wiring SiGML→JASigning playback for a demo is **days**.
- **Feasibility:** **Partial (Demo-level)** — we can realistically *consume and extend* this work and build a working demo; we cannot reproduce the corpus itself.

**Why this matters for our project:** Plan the architecture as **Colab = Bangla NLP (lemma/gloss), local machine = avatar rendering (JASigning/SiGML)**, and send the data-request email to the authors in week 1, because the whole schedule depends on their answer.

---

## 9. Direct Takeaways for Our Project

**Can adapt:**
1. **The free avatar stack end-to-end:** HamNoSys editor → SiS-Builder → SiGML → JASigning/SiGML Player. Zero budget, no GPU, web-deployable, 5 standard avatars. This solves our "3D avatar" requirement without touching Blender/Unity.
2. **HamNoSys + SiGML as our sign representation.** Machine-readable, standard, human-auditable, and it cleanly separates manual (`<hamnosys_manual>`) from non-manual (`<hamnosys_nonmanual>`) features — which gives us a hook for facial expression later.
3. **Lemma → dictionary-lookup → animation as our v0.1 baseline.** Simple, explainable, demo-able in weeks; it is also the baseline our better model must beat.
4. **Their human-evaluation protocol:** 1–4 categorical scale (Bad/Average/Good/Excellent), separate Alphabets/Numbers/Words/Sentences sections, ≥2 professional interpreters **plus a deaf native signer**, optional comment box, and the mean-score formula. Copy this for our own evaluation chapter.
5. **Category-based vocabulary organisation (36 semantic categories)** as the schema for whatever domain subset we build.
6. **BSTI/BCC standardised sign set as our ground truth source** — plus their reference [22] "Specification of Bangla Sign Language (first version)" as a document to try to obtain.

**Not applicable:**
1. **Manual authoring of thousands of HamNoSys notations** — infeasible for our team size/time; we must reuse their corpus or restrict ourselves to a small (~100–300 sign) domain lexicon.
2. **Their 79.22% BiLSTM lemmatizer as-is** — no code/weights/hyperparameters released; we would rebuild from scratch, and a modern Bangla morphology tool or small transformer would likely outperform it.
3. **Video-based datasets** (Sams et al. SignBD-Word) as an avatar source — different modality; not usable for SiGML animation.
4. **Any recognition/CNN direction** — this paper contains none, and recognition is not our goal.

**Open questions:**
1. Will the authors release the 3,823 SiGML files, and under what licence? (Blocking question.)
2. Is JASigning's current free build (VHG 2023) able to run headless-in-browser on a low-end machine, and can it be embedded in our own web demo?
3. What is the correct BdSL **sentence grammar / gloss order** for Bangla input? The paper never addresses reordering — do we need SVO→BdSL-order transformation, and who can validate it?
4. How should OOV words be handled — fingerspelling fallback using their 49 alphabets, a "no sign" placeholder, or a nearest-neighbour semantic guess? (Note: their alphabets scored worst, 2.48/4, so fingerspelling fallback may be visually poor.)
5. How do we evaluate *sentence-level* animation quality objectively, given they only used human ratings and their sentence scores were lower than word scores?

**Useful project phase:**
- [x] **Literature review** — foundational BdSL reference; gives us the related-work backbone and the comparison table format.
- [x] **Bangla text processing** — lemmatizer architecture and the morphological-complexity argument.
- [x] **Sign-language translation** — the lookup-based mapping baseline and its OOV limitation.
- [ ] Dataset collection — only partially: useful for *notation methodology*, not for audio/video collection.
- [x] **Model development** — small seq2seq design that fits a T4.
- [x] **Sign sequence generation** — sequence concatenation approach and its weaknesses.
- [x] **3D avatar development** — the entire JASigning/SiGML/HamNoSys toolchain.
- [x] **Evaluation** — human-rating protocol, score formula, evaluator composition.
- [x] **System integration** — the 4-step pipeline diagram is a template for our own architecture figure.

**Why this matters for our project:** Roughly 8 of our 9 project phases get something concrete from this one paper — which is why it should be the anchor of our literature review and the reference architecture for our demo.

---

## 10. Action Items

1. **Email the authors this week** (corresponding: rahmanms@sust.edu; first author: ashibul03abir@gmail.com) requesting the IsharaKotha SiGML corpus, the HamNoSys notations, the 94,781-word inflected corpus, and the lemmatizer code — and ask about licence/credit terms.
2. **Test the live evaluation interface** (http://bdsl-isharakotha.ap-1.evennode.com) to see actual animation quality, which avatar is used, and whether the site is still up (hosted on a free Node service — may be offline).
3. **Install and smoke-test the free toolchain locally:** JASigning / SiGML Player (VHG 2023) + SiS-Builder (web) + HamNoSys editor. Hand-author 5–10 test signs from the BdSL dictionary to learn the notation.
4. **Try to obtain the BSTI-standardised BdSL dictionary and the BCC "Specification of Bangla Sign Language (first version)"** — these are the authoritative sign sources; check the Bangladesh Computer Council and CDD websites, and the National Foundation for Development of the Hearing Impaired.
5. **Decide our corpus strategy** based on step 1: (a) full reuse of 3,823 signs, (b) reuse + extend a domain subset, or (c) author our own ~150–300 sign lexicon. Write this decision into the project proposal.
6. **Build a lemma→SiGML lookup demo** (even with 20 hand-made signs) to prove the pipeline on Colab (NLP) + local (rendering) before scaling.
7. **Improve the Bangla normalisation front-end:** benchmark a rule-based/morphological lemmatizer and a small transformer against the paper's 79.22% baseline on a self-built inflected-word list.
8. **Add what the paper lacks:** OOV fallback strategy, gloss-order/grammar handling, and at least one automatic evaluation metric — these are our claimed contributions.
9. **Recruit evaluators early:** contact ≥1 professional BdSL interpreter and ≥1 deaf native signer (the paper used a hearing-impaired athlete); this takes calendar time, so start now.
10. **Check their comparison-table references** for our related work: Islam et al. 2022 (3D animated BdSL from text+voice), Sams et al. 2023 (SignBD-Word), Hasib et al. 2022 (BDSL49), Sugandhi et al. 2020 (ISL grammar-based generation), Aliwy et al. 2021 (ArSL 3D dictionary), Goyal & Goyal 2016 (ISL synthetic animation dictionary). Also look for the newer Bangla text-to-gloss benchmark work that cites IsharaKotha.
11. **Log the avatar-rendering constraint** in our project plan: no GUI on Colab → rendering happens locally or in a browser-based player.

---

## 11. Questions for Supervisor / Team

**Supervisor:**
1. **Corpus access/licence:** If the authors do not release IsharaKotha, do we (a) hand-author a small domain lexicon ourselves, (b) pivot to a different representation (e.g. BVH/gloss+3D motion), or (c) change project scope? What is our fallback deadline?
2. **Scope of "translation":** Should we target word-level lookup + Bangla morphology (achievable), or attempt real Bangla→BdSL **gloss-order translation** with grammar rules (research-grade, needs a BdSL linguist)? Which is acceptable for this project's deliverable?
3. **Ethics/accessibility review:** Do we need institutional ethics approval and formal consent to involve deaf signers and interpreters in evaluation, and is there a budget/travel constraint for that?
4. **Avatar choice:** Are the standard JASigning avatars acceptable as our final output, or does the project require a custom/culturally Bangladeshi avatar (which would mean Blender/Unity work beyond our zero-budget, Colab-only constraint)?

**Team:**
1. **Division of labour:** Who owns (a) author contact + corpus acquisition, (b) Bangla NLP/lemmatizer on Colab, (c) JASigning/SiGML local setup, (d) evaluation recruiting and scoring? These are four independent tracks and can run in parallel.
2. **Local environment:** Can we get JASigning (Java) + SiGML Player running on the 24 GB / RX 570 machine this week, and confirm the RX 570 is *not* needed for it (CPU/OpenGL only)? Also confirm nobody plans ROCm on gfx803.
3. **Who learns HamNoSys first?** One person should become the notation expert (handshape/orientation/location/movement + symmetry operators) and document it internally, since 3,823 signs cannot be authored by committee.
4. **Minimum viable demo:** Do we agree the first milestone is "type a Bangla sentence → lemmatize → look up 20–50 hand-made SiGML signs → avatar plays them in order," with OOV words shown as a placeholder?
5. **Evaluation scale:** How many ratings can we realistically collect (they got 3,828, but 3,223 came from one dedicated deaf user)? Should we target ~100–200 ratings from 3–5 people instead?

---

## 12. Keywords & Concepts

**Relevant keywords:**
1. Bangla Sign Language (BdSL) / BSTI-standardised sign dictionary (~4,000 signs)
2. HamNoSys (Hamburg Notation System) — handshape, orientation, location, movement, symmetry/two-hand operators
3. SiGML (XML sign-language markup; `hamnosys_manual` / `hamnosys_nonmanual`, `gloss` attribute) + SiS-Builder
4. JASigning / SiGML Player — real-time 3D avatar sign synthesis (5 standard avatars)
5. Seq2Seq BiLSTM encoder–decoder with attention for Bangla **lemmatization** (79.22% accuracy, 94,781 inflected words)
6. Sign language corpus construction + categorical human evaluation (1–4 scale; interpreters + deaf user; 3.14/4)
7. Avatar-based vs video-based sign generation (memory, cost, speed trade-offs)

**Terms we need to learn:**
1. **HamNoSys** — the notation itself: symbol inventory, two-handed/symmetry operators, repetition, non-manual markers. (This is the core skill for our project.)
2. **SiGML + JASigning architecture** — how XML maps to avatar skeleton animation, and how to drive it programmatically / embed it in a web page.
3. **Lemmatization vs stemming for Bangla morphology** — inflectional paradigms, why a seq2seq model was used, and what modern alternatives exist.
4. **Gloss vs gloss-order translation in SLT** — the difference between word-lookup (this paper) and true text-to-gloss translation with SL syntax (what we must add).
5. **Non-manual features (NMFs)** — facial expression, head/lip/eye movement as grammatical markers; representable in HamNoSys but unused at sentence level here.

---

## 13. AI Reader Confidence Note

Everything below is **not explicitly stated by the paper**. Nothing here was guessed or filled in silently.

- **Section 1:** Target journal/conference not stated — only "arXiv preprint" is verifiable (arXiv:2511.16896v1, cs.HC, 21 Nov 2025). No DOI. The Elsevier-style layout is an observation, not a publication fact.
- **Section 1 / 5 / 8:** No code, model-weight, or corpus download link is given anywhere in the PDF. Absence of a link ≠ proof the data is private; the authors may release it on request. Marked **Unsure**.
- **Section 4A:** Tokenization granularity (character / subword / word) for the lemmatizer is **not stated**; input and output sequence-length limits are **not stated**.
- **Section 4C:** Pre-trained embeddings or models: **not stated**. All hyperparameters (hidden size, layers, dropout, optimizer, learning rate, batch size, epochs): **not stated**. Training/validation/test split: **not stated**. How "accuracy" for a sequence-output task was computed (exact string match vs token-level): **not stated**. Hardware and DL framework: **not stated**. The source and construction method of the 94,781-word inflected corpus: **not stated**.
- **Section 4D:** Which of the five JASigning avatars was used: **not stated**. Avatar rigging/skeleton details, renderer, frame rate, resolution: **not stated**. Motion smoothing or inter-sign interpolation/transition handling: **not stated** (this is why sentence scores may lag word scores, but the paper does not say so — that causal link is my inference, not theirs).
- **Section 5:** Whether a sentence-level dataset exists: **not stated** — sentences appear only inside the evaluation, and their count/source/authorship is not described. Licence terms: **not stated**. Inter-annotator agreement (kappa/ICC): **not computed or stated**.
- **Section 6:** No automatic/objective metric of any kind is reported; there is no baseline *system* comparison, only a qualitative dataset-scope table. Statistical significance of the rating differences between evaluators: **not analysed**.
- **Section 6 (internal inconsistencies noticed — flagged, not resolved):**
  - Abstract/intro say "3,828 evaluations"; Table 5's narrative says the sign-language user gave "3223 feedbacks in total", while Table 6's grand total is 3,828 (116+294+2,346+1,072). These reconcile only if the 3,223 is the user's subtotal (96+206+2,096+825 = 3,223) and 3,828 is the pooled total — but the paper does not explain this explicitly.
  - The user's overall score is written as **3.13** in Table 5 and the narrative, while the pooled "final evaluation score" is **3.14** in Table 6 and the abstract. Which is the headline number for the whole corpus is therefore slightly ambiguous (3.14 = pooled across all three evaluators).
  - Table 5's Words row (84+202+2,056+808 = 3,150) does not match the stated section narrative exactly, and the Alphabets row (11+3+26+3 = 43) implies 43 alphabet items although only 49 alphabets exist in the corpus; the paper does not explain item counts per section for the deaf user.
  - Section 6.2 and 6.3 contain broken cross-references ("Figure ??") in the PDF, so figure numbering for the SiGML example and its animation resolves to Figure 10 — a typesetting artifact, noted for completeness.
- **Section 7:** The claim that avatar-based systems are better than video-based ones (memory, cost, time) is **asserted without measurement** — no storage/latency/cost numbers are given.
- **Section 8:** GPU requirements, training time and reproduction effort are **not stated**. Every time/compute estimate in Section 8 is **my inference**, clearly labelled as such, and should be validated before being put in a project plan.
- **Section 8:** The statement that Colab cannot run JASigning/SiGML Player (no display server) and that the RX 570 has poor ROCm support is **my technical inference from our stated constraints**, not a claim made in the paper.
- **General:** The paper does not state how many of the ~4,000 BSTI signs were successfully completed vs abandoned (Figure 17 shows "some unfinished signs" without a count), so the true coverage percentage of the standardised dictionary **cannot be determined from the paper**.
- **General:** No mention anywhere of regional/dialectal variation in BdSL — **not covered in the paper**, despite the authors being based in Sylhet.
- **General:** No mention of audio/speech input, named-entity extraction, or a medical-domain focus beyond the 84-sign "Disease & Treatment" category — **not covered in the paper**.
