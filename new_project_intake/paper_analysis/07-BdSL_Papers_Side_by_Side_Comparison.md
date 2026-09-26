# Side-by-Side Comparison — 3 Sign-Language / 3D-Avatar Papers

**For:** Bangla Text-to-Bangla Sign Language (BdSL) Translation Using a 3D Avatar (research/exploration stage — zero budget, Colab T4, local 24GB RAM + RX 570)

**Papers compared:**
- **P1 — IsharaKotha:** Islam et al. 2025, arXiv preprint — *IsharaKotha: A Comprehensive Avatar-based Bangla Sign Language Corpus*
- **P2 — ISL Avatar:** Mehataj, Kanimozhi et al. 2026, Procedia Computer Science (ICMLDE) — *Real-time Sign Language Translation with 3D Avatar Interaction for Inclusive Communication*
- **P3 — HamNoSys→SiGML BdSL:** Karim, Rahaman et al. 2026, Artificial Intelligence Review (Springer) — *A computer graphics-based model to generate dynamic 3D animations for BdSL gestures using HamNoSys to SiGML conversion*

---

## Quick Snapshot

| | P1 — IsharaKotha | P2 — ISL Avatar | P3 — HamNoSys→SiGML BdSL |
|---|---|---|---|
| Language | Bangla | English | Bangla (text + voice) |
| Sign language | BdSL | ISL (Indian SL) | BdSL |
| Sign vocabulary | 3,823 signs, 36 categories | 50 signs / 324 words | 90 classes (13 numeral + 36 letter + 41 word) |
| Code released | No | No | **Yes** — GitLab (Laravel/PHP) |
| Dataset released | Unsure — not confirmed, must request | No | **Yes** — Zenodo DOI, ~45 KB SiGML, verified live |
| Medical-domain signs | 84 ("Disease & Treatment") | 0 | 0 |
| Has a translation *model*? | No — lemma lookup only | No — word lookup only | No — rule-based lookup + reordering |
| Overall relevance (per analysis) | **High** | Medium | **High** |

---

## 1. Relevance Scores (out of 5, from each analysis)

| Aspect | P1 | P2 | P3 |
|---|---|---|---|
| Bangla relevance | 5 | 1 | 5 |
| Sign-language relevance | 5 | 4 | 5 |
| Text-to-sign translation | 3 | 3 | 4 |
| NLP / grammar | 2 | 1 | 3 |
| Sign / motion generation | 3 | 2 | 3 |
| 3D avatar / animation | 4 | 4 | 4 |
| Dataset usefulness | 4 | 1 | 4 |
| Feasibility for our project | 4 | 3 | 5 |

---

## 2. Problem & Approach

| | P1 | P2 | P3 |
|---|---|---|---|
| Core problem | No BdSL corpus exists to build any generation system on | Deaf people excluded from real-time conversation / video calls | No automatic Bangla text/voice → BdSL system exists |
| Core approach | Hand-author 3,823 signs (HamNoSys→SiGML) from the BSTI dictionary + add a BiLSTM lemmatizer | Blender/Mixamo avatar + mocap for signs; VGG-16 CNN for the reverse sign→text direction; WebRTC video calls | Rule-based Bangla parser + HamNoSys→SiGML dictionary lookup + fingerspelling fallback + BdSL grammar-reordering rules |
| Motion generation | Authored (hand-notated), not learned | Mocap-authored, not learned | Authored (notation-driven), not learned |

---

## 3. Methodology — NLP / Text Layer

| | P1 | P2 | P3 |
|---|---|---|---|
| Tokenization | Not stated | NLTK (no detail given) | Whitespace split + punctuation strip |
| Grammar handling | Lemmatization only | None | Rule-based BdSL word-order rewriting (rules never enumerated) |
| OOV handling | **None — system hard-fails** | Not addressed | **Fingerspelling fallback** |
| ML model used | BiLSTM seq2seq + attention (79.22% acc, 94,781-word training corpus) | None (rule lookup) | None (purely rule-based) |

---

## 4. Methodology — Avatar / Sign Layer

