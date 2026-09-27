# Paper Analysis: Side-by-Side Comparison
**Project:** Bangla Text-to-BdSL Translation Using a 3D Avatar (research/exploration stage)

| | Paper A | Paper B |
|---|---|---|
| **Title** | IsharaKotha: A Comprehensive Avatar-based Bangla Sign Language Corpus | Multilingual Speech-to-Sign Language Translator with Avatar |
| **Authors** | MD. Ashikul Islam, Prato Dewan, Md Fuadul Islam, Md. Ataullha, M. Shahidur Rahman | Chandana A C, Sandarsh Gowda M. M. |
| **Year** | 2025 (arXiv preprint, Nov 2025) | 2026 (published Jan 2026) |
| **Venue** | arXiv (cs.HC), not yet peer-reviewed | IJARCCE, Vol. 15, Issue 1, Jan 2026 (peer-reviewed) |
| **Paper link** | arXiv:2511.16896v1 | DOI: 10.17148/IJARCCE.2026.151143 |
| **Code/Model/Dataset link** | Evaluation interface only: http://bdsl-isharakotha.ap-1.evennode.com (raw corpus download not stated) | Not stated in paper |

---

## 2. Relevance to Our Project

**Primary areas —**
- Paper A: Bangla/Low-resource NLP, Text-to-Sign Language, Sign Language Generation, 3D Avatar/Animation, NLP/Grammar Processing
- Paper B: Sign Language Translation (generic/multilingual), 3D Avatar/Animation, Sign Language Recognition (bonus, reverse direction)

| Aspect | Paper A (/5) | Paper B (/5) | Reason |
|---|---|---|---|
| Bangla relevance | 5 | 1 | A is BdSL-specific; B never mentions Bangla or BdSL |
| Sign-language relevance | 5 | 3 | A gives a real notation/pipeline; B only diagrams a generic module |
| Text-to-sign translation | 4 | 2 | A does word-level dictionary translation; B shows a black-box "mapping" step with no method |
| NLP / grammar | 3 | 1 | A has a real lemmatizer; B has an unspecified "Language Translation Module" |
| Sign/motion generation | 5 | 1 | A documents HamNoSys→SiGML→avatar in detail; B gives no generation method |
| 3D avatar / animation | 4 | 1 | A uses a documented third-party avatar system (JASigning); B's avatar looks like a flat 2D placeholder graphic (Fig. 2) with no technical detail |
| Dataset usefulness | 4 | 1 | A has a named, sized, categorized corpus (3823 signs); B names no dataset at all |
| Feasibility for our project | 3 | 1 | A's lemmatizer is lightweight/Colab-friendly, but JASigning/SiGML player is desktop software of unclear Colab fit; B is not reproducible as written |

**Overall relevance:** Paper A = **High**. Paper B = **Low**.
**Why:** Paper A is the closest thing either document has to a worked example of our exact goal (Bangla text → sign notation → 3D avatar animation), with a real corpus and pipeline. Paper B covers the right *topic* (speech/text-to-sign avatar) but reads as a shallow systems-project write-up with no BdSL support, no dataset, and no disclosed generation methodology — useful mainly as an architecture sketch and as a caution about paper quality.

---

## 3. Problem & Proposed Solution

### Paper A
- **Problem:** No comprehensive avatar-based BdSL corpus exists that supports translating Bangla text/words into sign animations at scale (prior BdSL work covers only alphabets, numerals, or small video sets).
- **Approach:** Built a 3823-word HamNoSys-notated corpus, converted each entry to SiGML, animated it via the JASigning avatar system, and added an LSTM-based lemmatizer so full sentences can be reduced to root words for dictionary lookup. Validated with human interpreter/signer ratings.
- **Connection to our project:**
  - *Directly useful:* the full generation pipeline (word → HamNoSys → SiGML → avatar) and the 3823-sign categorized corpus.
  - *Technique to adapt:* the BiLSTM-encoder / LSTM-decoder + attention lemmatizer for normalizing inflected Bangla words before dictionary lookup.
  - *Different from our project:* it's word-by-word dictionary lookup, not true sentence-to-BdSL-grammar translation — BdSL sentence structure/gloss reordering is not handled, and full dynamic sentence generation is explicitly stated as unfinished.

