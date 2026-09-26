# Paper Analysis — Next-Gen Communication: AI-driven Speech-to-Sign Language Translation

**Project context:** Bangla Text-to-Bangla Sign Language (BdSL) Translation using a 3D Avatar (research/exploration phase, zero budget, Google Colab T4 + local RX 570).

---

## 1. Basic Information

- **Title:** Next-Gen Communication: AI-driven Speech-to-Sign Language Translation
- **Authors:** Vinaya Kulkarni, Pranoti Kale, Sanika Chaudhari, Shruti Bhumkar, Manasi Deshmukh, Samruddhi Deshmukh (Bharati Vidyapeeth's College of Engineering for Women, Pune, India)
- **Year:** 2025 (received Dec 2024, accepted Feb 2025, published online Jul 2, 2025; PDF copyright line says 2024)
- **Venue / Journal / Conference:** Journal of Information Systems Engineering and Management (JISEM), Vol. 10, No. 56s, pp. 115–122, e-ISSN 2468-4376
- **Paper link:** https://www.jisem-journal.com/index.php/journal/article/view/11784 (found externally; no DOI printed in the PDF)
- **Code / Model / Dataset link:** None provided in the paper

> **Why this matters for our project:** A recent (2025) student-built, low-budget English→ISL avatar system — closest structural analog to what we want to build for Bangla→BdSL, useful as a pipeline reference and as a lesson in what makes a weak evaluation.

---

## 2. Relevance to Our Project

- **Primary area(s):** Text-to-Sign Language (sign language production); 3D Avatar / Sign Animation; NLP / Grammar Processing. Secondary: Speech-to-sign (ASR front-end).

| Aspect | Score /5 | Reason |
|---|---|---|
| Bangla relevance | 1 | No Bangla anywhere; English input, Indian Sign Language (ISL) output. Only indirect value: South-Asian low-resource setting. |
| Sign-language relevance | 3 | Full text/speech→sign production system for ISL; ISL ≠ BdSL, but pipeline concepts (glossing, sign sequencing) transfer. |
| Text-to-sign translation | 3 | Text-to-sign mapping + grammar restructuring is central, but described only at a high level; primary input is video/speech, mapping mechanism unexplained. |
| NLP / grammar | 3 | Concrete preprocessing stack (spaCy/NLTK) + BERT-based restructuring to sign syntax — a transferable idea; mechanism and Bangla applicability unaddressed. |
| Sign/motion generation | 3 | LSTM for gesture sequencing, DTW for timing — useful technique names; zero architecture/training detail. |
| 3D avatar / animation | 3 | Three.js web rendering + Bezier interpolation + IK for smooth, free browser-based avatar — directly reusable ideas; avatar model/rig not specified. |
| Dataset usefulness | 1 | Only dataset mentioned is ISL-CLTR (Indian SL, not Bangla, no link/size/modality given); test videos unspecified. |
| Feasibility for our project | 3 | All components are lightweight/free-ish and Colab-T4-compatible in principle, but no code, no hyperparameters, paid cloud ASR — exact reproduction impossible; concept-level rebuild is feasible. |

- **Overall relevance: Medium**
- **Why:** The end-to-end architecture (text → sign-syntax restructuring → LSTM gesture sequencing → Three.js avatar with DTW/IK/Bezier smoothing) is a directly adaptable blueprint for a zero-budget Bangla→BdSL demo, but the paper contributes no Bangla/BdSL resources, no code, and its evaluation measures transcription accuracy rather than sign quality — cite with caution.

---

## 3. Problem & Proposed Solution

**A. Problem:**
- Deaf/hard-of-hearing (DHH) users can't access audio/video digital content (WHO: 430M+ people with hearing loss).
- Captions are insufficient; human interpreters don't scale.
- Word-for-word translation fails because sign languages have their own grammar/syntax.

**B. Approach:**
- Video/URL/speech/text input → FFmpeg audio extraction → audio cleaning → IBM Watson Speech-to-Text → NLP preprocessing (spaCy tokenization/NER, NLTK stop-word removal, lemmatization) → BERT-based grammar restructuring into ISL word order → LSTM-RNN generates temporally smooth gesture sequences (fine-tuned on ISL-CLTR) → Three.js 3D avatar renders signs, with DTW (timing vs. speech), Bezier interpolation (smooth transitions), IK (natural joints).

**C. Connection to our project:**
- **Directly useful:**
  - The 6-stage pipeline blueprint (input → preprocess → sign-syntax restructure → sign sequence → avatar render).
  - The free avatar-smoothing stack: DTW + Bezier interpolation + IK + Three.js — all CPU/T4-friendly, zero cost.
  - The insight that spoken-language word order must be rearranged into sign-language gloss order *before* mapping to gestures.
- **Technique we can adapt:**
  - Contextual-model-based (BERT-style) restructuring → for us: BanglaBERT/Bangla embeddings + BdSL word-order rules to convert Bangla sentences to BdSL gloss sequences.
  - LSTM over gesture sequences for natural transitions between stored sign clips.
  - DTW to pace signing against audio duration (relevant if our medical audio recordings become an input modality).
- **Different from our project:**
  - Language pair: English→ISL vs. our Bangla→BdSL (different grammar, different sign vocabulary; BdSL is not ISL).
  - Input: video/speech via a paid cloud ASR (IBM Watson) vs. our text-first, zero-budget scope.
  - Domain: general YouTube content vs. our narrow medical domain with a small self-collected corpus.
  - Their evaluation measures ASR accuracy only; we must evaluate sign/gloss quality.

> **Why this matters for our project:** It validates a cheap, modular architecture we can mirror for Bangla→BdSL, while showing exactly which parts (ASR, ISL rules) we must replace.

---

## 4. Methodology

### 4A. NLP / Text Processing
- **Input language:** English (from video audio, direct speech, or typed text)
- **Tokenization:** spaCy (word/phrase tokens); stop-word removal via NLTK
- **Grammar / linguistic processing:** lemmatization; NER with spaCy pre-trained models (keep proper nouns/dates); BERT used for "contextual grammar correction" and rearranging word order into ISL syntax (example: "What is your name?" → "Your name what?"). Exact BERT mechanism not explained.
- **Translation method:** Not a trained NMT system per the methodology — preprocessing + BERT restructuring + word/phrase→gesture lookup with LSTM sequencing. Unsure: results section suddenly credits an "attention-based Seq2Seq model" never described in the methodology.
- **Output representation:** "ISL-compatible phrases" (gloss-like reordered text) → mapped to gesture entries in an ISL dataset

### 4B. Sign Language
- **Sign language:** Indian Sign Language (ISL)
- **Sign representation:** Each gesture "stored as a sequence of frames" in their dataset; exact format (pose keypoints? animation clips? video frames?) not stated
- **Sign vocabulary:** Not stated in the paper (no vocabulary size given)
- **Text-to-sign mapping:** Word/phrase-level linking of preprocessed text to gestures "stored in the ISL dataset"; mapping mechanism (dictionary lookup vs. learned) not stated
- **Sign sequence generation:** LSTM-based RNN trained on continuous sign sequences for temporal consistency; DTW adjusts each gesture's duration to speech pace

### 4C. ML / Deep Learning
- **Model:** BERT (grammar correction/restructuring) + LSTM-RNN (gesture sequencing); abstract also mentions a CNN, but no CNN appears in the described system
- **Pre-trained model:** spaCy pre-trained NER models; BERT (variant not stated); IBM Watson STT (cloud API)
- **Training data:** "a dataset containing continuous sign sequences"; LSTM fine-tuned on ISL-CLTR dataset (no size/details given)
- **Fine-tuning:** LSTM fine-tuned on ISL-CLTR for "context-specific ISL variations"; whether BERT was fine-tuned or used off-the-shelf: not stated
- **Important hyperparameters:** Not stated in the paper (no LR, batch size, layers, epochs numbers)
- **Training method:** Not stated; only qualitative claims that loss decreases / accuracy improves across epochs

### 4D. 3D Avatar / Animation
- **Avatar type:** 3D avatar rendered in the browser via Three.js; specific model/character not identified
- **Rigging / skeleton:** Joint-based (IK refines hand/arm joint movements); skeleton/rig details not stated
- **Motion representation:** Gesture frame sequences; exact motion data format not stated
- **Animation method:** LSTM-ordered gesture clips rendered by Three.js; DTW time-warps gestures to match speech pace
- **Motion smoothing / interpolation:** Bezier-curve interpolation between gestures + inverse kinematics to prevent unnatural joint distortion
- **Rendering method:** Three.js (WebGL, browser-based)

### 4E. System Pipeline
Input (YouTube URL / video file / speech / text)
→ [FFmpeg audio extraction → pydub MP3 → noise reduction, normalisation, segmentation]
→ [IBM Watson Speech-to-Text → transcript JSON]
→ [spaCy tokenization + NER; NLTK stop-word removal; lemmatization]
→ [BERT contextual correction + word-order restructuring to ISL syntax]
→ [LSTM-RNN gesture sequencing (fine-tuned on ISL-CLTR) + DTW timing alignment]
→ [Three.js avatar rendering with Bezier interpolation + IK]
→ Output: web-based 3D avatar signing ISL

> **Why this matters for our project:** Sections 4B/4D are the two blocks we'd rebuild for BdSL (sign inventory + avatar motion); 4A shows the Bangla tools we need to substitute; 4C shows how little detail this paper gives — our own write-up must document architectures and hyperparameters properly.

---

## 5. Dataset

- **Dataset name:** ISL-CLTR (used for LSTM fine-tuning); evaluation videos = YouTube links / user uploads (unnamed, 6 videos, 0.5–8 min)
- **Language:** English (text); **Sign language:** ISL
- **Size:** Not stated in the paper
- **Number of classes/signs:** Not stated in the paper
- **Text/sign pairs:** Not stated in the paper
- **Video / image / motion data:** Gestures stored as "sequences of frames"; modality details not stated
- **2D or 3D:** Not stated in the paper (external knowledge: ISL-CLTR is a 2D video dataset on Kaggle — not stated by the authors)
- **Publicly available:** Not stated in the paper; no link given
- **Link:** None
- **Collection method:** Test videos: YouTube URL download or local upload; training data collection: not described
- **Annotation method:** Not stated in the paper
- **Can we use it? Partial** (leaning No for core use)
- **Why:** ISL-CLTR is Indian Sign Language, not BdSL — it cannot train our Bangla sign output. It could serve only as a structural reference (how a continuous-sign dataset is organized) or for pipeline dry-runs. The paper itself provides no download info.

> **Why this matters for our project:** Confirms there is no ready-made dataset here for BdSL — our self-collected corpus (and its annotation scheme) remains the critical path, and ISL-CLTR is at best a format template.

---

## 6. Evaluation

| Task | Metric | Result |
|---|---|---|
| Translation | "Word-level accuracy" (Unsure: appears to measure ASR transcription accuracy, not sign-translation quality; no BLEU/gloss metric) | 97.44–98.59% across 6 videos (peak 98.59% at 5 min) |
| Sign recognition | Not covered in paper | N/A |
| Sign generation | No metric; qualitative epoch-convergence claims + sine/cosine "epoch visualization" (authors admit curves are "not substantively significant") | N/A |
| Motion quality | No metric; qualitative claims of smoothness from DTW/Bezier/IK | N/A |
| Avatar evaluation | No user study, no expert rating | N/A |
| Other | Processing time; real-time factor (RTF) | 2.56–37.61 s for 0.5–8 min videos; RTF 0.0785 (~12× real-time on CPU) |

- **Train / Validation / Test split:** Not stated in the paper
- **Baselines:** None — no comparison with any prior system
- **Hardware:** "hardware-based CPU" mentioned for inference timing only; training hardware not stated
- **Framework:** FFmpeg, pydub, spaCy, NLTK, IBM Watson STT API, BERT, LSTM (underlying DL framework — TensorFlow/PyTorch — not stated), Three.js

> **Why this matters for our project:** This is the paper's weakest part and a cautionary template for us: we must plan real sign-quality evaluation (gloss-level metrics + BdSL-fluent reviewer/user study) from day one, not just pipeline speed.

---

## 7. Results & Findings

- **Best result:** 98.59% word-level accuracy (5-min video); 8-min video processed in 37.61 s (RTF 0.0785, >12× real-time on CPU)
- **Compared with:** Nothing — no baselines or prior systems compared
- **Main finding:** Accuracy stays >97% regardless of video length; processing time scales quasi-linearly with duration (pipeline is sequential per module)
- **What worked (per authors' claims):** LSTM for temporally smooth gesture transitions; DTW to sync signing speed with speech; BERT for grammar/context correction; Three.js + IK + Bezier for realistic rendering
- **Failure cases:** Slight accuracy dip at 8 min, attributed speculatively to "context saturation", "model fatigue", or "ASR drift" (no evidence given); no linguistic/gesture failure examples shown
- **Limitations stated by authors:** No explicit limitations section; future-scope items imply current gaps: no real-time streaming, single sign language only, no facial expression/body-language cues, no user-feedback learning

> **Why this matters for our project:** The only hard numbers are ASR-side; everything about sign output quality is asserted, not measured — we should treat this paper as an architecture reference, not as evidence that the approach works.

---

## 8. Reproducibility & Feasibility

- **Code available:** No
- **Dataset available:** No links; ISL-CLTR not provided by the paper (exists publicly elsewhere — external knowledge)
- **Pre-trained model:** Not released
- **GPU requirement:** Not stated; inference timing reported on CPU; BERT/LSTM training requirements unknown
- **Free Colab feasible:** Partial — every named component (spaCy, NLTK, BERT-base, small LSTM, Three.js front-end) individually fits a T4/15GB Colab session, but without code, architectures, or hyperparameters an exact rebuild is impossible
- **Missing resources:** Source code; BERT variant & usage details; LSTM architecture/hyperparameters; sign vocabulary & motion representation; ISL grammar-restructuring rules; avatar 3D asset; train/val/test split; any sign-quality evaluation protocol
- **Estimated reproduction time:** Not stated in the paper. Our own estimate (not from paper): a concept-level prototype (Bangla text → gloss reorder → clip-based Three.js avatar for ~10–20 medical signs) ≈ 2–4 weeks for a beginner team on Colab
- **Feasibility: Partial** (demo-level re-implementation of the concept; exact reproduction not feasible)

> **Why this matters for our project:** Everything we'd take from this paper must be re-implemented from scratch — budget time for that, and document our own system far more rigorously than this paper did.

---

## 9. Direct Takeaways for Our Project

**Can adapt:**
1. **Pipeline blueprint:** text → preprocessing → sign-syntax restructuring → sign sequence generation → 3D avatar rendering; swap English→Bangla, ISL→BdSL, Watson ASR→direct text input (Whisper later if audio needed).
2. **Zero-cost avatar motion stack:** stored gesture clips + Bezier interpolation between clips + IK for joints + DTW to pace signs — all CPU/T4-friendly, browser-rendered via Three.js (no game engine, no license costs).
3. **Grammar-first translation principle:** rearrange spoken-language word order into sign gloss order (using a Bangla contextual model + BdSL rules) *before* mapping words to signs.

**Not applicable:**
1. **ASR/video ingestion via IBM Watson** — paid cloud service, conflicts with zero budget and text-first scope (free Whisper on Colab is the substitute if speech input is ever added).
2. **ISL-specific assets** — ISL-CLTR dataset and ISL syntax rules can't be reused for BdSL (different sign language); English NLP tools (spaCy/NLTK English models) don't cover Bangla.

**Open questions:**
1. How exactly does their BERT "restructure" text into ISL syntax — fine-tuned seq2seq, prompting, or hand rules? Never explained; results even mention an undescribed "attention-based Seq2Seq" model.
2. What does the LSTM actually consume/output — gloss IDs, animation-clip indices, or pose keypoints — and how big is the sign vocabulary?
3. Does their reported "accuracy" reflect the signed output at all? It appears to be transcription accuracy only — what metric should *we* commit to for sign quality?

**Useful project phase:**
- [x] Literature review (pipeline precedent; evaluation anti-pattern)
- [x] Bangla text processing (concept of preprocessing + syntax restructuring; tools must be swapped)
- [x] Sign-language translation (gloss-order restructuring principle)
- [ ] Dataset collection (only as a format reference via ISL-CLTR)
- [x] Model development (LSTM sequencing idea)
- [x] Sign sequence generation (temporal smoothing, DTW pacing)
- [x] 3D avatar development (Three.js + Bezier + IK)
- [x] Evaluation (as a negative example)
- [x] System integration (end-to-end modular architecture)

> **Why this matters for our project:** Gives us a concrete, cheap architecture to propose in our literature review, plus a clear list of what we must design ourselves (BdSL rules, sign inventory, evaluation).

---

## 10. Action Items

1. Sketch our own Bangla→BdSL pipeline diagram modeled on this paper's 6 stages, with text-only input for Phase 1 (no ASR).
2. Survey Bangla NLP tooling (BanglaBERT / sagorsarker's models, bnlp-toolkit, normalizer/tokenizer for Bangla) to replace spaCy/NLTK English components; collect whatever BdSL grammar/word-order references exist.
3. Build a minimal Three.js proof-of-concept: free rigged avatar (GLB, e.g., from Ready Player Me/Quaternius) playing 5–10 recorded/animated BdSL gesture clips with Bezier blending — runs on Colab/local, zero cost.
4. Download ISL-CLTR (Kaggle, external to this paper) purely to study continuous-sign dataset structure as a template for annotating our own 200–300 medical recordings.
5. Draft our evaluation plan *before* model work: gloss-level accuracy + BdSL-fluent reviewer ratings (+ optional user study) — explicitly avoiding this paper's ASR-only metric.
6. Note this paper in the related-work table with the caveat: no code, no baselines, evaluation measures transcription not translation.

---

## 11. Questions for Supervisor / Team

**Supervisor:**
1. This paper targets ISL; BdSL is a distinct sign language. Is it acceptable to use ISL resources (e.g., ISL-CLTR) for pipeline prototyping/pretraining, or must all data and rules be BdSL-specific from the start?
2. Given this paper's weak evaluation (transcription accuracy only, no baselines, no user study), what evaluation evidence would you require for our project milestones — expert review by BdSL users, gloss-level metrics, or a formal user study?

**Team:**
1. Who will own the avatar track (rigged GLB selection, gesture-clip animation in Blender, Three.js integration)? This paper shows the avatar side is where most manual effort goes.
2. Our project brief mentions both "~200–300 Bangla medical audio recordings + entity extraction" and "text-to-sign translation". Is speech→text (+NER) part of our pipeline (making this paper's ASR/DTW stages relevant), or is our input plain Bangla text? This changes scope significantly.

---

## 12. Keywords & Concepts

**Relevant keywords:**
1. Sign language translation (SLT) / sign language production (SLP)
2. Text-to-sign / speech-to-sign with 3D avatar
3. Gloss restructuring / sign-language syntax conversion
4. LSTM gesture sequencing; dynamic time warping (DTW)
5. Three.js avatar rendering; inverse kinematics (IK); Bezier motion interpolation
6. Indian Sign Language (ISL); ISL-CLTR dataset

**Terms we need to learn:**
1. **Gloss / glossing** — the written sign-language annotation layer between text and motion (and typical sign-language word order, e.g., topic-comment, question-last)
2. **DTW and IK** — how time-alignment and joint solving make clip-based avatar motion look continuous
3. **SLP evaluation metrics** — gloss BLEU, pose-based metrics (e.g., Jaccard Index / normalized joint distance), and Deaf-user study protocols — none used in this paper, all needed by us

---

## 13. AI Reader Confidence Note

Everything below was **not explicitly stated** or is **internally inconsistent** in the paper — nothing here was guessed into the form above:

- **Section 1:** No DOI printed in the PDF; landing-page URL and publication date (Jul 2, 2025) found externally on the journal site. PDF copyright line says 2024 while the issue is dated 2025 — reported as 2025.
- **Section 2 (scores):** All /5 scores are my judgment based on paper content, not from the paper.
- **Section 3/4A/4C:** The BERT-based "grammar restructuring" mechanism is never explained (fine-tuned? prompted? rule-assisted?). The results text credits an **"attention-based Seq2Seq model"** that appears nowhere in the methodology — inconsistency, flagged as Unsure.
- **Section 3.2 of the paper:** Says audio is prepared "before sending to **Google's** Speech Recognition API", then states transcription uses **IBM Watson** — which ASR was actually used is ambiguous (form reports IBM Watson, which the abstract and most of the text name).
- **Abstract vs. body:** Abstract claims the system integrates a **CNN**; no CNN appears anywhere in the described system — cannot determine its role.
- **Section 4B:** Sign representation format, sign vocabulary size, and the text→gesture mapping mechanism (lookup vs. learned) — not stated.
- **Section 4C:** All hyperparameters, LSTM architecture, BERT variant, DL framework (TensorFlow/PyTorch), training hardware, and training procedure — not stated.
- **Section 4D:** Avatar model/rig identity and motion data format — not stated.
- **Section 5:** ISL-CLTR size, modality, and link — not stated; the note that ISL-CLTR is a public 2D video dataset (Kaggle) is **external knowledge**, clearly labeled, not from the paper.
- **Section 6:** The definition of "accuracy" is ambiguous — context (per-video transcribed word counts) suggests **transcription** accuracy, not sign-translation accuracy; no train/val/test split stated; the 6 test videos' provenance/unseen status unclear; "hardware-based CPU" specs not given.
- **Section 7:** Explanations for the 8-minute accuracy dip ("model fatigue", "ASR drift", "context saturation") are speculative — no supporting analysis in the paper.
- **Section 8:** The 2–4 week reproduction estimate is **our own judgment**, explicitly not from the paper.
- **General rigor caveat:** The "epoch visualization" (sine/cosine curves) is admitted by the authors to be substantively meaningless; there are no ablations, no baselines, no qualitative output examples, and no end-to-end evaluation of the signed output. Reference list contains errors (e.g., ref [15] "Sign Avatars" listed under an unrelated conference title; refs [3], [5], [20] unnumbered in text). Treat quantitative claims with low confidence.
