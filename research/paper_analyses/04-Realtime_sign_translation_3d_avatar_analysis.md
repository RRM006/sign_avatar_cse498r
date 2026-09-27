# Paper Analysis: Real-time Sign Language Translation with 3D Avatar Interaction for Inclusive Communication

> Project context: Bangla Text → Bangla Sign Language (BdSL) via 3D Avatar | Zero budget, Google Colab T4 + local RX 570
> Analysis date: 2026-09-25

---

## 1. Basic Information

- **Title:** Real-time Sign Language Translation with 3D Avatar Interaction for Inclusive Communication
- **Authors:** M. Mehataj, P. Kanimozhi, Sunday Adeola Ajagbe, Praise I. Akinsipe, T. Ananth Kumar, John B. Oladosu, Pragasen Mudali
- **Year:** 2026
- **Venue / Journal / Conference:** Procedia Computer Science, Vol. 283, pp. 2958–2966 — proceedings of the International Conference on Machine Learning and Data Engineering (ICMLDE); Elsevier, open access (CC BY-NC-ND)
- **Paper link:** https://www.sciencedirect.com/science/article/pii/S1877050926019940
- **Code / Model / Dataset link:** Not stated in paper (no repository, model, or dataset link provided anywhere in the text)

---

## 2. Relevance to Our Project

**Primary area(s):**
- Text-to-Sign Language (speech/text → ISL via avatar)
- Sign Language Recognition (ISL gestures → text/speech, reverse direction)
- 3D Avatar / Sign Animation (Blender + motion capture pipeline)
- System integration (WebRTC video call)
- NOT: Bangla/low-resource NLP; NLP/grammar processing is minimal

**Aspect scores (my assessment, not from the paper):**

| Aspect | Score /5 | Reason |
|---|---|---|
| Bangla relevance | 1 | English speech/text and Indian Sign Language (ISL) only; no Bangla or BdSL content. Possible indirect value: ISL and BdSL are both South Asian sign languages, but the paper never discusses this. |
| Sign-language relevance | 4 | Fully in the sign-language translation domain; bidirectional (speech↔sign) real-time system with avatar output. |
| Text-to-sign translation | 3 | Has a speech→text→sign module, but it is a simple word-to-predefined-animation lookup. No translation model, no syntax handling, no gloss generation. |
| NLP / grammar | 1 | Only a one-line mention of NLTK for converting English sentences to signs. No grammar rules, no reordering, no linguistic processing described. |
| Sign/motion generation | 2 | Animations are hand-crafted/mocap-recorded per word in Blender, then replayed. Not learned motion generation; "assembling sign subunits" mentioned but not detailed. |
| 3D avatar / animation | 4 | Strongest part: complete free-tool avatar pipeline — Mixamo/Blender modeling, rigging, UV texturing, Rokoko mocap from sign videos, retargeting, IK, Graph Editor smoothing, real-time rendering in video call. |
| Dataset usefulness | 1 | Small self-built ISL dataset (50 signs, 78 sentences, 324 words); not public, no link, wrong sign language for us. |
| Feasibility for our project | 3 | Architecture reproducible with free tools (Blender, Mixamo, WebRTC); CNN training easily fits Colab T4. But no code/dataset released, weak evaluation details, and exact mocap setup is ambiguous. |

**Overall relevance: Medium**
**Why:** Valuable as an end-to-end *system architecture blueprint* (text→sign avatar + video-call integration) and for its free 3D avatar animation workflow. Weak as a methodological reference: no real translation/NLP model, tiny non-public dataset, and near-absent quantitative evaluation.

**Why this matters for our project:** It confirms a lookup-based avatar pipeline is a viable *v1 baseline* for Bangla→BdSL, but we must build our own BdSL animation data and add real Bangla NLP, which this paper does not provide.

---

## 3. Problem & Proposed Solution

**A. Problem:**
- Deaf/hard-of-hearing people are excluded from conversation with hearing people; human interpreters are unavailable, costly, and impractical in real time.
- Video-conferencing tools ignore signers (speaker-focused windows; real-time sign recognition from video streams is computationally expensive).
- Goal: a real-time, bidirectional communication prototype — spoken/typed input → ISL signs shown by a 3D avatar; ISL gestures → text + speech — integrated into video calls.