### Paper B
- **Problem:** Lack of accessible, real-time tools for converting speech/text into sign language for hearing-impaired communication.
- **Approach:** A web app (Flask backend, HTML/CSS/JS frontend) that takes speech, text, or webcam gesture input, runs speech recognition / MediaPipe gesture detection, translates the text, and shows an "avatar animation or sign video" as output.
- **Connection to our project:**
  - *Directly useful:* the client–server architecture idea (web front end + backend translation service) as a possible later deployment shape.
  - *Technique to adapt:* MediaPipe as a lightweight, CPU-friendly library — relevant to our own resource constraints even though this paper uses it for gesture *recognition*, not generation.
  - *Different from our project:* not Bangla/BdSL at all (supports ISL, LSE, DGS, JSL, KSL, CSL, LSF, ArSL per Fig. 3); the "sign language mapping" step is an unexplained black box; the avatar shown (Fig. 2) is a simple flat illustration, not a documented rigged 3D model.

---

## 4. Methodology

### 4A. NLP / Text Processing
| | Paper A | Paper B |
|---|---|---|
| Input language | Bangla sentences | Multilingual speech/text (English shown in examples) |
| Tokenization | Implied word-level, then lemmatized | Not stated in paper |
| Grammar / linguistic processing | Not stated in paper (no BdSL syntax reordering — plain lemmatization only) | Not stated in paper |
| Translation method | Dictionary lookup of lemmatized root word → pre-built sign entry | Not stated in paper (generic "Language Translation Module," no method given) |
| Output representation | Sequence of SiGML/HamNoSys entries for root words | "Mapped sign meaning" / gloss text + spoken-language pronunciation guide |

### 4B. Sign Language
| | Paper A | Paper B |
|---|---|---|
| Sign language | BdSL | ISL, LSE, DGS, JSL, KSL, CSL, LSF, ArSL (no BdSL) |
| Sign representation | HamNoSys notation → SiGML | Not stated in paper |
| Sign vocabulary | 3823 words | Not stated in paper |
| Text-to-sign mapping | Lemmatized word → dictionary sign entry | Not stated in paper (black-box "Sign Language Mapping" module) |
| Sign sequence generation | Sequential, word-by-word avatar playback | Not stated in paper |

### 4C. ML / Deep Learning
| | Paper A | Paper B |
|---|---|---|
| Model | Seq2Seq: BiLSTM encoder + LSTM decoder + attention (lemmatizer only) | MediaPipe hand-landmark detection + unspecified gesture classifier |
| Pre-trained model | None (lemmatizer trained from scratch) | MediaPipe's pretrained landmark model |
| Training data | Self-built corpus of 94,781 unique inflected Bangla words | Not stated in paper |
| Fine-tuning | Not applicable | Not stated in paper |
| Important hyperparameters | Not stated in paper | Not stated in paper |
| Training method | Supervised seq2seq (details not given) | Not stated in paper |

### 4D. 3D Avatar / Animation
| | Paper A | Paper B |
|---|---|---|
| Avatar type | JASigning virtual human (5 standard avatar choices) | "Animated avatar" — appears to be a simple flat/cartoon graphic in Fig. 2, not a documented 3D model |
| Rigging / skeleton | Not stated in paper (internal to JASigning) | Not stated in paper |
| Motion representation | HamNoSys/SiGML parameters (handshape, orientation, location, movement) | Not stated in paper |
| Animation method | SiGML player renders from SiGML XML | Not stated in paper |
| Motion smoothing/interpolation | Not stated in paper | Not stated in paper |
| Rendering method | JASigning / SiGML player (desktop, Windows/Mac/Linux) | Web-based (HTML/CSS/JS), rendering approach unspecified |

