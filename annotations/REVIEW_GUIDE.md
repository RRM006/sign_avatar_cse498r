# How to review a pilot gloss (for team members)

You will check the automatic drafts in `pilot50_v1_gloss_v01.csv` against the videos. Read
`GLOSS_CONVENTION_v0.1.md` first (10 minutes). Nothing here needs programming.

## Before you start
1. Ask the owner for your **reviewer code** (for example `T1`). The owner adds it to `REVIEWERS.csv`.
   Never write your name in any file: the repository is public.
2. Open the CSV in **LibreOffice Calc**, **Google Sheets** or **VS Code**. In Excel, save with
   *File → Save As → "CSV UTF-8"*, otherwise the Bangla text is damaged.
3. The clips are in `dataset/pilot50_v1/videos/<index>.mp4` (local copies, not in git).

## For each row
1. Play `videos/<index>.mp4` (twice if needed). Read `sentence_raw` and the draft `gloss_auto`.
   - `?` = the drafter had no rule for that word; `~` = a suggested stem; no marker = a fixed rule.
2. Write the gloss you see signed into **`gloss_reviewed`**, following the convention:
   - one token per sign, in the order signed; no `?` or `~` markers;
   - `NOT` / `NOT.BE` / `NOT.HAVE`, `FS(...)`, `NUM(...)`, `UNK(...)` where they apply;
   - if you change the word order, say so in `notes`.
3. Write the sentence tags into **`tags_reviewed`**: `neg`, `q-wh`, `q-yn`, separated by `;` (empty
   if none). Replace a `q?` draft tag with `q-wh` or `q-yn`.
4. Optional: tense in **`tense_note`** (e.g. `future`, `past`).
5. Fill **`reviewer_id`** (your code), **`review_date`** (`YYYY-MM-DD`), **`confidence`**
   (`low` / `med` / `high`), and set **`status`** to `team_reviewed`.
6. If the video does not match the sentence, or cannot be glossed, set `status` to `rejected` and
   explain in `notes`.

Do not edit `index`, `split`, `sentence_raw`, `sentence_norm`, `norm_ver`, `g0_ver`, `gloss_auto`,
`tags_auto`, `annotator_id` or `is_mock`.

## After reviewing
Give the file back to the owner. The check `uv run python -m bdsl.cli gloss-validate` must report no
problems (it confirms your code is registered and every reviewed row is complete). Only
`expert_validated` rows count as linguistically validated; `team_reviewed` rows are the team's best
reading of the clip.