**B. Approach:**
- Four modules:
  1. **Avatar creation:** 3D character (Blender/Maya or pre-built from Mixamo/Sketchfab), rigged skeleton, UV textures; animated via Rokoko motion capture (incl. face capture for emotion-based expressions).
  2. **Speech-to-sign:** microphone audio → speech-to-text → text words mapped to a pre-built database of Blender animations → avatar plays the sign sequence.
  3. **Sign-to-speech/text:** camera video → frame extraction → preprocessing (resize, normalize) → VGG-16 CNN classifies gesture into one of ~50 ISL signs → predefined sign→word mapping → text display + GTTS speech output.
  4. **Video-call integration:** WebRTC for peer-to-peer streaming; UI in Flutter; real-time synchronization of avatar motion with conversation.

**C. Connection to our project:**
- **Directly useful:** the overall system architecture (text/speech → sign animation → avatar → real-time display) and the free-tool avatar animation workflow (Blender + Mixamo + video-based mocap + retargeting + smoothing).
- **Technique we can adapt:** per-word animation library with lookup mapping as a first-pass Bangla→BdSL prototype; frame-preprocessing + transfer-learned CNN recipe if we later add a BdSL *recognition* module; scenario-based accuracy testing (speech speed, lighting, ambiguity).
- **Different from our project:** ISL (not BdSL); English (not Bangla); word-by-word lookup (no translation model, no grammar — Bangla is SOV and will likely need reordering); animations hand-authored (not generated); it is bidirectional while we only need text→sign.

**Why this matters for our project:** It gives us a concrete, budget-friendly pipeline skeleton to copy for the avatar half of our system, while showing exactly what is missing (Bangla NLP + BdSL data + generated motion) that we must research and build ourselves.

---

## 4. Methodology

### 4A. NLP / Text Processing
- **Input language:** English (spoken or typed)
- **Tokenization:** NLTK used to convert English sentences to signs — no further detail stated
- **Grammar / linguistic processing:** Not stated (implied word-by-word mapping; no syntax reordering or glossing described)
- **Translation method:** Rule-based lookup — each recognized word/phrase mapped to a predefined avatar animation in a database
- **Output representation:** Sequence of pre-authored 3D animation clips (one per word/phrase); reverse direction outputs text + synthesized speech

### 4B. Sign Language
- **Sign language:** Indian Sign Language (ISL)
- **Sign representation:** Keyframed Blender animations per sign; inverse kinematics controlling bone rotations/joint translations; motion expressed as transform T = R(θ) × T(dx, dy, dz) (rotation × translation)
- **Sign vocabulary:** 50 frequently used signs (e.g., I, sorry, thank you, please, welcome, good morning/evening/night, today, tomorrow, yesterday); 324 distinct words; 78 unique sentences; 4 animation variants per phrase
- **Text-to-sign mapping:** Predefined word/phrase → animation database entries
- **Sign sequence generation:** Concatenative playback of animation clips; authors mention "assembling sign subunits to produce animated motions" but give no detail on blending or transitions

### 4C. ML / Deep Learning
- **Model:** VGG-16 CNN — used only for the *sign→text* recognition direction (no learned model for text→sign)
- **Pre-trained model:** VGG-16 described as "pre-trained"; source of pretraining weights (e.g., ImageNet) not stated
- **Training data:** Self-collected ISL sign videos (50 signs); collection details (signers, count, conditions) not stated
- **Fine-tuning:** Not explicitly stated — transfer learning implied but no details
- **Important hyperparameters:** Not stated in paper (no learning rate, batch size, epochs, optimizer)
- **Training method:** Not stated; inference pipeline described: frame extraction → resize/normalize to VGG-16 input size → convolutional feature extraction → classification → text mapping

### 4D. 3D Avatar / Animation
- **Avatar type:** Humanoid 3D mesh character; either custom-built (Blender/Autodesk Maya) or pre-built .fbx/.glb downloaded from free platforms (Mixamo, Open3DModel, Sketchfab)
- **Rigging / skeleton:** Bone-and-joint skeleton rig added to mesh; UV mapping for skin/clothing/hair textures; IK for joint control
- **Motion representation:** Keyframe animation + motion-capture skeletal data; rigid transforms (rotation + translation) per Eq. (1)
- **Animation method:** Rokoko motion capture (Smartsuit Pro mentioned in text; Fig. 3 shows capture from pre-recorded sign videos in Rokoko Studio — ambiguous which was actually used); Rokoko Face Capture via smartphone for emotion-based facial expressions; motion imported to Blender via Rokoko Studio Live plugin and retargeted onto the avatar rig; manual fine-tuning in Pose Mode
- **Motion smoothing / interpolation:** Constraint-based retargeting; Graph Editor + Dope Sheet used to refine motion curves, timing, and transitions
- **Rendering method:** Real-time rendering through Unity and/or WebRTC video-call interface (Flutter UI); exact rendering engine/settings not stated