### 4E. System Pipeline
- **Paper A:** Bangla Word → HamNoSys Notation → SiGML File Generation → Avatar Animation → Sign Validation → added to corpus. Sentence-level: Bangla sentence → Lemmatization (BiLSTM+LSTM+attention) → Root words → SiGML files → Avatar Animation.
- **Paper B:** User Input (speech/text/gesture) → [Speech Recognition | Text Processing | Hand Gesture Detection] → Recognized Text / Gesture Classification → Language Translation / Mapped Sign Meaning → Sign Language Mapping → Avatar Animation or Sign Video → Output.

**Why this matters for our project:** Paper A's pipeline (4A–4E) is essentially a template we can study step-by-step, including a real lemmatizer we could reimplement or adapt. Paper B's pipeline is only a high-level box diagram — every box that actually matters for sign *generation* ("Sign Language Mapping," "Avatar Animation") is undocumented, so it offers little beyond the idea of the pipeline shape.

---

## 5. Dataset

| | Paper A: IsharaKotha | Paper B |
|---|---|---|
| Dataset name | IsharaKotha | Not covered in paper |
| Language | Bangla | N/A |
| Sign language | BdSL | N/A |
| Size | 3823 signs | Not stated in paper |
| Number of classes/signs | 3823 (across 36 categories, see Table 1 of paper) | Not stated in paper |
| Text/sign pairs | Yes — Bangla word ↔ HamNoSys/SiGML/animation | Not stated in paper |
| Video/image/motion data | Avatar animation driven by SiGML (not raw video) | Not stated in paper |
| 2D or 3D | 3D avatar | Not stated in paper |
| Publicly available | Unsure: evaluation web interface is public; raw corpus/SiGML files' downloadability and license are not stated | Not stated in paper |
| Link | http://bdsl-isharakotha.ap-1.evennode.com | N/A |
| Collection method | Based on ~4000 signs standardized by BSTI/BCC; HamNoSys notation authored per word, converted to SiGML via "SiS-Builder," verified with SiGML player | Not stated in paper |
| Annotation method | Manual HamNoSys authoring + human evaluator validation (interpreters + native signer) | Not stated in paper |
| **Can we use it?** | **Partial** — strong reference/vocabulary and a proven pipeline, but public download access and licensing are unclear | **No** — no dataset is named, sized, or linked |

**Why this matters for our project:** A dataset like IsharaKotha (or its methodology) is close to a starting dictionary for a dictionary-lookup version of our system, provided we can confirm access/licensing. Paper B gives us nothing to reuse on the data side.

---

## 6. Evaluation

### Paper A
| Task | Metric | Result |
|---|---|---|
| Sign generation / avatar quality | Human rating scale, 1 ("Bad")–4 ("Excellent") | Overall corpus average 3.14/4.00 (first interpreter 3.32, second interpreter 3.17, native signer 3.13) |
| Lemmatizer (NLP component) | Accuracy | 79.22% on 94,781-word corpus |

- Train/Val/Test split: Not stated in paper (only final accuracy reported for the lemmatizer)
- Baselines: Compared corpus *scope* (not performance) against 3 existing BdSL datasets — numerals-only, 6,000 videos/200 words, and 29,490 alphabet images
- Hardware: Not stated in paper
- Framework: HamNoSys authoring tool, SiS-Builder, SiGML player, JASigning

### Paper B
| Task | Metric | Result |
|---|---|---|
| Translation | None reported | Qualitative claim only ("effective translation across multiple languages") |
| Sign recognition (gesture→text) | None reported | Qualitative claim only ("accurately detected basic hand signs") |
| Sign generation | None reported | Not stated in paper |
| Motion quality | None reported | Not stated in paper |
| Avatar evaluation | None reported | Not stated in paper |

- Train/Val/Test split: Not covered in paper
- Baselines: Narrative comparison to 3 cited related-work papers only, no quantitative benchmark
- Hardware: Listed as *requirements* (standard desktop, ≥8GB RAM, webcam+mic), not as evaluation hardware
- Framework: HTML/CSS/JS, Python + Flask, MediaPipe

