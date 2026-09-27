# Bangla Text → BdSL on a 3D Avatar: A Beginner's Research Guide and Initial Project Design (CSE498R, NSU)

> **Status: PROPOSAL — not a confirmed project decision.** Partly superseded by `02_BdSL_Text-to-Sign_Research_and_Build_Guide.md`, which corrects this guide's assumption that repeated spreadsheet rows are extra takes. Confirmed decisions are recorded in the project `README.md`.

Your dataset most likely supports a learned **Bangla text → pose/motion** system, trained on keypoints you extract from your own sentence videos and then played on a 3D avatar. It cannot support a supervised **text → gloss** model, because it contains no glosses, no word-to-sign alignment and no sign boundaries. You also can't commit to any design until you've inspected the videos (framing, fps, signer count, whether the takes come from different signers).

**TL;DR**
- **What you have (verified):** 3,395 unique, heavily templated everyday Bangla sentences (mean 4.26 words, 1,429-word vocabulary). They are linked by `Index` to sentence-level videos that you haven't inspected yet (about 5,010 by your own account). There are no glosses, alignments, poses, signer IDs or splits. Every published BdSL text-to-sign system in your paper set is a lookup pipeline (word → hand-written HamNoSys/SiGML → JASigning avatar). None of them learns translation or motion from data.
- **Most realistic first direction (proposal):** (1) extract 2D/3D whole-body keypoints from every video with a pretrained pose estimator; (2) train a small text → pose model on template-aware, leakage-safe splits; (3) compare it against a lookup baseline and a retrieval baseline; (4) evaluate automatically with pose distance (DTW) and back-translation through a BdSL recognizer trained on the same data; (5) retarget the best poses to an avatar. The avatar is a display step, not the research contribution.
- **Plausible research contributions (not yet proven novel):** compositional (unseen slot-combination) evaluation for BdSL production; weakly supervised discovery of sign segments that exploits the one-slot-difference template structure; a retrieval-plus-transition hybrid versus a fully generative model; and expert-free automatic evaluation. Each needs the experiments listed in Section 8 before anyone can call it a contribution.

---

## 1. What We Actually Have

### 1.1 Dataset — Verified (inspected on 2026-09-26)

| Item | What was found |
|---|---|
| Files | Three Excel files only: `FinalSheet.xlsx`, `FinalSheet2.xlsx`, `FinalSheet_DuplicateGroups.xlsx`. **No videos in the folder.** |
| `FinalSheet.xlsx` | Columns `Names` (Bangla sentence) and `Index` (integer). 3,491 rows. Index runs 0–332 and then 784–3941; values 333–783 (451 of them) are missing. No duplicate indexes. |
| Unique sentences | 3,395 after trimming whitespace; 3,379 after also normalising internal spaces and final punctuation. 82 duplicate groups covering 178 rows. |
| `FinalSheet2.xlsx` | 5,010 rows. The first 3,491 are identical to FinalSheet. The extra 1,519 rows (Index 3942–5460) all repeat sentences already in FinalSheet. |
| Sentence length | 1–13 words, mean 4.26, median 4. Most are 3–5 words (648 + 1,404 + 932). |
| Vocabulary | 1,429 unique whitespace tokens; 640 appear only once. Top words: আমার (1,648), আমি (842), যাবে (477), যাব (327), ভাই (315)… |
| Structure | Heavily templated slot-filling. Weekday names appear in 509 unique sentences, month names in 340. A crude slot replacement collapses the 3,395 sentences into ≤2,088 templates. The top template "আমার ‹KIN› ‹DAY› ‹FOOD› খায়" covers 157 sentences. |
| Quality issues | Spelling variants (মংগলবার/মঙ্গলবার, মুরগী/মুরগি, যাব/যাবো, ধ্যানবাদ/ধন্যবাদ); typos ("ভার" for ভাত); grammatical slips ("তুমি বৃহস্পতিবার দুধ খাবো"); 9 rows with Latin script, including garbled Banglish; 7 rows with zero-width-non-joiner artefacts; 1,302 rows with stray whitespace; almost no final punctuation (4 "।", no "?"). |
| **Absent** | Gloss annotations, BdSL word order, word/sign alignment, sign boundaries, timestamps, frame labels, pose/keypoints, signer IDs, video metadata, sign vocabulary, train/validation/test split. |

### 1.2 Stated by the team (not yet verified)

- Sign videos exist and will be provided.
- `Index` is the video ID.
- The 1,519 repeated sentences are extra takes (another signer or session). That would make roughly **5,010 sentence-level videos for 3,395 unique sentences**, with about 1,478 sentences having two or more takes.
- There is no (or unknown) access to a BdSL signer or interpreter.
- Compute is a free Colab T4 plus a local machine with 24 GB RAM and an AMD RX 570, which is impractical for training.

### 1.3 Unknown — pending inspection of the videos

Format, count, duration, resolution, fps, number of signers, whether takes are by different signers, framing (full body vs upper body; whether hands and face stay in frame), background, naming scheme, and whether each video contains exactly one sentence with lead-in/lead-out pauses. **I don't know based on the available evidence** whether videos exist for the 451 missing Index values (333–783).

### 1.4 Papers — Verified from your analyses, plus literature checks