### 4E. System Pipeline
- **Speech→sign:** Mic audio → [speech-to-text — paper confusingly names GTTS here, likely an error] → [NLTK tokenization + word→animation lookup] → [avatar plays ISL animation sequence] → rendered live in WebRTC/Unity video call
- **Sign→speech/text:** Camera video → [frame extraction + resize/normalize] → [VGG-16 CNN classification into 50 ISL signs] → [sign→word mapping] → text display + GTTS speech output

**Why this matters for our project:** The avatar workflow (Mixamo rig → video mocap → retarget → smooth → export clips) is directly reusable with zero budget; the "ML" part is shallow (a stock CNN for recognition only), so we cannot borrow any translation/generation modeling from this paper.

---

## 5. Dataset

- **Dataset name:** Self-built ISL database (no formal name given)
- **Language:** English text/speech ↔ Indian Sign Language
- **Sign language:** ISL
- **Size:** 50 frequently used signs; 78 unique sentences; 324 distinct words; 4 animation sequences per phrase
- **Number of classes/signs:** 50 (recognition classes)
- **Text/sign pairs:** Yes — 78 sentences mapped to animation sequences; word→animation entries
- **Video / image / motion data:** Videos of performed signs (used as mocap source); Blender animation files; mocap skeletal data
- **2D or 3D:** Both (2D video input for recognition; 3D animations for output)
- **Publicly available:** No — not stated as public; no download link given
- **Link:** Not stated in paper
- **Collection method:** Animations created with the Blender toolset; body motion captured with Rokoko from pre-recorded sign videos; number of signers and recording conditions not stated
- **Annotation method:** Predefined word/phrase → animation mapping (annotation process details not stated)
- **Can we use it?** No
- **Why:** It is ISL (not BdSL), English-linked (not Bangla), small, non-public, and animation-based rather than raw sign video we could retrain on. Only indirect value: the *recipe* for building an equivalent Bangla→BdSL animation library.

**Why this matters for our project:** Confirms we will have to collect/build our own BdSL data; no shortcut dataset exists in this paper.

---

## 6. Evaluation

Only metrics actually used in the paper:

| Task | Metric | Result |
|---|---|---|
| Translation | Not covered in paper (no BLEU/exact-match/semantic scores) | N/A |
| Sign recognition | Accuracy across scenarios (Fig. 5): speech speed (fast/normal/slow), lighting (bright/dim), gesture ambiguity | Numeric values only in figure image; not stated in text |
| Sign generation | Not covered in paper | N/A |
| Motion quality | Not covered in paper (no quantitative motion metrics) | N/A |
| Avatar evaluation | No formal user study; qualitative claims only (emotion expressions make interaction "natural", "human-like") | Not quantified |
| Other | Qualitative demo outputs (Figs. 6–7: "I'm fine" sign→text; speech→sign avatar overlay) | Demonstrated, not measured |

- **Train / Validation / Test split:** Not stated in paper
- **Baselines:** None — no comparison with any prior system
- **Hardware:** Not stated in paper
- **Framework:** Blender, Rokoko Studio, Unity, Flutter, WebRTC, NLTK, GTTS; deep-learning framework (TensorFlow/PyTorch) not stated

**Why this matters for our project:** This is the paper's weakest section — we should treat its evaluation as an anti-pattern and plan our own proper metrics (translation accuracy vs. BdSL glosses, avatar intelligibility user tests, latency) rather than copying its scenario-only accuracy plot.

---

## 7. Results & Findings