**Why this matters for our project:** Paper A gives us a concrete, if informal, human-rating methodology (Bad/Average/Good/Excellent) we could reuse for evaluating our own avatar output. Paper B has essentially no measurable results to benchmark against or learn from.

---

## 7. Results & Findings

### Paper A
- **Best result:** Numbers section rated highest across all evaluators (2.83–4.00); overall average 3.14/4.00 ("Good" to "Excellent").
- **Compared with:** Three prior BdSL datasets (numerals-only, video-based, alphabet-image-based) — IsharaKotha is presented as the largest word-level, notation-based BdSL corpus to date.
- **Main finding:** A HamNoSys/SiGML avatar pipeline can produce BdSL animations rated acceptable-to-good by interpreters and a native signer.
- **What worked:** Numbers and Words sections scored well; symmetry/replace operators handled two-handed signs effectively.
- **Failure cases:** Alphabets section scored lowest by all three evaluators (2.48–2.83); the native signer rated the corpus lower overall than the two interpreters.
- **Limitations stated by authors:** Difficulty representing some directional/body-contact signs (touching lower body, backside, spine) and some real-time facial expressions; full dynamic sentence generation isn't complete because not all vocabulary is mapped yet.

### Paper B
- **Best result:** Not stated in paper (no quantitative results).
- **Compared with:** Three related-work papers, narratively only.
- **Main finding:** The authors claim the system achieves "effective multimodal communication with good responsiveness," but no numbers back this up.
- **What worked:** Claimed (not measured): accurate multilingual translation, smooth avatar animation, low latency.
- **Failure cases:** Authors note accuracy depends on lighting conditions, gesture clarity, and network stability, but give no specific failure data.
- **Limitations stated by authors:** Currently supports "limited gestures and languages."

**Why this matters for our project:** Paper A's failure modes (alphabets/body-contact signs, incomplete sentence-level mapping) are a useful preview of problems we're likely to hit ourselves. Paper B offers no verifiable findings to learn from.

---

## 8. Reproducibility & Feasibility

| | Paper A | Paper B |
|---|---|---|
| Code available | Not stated in paper (relies on third-party open tools: HamNoSys authoring tool, SiS-Builder, SiGML player, JASigning) | Not stated in paper |
| Dataset available | Unsure — evaluation interface is public, raw corpus access unclear | N/A (none described) |
| Pre-trained model | No (lemmatizer trained from scratch, not released) | MediaPipe only (external, pretrained) |
| GPU requirement | Low — lemmatizer is a small BiLSTM/LSTM model; avatar rendering is desktop-based, not GPU-heavy | Not stated in paper |
| Free Colab feasible | Likely yes for retraining the lemmatizer; **Unsure** whether JASigning/SiGML player (desktop software) works in a Colab-only environment | Unsure — paper describes a Flask web app, not a Colab workflow |
| Missing resources | Clear public download/license for the corpus itself; per-word HamNoSys authoring is manual/labor-intensive | Dataset, mapping methodology, and code are all absent |
| Estimated reproduction time | Not stated in paper | Not stated in paper |
| **Feasibility** | **Partial** | **Not feasible** (as documented) |

**Why this matters for our project:** Given our zero-budget, Colab-only + local RX 570 setup, Paper A's lightweight lemmatizer is realistic to reproduce, but the avatar-rendering side (JASigning/SiGML player) needs verification since it looks like desktop software rather than something that runs natively in Colab. Paper B isn't reproducible with the information given, regardless of our resources.

---

## 9. Direct Takeaways for Our Project

### Paper A
- **Can adapt:**
  1. The HamNoSys → SiGML → avatar generation pipeline as the architectural backbone for our system.
  2. The BiLSTM + attention Seq2Seq lemmatizer approach for normalizing inflected Bangla words before dictionary lookup.
  3. The 4-point (Bad/Average/Good/Excellent) human-rating protocol for evaluating our own generated animations.
