# Gloss convention v0.1 — PROVISIONAL

> **Status: provisional.** Accepted in principle by the owner (ADR-0015, 2026-10-22). It has **not**
> been checked by a BdSL-competent person. It is a working agreement for writing pseudo-glosses, not
> a description of BdSL. Source: `research/design_proposals/03_Stage1_Audit_and_Design_Plan_2026-10-21.md`
> §F and ADR-0015. Changes need the owner's OK and a new version number.

## 1. Three different things — keep them apart
- **Bangla word order** — the sentence in `FinalSheet2.xlsx` (the input text).
- **Gloss notation** — labels for signs, written in Bangla words or caps. Notation is not a language.
- **BdSL grammar** — use of space, non-manual signals (face, head, body) and simultaneity. Glosses lose
  most of this; the video keeps it.

A gloss written by the rule drafter (G0) is a **pseudo-gloss**: a function of the Bangla text. It is
never presented as a BdSL annotation.

## 2. Statuses (ADR-0015)
| Status | Meaning | Who sets it |
|---|---|---|
| `auto_draft` | G0 output; nobody has checked it | the drafter (`bdsl.cli gloss-draft`) |
| `team_reviewed` | a team member compared it with the clip and corrected it | a reviewer registered in `REVIEWERS.csv` (role `team` or `expert`) |
| `expert_validated` | a BdSL-competent person checked it | a reviewer registered with role `expert` |
| `rejected` | the clip cannot be glossed as given (e.g. the video does not match the sentence) | a registered reviewer, with a note |

The AI never sets `team_reviewed` or `expert_validated` and never registers reviewers. Models learn
only from `team_reviewed` / `expert_validated` rows that are not mock (design doc 04 §F-10). Mock or
simulated rows exist only in tests (`is_mock=true`) and are refused in real files.

## 3. Tokens
- One gloss token per sign, separated by single spaces, in the order the signs are made.
- A token is a Bangla citation form (dictionary form) where the reviewer knows it; otherwise the word
  as written. An optional English caps label may be given later in the lexicon, not in this file.
- **Case endings** (genitive, locative, …) are dropped when the reviewer is sure. Possessive pronouns
  (আমার, তোমার, …) stay as tokens until reviewed.
- **Verbs:** the verb's base form; tense goes into `tense_note` (e.g. `future`), not into a made-up token.
- **Word order:** Bangla order is kept. A reviewer may reorder to match the signing seen in the clip
  and should say so in `notes`. Candidate patterns (time first, wh-word last) are recorded, not
  applied automatically.

## 4. Special tokens and tags
| Notation | Use |
|---|---|
| `NOT`, `NOT.BE`, `NOT.HAVE` | negation candidates for না / নয় / নেই (+ tag `neg`) |
| `FS(word)` | fingerspelled item (e.g. a name or a Latin letter) |
| `NUM(n)` | number sign |
| `UNK(word)` | a word whose sign is unknown or absent (also used by the system at inference) |
| tags `neg`, `q-wh`, `q-yn` | sentence-level negation, wh-question, yes/no question |

No timestamps are written anywhere: every clip is one complete sentence, and no word-level timing is
claimed.

**Unverified pointers** (read by the team, not by the AI): a 2026 FASAL proceedings paper (Reed) is
reported to describe default SOV order, three negation particles and an optional headshake; the
Bangla-SGP paper reports future tense as root + "will be" and fingerspelled names. Both come from
search summaries only and are not part of this convention until the team has read and agreed them.

## 5. The G0 drafter (G0-v0.1, `src/bdsl/text/gloss_rules.py`)
G0 never reorders and never guesses a lemma. Its markers tell the reviewer what to check:

| Marker | Meaning |
|---|---|
| none | a closed-list rule applied: pronoun kept (R0), negation (R1), question word (R2/R2b) |
| `~` | stem suggested by the genitive rule R5 (the stem is itself a word in the sheet) — check it |
| `?` | no rule: written as in the sentence, or a `NUM()`/`FS()` candidate — the reviewer decides |

Tag `q?` means a sentence with কি/কী, which can be "what" or a yes/no question particle: the
reviewer writes `q-wh` or `q-yn` in `tags_reviewed`.

## 6. Annotation file columns
`index, split, sentence_raw, sentence_norm, norm_ver, g0_ver, gloss_auto, tags_auto, gloss_reviewed,
tags_reviewed, tense_note, status, annotator_id, reviewer_id, review_date, confidence, notes, is_mock`

`gloss_reviewed` is written without markers (`?`, `~`). `confidence` is `low`, `med` or `high`.

## 7. Review protocol (ADR-0015, accepted in principle)
1. A registered team reviewer checks each draft against its clip → `team_reviewed` (or `rejected`).
2. A second team member spot-checks about 20% of reviewed rows; disagreements go into `notes`.
3. The BdSL-competent person reviews a stratified sample when available → `expert_validated` for
   those rows only; agreement with team reviews is reported.