- **Best result:** Not stated numerically in text — accuracy values appear only in the Fig. 5 graph image (not machine-readable in our PDF text). Unsure: cannot extract exact numbers.
- **Compared with:** Nothing — no baselines or prior systems compared.
- **Main finding:** A modular bidirectional prototype (avatar speech-to-sign + CNN sign-to-speech) integrated into WebRTC video calls can enable real-time hearing↔deaf communication; emotion-aware facial animation improves perceived naturalness.
- **What worked:** VGG-16 transfer learning for classifying 50 ISL gestures from video frames; predefined word→animation lookup for speech-to-sign; Blender+Rokoko pipeline for producing per-word sign animations; WebRTC/Flutter for live integration.
- **Failure cases:** Fig. 5 shows accuracy varies by scenario (fast speech, dim lighting, ambiguous gestures degrade performance) — exact magnitudes not readable from text.
- **Limitations stated by authors:** No explicit limitations section. Scattered statements imply: static word-level vocabulary that must grow ("as more dynamic movements are specified, the approach will be improved"); sign-writing synthesis named as a goal/future direction. (Partly inferred — see Section 13.)

**Why this matters for our project:** Sets expectations: a lookup + replay avatar system "works" as a demo but has no evidence of translation quality — our project must add measurable evaluation and Bangla-specific grammar handling to go beyond this level.

---

## 8. Reproducibility & Feasibility

- **Code available:** No
- **Dataset available:** No
- **Pre-trained model:** No (only generic off-the-shelf VGG-16 weights, source unspecified)
- **GPU requirement:** Not stated in paper. (My estimate: fine-tuning VGG-16 on 50 small image classes easily fits a Colab T4/15GB; avatar pipeline needs no GPU-heavy training.)
- **Free Colab feasible:** Partial — CNN recognition experiments: yes; Blender/Rokoko/Unity/WebRTC avatar work: runs on a local CPU machine (our 24GB RAM box), not on Colab.
- **Missing resources:** Dataset, code, hyperparameters, train/test split, exact accuracy numbers, actual ASR component used, rendering/latency specs.
- **Estimated reproduction time:** Not stated in paper. My rough estimate: days for the CNN recognition toy version on Colab; several weeks to hand-build even a 50-sign BdSL animation library in Blender.
- **Feasibility:** Partial — architecture and toolchain are reproducible with free tools; exact results are not reproducible because no data/code is released.

**Why this matters for our project:** We can safely borrow the toolchain (all free/local-friendly), but we cannot benchmark against this paper; any comparison we claim in our write-up must be qualitative.

---

## 9. Direct Takeaways for Our Project

**Can adapt:**
1. **Free avatar animation pipeline:** Mixamo pre-built rigged avatar (.fbx) → Blender → motion capture from recorded sign videos (Rokoko Studio video mode / free alternatives like MediaPipe) → retarget to rig → smooth with Graph Editor/Dope Sheet → export per-sign clips. Zero-budget compatible; runs on our local machine, not Colab.
2. **Word-level animation lookup as v1 baseline:** Build a small BdSL animation DB (start with high-frequency words) and play concatenated clips from Bangla text — a working demo before attempting learned generation.
3. **Scenario-based stress testing:** Test our system across input variations (speech speed, lighting, ambiguous signs) as they did in Fig. 5 — a cheap evaluation idea; plus their CNN frame-preprocessing recipe (extract → resize → normalize) if we ever add a BdSL recognition module.

**Not applicable:**
1. Their ISL sign inventory and English↔ISL mappings — BdSL has its own lexicon/grammar; we must source BdSL references (e.g., Bangladesh National Federation of the Deaf materials) instead.
2. Their "GTTS for speech recognition" step — GTTS is text-to-speech, not ASR (and speech input is out of our scope). Do not replicate this confusion.

**Open questions:**
1. Is word-by-word lookup acceptable for BdSL, or does Bangla SOV word order + BdSL grammar require reordering/glossing first? (This paper offers no answer — a known gap in word-by-word systems.)
2. Which free mocap route gives finger-level precision adequate for BdSL handshapes — Rokoko Video free tier, MediaPipe Holistic, or manual keyframing in Blender?

**Useful project phase:**
- [x] Literature review (system-architecture reference)
- [x] Bangla text processing (only as a contrast: shows how little NLP such systems often include)
- [ ] Sign-language translation
- [x] Dataset collection (recipe for building an animation library)
- [x] Model development (CNN recognition baseline only)
- [x] Sign sequence generation (concatenative clip playback)
- [x] 3D avatar development (primary value of this paper)
- [x] Evaluation (scenario-based testing idea; anti-pattern for metrics)
- [x] System integration (WebRTC/Flutter video-call integration)

