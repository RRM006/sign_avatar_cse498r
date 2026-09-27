# BdSL Text-to-Sign: Research & Build Guide

> **Status: PROPOSAL — not a confirmed project decision.** The "recommended direction", models and pipeline below are proposals. Confirmed decisions are recorded in the project `README.md`.

Sep 26, 2026 · @EHR

**Recommended direction:** learn Bangla text → body-and-hand keypoint motion from your 3,456 sentence–video pairs. Test it on splits that never share a sentence or a duplicate video between training and testing. Train a text↔motion matching model first, then a text→motion generator. Add the 3D avatar last, as a display layer.

Labels used throughout: **Verified** (your dataset profiling or my file inspection), **Literature** (cited), **Proposed** (our design choice, untested), **Assumption**, **Unknown**. No experiments have been run, so this guide contains no results.

## 1. Current Project Status

The project has finished investigating its evidence. It has not yet defined its training problem, so nothing should be coded beyond data preparation.

| Area | Status |
| --- | --- |
| Literature | Done: 6 papers analysed, plus a web check of newer work |
| Dataset profiling | Done: videos, duplicates, codecs, framing, audio, MediaPipe feasibility |
| Reproducible train/validation/test split | Not started |
| Keypoints for the full dataset | Not started (MediaPipe tested only) |
| Baseline, model, evaluation | Not started |
| 3D avatar | Not started (correctly, since it comes last) |

**Correction to the earlier research report.** That report assumed the repeated spreadsheet rows were extra takes of the same sentence, because that was the team's earlier answer. Your profiling shows most repeats are duplicate files, and about 98.5% of sentences have only one usable video. So two ideas from that report are dropped: the "take-agreement ceiling" and "multi-take supervision". Both needed several recordings per sentence.

## 2. What We Actually Have

We have about 3,456 distinct pairs of (Bangla sentence, sign video), usually one video per sentence, and no labels below the sentence level.

| Item | Value | Label |
| --- | --- | --- |
| Videos | 5,010 MP4 files, 66.3 GB, about 9.9 h, mean about 7.1 s, median about 6.4 s | Verified (profiling) |
| After duplicate removal | 3,456 unique video/sentence pairs | Verified (profiling) |
| Unique normalised sentences | 3,381 (my spreadsheet check gave 3,379 with a slightly different normaliser) | Verified |
| Videos per sentence | About 98.5% of unique sentences have exactly one usable video | Verified (profiling) |
| Sentence length | About 4.2 words on average; about 1,446 unique words (my whitespace count: 1,429) | Verified |
| Sentence structure | Heavily templated. "আমার ‹আত্মীয়› ‹বার› ‹খাবার› খায়" alone covers 157 sentences | Verified (my inspection) |
| Labels | Sentence-level only. No gloss, word alignment, sign boundaries, frame labels, pose ground truth, signer ID or split | Verified |
| Video format | H.264, HEVC and a few others; about 30 fps with variable frame rate; mixed resolutions; mostly portrait (1080×1920, 720×1280), some landscape (1280×720, 1284×720) | Verified (profiling) |
| MediaPipe | Body detection reliable. Hands noisier: not always both detected, sometimes out of frame, lost to motion blur, worse in portrait. Head generally visible | Verified (profiling) |
| Audio | Mostly silence, noise or background speech; not a training signal | Verified (profiling) |
| Text quality | Spelling variants (মংগলবার / মঙ্গলবার, মুরগী / মুরগি), typos, 9 rows with Latin script, 7 rows with zero-width characters | Verified (my inspection) |
| Number and identity of signers | — | Unknown |
| Where the videos came from; consent and licence | — | Unknown |

The limitations that shape every later decision:

- **One video per sentence.** The model never sees two versions of the same sentence. It must handle new sentences by recombining parts it has seen.
- **No gloss or boundaries.** Nothing tells us which frames show which word.
- **Noisy hands.** The most informative part of signing is the least reliable part of our targets.
- **Duplicates.** A random split would put the same video in training and testing.

One figure needs its denominator stated before it goes in a paper. "About 61% byte-identical duplicates" does not match 5,010 files shrinking to 3,456, which removes about 31% of files. The 61% probably counts something else, such as duplicate groups. The design is the same either way.

## 3. What We Are Trying to Learn

We are learning which body and hand movements go with which Bangla words, and how those movements combine into a sentence. Nobody tells the model where each word's sign starts or ends.

The running example is "আমি স্কুল যাই". Your example "আমি স্কুলে যাই।" is not in the dataset, but this version is.

1. **What enters the system?** The typed sentence "আমি স্কুল যাই".
2. **What happens to the text?** It is cleaned: Unicode fixed, zero-width characters removed, spelling variants mapped to one form. It is then split into **tokens**, the small pieces a model reads (here, words): আমি | স্কুল | যাই.
3. **What does the ML model receive?** Each token becomes an ID number, then a learned list of numbers called an **embedding**. An embedding is a numeric code the model adjusts during training so that words used alike get similar codes.
4. **What does the model try to predict?** A sequence of **keypoints**, frame by frame. Keypoints are (x, y, z) positions of body points: shoulders, elbows, wrists, and 21 points on each hand.
5. **What is the target?** The keypoints that **MediaPipe** extracted from the real video of this sentence. MediaPipe is a ready-made **pose estimator**, a program that finds body points in video. The target is therefore an estimate, and the hand points can be wrong or missing.
6. **How does the model know if it is good or bad?** It compares its predicted points with the target points and computes an error number, the **loss**. Smaller loss means closer to the real signer.
7. **What does the trained model produce?** For a sentence it has never seen, a new keypoint sequence. Think of it as a moving stick figure.
8. **How does that become sign motion?** Simple processing removes jitter and keeps bone lengths constant. The result is a clean skeleton animation.
9. **How does it control a 3D avatar?** A conversion step turns point positions into joint rotations for the avatar's skeleton, called its **rig**. The avatar software then plays those rotations. This step is rule-based, not trained.

**Why an intermediate representation is needed.** An avatar cannot be driven by text. It needs joint information for every frame. Our videos can give us joint positions through MediaPipe, but they cannot give us glosses (written labels for each sign). So keypoints are the only intermediate representation our data can supervise. They are also far smaller than video. By my rough arithmetic, body and hand points for all 9.9 h come to about 1 GB as 32-bit numbers, against 66.3 GB of video. That makes training on Colab or Kaggle practical.

## 4. Possible Problem Formulations

Three formulations fit our data now: text↔motion retrieval, text→keypoint generation, and weak supervision from sentences that differ by one word. Gloss-based formulations need annotation we do not have.