| # | Paper | What it does | Key limitation |
|---|---|---|---|
| P1 | **IsharaKotha** (Islam, Dewan, Islam, Ataullha, Rahman; arXiv:2511.16896, 2025) | A HamNoSys corpus for 3,823 BdSL words, built from the nearly 4,000 signs standardised by the Bangladesh Standards and Testing Institution (BSTI) → SiGML → JASigning avatar. A BiLSTM lemmatizer (79.22% accuracy) maps sentence words to root words before dictionary lookup. | No Bangla→BdSL reordering, no OOV handling, no learned motion, human-only evaluation (average 3.14/4.00 from two professional interpreters and one hearing-impaired signer, per the arXiv version). |
| P2 | Smart Tutor Avatar (Apu Islam et al., BRAC) | YOLOv8-nano recognition on BDSL-49 letters; the "avatar" is static images. | Not text-to-sign. |
| P3 | Multilingual Speech-to-Sign Translator (Chandana & Sandarsh Gowda, IJARCCE 2026) | Flask demo with unnamed APIs. | No dataset or metrics. Your two analyses disagree on which sign language it targets. |
| P4 | Real-time SLT with 3D Avatar (Mehataj et al., Procedia CS 283, 2026) | English → ISL through word → pre-made Blender animation lookup; Rokoko mocap. | 50 signs; no evaluation of generation quality. |
| P5 | HamNoSys-to-SiGML BdSL animation (Karim et al., Artificial Intelligence Review 59:25, 2026) | Rule-based parser → SiGML lookup, with fingerspelling fallback for OOV words and unlisted "grammar rewriting rules" → JASigning. 97.5% text / 94.75% voice accuracy judged by one expert. | Small public set (90–94 classes); no non-manual signals; compound-letter failures. |
| P6 | Next-Gen AI Speech-to-Sign (Kulkarni et al., JISEM 2025) | English → ISL; BERT reordering; LSTM gesture sequencing; Three.js avatar. | Only ASR accuracy reported; no evaluation of sign quality. |

**Citation check for IsharaKotha (resolving your inconsistency).** Three separate records exist:
- An arXiv version (2511.16896, Nov 2025) by MD. Ashikul Islam and four co-authors.\[1\] Its evaluation reports an average score of 3.14 out of 4.00 from two professional interpreters and one hearing-impaired signer.
- An earlier SSRN preprint (abstract 4696066) credited to M. Shahidur Rahman, MD. Ashikul Islam, Prato Dewan and Md Fuadul Islam. It reports that a professional interpreter gave the animations 3.32 out of 4.00.\[2\]
- A dataset record on Mendeley Data ("IsharaKotha: Avatar-based Bangla Sign Language Corpus", v2).\[3\]

P5 cites IsharaKotha as "Rahman et al. 2023" with the 3.32/4.00 figure, which matches the SSRN preprint.\[4\] **I don't know based on the available evidence** whether a Heliyon journal version exists; I found none. There is also a second discrepancy: the Mendeley record says the corpus covers **31** semantic categories, while your analysis says **36**.\[3\] Recheck this against the arXiv PDF.

**Shared gap across P1–P6 (from your comparison tables, confirmed by reading the literature).** Every BdSL text-to-sign system is lookup-based. None has a learned translation or motion model, automatic evaluation, or facial grammar, and none documents its BdSL word-order rules.

---

## 2. The Problem in Simple Words

**Bangla text → BdSL translation** takes a written Bangla sentence and produces the same meaning in Bangladeshi Sign Language, performed here by a 3D character (an *avatar*).

It is not a word-by-word substitution, for three reasons:

1. **BdSL is its own language.** It has its own vocabulary and grammar. Sign languages also use the face, head and body (*non-manual markers*) to carry grammar such as questions and negation.\[5\]\[6\]
2. **Bangla word endings often disappear.** In glosses written by a professional BTV signer (Bangla-SGP dataset, Saha et al., LREC 2026), "আমি ভাত খাবো" becomes "আমি ভাত খাওয়া হবে". The verb turns into a root form and the future tense becomes a separate sign.\[5\]
3. **Signs flow together.** Hands move from the end of one sign into the start of the next (*co-articulation*), so gluing isolated clips together looks robotic.\[7\]

**Tiny example (illustrative, not verified BdSL):** "আমার চাচা বুধবার মাংস খায়". A word-by-word system would need a sign for each of the five words, including the inflected form খায়. Real signing may drop, reorder or merge some of these, and only a BdSL signer can confirm how. That is exactly the knowledge your dataset doesn't contain in written form. It exists only implicitly, inside the videos.

**What little is documented about BdSL grammar (literature).**
- Teachers and signers interviewed for the *Breaking the Silence* text-to-gloss paper (Abdullah et al., arXiv:2504.02293) said "There is no set standard for BdSL" and that "BdSL does not have a strict grammatical structure, rather rule of thumbs", such as using the infinitive verb in place of inflected forms.\[8\]
- The Bangla-SGP examples keep SOV order, reduce verbs to a root/verbal-noun form (খাওয়া), and mark tense with separate words (ছিলো past, হবে future, আছে progressive). These come from a single signer, and the authors warn of signer bias.\[5\]
- The earliest version of *Breaking the Silence* used rules such as "move negation to the end". Those rules were adapted from German Sign Language work, so treat them as heuristics, not BdSL facts.\[9\]
- I found no peer-reviewed description of how BdSL marks questions, of head-shake negation scope, or of the functions of specific facial markers. **Little is documented.**

---

## 3. End-to-End Example

Running sentence (from your dataset): **"আমার চাচা বুধবার মাংস খায়"**

| Step | What happens | Type |
|---|---|---|
| 1. Input | A user types the sentence (it may contain typos, "মংগলবার", Banglish). | — |
| 2. Normalisation | Fix Unicode, remove zero-width characters, trim spaces, map spelling variants (মংগলবার→মঙ্গলবার). Example tool: the csebuetnlp normalizer used by BanglaBERT/BanglaT5. | Deterministic / rule-based |
| 3. Text encoding | Turn the words into numbers a model can read (tokenise; optionally use a pretrained Bangla encoder such as BanglaT5). | Pretrained, reused |
| 4. Translation to a sign representation | The key learned step. The model outputs either (a) a sequence of body poses frame by frame, or (b) a list of sign units/tokens that are later turned into poses. | **Trained on your data** |
| 5. Motion clean-up | Smooth jitter, fix bone lengths, fill in missing hand points. | Deterministic |
| 6. Retargeting | Convert keypoints (dots in space) into joint rotations for a rigged 3D character (e.g., in Blender or Three.js). | Deterministic + tooling (needs research for fingers) |
| 7. Output | The avatar performs the sentence as an animation or video. | — |