**Why this matters for our project:** The paper's main gift to us is a validated free toolchain for the avatar half and a warning that the translation half needs real linguistic work they skipped.

---

## 10. Action Items

1. Set up Blender locally (free) + download a Mixamo rigged humanoid; reproduce their avatar setup as a weekend test.
2. Pilot video-based mocap on 3–5 recorded BdSL signs (try Rokoko Video free tier; fallback MediaPipe Holistic) and compare finger fidelity vs. manual keyframing.
3. Build a prototype lookup player: Bangla sentence → tokenized words → concatenated animation clips (Blender/Unity or pre-rendered video).
4. Add this paper to the literature-review matrix under "avatar pipeline / concatenative synthesis"; search its related-work references ([6] SignCom/Portuguese LGP, [8] SawtiEshara/Saudi, [10] SLAnimator, [2] ES2ISL) as next papers to read.

---

## 11. Questions for Supervisor / Team

**Supervisor:**
1. Should we cite this paper only as a system-design reference (no quantitative comparison possible), and is a word-lookup v1 demo an acceptable first milestone for the project report?
2. For scope: do we need only text→BdSL (avatar), or also BdSL→text recognition? This paper is bidirectional, which doubles the workload.

**Team:**
1. Who owns the Blender/animation track vs. the ML/NLP track? The avatar pipeline is local-CPU work; the ML work is Colab — they can proceed in parallel.
2. Can we record a native BdSL signer (video) to use as mocap source, given Rokoko hardware suits are out of budget — is webcam-based capture good enough for finger-level signs?

---

## 12. Keywords & Concepts

**Relevant keywords:**
1. Speech/text-to-sign translation
2. 3D signing avatar animation
3. Motion capture & retargeting (Rokoko, Blender)
4. VGG-16 CNN gesture/sign recognition (transfer learning)
5. Concatenative sign synthesis / word-level animation lookup (plus: WebRTC real-time integration, NLTK, GTTS, Indian Sign Language)

**Terms we need to learn:**
1. **Rigging & inverse kinematics (IK)** — skeleton bones/joints and how IK controls limbs/hands for animation.
2. **Motion-capture retargeting** — mapping captured skeletal motion onto a differently proportioned avatar rig (constraint-based retargeting).
3. **Gloss & sign-language linguistics (phonology/morphology/syntax)** — why word-by-word text→sign fails and what gloss-based translation means (the paper cites Sutton-Spence & Woll for this).

---

## 13. AI Reader Confidence Note

Everything below was NOT explicitly stated by the paper (no silent guessing was done):

- **Section 1:** DOI not printed in the extracted PDF text; paper link was located via the ScienceDirect record (URL verified: S1877050926019940).
- **Section 4A / 4E:** The paper claims the **GTTS API (a text-to-speech service) performs speech recognition/transcription** — this is internally contradictory and almost certainly an author error. The actual ASR component used is **not stated in the paper**.
- **Section 4B:** "Assembling sign subunits" for motion generation is mentioned but **no detail on clip blending/transitions** is given — cannot determine how sign sequences are smoothed together.
- **Section 4C:** Deep-learning framework, hyperparameters, epochs, optimizer, pretraining source of VGG-16, and fine-tuning details are **all not stated in the paper**.
- **Section 4D:** Whether motion capture used the commercial **Rokoko Smartsuit Pro** (text) or **video-based capture from recorded sign videos** (Fig. 3 caption) is ambiguous — Unsure which was actually used; budget implications differ greatly.
- **Section 5:** Number of signers, recording conditions, and video hours for the dataset are **not stated**; public availability is never claimed (assumed not public due to absence of any link — flagged as inference).
- **Section 6:** Numeric accuracy values exist only inside the **Fig. 5 image**, which is not text-extractable from our PDF — results marked unavailable. Train/val/test split, hardware, and DL framework: **not stated in the paper**.
- **Section 7:** The paper has **no explicit limitations section**; listed limitations are inferred from scattered sentences (vocabulary growth, future sign-writing goal) — flagged as inference.
- **Section 8:** GPU requirement and reproduction time are **my estimates, not from the paper**.
- **General:** Section numbering in the paper itself is inconsistent ("2. Proposed System" followed by subsections 3.1–3.4, then "3. Result and Discussion", then "5 Conclusion") — minor quality signal; no additional hidden content was skipped.