Two terms first. **Contrastive learning** teaches a model that a sentence and its own video belong together and mismatched pairs do not. **Retrieval** means answering a query by picking the best item from a stored collection.

| Formulation | Input → target | Supervision and training objective | Inference | Main limitation | With our data |
| --- | --- | --- | --- | --- | --- |
| 1. Text → sign retrieval | Sentence → the matching video's keypoints, among many | Sentence–video pairs; contrastive loss that scores the true pair above the others | Return the stored motion that best matches the text | Can only replay sentences already recorded | **Feasible now** |
| 2. Text↔video representation learning | Same model as 1, used as a "meaning checker" | Same | Score how well any motion (including generated motion) matches a sentence | Proves agreement with a model, not with a signer | **Feasible now** |
| 3. Text → keypoint sequence | Sentence → MediaPipe keypoints of its video | Masked distance between predicted and extracted points | Generate new motion for new sentences | Tends to average motions into vague hands; targets are noisy | **Feasible now** (main research risk) |
| 4. Text → learned motion tokens → keypoints | Sentence → discrete "motion words" learned by a VQ-VAE | Two stages: compress motion, then predict tokens | Decode generated tokens into motion | More components, more data-hungry | **Difficult**: a later upgrade only |
| 5. Text → gloss → keypoints | Sentence → gloss → motion | Needs sentence–gloss pairs | Two-step translation | No glosses; no BdSL expert available | **Needs additional annotation** |
| 6. Weakly supervised text → motion | Sentence pairs differing in one word → the video segment that differs | Alignment between the two videos; no labels | Build or edit motion from located word segments | Unproven on BdSL; signs blend at boundaries | **Feasible as a research experiment** |
| 7. Dictionary lookup (HamNoSys/SiGML, papers P1 and P5) | Word → hand-written sign file | None; experts write the dictionary | Play dictionary signs in order | Needs a dictionary, not our videos | **Not supported by our data**; optional outside comparison |
| 8. Photoreal video generation | Sentence → video pixels | Video generation | Render a video | Far beyond our data and compute | **Not supported** |

What the literature says about these:

- Text↔sign-video retrieval is an established task ([CiCo](https://arxiv.org/abs/2303.12793), CVPR 2023). [SignCLIP](https://aclanthology.org/2024.emnlp-main.518/) (EMNLP 2024) trained text↔sign contrastive models on MediaPipe Holistic poses, and reports that pose input worked better than 3D-CNN video encoders in its setup.
- Direct text→pose generation without glosses exists for other sign languages: [Progressive Transformers](https://github.com/BenSaunders27/ProgressiveTransformersSLP) (ECCV 2020). The "averaging" problem is documented by [Saunders et al.](https://arxiv.org/abs/2008.12405) (BMVC 2020): "under-articulated output caused by regression to the mean".
- Motion-token approaches: [T2S-GPT](https://arxiv.org/abs/2406.07119) (ACL 2024) and [SOKE](https://openaccess.thecvf.com/content/ICCV2025/papers/Zuo_Signs_as_Tokens_A_Retrieval-Enhanced_Multilingual_Sign_Language_Generator_ICCV_2025_paper.pdf) (ICCV 2025).
- Weakly supervised sign localisation from subtitles exists for British Sign Language: [Watch, Read and Lookup](https://arxiv.org/abs/2010.04002) (ACCV 2020) and [Read and Attend](https://openaccess.thecvf.com/content/CVPR2021/papers/Varol_Read_and_Attend_Temporal_Localisation_in_Sign_Language_Videos_CVPR_2021_paper.pdf) (CVPR 2021). Both use far more data than ours.

## 5. Initial Research Direction

**Proposed:** gloss-free, keypoint-based BdSL sentence production, tested on leakage-safe and unseen-combination splits. It is built in three steps: (1) data, splits and keypoints; (2) a text↔motion matching model; (3) a text→motion generator that must beat a retrieval baseline.

Why it fits the evidence:

- **No glosses:** keypoints are the only target we can extract automatically.
- **Templated sentences, one video each:** the real question is whether a model can recombine known parts. The unseen-combination split tests exactly that.
- **Duplicates:** grouped splits are built before any model exists.
- **Noisy hands:** presence masks and per-quality reporting are part of the design from day one.
- **Hardware:** keypoints and small models fit a free T4. Extraction runs on local CPUs.
- **Literature:** gloss-free text→pose exists for other sign languages. Every BdSL text-to-sign system in our six papers is dictionary lookup. I found no expert-free, sentence-level BdSL production benchmark, but that is a search result, not proof.

Do not claim "first BdSL pose generation". [SignBD-Word](https://ieeexplore.ieee.org/document/10306914/) (2023) already covers video-based, word-level Bangla sign language *and pose* translation. [Bangla-SGP](https://arxiv.org/abs/2511.08507) (LREC 2026) released 1,000 human-annotated Bangla sentence–gloss pairs for BdSL translation.

**The direction at a glance:**

|  | Question | Answer |
| --- | --- | --- |
| A | What is the baseline? | B1: replay the motion of the most similar training sentence (section 6) |
| B | What is our first ML model? | A text↔motion matching model (section 7) |
| C | What is the input? | A normalised Bangla sentence (plus, for the matching model, a keypoint sequence) |
| D | What is the target? | The MediaPipe keypoint sequence extracted from that sentence's video |
| E | What does the model learn? | Which motion goes with which words, and how word motions combine into a sentence |
| F | What is the loss? | Contrastive loss for the matching model; masked point distance + velocity + length loss for the generator |
| G | What happens at inference? | New sentence → normalise → generator → keypoint sequence → smoothing |
| H | How does it reach the avatar? | Retargeting turns points into bone rotations, which a rigged 3D character plays (section 12) |

**Decision record** (keep this in your decisions log):

| # | Decision | Choice | Why | Revisit if |
| --- | --- | --- | --- | --- |
| D1 | Intermediate representation | MediaPipe keypoints: upper body + both hands; face only as an ablation | The only representation our data can supervise | A gloss annotator becomes available |
| D2 | First ML model | Text↔motion matching (retrieval) model | Well defined with one video per sentence; shows whether keypoints carry sentence meaning; later judges the generator | Retrieval stays near chance → fix keypoint quality first |
| D3 | Main generator | Small non-autoregressive text→keypoint model | Simplest trainable generator; fast on a T4 | Output collapses to average motion → try motion tokens |
| D4 | Splits | Grouped by sentence and duplicate cluster, plus template and combination splits | Prevents leakage; tests generalisation | Signer IDs recovered → add a signer split |
| D5 | Avatar | After the ML pipeline; skeleton player first, 3D avatar later | Research validity before visuals | — |
| D6 | Audio | Not used | Verified to be mostly silence or noise | New evidence of signer narration |

## 6. Baseline

The main baseline is **"copy the nearest training sentence"**. A learned model is only worth anything if it beats it, especially on sentence combinations it has never seen.

**B1 — Nearest training sentence (main baseline, Proposed).**

1. Normalise the input text.
2. Represent every sentence by counts of its character sequences (character n-gram TF-IDF, a standard text-similarity method).
3. Find the most similar sentence in the training split.
4. Output that sentence's real keypoint sequence. No motion model is trained.

**Why it suits this dataset.** The sentences are templated, so the nearest training sentence usually differs by one slot word. For "আমার চাচা বুধবার মাংস খায়" it might return "আমার চাচা শুক্রবার মাংস খায়". That motion is mostly right, with one wrong sign. It is a strong, honest opponent that exposes a model which only memorises.

**B0 — Average motion (sanity baseline).** Output the average training keypoint sequence. A model that scores close to B0 is producing blurred, meaningless motion.

**Retrieval baselines (for the matching model).** Report **chance level** (1 divided by the number of candidate videos). Also use B1 as a retriever: rank the test videos by how close they are to the nearest training sentence's motion.

**Optional outside comparison.** The public SiGML signs from Karim et al. (paper P5, about 90 signs) can show how many test sentences a dictionary system could sign at all. Its avatar output is not in our keypoint format, so it is not a numeric baseline.

**What the proposed models should improve on.** The generator should get the changed word's sign right where B1 copies the wrong one. The matching model should rank the correct video far above chance. Both are measured in section 10.

## 7. Proposed ML Model

Two small models, trained in this order: a **matching model** that learns whether a sentence and a motion belong together, then a **generator** that creates motion for a sentence. Both are Proposed and untested.

### Model 1 — Text↔motion matching model (the first ML model)

- **Why we need it.** Before generating motion, we must know whether our keypoints even distinguish sentences. If a model cannot tell a "বুধবার" video from a "শুক্রবার" video, a generator will not learn them either. This model answers that cheaply and later acts as an automatic judge for the generator.
- **Input:** a sentence, and a keypoint sequence with presence flags (which points MediaPipe found).
- **Output:** one embedding for each, and a similarity score between them.
- **Architecture concept:** a text encoder (a small Transformer or GRU over word tokens) and a motion encoder (a small Transformer or temporal convolution over frames). Both map into the same vector space. A **Transformer** is a network that lets every token or frame look at every other one, which suits relating words to stretches of motion. A GRU is a simpler recurrent network that reads items one by one.
- **Training objective:** contrastive loss (InfoNCE, as in CLIP and SignCLIP). In a batch of N pairs, each sentence should score its own video higher than the other N−1.
- **Inference:** give it a sentence and it ranks all stored motions; give it a generated motion and it says whether that motion matches its sentence.

### Model 2 — Text→motion generator (the production model)

- **Input:** the sentence's tokens.
- **Output:** a keypoint sequence up to a maximum length, plus a predicted length (how many of those frames are real).
- **Representation per frame:** upper-body points (legs dropped) and 21 points per hand. Coordinates are centred on the shoulders and scaled by shoulder width, following SignCLIP. They stay in MediaPipe's point layout, so the avatar step can consume real and generated motion the same way.
- **Architecture concept:** a text encoder, then a decoder with one learnable slot per output frame. Each slot looks at the words and predicts its frame's points. This is **non-autoregressive**: all frames are predicted at once instead of one after another. It is simpler and faster, and one bad frame cannot derail the next. Move to an autoregressive or motion-token model only if this one fails.
- **Training objective:** a distance loss between predicted and extracted points, counted only where MediaPipe detected the point. Add a velocity loss (match how fast points move) and a length loss. A bone-length consistency term is optional.
- **Inference:** normalise → encode → predict frames and length → trim → smooth → retarget → avatar.
- **Known risk:** averaged, under-articulated hands ("regression to the mean", [Saunders et al. 2020](https://arxiv.org/abs/2008.12405)). Detect it by comparing against B0 and by measuring how much the hands move.

### Training in plain words

- **One training sample:** (normalised sentence, keypoint sequence of its video, presence mask).
- **Loss:** a single number for how wrong the model was on a batch.
- **Optimisation:** an optimiser such as Adam nudges the model's internal numbers (its weights) to lower the loss. It repeats this over many passes through the data, called **epochs**.
- **Validation:** a held-out part of the training data, checked after each epoch. It is used to choose settings and to stop before the model memorises the training data (**overfitting**).
- **Testing:** a separate held-out set, used once at the end. If test sentences or duplicate videos leak into training, the score measures memory, not translation.
- **A completely new sentence:** if all its words appeared in training, the generator composes motion from what it learned. If a word never appeared (out-of-vocabulary), no motion was ever learned for it. Flag it; a fingerspelling fallback is a later option.

| Component | Type |
| --- | --- |
| Text normaliser and variant map | Rule-based |
| Tokeniser and vocabulary | Deterministic, built from the training split only |
| Pretrained Bangla encoder (BanglaBERT) | Pretrained; optional, used as an ablation |
| MediaPipe Holistic | Pretrained, reused |
| Decoding, keypoint normalisation, resampling | Deterministic |
| Model 1 and Model 2 | Trained on our data |
| Slot recogniser | Trained on our data; used for evaluation only |
| Smoothing, retargeting, avatar rendering | Deterministic or existing tools; not trained |

## 8. MediaPipe Role

MediaPipe runs once, offline, between the raw videos and everything else. Its output is both the training target and the format the avatar step consumes. It runs a second time at the end, on rendered avatar videos, as a round-trip check.

**Where it enters (Proposed flow):**

1. **Probe** each video with ffprobe: codec, resolution, frame timestamps and **rotation metadata**. Phone videos are often stored sideways with a rotation flag. If the flag is ignored, MediaPipe sees a rotated person and hand detection fails.
2. **Decode** frames with their real timestamps. This handles variable frame rate and HEVC without re-encoding 66 GB.
3. **Run MediaPipe Holistic** on each frame: 33 body points, 21 per hand, 468 face points, plus which parts were found. Pin the MediaPipe version and record which API you used.
4. **Convert to pixel units.** MediaPipe gives x and y as fractions of width and height. In a portrait 1080×1920 frame one unit of x is not one unit of y, so convert before measuring any distance.
5. **Normalise:** centre on the midpoint between the shoulders and scale by shoulder width (as SignCLIP does). A tall and a short signer then produce comparable numbers.
6. **Resample** to one fixed frame rate using the timestamps. Choose 15 or 30 fps in the pilot.
7. **Store** per video: coordinates, presence mask and quality statistics, in one small file.

| Question | Answer |
| --- | --- |
| What MediaPipe gives us | Joint positions per frame, small files, and a representation with no clothing or background |
| Why it is useful | It creates a training target without annotation, and makes training affordable |
| What is lost | Fingers under blur or occlusion; hand shape when hands touch or overlap; reliable depth (z is estimated); fine facial detail |
| Is face information necessary? | Unknown. Start without it; add a reduced face set (lips, eyes, eyebrows) as an ablation. SignCLIP kept only face-contour points. The full 468 points would outnumber everything else |
| Is body pose necessary? | Yes. Where a hand is relative to the body is part of a sign's meaning, and the shoulders are the reference for normalisation. Drop the legs |
| Do hands need special treatment? | Yes. Represent hand shape relative to the wrist, and wrist position relative to the shoulders. Report hand errors separately. SOKE also treats body, left hand and right hand separately |
| Should RGB video be added? | Later, as an optional ablation only. SignCLIP found pose input beat 3D-CNN video encoders in its setup, and 66 GB of video is costly on free GPUs |

**Handling missing hands:**

- Keep a presence mask per hand per frame. Never treat a missing point as a real position at (0, 0).
- Fill short gaps of a few frames by interpolation, and mark them as filled.
- Leave long gaps missing. The loss and the metrics skip missing points.
- Compute the share of frames with a missing hand for every clip. Exclude or down-weight the worst clips, with the cut-off chosen from the pilot's distribution rather than fixed now.
- Train the matching model with random "hand dropout" (hiding a hand for some frames), so it does not depend on perfect detection.
- Report results for the whole test set and for a good-hand subset, split by portrait and landscape.

**Other estimators.** [O'Brien et al. 2026](https://arxiv.org/abs/2604.24609) compared eight pose estimators for sign language translation. Estimators that often leave out hand keypoints were associated with lower translation scores, and SDPose and Sapiens (BLEU about 11.5) beat MediaPipe Holistic (about 10). Keep MediaPipe, which you have already tested. Consider a second estimator only for a small comparison if portrait hands prove unusable.

## 9. Novelty Options

Use N1 as the backbone of the paper and N2 as its main method candidate; N3 and N4 are supporting analyses. Each one could be a potential contribution if the literature review confirms the gap and the experiments support it.

### N1 — A compositional, leakage-safe benchmark for BdSL sentence production

- **Problem:** templated sentences and duplicate videos make random splits overestimate quality. A model can look good by memorising.
- **Existing approach:** standard sign-production benchmarks (PHOENIX-2014T, How2Sign) use fixed splits. The BdSL text-to-sign papers we reviewed (P1, P5) are judged by human raters only. My searches found no sign-production work that reports unseen-combination splits; that is not proof that none exists.
- **Proposed contribution:** duplicate-aware grouped splits S1–S3 (section 10), baselines B0 and B1, a metric suite, and the gap between seen and unseen combinations.
- **Dataset compatibility:** yes, with the current data.
- **Additional requirement:** none. Signer IDs would add a signer-independent split.
- **Experiment:** run B1, Model 1 and Model 2 on S1, S2 and S3.
- **Evaluation:** R@K, DTW-MJE for body and hands, slot accuracy (section 10).
- **Research significance:** answers "does it translate or memorise?" for a low-resource sign language.
- **Limitations:** a templated everyday domain from an unknown number of signers. Results do not describe BdSL in general.

### N2 — Minimal-pair weak supervision to locate and recombine signs

- **Problem:** there are no sign boundaries, so we cannot tell which frames show "বুধবার".
- **Existing approach:** weakly supervised sign spotting and localisation from subtitles plus dictionaries on large British Sign Language data ([Watch, Read and Lookup](https://arxiv.org/abs/2010.04002); [Read and Attend](https://openaccess.thecvf.com/content/CVPR2021/papers/Varol_Read_and_Attend_Temporal_Localisation_in_Sign_Language_Videos_CVPR_2021_paper.pdf)). Sign segmentation models also exist ([Moryossef et al. 2023](https://arxiv.org/abs/2310.13960)).
- **Proposed contribution:** take sentence pairs that differ in exactly one slot word. Align their keypoint sequences with DTW (dynamic time warping, which stretches time so two recordings at different speeds line up). The region where they disagree is the candidate sign for the changed word. Collect these regions into a small bank of slot signs, then compose unseen combinations by swapping the segment in.
- **Dataset compatibility:** yes. Minimal pairs are verified in the text (one template alone has 157 sentences).
- **Additional requirement:** a manual boundary check on about 50 segments. It needs no BdSL fluency ("where does the motion change?"), but must be reported as a non-expert check.
- **Experiment:** (a) consistency: segments mined for the same word from different pairs should resemble each other more than segments for other words. (b) Composition on S3: swap-in generator versus B1 versus Model 2.
- **Evaluation:** DTW between mined segments; slot accuracy; DTW-MJE on S3.
- **Research significance:** turns the dataset's weakness (templating) into a supervision signal, which suits low-resource sign languages.
- **Limitations:** neighbouring signs blend at the boundaries, so swapped segments need smoothing ([Sign Stitching](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_721/paper.pdf), BMVC 2024, addresses this). Works only for templated slots. Ignores the face.

### N3 — Robustness to missing hand landmarks in phone-recorded signing

- **Problem:** verified. Hands are noisy, and worse in portrait video.
- **Existing approach:** pose-based work normalises the pose and zero-fills missing points (SignCLIP). O'Brien et al. 2026 linked missing hand keypoints to lower translation quality.
- **Proposed contribution:** mask-aware encoders and losses plus hand-dropout augmentation, with results reported by hand-missing rate and orientation.
- **Dataset compatibility:** yes.
- **Additional requirement:** none.
- **Experiment:** compare zero-fill, interpolation and mask-aware training on the same split.
- **Evaluation:** R@K and hand-only DTW per quality bin.
- **Research significance:** practical for real phone-recorded, low-resource data. Likely a supporting analysis rather than a paper on its own.
- **Limitations:** no method can recover a hand the estimator never saw.

### N4 — Expert-free automatic evaluation for BdSL production

- **Problem:** no BdSL expert is available, and existing BdSL papers rely on human raters.
- **Existing approach:** [Jiang et al.](https://aclanthology.org/2025.wmt-1.4/) (WMT 2025) compared keypoint-distance, embedding-based and back-translation metrics, with a human-correlation study for other sign languages. SignCLIP lists sign-production evaluation as future work.
- **Proposed contribution:** a BdSL text↔motion score (from Model 1) plus a slot-recognition check. Test the metrics automatically: does each one rank real motion above minimal-pair-wrong motion, and that above average motion?
- **Dataset compatibility:** yes.
- **Additional requirement:** none for the automatic check. Correlation with human judgement needs BdSL users.
- **Research significance:** a reusable evaluator for future BdSL work.
- **Limitations:** a recogniser agreeing with generated motion does not prove that a Deaf signer understands it. Recognisers can also be fooled by motion that exploits their quirks.

## 10. Evaluation Plan

Build the splits and the metric code before any model. Every split assigns whole groups: a group is all videos that share a normalised sentence or belong to the same duplicate or near-duplicate cluster, with overlapping groups merged.

| Split | How it is built | Research question | Used for |
| --- | --- | --- | --- |
| S1 Sentence-grouped | Random 80/10/10 by group, repeated with 3 seeds | Can the model handle new sentences similar to the training ones? | Main results |
| S2 Template-grouped | Whole templates held out, e.g. every "‹আত্মীয়› ‹দেশ› যাবে" sentence | Can it handle new sentence structures? | Stress test; expected to be hard |
| S3 Unseen combination | Every slot word appears in training, but some combinations are held out (e.g. চাচা + বুধবার + মাংস) | Can it recombine parts it knows? | N1 and N2 |
| S4 Signer-independent | Hold out whole signers | Does it work for new signers? | Only if signer IDs can be recovered; currently unknown |

**Automated leakage checks** (run on every split, every time):

- No normalised sentence appears in two splits.
- No file hash appears in two splits.
- No near-duplicate appears across splits, checked by a perceptual video hash or by keypoint similarity.
- The test split is frozen and used once, for the final numbers.

**Level 1 — Retrieval (Model 1).**

- **Recall@1, @5, @10:** the share of test sentences whose correct video is ranked 1st, in the top 5, or in the top 10. Higher is better.
- **Median rank:** the middle position of the correct video over all test sentences. Lower is better.
- Always report the number of candidate videos and the chance level, in both directions (text→motion and motion→text).

**Level 2 — Motion (Model 2 versus B0 and B1).**

- **DTW-MJE** (DTW mean joint error): align predicted and real sequences in time, then average the distance between matching joints. Report body and hands separately, over detected points only. Lower is better.
- **Length error:** predicted versus real duration.
- **Smoothness:** acceleration and jerk (change in acceleration) compared with real motion. Closer to real is better; lower is *not* automatically better, since frozen motion is perfectly smooth.
- **Hand motion energy** compared with real motion. Too little means the model is averaging.
- Use the open-source pose-evaluation toolkit from [Jiang et al.](https://aclanthology.org/2025.wmt-1.4/) for standard implementations.

**Level 3 — Automatic proxies for meaning.**

- **Matching score:** Model 1, trained on the training split only, checks whether generated motion retrieves its own sentence.
- **Slot accuracy:** a small classifier trained on real training motion predicts the slot value, e.g. which weekday. Apply it to generated motion.
- **Limitation:** a recogniser agreeing with generated motion does not prove that a human BdSL user considers the signing correct.

**Level 4 — Human evaluation.** No BdSL users are available now, so every quality claim must be stated as an automatic proxy. If two or three users become available later, run two tests. The first is forced choice: watch the avatar and pick the sentence from four minimal-pair options. The second is a 1–4 naturalness rating, the scale IsharaKotha used.

## 11. Full Initial Pipeline

The pipeline has an offline half that turns data into trained models, and an online half that turns a new sentence into avatar motion. Labels: \[existing\], \[pretrained\], \[trained on our data\], \[rule-based\], \[deterministic\], \[needs research\].

```text
OFFLINE: DATA -> TRAINING

+--------------------------+     +--------------------------+
| FinalSheet2.xlsx         |     | 5,010 MP4 videos         |
| sentence + Index         |     | mixed codec / VFR / size |
| [existing]               |     | [existing]               |
+------------+-------------+     +------------+-------------+
             |                                |
             v                                v
+--------------------------+     +--------------------------+
| Text normaliser          |     | Probe + decode with      |
| Unicode, ZWNJ, spelling  |     | timestamps, fix rotation |
| [rule-based]             |     | [deterministic]          |
+------------+-------------+     +------------+-------------+
             |                                |
             v                                v
+--------------------------+     +--------------------------+
| Manifest + dedup groups  |     | MediaPipe Holistic       |
| hash, sentence, template |     | body + hands (+ face)    |
| [deterministic]          |     | [pretrained]             |
+------------+-------------+     +------------+-------------+
             |                                |
             v                                v
+--------------------------+     +--------------------------+
| Grouped splits S1-S3     |     | Keypoint QC + normalise  |
| + leakage checker        |     | pixel units, shoulders,  |
| [rule-based]             |     | masks, resample          |
+------------+-------------+     | [deterministic]          |
             |                   +------------+-------------+
             +---------------+----------------+
                             v
              +------------------------------+
              | Training pairs:              |
              | (sentence, keypoints, mask)  |
              +-------+--------------+-------+
                      |              |
                      v              v
        +----------------------+  +----------------------+
        | Model 1: text<->     |  | Model 2: text ->     |
        | motion matching      |  | motion generator     |
        | [trained on our data]|  | [trained on our data]|
        +----------------------+  +----------------------+

ONLINE: NEW SENTENCE -> AVATAR

        +----------------------+
        | Bangla text          |
        +----------+-----------+
                   v
        +----------------------+
        | Text normaliser      |  [rule-based]
        +----------+-----------+
                   v
        +----------------------+
        | Text encoder         |  [trained; BanglaBERT optional]
        +----------+-----------+
                   v
        +----------------------+     +--------------------------+
        | Model 2 generator    |     | Baseline B1: nearest     |
        | [trained]            |     | training sentence -> its |
        +----------+-----------+     | real motion [rule-based] |
                   v                 +--------------------------+
        +----------------------+
        | Keypoint sequence    |  intermediate representation
        +----------+-----------+
                   v
        +----------------------+
        | Motion processing    |  trim, smooth, bone lengths
        +----------+-----------+  [deterministic]
                   v
        +----------------------+
        | Retargeting          |  points -> joint rotations
        +----------+-----------+  [deterministic; fingers need research]
                   v
        +----------------------+
        | 3D avatar renderer   |  skeleton player first, avatar later
        +----------+-----------+  [existing tools, not trained]
                   v
        +----------------------+
        | BdSL output video    |
        +----------------------+

EVALUATION (test split, used once)
  Model 1              -> Recall@1/5/10, median rank
  Model 2, B0, B1      -> DTW-MJE (body, hands), length error, jerk
  Proxies              -> Model 1 score, slot accuracy [trained on train split]
  Avatar               -> round trip: render -> MediaPipe -> compare
```

## 12. Diagram Explanation

Each block has one job. Only the two models learn anything; every other block is fixed code or an existing tool.

| Block | What it does, in simple words | Why we need it |
| --- | --- | --- |
| FinalSheet2.xlsx | Links each sentence to its video through Index | The only source of labels |
| 5,010 MP4 videos | The raw signing | The only source of motion |
| Text normaliser | Makes "মংগলবার" and "মঙ্গলবার" identical; removes hidden characters | Otherwise the model treats one word as two |
| Probe + decode | Reads each video correctly, whatever its codec, frame rate or rotation | A sideways or badly timed video gives wrong keypoints |
| MediaPipe Holistic | Finds body, hand and face points in each frame | Turns video into numbers a model can learn from |
| Manifest + dedup groups | One table listing every video, its hash, sentence and template | The basis for leak-free splits and for reporting |
| Grouped splits + leakage checker | Divides groups into train, validation and test, then proves nothing leaked | Without it, scores measure memory |
| Keypoint QC + normalise | Converts to pixel units, centres and scales, masks missing points, fixes the frame rate | So the model learns signs, not body size, camera shape or detection errors |
| Training pairs | (sentence, keypoints, mask) triples | What both models are trained on |
| Model 1: matching | Scores how well a sentence and a motion belong together | Feasibility test, retrieval results, and automatic judge |
| Model 2: generator | Produces a keypoint sequence for a sentence | The part that can sign sentences never recorded |
| Baseline B1 | Replays the motion of the most similar training sentence | The bar the generator must clear |
| Keypoint sequence | Moving dots over time | Can be scored before any avatar exists |
| Motion processing | Trims idle frames, removes jitter, keeps bone lengths fixed | Clean input for the avatar |
| Retargeting | Turns dot positions into joint angles for the avatar's bones | Avatars move by rotating bones, not by placing dots |
| 3D avatar renderer | Plays the joint angles on a character and records video | The visible output |
| Evaluation | Scores retrieval, motion, meaning proxies and avatar fidelity on the test split | Tells us whether anything works |

### How the output reaches the 3D avatar

- **What the ML model outputs:** per frame, the positions of upper-body and hand points in MediaPipe's layout.
- **What the avatar needs:** a rigged character (a 3D mesh with a skeleton of bones) and, per frame, a rotation for each bone, fingers included.
- **The conversion layer (retargeting):** compute each bone's direction from pairs of points (shoulder → elbow, wrist → finger joints) and turn directions into rotations. This is geometry, not learning.
- **Is the avatar trained?** No. The avatar and the conversion layer are deterministic.
- **Recommended first avatar (Proposed):** a plain skeleton player (stick figure). It is enough for every research result.
- **Recommended 3D avatar (Proposed; verify before relying on it):** a VRM humanoid in the browser with Three.js and three-vrm. [Kalidokit](https://github.com/yeemachine/kalidokit) is an existing open-source solver that turns MediaPipe face, pose and finger landmarks into rig rotations. It matches our output format, but it is an older hobby library, so test it before depending on it.
- **Alternative:** Blender, scripted in Python, with a rigged character and bone constraints. It is better for high-quality offline renders, but more retargeting work.
- **Not recommended now:** Unity. It adds a game engine and C# without solving a research problem.
- **Test the avatar without any model first:** feed it keypoints extracted from real videos. If real motion looks wrong on the avatar, the problem is retargeting, not the ML model. Then re-run MediaPipe on the rendered avatar video and compare with the input (the round-trip check).

## 13. Initial Code Architecture

One Python package with a module per pipeline block. Raw data is read-only, and every result is regenerated from configs. No code is written in this guide.

```text
bdsl_text2sign/
├── configs/            paths, landmark set, split seeds, model settings (YAML)
├── data/
│   ├── raw/            videos + Excel files, read-only, never edited
│   ├── manifest/       manifest.csv, duplicate groups
│   ├── splits/         S1-S3 group lists (JSON)
│   └── keypoints/      one file per unique video + QC table
├── src/
│   ├── dataset_prep/   manifest, hashing, duplicate grouping
│   ├── text/           normaliser, variant map, templates, vocabulary
│   ├── video_io/       probing, timestamped decoding, rotation
│   ├── keypoints/      MediaPipe extraction, normalisation, masks, resampling
│   ├── splits/         split builders + leakage checker
│   ├── viz/            skeleton player, overlays, QC plots
│   ├── baselines/      B0 average motion, B1 nearest sentence
│   ├── models/         matching model, generator, slot recogniser
│   ├── training/       training loops, checkpoints, logging
│   ├── evaluation/     Recall@K, DTW-MJE, jerk, slot accuracy, reports
│   ├── inference/      text -> keypoints -> file for the avatar
│   └── avatar/         retargeting + renderer bridge (Phase 8 only)
├── notebooks/          exploration; thin Colab/Kaggle launchers
├── tests/              leakage test, normaliser tests, shape tests
├── outputs/            checkpoints, predictions, figures, metric tables
└── docs/               decisions log, experiment log, dataset card
```

| Module | Purpose (and why we need it) | Code that belongs there | Input → output | Tools | Runs on |
| --- | --- | --- | --- | --- | --- |
| dataset\_prep | One trusted table of the dataset; everything else reads it | Excel reading, file hashing, ffprobe calls, duplicate grouping | Excel + videos → manifest.csv | pandas, openpyxl, hashlib, ffprobe | Local |
| text | One consistent spelling for every sentence | Unicode normalisation, variant map, template extraction, vocabulary building | Raw sentence → normalised sentence, template ID, tokens | Python, csebuetnlp normalizer | Local |
| video\_io | Read mixed-codec, variable-frame-rate, rotated videos correctly | Probing, decoding with timestamps, rotation handling | Video path → frames + timestamps | FFmpeg / PyAV, OpenCV | Local |
| keypoints | Turn video into training targets | MediaPipe calls, pixel conversion, shoulder normalisation, masks, gap filling, resampling | Frames → keypoint file + QC statistics | MediaPipe, NumPy | Local CPU |
| splits | Leak-free experiments | S1–S3 builders, leakage assertions | Manifest → split JSON files | Python, scikit-learn helpers | Local |
| viz | See what the numbers mean before trusting them | Skeleton animation, overlays on video, QC charts | Keypoints → MP4 / PNG | Matplotlib, OpenCV | Local |
| baselines | The bar every model must clear | B0 average motion, B1 nearest sentence | Text → keypoint sequence | scikit-learn (TF-IDF), NumPy | Local |
| models | The learned parts | Network definitions for matching model, generator, slot recogniser | Tensors → embeddings / keypoints / slot labels | PyTorch | Cloud GPU |
| training | Repeatable training runs | Data loaders, loss functions, optimiser, checkpointing, logging | Split + keypoints → checkpoints | PyTorch | Colab / Kaggle |
| evaluation | Decide whether anything works | Metrics, per-split tables, significance across seeds | Predictions + ground truth → metric tables | NumPy, DTW library or the Jiang et al. toolkit | Local or cloud |
| inference | Run the finished pipeline on a new sentence | Loading checkpoints, text → keypoints → export file | Sentence → keypoint file | PyTorch | Local |
| avatar | Show the result as a 3D character | Retargeting, export to the renderer, round-trip check | Keypoint file → bone rotations → video | Three.js + three-vrm (+ Kalidokit), or Blender | Local |
| tests | Catch silent data bugs | Leakage test, normaliser cases from the known bad rows, tensor-shape checks | — | pytest | Local |
| docs | Explicit decision and experiment records | Decisions log, experiment log, dataset card (your repo's agent\_docs templates fit here) | — | Markdown | — |

## 14. Frameworks and Tools

Python with PyTorch and MediaPipe covers the whole research pipeline. The avatar tools are needed only in Phase 8.

| Tool | Why we need it | Part of the system that uses it | When |
| --- | --- | --- | --- |
| Python | One language for data, ML and scripting | Everything | Now |
| pandas + openpyxl | Read the Excel files; hold the manifest | dataset\_prep, splits | Phase 1 |
| FFmpeg / ffprobe (or PyAV) | Read codec, rotation and real frame timestamps; decode HEVC and variable frame rate reliably | video\_io | Phase 1–2 |
| OpenCV | Frame handling and drawing overlays | video\_io, viz | Phase 2–3 |
| MediaPipe | Body, hand and face landmarks (already tested) | keypoints | Phase 2 |
| NumPy | Store and transform keypoint arrays | keypoints, baselines, evaluation | Phase 2 onward |
| csebuetnlp normalizer | Standard Unicode normalisation for Bangla | text | Phase 1 |
| scikit-learn | TF-IDF for baseline B1; grouped-split helpers | baselines, splits | Phase 1, 4 |
| Matplotlib | Skeleton playback and QC plots | viz | Phase 3 |
| DTW library, or the pose-evaluation toolkit (Jiang et al.) | Time-aligned motion comparison | evaluation, N2 | Phase 4 |
| PyTorch | Build and train Model 1, Model 2 and the slot recogniser | models, training | Phase 5 onward |
| Google Colab / Kaggle | Free GPUs for training; keypoints are small enough to upload | training | Phase 5 onward |
| Hugging Face Transformers | Only to load a pretrained BanglaBERT for the text-encoder ablation | models (optional) | Phase 9 |
| Three.js + three-vrm (+ Kalidokit), **or** Blender | Show motion on a 3D character; pick one | avatar | Phase 8 |

Not selected, and why: **Unity** (a game engine with no research payoff here), **TensorFlow** (one framework is enough), **SMPL-X body-model tools** (heavier 3D fitting before we know keypoints suffice), **large language models or diffusion generators** (too heavy for free GPUs and our data size), **JASigning** (only if you later add the optional SiGML comparison).

## 15. Build Order

Nine phases, with one change to your suggested order: the evaluation code is built in Phase 4, together with the baselines and before any neural model. That way no model result exists without a trustworthy way to score it.

| Phase | What we build | Why | Expected output | What to verify | Not yet |
| --- | --- | --- | --- | --- | --- |
| 1. Data and splits | Manifest, text normaliser, duplicate groups, S1–S3, leakage tests | Every later number depends on it | manifest.csv, split files, dataset card | Every row maps to a file; counts match profiling (3,456 / 3,381); leakage tests pass | Keypoints, models |
| 2. Keypoint extraction | Probing, decoding, MediaPipe, normalisation, masks; pilot first, then all unique videos | Creates the training targets | One keypoint file per video + QC table | Rotation handled; timestamps increase; hand presence by orientation | Training |
| 3. Visualisation and QC | Skeleton player, overlays, idle-frame trimming, exclusion rules | Numbers can look fine while being wrong | QC report, cleaned subset list | A person watches 30–50 clips; minimal-pair differences are visible | Models |
| 4. Evaluation + baselines | Metric code, B0, B1, chance-level retrieval | Scoring must exist before models | Baseline table on validation splits | Metrics behave sensibly: real vs itself = 0, real vs B0 is large | Neural models |
| 5. Model 1 (matching) | Contrastive text↔motion model | Feasibility test and future judge | Recall@K on validation | Clearly above chance; hands-only vs body+hands | Generator tuning |
| 6. Model 2 (generator) | Non-autoregressive text→keypoint model | The production component | DTW-MJE vs B0 and B1 | Beats B0; hands still move (no averaging) | Motion tokens, diffusion |
| 7. Novelty experiment | S3 analysis; minimal-pair segment mining; swap-in composition | Where the paper's contribution lives | Segment bank; S3 comparison | Segment consistency; 50 manual boundary checks | Avatar polish |
| 8. Avatar integration | Skeleton → 3D avatar; round trip on real keypoints first, then model output | Visible output, after the research is sound | Rendered videos | Fingers look right on real motion; round-trip error | Web UI, real time |
| 9. Ablations + final test | Body / hands / face; mask strategies; scratch vs BanglaBERT encoder; one final test run | Explains which choices matter | Final tables for the paper | Several seeds; test split used exactly once | New features |

The ablation in Phase 9 answers one question: which information does BdSL production in this dataset actually need? Compare model A (hands only), model B (body + hands) and model C (body + hands + face subset) on the same split.

## 16. First Milestone

**M1: a leak-free data foundation plus a keypoint pilot on about 300 videos, ending in a written go/no-go decision.** It runs on local CPUs, needs no GPU and no model, and tests the two assumptions everything else rests on: clean splits, and keypoints that carry the signing.

Deliverables:

- [ ] manifest.csv covering all 5,010 rows: Index, file path, SHA-256 hash, codec, resolution, rotation, duration, frame-timing statistics, raw text, normalised text, template ID, group ID
- [ ] Text normaliser and variant map, with tests built from the known bad rows (Latin script, zero-width characters, spelling variants)
- [ ] Splits S1–S3 and an automated leakage test that passes
- [ ] MediaPipe keypoints for about 300 unique videos, stratified by portrait/landscape, resolution and codec, including at least 10 minimal-pair groups
- [ ] QC table: share of frames with a missing hand, jitter, and both broken down by orientation
- [ ] Skeleton playback for 30 clips, watched by a team member, with notes
- [ ] Feasibility check: DTW distance between minimal pairs versus unrelated pairs. Does the difference sit in the changed word's region?
- [ ] A go/no-go entry in the decisions log

Exit criteria, judged by the team rather than fixed numbers:

- The leakage test passes.
- Keypoints look usable for most pilot clips.
- In minimal pairs, the hands visibly differ around the changed word.

If hands are unusable in a large share of portrait clips, fix extraction before Phase 4, for example by testing a second pose estimator.

## 17. What We Should NOT Build Yet

Each of these either depends on results we do not have, or would consume weeks without answering a research question.

- **The 3D avatar, a web app or any user interface.** They wait until Phase 8, after the keypoints and the generator are validated.
- **Unity or real-time signing.** Not needed for a research result.
- **A text→gloss model or a gloss annotation tool.** There are no glosses and no expert to write them.
- **Motion-token (VQ-VAE), diffusion or LLM-based generators.** They are upgrades if the simple generator averages out, not starting points.
- **RGB video models.** An optional late ablation only.
- **SMPL-X body fitting.** Heavier 3D fitting before we know simpler keypoints are enough.
- **Full-dataset keypoint extraction before the 300-video pilot passes.** Otherwise a rotation or timestamp bug has to be fixed across 66 GB.
- **Speech input or audio features.** Audio is verified to be mostly noise.
- **JASigning or SiGML integration.** Optional outside comparison, later.
- **Large hyperparameter searches.** Pointless until the evaluation harness and baselines exist.

## 18. Open Research Questions

Eight questions remain. The first two need answers before anything is published; the rest are settled by planned experiments or small checks.

| # | Question | Why it matters | How it gets answered |
| --- | --- | --- | --- |
| 1 | Where did the videos come from, and is there consent and a licence for research use and publication? | Faces are visible; any paper or data release depends on this | Ask whoever collected the videos |
| 2 | How many signers are there, and can signer IDs be recovered? | Decides whether S4 and any "works for new signers" claim is possible | Label a sample by hand, then decide |
| 3 | Do the videos follow the BSTI-standard signs used by papers P1 and P5? | Decides whether a SiGML comparison is meaningful | Compare a handful of common words against the P5 SiGML files |
| 4 | Is the face needed (mouthing, facial grammar)? | Affects the landmark set and the model size | Phase 9 ablation |
| 5 | Are MediaPipe hands good enough on portrait clips? | Hands carry most of a sign's meaning | M1 pilot QC |
| 6 | Can two or three BdSL users review a small sample later? | Without them, every quality claim stays an automatic proxy | Team outreach |
| 7 | What denominator does "about 61% byte-identical duplicates" use? | Needed to report the dataset correctly | Recheck the profiling script |
| 8 | Do the few sentences with several distinct videos (about 1.5%) come from different signers? | A small, free measure of natural variation between recordings | Watch them during Phase 3 |

## Sources

Dataset figures come from your profiling summary and my inspection of the three Excel files. The paper references P1–P6 come from your paper\_analysis folder.

- Saunders, Camgöz, Bowden — [Progressive Transformers for End-to-End Sign Language Production](https://github.com/BenSaunders27/ProgressiveTransformersSLP), ECCV 2020
- Saunders, Camgöz, Bowden — [Adversarial Training for Multi-Channel Sign Language Production](https://arxiv.org/abs/2008.12405), BMVC 2020
- Jiang, Sant, Moryossef, Müller, Sennrich, Ebling — [SignCLIP: Connecting Text and Sign Language by Contrastive Learning](https://aclanthology.org/2024.emnlp-main.518/), EMNLP 2024
- Jiang et al. — [Meaningful Pose-Based Sign Language Evaluation](https://aclanthology.org/2025.wmt-1.4/), WMT 2025
- Cheng et al. — [CiCo: Domain-Aware Sign Language Retrieval via Cross-Lingual Contrastive Learning](https://arxiv.org/abs/2303.12793), CVPR 2023
- Momeni et al. — [Watch, Read and Lookup: Learning to Spot Signs from Multiple Supervisors](https://arxiv.org/abs/2010.04002), ACCV 2020
- Varol et al. — [Read and Attend: Temporal Localisation in Sign Language Videos](https://openaccess.thecvf.com/content/CVPR2021/papers/Varol_Read_and_Attend_Temporal_Localisation_in_Sign_Language_Videos_CVPR_2021_paper.pdf), CVPR 2021
- Moryossef et al. — [Linguistically Motivated Sign Language Segmentation](https://arxiv.org/abs/2310.13960), Findings of EMNLP 2023
- Yin et al. — [T2S-GPT](https://arxiv.org/abs/2406.07119), ACL 2024
- Zuo et al. — [Signs as Tokens (SOKE)](https://openaccess.thecvf.com/content/ICCV2025/papers/Zuo_Signs_as_Tokens_A_Retrieval-Enhanced_Multilingual_Sign_Language_Generator_ICCV_2025_paper.pdf), ICCV 2025
- Walsh, Saunders, Bowden — [Sign Stitching](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_721/paper.pdf), BMVC 2024
- O'Brien, Sant, Müller, Ebling — [Evaluation of Pose Estimation Systems for Sign Language Translation](https://arxiv.org/abs/2604.24609), arXiv 2026
- [SignBD-Word: Video-Based Bangla Word-Level Sign Language and Pose Translation](https://ieeexplore.ieee.org/document/10306914/), IEEE, 2023
- Saha et al. — [Introducing A Bangla Sentence – Gloss Pair Dataset for Bangla Sign Language Translation and Research (Bangla-SGP)](https://arxiv.org/abs/2511.08507), LREC 2026
- Islam et al. — [IsharaKotha](https://arxiv.org/abs/2511.16896), arXiv 2025 (paper P1)
- Karim et al. — [HamNoSys-to-SiGML BdSL animation](https://link.springer.com/article/10.1007/s10462-025-11370-z), Artificial Intelligence Review 2026 (paper P5)
- [Kalidokit](https://github.com/yeemachine/kalidokit): MediaPipe landmarks → rig rotations
- [csebuetnlp normalizer](https://github.com/csebuetnlp/normalizer) and [BanglaBERT](https://huggingface.co/csebuetnlp/banglabert)