**What the model "sees" during training for this sentence:** the input is the text "আমার চাচা বুধবার মাংস খায়". The target is the sequence of keypoints extracted from video #(its Index). Nothing tells the model which frames belong to "বুধবার". It has to discover that on its own.

---

## 4. Possible Technical Approaches

Terms used below:
- **Gloss:** a written label for each sign, e.g., "চাচা বুধবার মাংস খাওয়া".
- **Pose/keypoints:** (x, y, z) positions of body, hand and face points in each frame.
- **SMPL-X:** a standard 3D body model with detailed hands and face.

| Approach | What it means | What is learned | Data required | Strengths | Limitations | Supported by your data now? |
|---|---|---|---|---|---|---|
| **A. Notation lookup (HamNoSys/SiGML → JASigning)** | Each word maps to a hand-written sign description that a player animates | Nothing, or just a lemmatizer | A sign dictionary written by experts | No training; clean hands; used by P1 and P5 | Needs a dictionary; robotic transitions; no grammar; fails on OOV words | **Partly.** Only if you can obtain the IsharaKotha/P5 SiGML files (licence unconfirmed). Useful as a **baseline**. |
| **B. Text → gloss (then gloss → sign)** | Translate Bangla into a gloss sequence first | Seq2seq text → gloss | Sentence–gloss pairs (expert-annotated) | Interpretable; published Bangla baselines exist (*Breaking the Silence*; Bangla-SGP) |\[5\]\[8\] **Your data has no glosses.** External gloss sets use different signers and conventions. | **No** as supervised training on your data. External data could be tried, but it wouldn't align with your videos. |
| **C. Gloss → pose** (e.g., Progressive Transformers' stacked variant, Saunders et al., ECCV 2020) | Generate poses from glosses | Gloss → pose sequence | Gloss + pose pairs | Easier than raw text | Needs glosses | **No.** |\[10\]
| **D. Gloss-free text → pose/motion** (Progressive Transformers end-to-end; T2S-GPT, Yin et al., ACL 2024; SOKE, Zuo et al., ICCV 2025; SignAvatars benchmark, Yu et al., ECCV 2024) | Generate a pose sequence directly from the sentence | Text → continuous poses, or text → discrete motion tokens (VQ-VAE) → poses | Sentence + pose pairs; poses can be *estimated* from video | Uses exactly the (sentence, video) pairs you have | The target is noisy estimated pose; models "regress to the mean" (blurry, under-articulated hands) with little data | **Yes, conditionally.** Depends on video quality. |
| **E. Retrieval + stitching** (Sign Stitching, Walsh, Saunders & Bowden, BMVC 2024; SOKE's dictionary retrieval) | Retrieve stored sign clips and blend the transitions | Optionally the transitions, timing and ordering | Isolated signs or **sign boundaries** inside sentences | Real, crisp motion | Needs segmentation you don't have (yet) | **Not yet.** Possible after segmentation (Section 8, G2), or at whole-sentence level. |
| **F. Notation → pose** (Ham2Pose, Arkushin, Moryossef & Fried, CVPR 2023) | Animate HamNoSys text into poses | HamNoSys → pose | HamNoSys + video | Language-independent notation | Needs HamNoSys for your vocabulary | **No** for now. |

**Key literature details:**

- **Progressive Transformers** (Saunders, Camgöz, Bowden, ECCV 2020). The first end-to-end model mapping spoken-language sentences to continuous 3D sign pose sequences. It has two configurations: direct text → pose, and a stacked model with a gloss intermediary. It introduced back-translation evaluation on RWTH-PHOENIX-Weather-2014T.\[10\]\[11\]\[12\] Its skeletons came from OpenPose with 2D → 3D lifting.\[13\]
- **T2S-GPT** (Yin et al., ACL 2024). A dynamic VQ-VAE compresses sign motion into variable-length codes, then a GPT-like model generates the codes and their durations from text. Tested on PHOENIX14T. The authors also report gains from more data, using their 486-hour PHOENIX-News set.\[14\]\[15\]
- **SOKE** (Zuo et al., ICCV 2025). A decoupled tokenizer turns upper body, left hand and right hand into discrete tokens, which are fed to a *pretrained language model*. It adds retrieval of word-level signs from external dictionaries to sharpen results, and ran a user study with professional ASL and CSL signers.\[16\]\[17\]
- **SignAvatars** (Yu, Huang, Cheng, Birdal, ECCV 2024). 70,000 videos from 153 signers (8.34M frames), annotated automatically with SMPL-X body/hand/face. It supports 3D SLP from text, words or HamNoSys.\[18\] This shows that automatic 3D annotation of sign videos is an accepted practice.
- **Sign Stitching** (BMVC 2024). Dictionary examples are normalised to a canonical skeleton (stored as joint angles), cropped, stitched, frequency-filtered and resampled. The authors argue that plain concatenation looks "robotic and unnatural". Their dictionary skeletons came from MediaPipe, uplifted to 3D.\[7\]\[11\]

**Interpretation.** Approach **D** is the only learned approach your verified data can feed directly. Approach **A** is the natural published BdSL baseline. Approach **E** becomes possible if segmentation (weakly supervised) works on your template-structured videos.

---

## 5. What Needs Training

| Component | Status | Explanation |
|---|---|---|
| Text normalisation (Unicode, ZWNJ, spelling variants, digits like "২৫") | **Rule-based / deterministic** | Write a variant dictionary from the spelling issues you've already found; reuse the csebuetnlp normalizer. |
| Tokeniser + text encoder (BanglaT5 / BanglaBERT / mT5) | **Pretrained, reused** (optionally fine-tuned) | BanglaT5 (Bhattacharjee et al., BanglaNLG, 2022) must be used with its normalisation pipeline, per the model card.\[19\] The small checkpoint is realistic on a T4 (assumption; test it). |
| Pose extraction from videos (MediaPipe Holistic, RTMPose/MMPose-WholeBody, AlphaPose, Sapiens, SMPLer-X/SMPLest-X) | **Pretrained, reused, run once offline** | Creates your *training targets*. No training needed, but quality control is. |
| Pose normalisation (centre on shoulders, scale by shoulder width, fill gaps) | **Deterministic** | Standard preprocessing (e.g., the Zurich pose-based SLT pipeline normalises per sequence and zero-fills missing points).\[20\] |
| **Text → pose (or text → motion-token) model** | **Trained on your data** | The core research component. |
| Motion tokenizer (VQ-VAE), if used | **Trained on your data** (pose only, no text) | Optional second stage, as in T2S-GPT and SOKE. |
| BdSL sentence recognizer for back-translation evaluation | **Trained on your data** (pose → Bangla text) | An evaluation tool, not part of the product. |
| Sign segmentation / alignment | **Needs research** | Pretrained segmentation models exist (Moryossef et al., Findings of EMNLP 2023) but were not built on BdSL.\[21\] |
| Retargeting to avatar | **Deterministic + tooling; fingers need research** | Keypoints → joint rotations (inverse kinematics) → rig. |
| Avatar rendering (Blender / Three.js / Unity; or JASigning for the SiGML baseline) | **Existing tools, no training** | Choose later. |

---

## 6. How Training Works

Example training pair: text "আমি স্কুল যাই" → video Index *k* → extracted keypoints for T frames (say 90 frames × 75 points × 3 values; the numbers are illustrative).

1. **What goes into training?** Pairs of (normalised sentence, pose sequence), one pair per video take.
2. **Input:** the tokenised sentence.
3. **Target (ground truth):** the pose sequence *estimated* from the real video. It is "ground truth" only in the sense of being the best available answer: it inherits pose-estimator errors, especially on fingers.
4. **Prediction:** the model outputs its own pose sequence, frame by frame (or token by token).
5. **Comparison:** measure how far the predicted joints are from the target joints, e.g., mean squared error per joint, after aligning lengths. For token models, check whether the right motion token was predicted (cross-entropy).
6. **Loss:** one number summarising "how wrong" the model was on a batch. Lower is better.
7. **Improvement:** the optimiser (e.g., Adam) nudges the model's weights to reduce the loss, and this repeats over many passes (*epochs*).
8. **Validation data:** held-out pairs checked after each epoch to choose settings and to stop before *overfitting* (memorising training data).
9. **Test data:** a separate held-out set, used **once** at the end to report results.
10. **Why the test set must stay unseen:** if the model has seen a test sentence (or another take of it), the score measures memory, not translation.

**The leakage trap specific to your data.** About 1,478 sentences have repeated takes, and many sentences differ only in one slot word. A random split would put take 1 of "আমার চাচা বুধবার মাংস খায়" in training and take 2 in the test set, which inflates scores. Use these splits instead:

- **Split S1 (sentence-level):** group by unique normalised sentence, so all takes stay together.
- **Split S2 (template-level):** group by template ("আমার ‹KIN› ‹DAY› ‹FOOD› খায়"), so whole templates are unseen at test time.
- **Split S3 (compositional):** every slot word is seen in training, but specific combinations are held out.
- **Signer-independent split:** only possible if signer IDs become available.

**What cannot be trained directly.** Text → gloss (no gloss targets), gloss → pose (no glosses), and per-sign retrieval (no boundaries). Don't pretend these exist.

---

## 7. How We Test the Model

No experiments have been run, so no results are reported or implied.

| Level | Metric | What it measures (simple words) | Why it matters | Good result means | Valid without expert/gloss? |
|---|---|---|---|---|---|
| Pose accuracy | **DTW-MJE** (Dynamic Time Warping + Mean Joint Error): align the two sequences in time, then average the joint distance\[22\] | How close the generated motion is to the real signer's motion, allowing different speeds | Direct, cheap | Lower than baselines on unseen test sentences | **Yes** |
| Pose accuracy (hands) | DTW on hand keypoints only; *nDTW* variants | Fingers carry most lexical meaning | Body-only scores hide hand failures | Close to the gap between two real takes of the same sentence | **Yes** |
| Meaning | **Back-translation**: a pose → text recognizer (trained on your real poses) reads the generated poses; compute BLEU/chrF/WER against the source sentence | Whether the motion is "readable" as the intended sentence | Used since Progressive Transformers |\[10\] High BLEU, low WER relative to baselines | **Yes**, but biased (see caveat) |
| Distribution realism | FGD (Fréchet Gesture Distance)\[22\] | Whether generated motion "looks like" real motion overall | Catches frozen or average-looking motion | Low FGD | Yes |
| Pose-extraction quality | % frames with a missing hand; jitter (acceleration/jerk) | Whether your targets are trustworthy | Garbage targets → garbage model | Few missing hands, low jitter | Yes |
| Take-agreement ceiling | DTW between two real takes of the same sentence | The natural variation between human performances | Tells you what "perfect" can look like | Model error approaches this ceiling | **Yes (unique to your multi-take data)** |
| Avatar fidelity | Re-extract pose from the *rendered* avatar video; compare it with the input pose | What retargeting loses, especially fingers | Avatars often break handshapes | Small loss | Yes |
| Human evaluation | Comprehension or rating by BdSL users | Actual usefulness | The only true test | — | **Needs signers** — later, small-scale if possible |

**Literature support and caveats:**
- *Meaningful Pose-Based Sign Language Evaluation* (Jiang et al., WMT 2025) groups pose metrics into three families: keypoint distance with DTW, embedding-based, and back-translation. It studies how well each correlates with human judgment and releases a pose-evaluation toolkit.\[23\]\[24\] Use it rather than writing metrics from scratch.
- Back-translation has a known weakness. The recognizer can reward motions that exploit its own quirks, and in SiLVERScore's (arXiv:2509.03791) words, "the absence of a standardized sign-to-text translation system complicates this approach, introducing unknown error propagation."\[25\] Always report it alongside DTW and the take-agreement ceiling. Train the recognizer on training-split real poses only.
- Because your sentences are templated, a recognizer might "guess" the template from coarse motion. Report per-slot accuracy (did it get চাচা vs মামা, বুধবার vs শুক্রবার right?), not just BLEU.

---

## 8. Research Gaps / Possible Novel Contributions

None of these is established as novel. Each lists the evidence needed before claiming it.

**G1. Learned, gloss-free Bangla text → BdSL pose generation, compared against the lookup/SiGML baseline**
- *Existing problem:* BdSL systems are all lookup (P1, P5).
- *Existing approach:* gloss-free text → pose exists for other languages (Progressive Transformers; T2S-GPT; SOKE).
- *Related BdSL work:*
  - SignBD-Word (Sams, Akash & Rahman, 2023) is titled "Video-based Bangla word-level sign language and pose translation" and is described as a baseline for "pose synthesis" at word level.\[5\]
  - Bangla-SGP explicitly plans "a pipeline that generates 3D sign language representations from Bangla text".\[5\]
  - So "first BdSL pose generation" should **not** be claimed. I found no sentence-level, gloss-free BdSL text → pose paper, but that is not proof one doesn't exist.
- *Gap:* no sentence-level, data-driven BdSL production with automatic evaluation (to my search).
- *Proposed idea:* train a small text → pose model on your videos and compare it with (a) SiGML lookup (if obtainable), (b) nearest-sentence retrieval, and (c) a mean-pose baseline.
- *Required data:* your videos + extracted poses.
- *Components:* pose estimator, text encoder, seq2seq pose decoder.
- *Evaluation:* DTW-MJE, back-translation, take-agreement ceiling.
- *Why research-worthy:* a first quantitative benchmark for BdSL SLP, *if* the literature check still holds at submission time.

**G2. Weakly supervised sign-unit discovery from template-structured videos**
- *Problem:* no sign boundaries.
- *Existing approach:* Moryossef et al. (Findings EMNLP 2023) segment signs and phrases with BIO tagging and report zero-shot generalisation across signed languages.\[21\]\[26\]
- *Gap:* nobody (to my knowledge) has exploited *minimal pairs*, i.e., sentences differing in exactly one slot word, to localise that word's sign.
- *Idea:* align the pose sequences of "আমার চাচা বুধবার মাংস খায়" and "আমার চাচা শুক্রবার মাংস খায়" with DTW; the region where they disagree is a candidate for the weekday sign.
- *Required data:* your templated videos (the slot structure is already verified).
- *Evaluation:* consistency of discovered segments across sentences; recognition accuracy on the mined clips; a small manually checked subset (possible even without expert fluency, since it's just "where does it change").
- *Why worthwhile:* it turns a dataset weakness (templating) into a supervision signal. **Requires experiments.**

**G3. Compositional generalisation evaluation**
- *Problem:* random splits overestimate quality on templated data.
- *Gap:* I found no BdSL SLP work reporting template-aware or compositional splits.
- *Idea:* splits S1/S2/S3 (Section 6); report the performance drop from seen to unseen combinations.
- *Data:* already verified in your spreadsheet.
- *Why worthwhile:* it's cheap, rigorous, and directly addresses whether a model *translates* or *memorises*.

**G4. Retrieval-plus-transition hybrid vs fully generative**
- *Existing approach:* Sign Stitching (BMVC 2024) stitches dictionary signs with filtering and resampling; SOKE conditions generation on retrieved dictionary signs.\[7\]\[16\]
- *Gap:* BdSL has neither a video sign dictionary aligned to your signer(s) nor learned transitions.
- *Idea:* use G2's mined segments as a dictionary, then stitch vs generate vs hybrid.
- *Requires* G2 to work first.

**G5. Noisy Bangla / Banglish front-end normalisation for SLP**
- *Problem (verified in your data):* spelling variants, ZWNJ, Latin script.
- *Existing approach:* the csebuetnlp normalizer handles Unicode, not colloquial variants.\[27\]
- *Gap:* small. Probably an engineering contribution, not a paper on its own. Measure the downstream effect (error with vs without normalisation).

**G6. Expert-free automatic evaluation for BdSL SLP**
- *Existing approach:* back-translation and DTW metrics (Saunders 2020; Jiang et al. 2025).
- *Gap:* nothing validated for BdSL.
- *Idea:* a BdSL sentence recognizer trained on your data, plus the take-agreement ceiling as a calibration reference.
- *Limitation:* without signers you can't show human correlation, so claim it as a *proxy*.

**G7. Multi-take / multi-signer supervision**
- *Idea:* use two takes as two valid targets (reducing "averaging"), as augmentation, or to estimate natural variability.
- *Requires* confirming that takes differ meaningfully (different signer or session). **Unverified.**

**G8. Retargeting fidelity for BdSL handshapes**
- *Evidence:* a 2026 comparison of eight pose estimators (O'Brien, Sant, Müller, Ebling, arXiv:2604.24609) found:
  - MediaPipe misses a hand in about 20–24% of signing frames on PHOENIX.\[20\]
  - Sapiens handled 15/15 occlusion cases.\[20\]
  - SMPLest-X is smooth but produced "rigid or implausible" hands (0/15 occlusion cases correct).\[20\]
  - The paper's abstract states that "SDPose and Sapiens achieve the best translation performance (BLEU ~11.5), outperforming the common MediaPipe baseline (BLEU ~10)". Translation was measured on RWTH-PHOENIX-Weather 2014 and occlusion on Signsuisse videos.
- *Gap:* no BdSL study of how finger errors propagate from video → pose → avatar.
- *Idea:* a round-trip evaluation (render the avatar, re-estimate its pose, compare).
- *Worthwhile as a secondary analysis.*

---

## 9. What Our Current Dataset Can Support

| Task | Now (spreadsheets only) | After video verification | Never, without new annotation |
|---|---|---|---|
| Text statistics, normalisation, template analysis, leakage-safe split design | **Yes** | — | — |
| Text → pose/motion (gloss-free) | No | **Likely**, if hands and face are visible and fps is adequate | — |
| BdSL sentence recognizer (pose → text) for back-translation | No | **Likely** | — |
| Weakly supervised segmentation (G2) | No | **Possible** (research risk) | — |
| Supervised text → gloss on your data | — | — | **Needs glosses** |
| Signer-independent evaluation | — | Only if signer IDs can be recovered | — |
| Facial grammar / non-manual modelling | — | Partially (face keypoints), but unlabelled | Labels need a signer |
| Human validation of meaning | — | — | **Needs BdSL users** |

**How your size compares with benchmarks (context, not a guarantee):**
- **RWTH-PHOENIX-2014T:** about 7,096 train / 519 dev / 642 test sentences, 9 signers, weather domain. These split counts are as tabulated in Chen et al. (arXiv:2203.04287), whose abstract describes these benchmarks as containing "only about 10K-20K pairs of sign videos, gloss annotations and texts".
- **CSL-Daily:** about 18,401 / 1,077 / 1,176.\[28\]
- **How2Sign:** about 31,128 / 1,741 / 2,322. That figure comes from a community list, not the official paper; verify it before citing.\[29\]
- **Your data:** ~5,010 videos and 3,395 unique sentences. That is a PHOENIX-sized order of magnitude, but in a much narrower, templated domain.
- **Interpretation:** small models are plausible, but large LM-based generators like SOKE are probably too heavy for a free T4 (assumption).

**Is this a known public dataset?** I found no public BdSL sentence-level video dataset matching yours (about 3–5k templated everyday sentences). The closest sentence-level BdSL sets I found are:
- **IsharaKhobor** (Rubaiyeat, Mahmud, Hasan, arXiv:2511.21533): 5,642 BTV news clips, 8 signers, no gloss.\[30\]\[31\]
- **BornilDB v1.0** (Bornil platform, arXiv:2308.15402): 73 hours, 3 signers.\[32\]
- **BTVSL** (IEEE FG 2024): 60 hours of BTV news.\[33\]
- A Kaggle "Bangla Sign Language Video Dataset" (user sumon3455) exists, but its page content couldn't be read,\[34\] so **I don't know based on the available evidence** whether your data overlaps with it.\[34\] Ask whoever collected your videos where they came from and under what licence or consent.

---

## 10. Initial Recommended Research Direction

**Recommendation:** a **gloss-free, pose-based BdSL production benchmark with leakage-safe, compositional evaluation**. Build it in stages:

1. **Pilot:** verify the videos and extract poses for about 50 videos.
2. **Baselines:** nearest-sentence retrieval, and SiGML lookup if the files are obtainable.
3. **Model:** a small text → pose model (Progressive-Transformer-style, or VQ tokens + small transformer).
4. **Evaluation:** DTW (whole body + hands), a back-translation recognizer, and the take-agreement ceiling on splits S1/S2/S3.
5. **Avatar retargeting** as a demonstration.

Why this direction:
- It uses only the (sentence, video) pairs you actually have.
- It needs no expert annotation.
- It fits a T4 if you work on keypoints rather than raw video.
- It produces measurable comparisons against the lookup paradigm that every existing BdSL paper uses.

G2 (minimal-pair segmentation) is the most promising *extension*, because your templated structure is unusual and verified.

**Not recommended as a first step:** text → gloss (no targets), photorealistic video generation, full SMPL-X avatar pipelines before pose quality is checked, or large LLM-based generators.

---

## 11. Initial System Pipeline

```
 TRAINING (offline)                                          
 ┌────────────────────┐   ┌───────────────────────────┐       
 │ Sentence videos    │──▶│ Pose extraction            │       
 │ [existing, UNVERIF]│   │ MediaPipe/RTMPose/Sapiens  │       
 └────────────────────┘   │ [pretrained]               │       
                          └────────────┬──────────────┘       
                                       ▼                      
                          ┌───────────────────────────┐       
                          │ Pose QC + normalisation    │       
                          │ (missing hands, jitter,    │       
                          │ shoulder-centred scaling)  │       
                          │ [deterministic]            │       
                          └────────────┬──────────────┘       
 ┌────────────────────┐                ▼                      
 │ FinalSheet2.xlsx   │   ┌───────────────────────────┐       
 │ (sentence, Index)  │──▶│ Leakage-safe splits S1/S2/ │       
 │ [existing]         │   │ S3 (group by sentence &    │       
 └────────────────────┘   │ template) [rule-based]     │       
                          └────────────┬──────────────┘       
                                       ▼                      
 INFERENCE (online)                                           
 ┌────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐
 │ Bangla text│─▶│ Normalisation  │─▶│ Text encoder │─▶│ Text→pose / motion│
 │ input      │  │ (Unicode, ZWNJ,│  │ (BanglaT5 /  │  │ -token model      │
 │            │  │ spelling vars) │  │ tokenizer)   │  │ [trained on our   │
 │            │  │ [rule-based]   │  │ [pretrained] │  │ data]             │
 └────────────┘  └────────────────┘  └──────────────┘  └────────┬─────────┘
                                                                ▼
        ┌────────────────────┐   ┌────────────────────┐   ┌───────────────────┐
        │ 3D avatar animation│◀──│ Retargeting: key-  │◀──│ Pose sequence     │
        │ (Blender/Three.js; │   │ points→joint rot.  │   │ (intermediate     │
        │ tool TBD)          │   │ fingers [needs     │   │ representation)   │
        │ [existing tools]   │   │ research]          │   │ + smoothing [det.]│
        └────────────────────┘   └────────────────────┘   └───────────────────┘

 BASELINES:  text → lemma → SiGML lookup → JASigning  [existing, P1/P5; access TBD]
             text → nearest training sentence → its real pose  [rule-based]
 EVALUATION: DTW-MJE (body/hands) · back-translation via pose→text recognizer
             [trained on our data] · take-agreement ceiling · avatar round-trip
 OPTIONAL:   minimal-pair segmentation → sign-segment bank → retrieval+stitch
             [needs research]
```

---

## 12. System Diagram Explanation

- **Sentence videos:** your raw material. Nothing works until you've inspected them.
- **Pose extraction:** a ready-made model that finds body, hand and face points in each frame. It turns video into numbers the model can learn from.
- **Pose QC + normalisation:** throw out or repair bad frames (missing hands, shaking points), then centre and scale every signer the same way so the model learns signs, not body size.
- **Spreadsheet + splits:** links each sentence to its video(s). Divides the data so no sentence or template leaks into the test set.
- **Normalisation (input text):** fixes spelling and Unicode so "মংগলবার" and "মঙ্গলবার" look the same to the model.
- **Text encoder:** converts words into number vectors. A pretrained Bangla model already "knows" Bangla.
- **Text → pose model:** the part you train. It learns which movements go with which sentences.
- **Pose sequence:** the intermediate representation, i.e., moving dots over time. It can be scored before any avatar is involved.
- **Smoothing:** removes jitter, the unnatural small shakes.
- **Retargeting:** converts dot positions into joint angles that rotate the avatar's bones. Fingers are the hardest part.
- **3D avatar:** a rigged character that plays the joint angles. The avatar choice is still open.
- **Baselines:** simple systems to beat. If your model can't beat "copy the closest training sentence", it isn't translating.
- **Evaluation block:** measures motion closeness, readability (back-translation) and avatar fidelity, all without an expert.

---

## 13. Research Roadmap

1. **What we already have:** 3,395 verified unique sentences, a template structure, known quality issues, six paper analyses, and a literature map (this report).
2. **Understand next:**
   - Video properties.
   - Whether takes are by different signers.
   - Whether each video has one clean sentence.
   - Whether the 451 missing indexes matter.
   - Where the videos came from, and their consent/licence.
3. **Missing data/annotations:**
   - Signer IDs (recoverable from metadata or visually).
   - A cleaned sentence list with a variant map.
   - Optionally, a small set of manually marked sign boundaries (for validating G2).
   - Glosses and human evaluation remain unavailable; plan around them.
4. **First experiment (pilot, about 1–2 weeks):**
   - Take ~50 videos covering 10 minimal-pair groups (e.g., the same template with different weekdays).
   - Run 2–3 pose estimators (MediaPipe Holistic, plus a whole-body RTMPose/MMPose or AlphaPose model).
   - Measure the percentage of frames with a missing hand, jitter, and runtime on a T4.
   - Visually check that finger shapes are captured.
   - Compute DTW between the two takes of the same sentence, and between minimal-pair sentences.
5. **Next component:** nearest-neighbour retrieval baseline → small text → pose transformer (Progressive-Transformer-style) → optionally a VQ-VAE token model (T2S-GPT/SOKE-style, small).
6. **Evaluation to prepare:**
   - Splits S1/S2/S3.
   - The pose-evaluation toolkit from Jiang et al. 2025.
   - A pose → text BdSL recognizer trained only on training-split real poses.
   - The take-agreement ceiling.
7. **Decide before implementation:**
   - Pose estimator and keypoint set (body + hands ± face).
   - 2D vs 3D target.
   - Continuous vs token output.
   - Avatar tool (Blender, Three.js/VRM, or SMPL-X viewer).
   - Whether to seek IsharaKotha/P5 SiGML files for the baseline.
8. **Possible main contribution:** a leakage-safe, compositional benchmark for BdSL production from sentence videos, with learned models compared against lookup, and optionally minimal-pair segmentation (G2) as the methodological novelty.

**Storage/compute sanity check (my arithmetic, under stated assumptions — verify in the pilot):**
- *Storage:* MediaPipe Holistic's standard output is 543 landmarks (468 face + 33 pose + 21 per hand; the O'Brien et al. benchmark lists 576 for its configuration). At 3 floats × 4 bytes each, that is ≈ 6.5 KB per frame. For an *assumed* 5-second, 30-fps clip (150 frames) that is ≈ 1 MB, so ≈ 5 GB for 5,010 videos. Using ~75 body+hand points (as BdSLW401 does) cuts this to under 1 GB.
- *Runtime:* speed varies widely by estimator. In O'Brien et al. (arXiv:2604.24609, Table 1, measured on a single V100 GPU), AlphaPose ran at 22.89 fps, SMPLest-X at 8.36, Sapiens at 3.29, MediaPipe Holistic at 3.15 (0.89 on CPU) and SDPose at 0.84. Measure it yourself on a T4 before planning.

---

## 14. Open Questions (must be answered before implementation)

1. What are the video format, fps, resolution and framing? Are both hands and the face always in frame?
2. How many signers are there? Are repeated takes by different signers? Can signer IDs be recovered?
3. Does each video contain exactly one sentence, and does it match its `Index`? Do videos exist for Index 333–783?
4. Where did the videos come from (own recording or an existing dataset), and what consent and licence apply?
5. Can you get the IsharaKotha or P5 SiGML files (and under what licence) to build the lookup baseline?
6. Could even 2–3 BdSL users review a small sample late in the project? If not, the paper must present all quality claims as automatic proxies.

**Caveats**
- BdSL grammar claims above come from NLP datasets glossed by one or a few signers, not from linguistic studies.\[5\]
- Some dataset details (MV-BSL, SignBD-Word, the How2Sign split) come from secondary descriptions and should be verified against the original papers.
- Novelty statements reflect a limited literature search as of September 2026. Re-check arXiv and ACL Anthology before submission.

## Sources

1. [\[2511.16896\] IsharaKotha: A Comprehensive Avatar-based Bangla Sign Language Corpus](https://arxiv.org/abs/2511.16896)
2. [Isharakotha: A Comprehensive Avatar-Based Bangla Sign Language Corpus by M. Shahidur Rahman, MD. Ashikul Islam, Prato Dewan, Md Fuadul Islam :: SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4696066)
3. [IsharaKotha: Avatar-based Bangla Sign Language Corpus - Mendeley Data](https://data.mendeley.com/datasets/6ykgx65ks5/2)
4. [A computer graphics-based model to generate dynamic 3D animations for corresponding Bangla sign language gestures using HamNoSys to SiGML conversion | Artificial Intelligence Review | Springer Nature Link](https://link.springer.com/article/10.1007/s10462-025-11370-z)
5. [Introducing A Bangla Sentence - Gloss Pair Dataset for Bangla Sign Language Translation and Research](https://arxiv.org/pdf/2511.08507)
6. [Introducing A Bangla Sentence – Gloss Pair Dataset for Bangla Sign Language Translation and Research](https://arxiv.org/html/2511.08507)
7. [\[2405.07663\] Sign Stitching: A Novel Approach to Sign Language Production](https://arxiv.org/abs/2405.07663)
8. [Breaking the Silence: A Dataset and Benchmark for Bangla Text-to-Gloss Translation](https://arxiv.org/html/2504.02293v3)
9. <https://arxiv.org/html/2504.02293v1>
10. [Progressive Transformers for End-to-End Sign Language Production | Computer Vision – ECCV 2020](https://dl.acm.org/doi/10.1007/978-3-030-58621-8_40)
11. [H. WALSH, B. SAUNDERS, R. BOWDEN: SIGN STITCHING 1](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_721/paper.pdf)
12. [\[PDF\] Sign Stitching: A Novel Approach to Sign Language Production | Semantic Scholar](https://www.semanticscholar.org/paper/Sign-Stitching:-A-Novel-Approach-to-Sign-Language-Walsh-Saunders/1eedb3c0b8b59abb51db53eaca15abaa7314a095)
13. [GitHub - BenSaunders27/ProgressiveTransformersSLP: Source code for "Progressive Transformers for End-to-End Sign Language Production" (ECCV 2020) · GitHub](https://github.com/BenSaunders27/ProgressiveTransformersSLP)
14. [\[2406.07119v1\] T2S-GPT: Dynamic Vector Quantization for Autoregressive Sign Language Production from Text](https://arxiv.org/abs/2406.07119v1)
15. [\[2406.07119\] T2S-GPT: Dynamic Vector Quantization for Autoregressive Sign Language Production from Text](https://arxiv.org/abs/2406.07119)
16. [Signs as Tokens: A Retrieval-Enhanced Multilingual Sign Language Generator](https://arxiv.org/pdf/2411.17799)
17. [Signs as Tokens: A Retrieval-Enhanced Multilingual Sign Language Generator](https://openaccess.thecvf.com/content/ICCV2025/papers/Zuo_Signs_as_Tokens_A_Retrieval-Enhanced_Multilingual_Sign_Language_Generator_ICCV_2025_paper.pdf)
18. [SignAvatars: A Large-scale 3D Sign Language Holistic Motion Dataset and Benchmark](https://arxiv.org/pdf/2310.20436)
19. [csebuetnlp/banglat5\_small · Hugging Face](https://huggingface.co/csebuetnlp/banglat5_small)
20. <https://arxiv.org/pdf/2604.24609>
21. [\[2310.13960\] Linguistically Motivated Sign Language Segmentation](https://arxiv.org/abs/2310.13960)
22. [Autoregressive Sign Language Production: A Gloss-Free Approach with Discrete Representations](https://arxiv.org/pdf/2309.12179)
23. [Meaningful Pose-Based Sign Language Evaluation - ACL Anthology](https://aclanthology.org/2025.wmt-1.4/)
24. [\[2510.07453\] Meaningful Pose-Based Sign Language Evaluation](https://arxiv.org/abs/2510.07453)
25. [SiLVERScore: Semantically-Aware Embeddings for Sign Language Generation Evaluation](https://arxiv.org/pdf/2509.03791)
26. [Linguistically Motivated Sign Language Segmentation](https://arxiv.org/pdf/2310.13960)
27. [banglanlptoolkit · PyPI](https://pypi.org/project/banglanlptoolkit/)
28. [\[2203.04287\] A Simple Multi-Modality Transfer Learning Baseline for Sign Language Translation](https://ar5iv.labs.arxiv.org/html/2203.04287)
29. [GitHub - ZechengLi19/Awesome-Sign-Language: Paper list of sign language, including sign language recognition(SLR), sign language translation(SLT) and other work. Quick start your awesome work with us!! 🤟🤟🤟](https://github.com/ZechengLi19/Awesome-Sign-Language)
30. <https://arxiv.org/abs/2511.21533>
31. [Bangla Sign Language Translation: Dataset Creation Challenges, Benchmarking and Prospects — Speech & Audio](https://awesomepapers.io/speech-audio/papers/2511.21533)
32. <https://arxiv.org/abs/2308.15402>
33. [(PDF) State-of-the-Art Translation of Text-to-Gloss using mBART : A case study of Bangla](https://www.researchgate.net/publication/390467809_State-of-the-Art_Translation_of_Text-to-Gloss_using_mBART_A_case_study_of_Bangla)
34. [Bangla Sign Language Video Dataset](https://www.kaggle.com/datasets/sumon3455/bangla-sign-language-video-dataset)