- **Not applicable:**
  1. Reusing the corpus's specific signs directly, until download access/licensing is confirmed.
  2. Any webcam/gesture-recognition component (not covered by this paper).
- **Open questions:**
  1. Is the IsharaKotha corpus/SiGML data actually downloadable, and under what license?
  2. Can JASigning/SiGML-player-style rendering run in a Colab-only, GPU-constrained pipeline, or does it require a local desktop environment?
- **Useful project phase:** Literature review; Bangla text processing; Text-to-sign-language translation; 3D avatar development.

### Paper B
- **Can adapt:**
  1. The general client–server (web frontend + backend) architecture as a possible future deployment shape.
  2. MediaPipe as a lightweight, low-resource library reference, relevant given our own hardware constraints.
  3. The idea of pairing pronunciation/TTS output with sign output for broader accessibility.
- **Not applicable:**
  1. No BdSL support or sign-generation methodology to reuse.
  2. No dataset or trained model to build on.
- **Open questions:**
  1. What sign notation or mapping approach does the system actually use internally? The paper never says.
  2. Is this a working system or a conceptual/demo-level project? The generic screenshots and lack of methodological depth make this unclear.
- **Useful project phase:** Literature review only (mainly as a contrast/caution case); possibly system-integration/UI ideas much later.

---

## 10. Action Items
- Try to locate a public repository or license terms for the IsharaKotha corpus/SiGML files (check the paper's evaluation site and author contacts).
- Investigate whether SiGML/JASigning-style rendering has any Colab-compatible or browser-based alternative (e.g., other SiGML players), since the original tooling looks desktop-bound.
- Treat Paper B as background context only; don't rely on it for methodology.

## 11. Questions for Supervisor / Team
- **Supervisor:**
  1. Should we treat dictionary/lookup-based generation (as in Paper A) as an acceptable first milestone, or is grammar-aware sentence-to-BdSL translation a hard requirement from the start?
  2. Given our zero-budget/Colab constraint, is it acceptable to prototype with a browser-based sign renderer instead of JASigning if JASigning proves Colab-incompatible?
- **Team:**
  1. Do we want to attempt contacting Paper A's authors about corpus access?
  2. Should we deprioritize gesture-recognition (sign-to-text) entirely, since our project direction is text-to-sign?

## 12. Keywords & Concepts
**Relevant keywords:** HamNoSys, SiGML, JASigning, BdSL corpus, avatar-based sign generation, lemmatization, Seq2Seq attention.
**Terms we need to learn:**
1. HamNoSys notation system (handshape/orientation/location/movement symbols).
2. SiGML XML schema and how it's authored/consumed.
3. JASigning / SiGML player setup and whether a Colab-compatible equivalent exists.

---

## 13. AI Reader Confidence Note
- **Paper A, Section 5 (Dataset):** Paper does not clearly state whether the raw IsharaKotha corpus (SiGML files) is downloadable or under what license — only the evaluation web interface link is given.
- **Paper A, Section 8 (Reproducibility):** Information unavailable on whether JASigning/SiGML player can run in a cloud/Colab environment; the paper describes it as desktop software (Windows/Mac/Linux).
- **Paper A, Section 6 (Evaluation):** Cannot determine training/validation/test split for the lemmatizer — only a final accuracy figure is reported.
- **Paper B, Section 4 (Methodology, all subsections):** Cannot determine the actual sign-generation or text-to-sign mapping method — the paper describes only a labeled box ("Sign Language Mapping") with no technical detail.
- **Paper B, Section 5 (Dataset):** Information unavailable — no dataset of any kind is named, sized, or linked anywhere in the paper.
- **Paper B, Section 6/7 (Evaluation/Results):** Not stated in the paper — all performance claims are qualitative, with no metrics, numbers, or benchmark comparisons given.
- **Paper B, general:** Unsure whether the system described (including the avatar shown in Fig. 2) is a functioning implementation or a conceptual mockup, given the shallow methodology and generic screenshots.