| | P1 | P2 | P3 |
|---|---|---|---|
| Sign notation | HamNoSys → SiGML | Keyframed Blender animation + IK | HamNoSys → SiGML |
| Avatar engine | JASigning / SiGML Player | Blender/Mixamo rig + WebRTC delivery | JASigning / UEA engine |
| Non-manual features (face/expression) | Representable in notation, unused at sentence level | Rokoko face capture for emotion (general, not BdSL-specific) | Present in framework, **absent in actual output** (expert-flagged) |
| Motion smoothing | Not stated | Graph Editor / Dope Sheet | Not stated |

---

## 5. Dataset Comparison

| | P1 — IsharaKotha | P2 — ISL set | P3 — BdSL SiGML (Zenodo) |
|---|---|---|---|
| Size | 3,823 signs | 50 signs / 78 sentences / 324 words | 90 classes |
| Public? | Not confirmed — email required | No | **Yes, verified live** |
| Medical coverage | 84 signs | 0 | 0 |
| Usable for us? | Partial, pending author response | Not really — wrong sign language/language | Partial — seed + format template |

---

## 6. Evaluation & Results

| | P1 | P2 | P3 |
|---|---|---|---|
| Evaluation type | Human rating, 1–4 scale (2 interpreters + 1 deaf user) | Scenario-based stress testing (qualitative) | Expert pass/fail + accuracy % + 90-person dialect-stratified test |
| Headline result | 3.14/4 pooled | Not extractable (figure-only in PDF) | 97.5% text accuracy, 94.75% voice accuracy |
| Automatic/objective metric | **None** | **None** | **None** (accuracy = human judgment) |
| Sentence vs. word-level quality | Sentences score *lower* | Not measured | Sentence 94% vs. alphabet 100% — same pattern |
| Dialect testing | Not mentioned | N/A | Dhaka 96.5% → Sylhet 92% (matches our dialect list) |

---

## 7. Feasibility for Our Setup (zero budget, Colab T4, local 24GB RAM + RX 570)

| | P1 | P2 | P3 |
|---|---|---|---|
| GPU needed? | No — tiny BiLSTM | Not stated — CNN is light | No — ran on i5 laptop + 2GB GPU |
| Colab-compatible part | NLP/lemmatizer training | CNN recognition training | Bangla parsing logic (if reimplemented in Python) |
| Must run locally | JASigning/SiGML rendering (no display server on Colab) | Blender/Mixamo/WebRTC avatar work | JASigning/UEA avatar rendering |
| Overall feasibility | Partial — demo-level; corpus access is the blocker | Partial — architecture reproducible, results are not | Partial→High — demo in ~2–5 days, full replication in 1–2 weeks |

---

## 8. What Each Paper Is Missing

**All three, in common:**
- No medical-domain vocabulary
- No automatic/objective evaluation metric — every result is human-judged
- Non-manual features (facial grammar) unused, unimplemented, or expert-flagged as missing
- Sentence-level output quality is consistently worse than word/sign-level quality

**P1 (IsharaKotha) specifically:**
- No OOV handling — the system hard-fails on any unknown root word
- No real translation model, only lemma→lookup
- Corpus public access is unconfirmed

**P2 (ISL Avatar) specifically:**
- Wrong sign language and spoken language entirely (ISL / English)
- Tiny, non-public dataset
- Near-zero NLP/grammar layer

**P3 (HamNoSys→SiGML BdSL) specifically:**
- BdSL grammar-rewriting rules exist but are never enumerated or documented
- Zero ML/NLP model — purely rule-based lookup
- Small 90-sign vocabulary
- Struggles with Bangla compound letters (যুক্তাক্ষর) during fingerspelling

---

## 9. What to Borrow From Each, Combined

- **From P3:** the working end-to-end architecture (rule-based parser → SiGML lookup → fingerspelling fallback → JASigning avatar), its public dataset as a seed, and its dialect-stratified evaluation protocol.
- **From P1:** the larger 3,823-sign corpus (pending access), the HamNoSys/SiGML authoring workflow for creating new signs, and its human-evaluation rubric (1–4 scale, interpreter + deaf-user raters).
- **From P2:** the free Blender/Mixamo/mocap pipeline as an alternative avatar-authoring route, and its scenario-based stress-testing idea for robustness checks.
