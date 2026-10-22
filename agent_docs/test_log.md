# test_log.md — What Was Tested + Results

> Records what we tested or verified, how, and the result, including failures. This makes progress
> verifiable.
>
> Template for each entry:
> ```
> ## YYYY-MM-DD — <area/module> — <what was tested>
> - Setup: <how it was tested; tools/versions; environment; data used>
> - Metric(s) / checks: <what was measured or verified>
> - Result: <the numbers / pass-fail / observations>
> - Notes: <what helped or hurt; errors; next idea>
> ```

---

## What we care about (per area)
Evaluation protocol: ADR-0020 (metric set accepted in principle). Pilot results are "pipeline tests";
reported numbers need the S1 test set, 3 seeds and confidence intervals.

## Planned test cases
Acceptance tests per step are listed in `milestone_log.md` (milestones 5–10) and `current_task.md`.
Results are logged here only after they are actually run.

---

## 2026-10-22 — Audit + report generation (Session 6)
- Setup: read-only audit of the repository, `work/`, git, hardware and PDF tools; then (owner-approved)
  the two reports. `.venv` unchanged (no installs). PDFs built with system Python 3.14.4 +
  markdown-it-py 4.2.0 and headless Google Chrome (`research/reports/build_reports.py`); checked with
  pdf.js 4.10.38 (jsDelivr) in the browser pane.
- Metric(s) / checks and results:
  - **Hashes:** manifest_v1 `2ff133cf…`, S1_v0 `40481a5f…`, pilot selection `8affc876…` equal their
    meta files; holistic model `e2dab611…`; VRM `1995f174…`.
  - **Pilot copies:** 50/50 SHA-256 match `pilot50_manifest.csv` (40/5/5).
  - **Leakage re-check on S1 v0:** 0 SHA-256 / 0 sentences / 0 groups across splits.
  - **Representative clips:** 3,456; 25,286.8 s ≈ 379,301 frames at 15 fps.
  - **Runs:** 12 current + 6 superseded folders; all 60 checkpoint files load; every run has its
    run/metrics files; every `run.json` records `dirty=True`.
  - **pytest:** 140 passed. **gloss-validate:** exit 1 (normal), exit 0 (`--allow-test-data`).
  - **Hardware:** Ryzen 5 3500X 6C/6T, 23.9 GB RAM, RX 570; D: 83.4 GB free, C: 121.7 GB free.
  - **Line endings:** `core.autocrlf=true`, no `.gitattributes`; annotation CSV working copy
    `9cd37d3d…` vs committed blob `a0be4e91…` (identical after removing CR).
  - **Training code:** no `.to(device)` in `src/bdsl/models/` → CPU only.
  - **Notebooks:** all 7 saved without outputs; only 00 was ever executed.
  - **PDFs:** `PILOT_TEST_VERSION_COMPLETE_REPORT.pdf` 19 pages (813,922 B);
    `FULL_DATASET_EXECUTION_PLAN.pdf` 31 pages (1,168,225 B). Text extractable on every page; all
    Markdown headings present (29 / 120); all 7 figures present (checked by text inside each
    diagram); "Page n of N" on every page except the title page; Bangla text intact; spot pages
    checked visually (tables, code blocks and figures fit).
- Notes:
  - My own build-script bugs, fixed: image paths not rewritten (first PDFs had only alt text, and my
    first figure check wrongly passed on that alt text); Chrome reused cached SVGs; the chart font
    was missing on Windows.
  - The pilot PDF could not be replaced while Adobe Acrobat Reader held it open; after the owner
    quit Acrobat, the final build was written at 21:14:43 and verified.
  - The table of contents links to sections but has no page numbers.

---

## 2026-10-22 — Day 5 — retargeting, skeleton video, avatar viewer, end-to-end demo ("pipeline test")
- Setup:
  - Command: `bdsl.cli demo --sentence <3246>` → `work/demo/demo_20261022T141520Z/`.
  - Text → gloss by G0. Model B = run `gloss2motion_gloss_pilot50_20261022T133822Z`, seed 42, best
    checkpoint (SHA-256 b7639820…). B1 = training clip 3225.
  - Post-processing: One-Euro filter (min cutoff 1.0, β 0.3) on body + hands; hands blend to rest
    over 3 frames where missing.
  - Retargeter rt-v1; avatar = CC0 VRoid `Base_Female.vrm` (VRM 0.x, SHA-256 1995f174…).
  - Viewer: three 0.186.1 + @pixiv/three-vrm 3.5.5 from jsDelivr, served by `http.server` on
    127.0.0.1, checked in the built-in browser.
- Measured before building:
  - MediaPipe "left shoulder" x > "right shoulder" x in 50/50 clips; y points down.
  - The hand world wrist equals the pose wrist (distance 0.000 m), so hands and pose share one frame.
  - The VRM declares CC0 in its own metadata. It has 54 humanoid bones, including 30 finger bones and
    upperChest (G5 answered).
  - Expression presets: a/i/u/e/o, blink (both, left, right), joy, angry, sorrow, fun (no "surprised").
- Checks and results:
  - Demo: G0 gloss "আমি স্কুল? যাই?", no unknown tokens. Model B predicts 91 frames; B1 = 3225
    "আমি সোমবার স্কুল এ যাই", 79 frames, hand coverage L 0.81 / R 0.51.
  - Hash checks (inputs, vocab, standardiser vs the run) all pass.
  - Round-trip, Python canonical T-pose, all 50 pilot recordings (4,806 frames): body / hands /
    fingers / head max ≤ 2.5e-6° (exact by construction; checks the quaternion maths).
  - Round-trip on the real avatar (three-vrm, raw bones after normalised → raw transfer), mean (max):
    - Model B: body 0.50° (3.42°), hand frames ~0° (n=182), fingers ~0° (n=2730);
    - B1: body 0.35° (2.79°), hand frames ~0° (n=104), fingers ~0° (n=1560).
    The body error is not broken down per bone. A likely source: the torso check measures from the
    hips, while the spine rotates around its own joint.
  - Avatar sides: after `rotateVRM0`, leftUpperArm x = +0.108 and rightUpperArm x = −0.109, so the
    avatar's left is on screen right, the same as the skeleton video.
  - Skeleton video: 91 frames, 15 fps, 960×570, two labelled panels; the B1 panel holds its last
    frame marked "(ended)".
  - Viewer: plays at 15 fps (30 frames in 2 s), no console errors. Mirror mode runs. "Record one
    pass" produced a 1.1 MB `.webm`, offered as a save link; it was not downloaded.
  - `uv run pytest`: 140 passed (15 new in `tests/test_avatar.py`).
- Notes:
  - A pipeline test only; nothing here is checked by a BdSL-competent person (`LIMITATIONS.md` in
    the demo folder).
  - Bugs found and fixed during the run:
    - a zero-length hand vector crashed the frame solver;
    - a negative first time-step crashed the viewer;
    - fingertip bones were measured with the previous bone's direction in the first viewer
      round-trip (mean 19°), fixed by measuring each fingertip bone's own rotation;
    - the VRM path under `avatar:` changed the config hash when the work folder moved (moved to
      `paths:`).

---

## 2026-10-22 — Day 4 — Model B pilot (gloss → motion), ablation T, B0/B1 ("pipeline test")
- Setup:
  - Environment: desktop CPU, torch 2.14.1+cpu, 2 threads per run (OMP/MKL_NUM_THREADS=2).
  - Data: pilot50_v1 (40/5/5), features `fa89892d4908`. Inputs: G0 `gloss_auto` (markers removed)
    plus G0 tag tokens, or the normalised Bangla words (ablation T). Reviewed glosses are not used.
  - Frames: 208 values (9 body points in shoulder widths; wrist-relative hands; 52 blendshapes;
    head rotation), standardised on the train clips.
  - Model B: NAR Transformer d 192, 4 heads, 3+3 layers, ff 512, dropout 0.1; 2,663,441 parameters
    (gloss vocab 100). AdamW 5e-4, batch 8, patience 60 on val masked L1. Loss weights: hands ×2,
    λ_v 0.5, λ_len 0.1 (ADR-0026).
- Measured before the runs:
  - Hand world points are NOT hand-centred: |wrist| p50 0.551 m (p5 0.399, max 0.854), while wrist
    → middle fingertip p50 0.128 m. Features were changed to wrist-relative hands, and the runs
    made before that change were superseded.
  - Feature NaNs match the masks exactly. Shoulder width 0.309–0.339 m.
- Checks and results:
  - Unit tests: 14 new, 125 total pass. They cover the masked loss (zero gradient and no effect
    from missing or padded values), gap interpolation, the layout, metrics, B0/B1, model shapes,
    resume and the input guard.
  - Overfit 1 clip (`…overfit1…T133821Z`): train masked L1 0.808 → 0.041 (5.1%) in 400 epochs.
  - Overfit 40 clips (`…overfit40…T134024Z`): 0.707 → 0.136 (19.2%). Train MPJPE body 0.107 vs B0
    0.216; hands 23.8/24.8 mm vs B0 51.8/59.6 mm.
  - Full runs (`gloss…T133822Z`, `text…T133822Z`), 3 seeds each. Gloss best epochs 37/26/38; text
    best epochs 48/45/36. Model B values are the mean over 3 seeds (sd ≤ 0.01 body, ≤ 6 mm hands).
    Body and DTW are in shoulder widths, hands (L/R) in mm, duration error in seconds:

    | split | method | body | hands L / R | DTW body | duration err | velocity ratio | hand-energy ratio | diversity ratio |
    |---|---|---|---|---|---|---|---|---|
    | val | B (gloss) | 0.220 | 63.7 / 57.2 | 0.199 | 3.18 | 0.25 | 0.07 | 0.32 |
    | val | B (text) | 0.217 | 60.0 / 61.1 | 0.199 | 2.99 | 0.30 | 0.09 | 0.39 |
    | val | B0 | 0.235 | 63.2 / 57.1 | 0.215 | 3.20 | 0.23 | 0.05 | 0.00 |
    | val | B1 | 0.244 | 73.4 / 69.0 | 0.210 | 3.76 | 1.06 | 1.30 | 0.89 |
    | test | B (gloss) | 0.224 | 55.9 / 65.3 | 0.209 | 1.91 | 0.20 | 0.05 | 0.27 |
    | test | B (text) | 0.224 | 58.4 / 65.1 | 0.207 | 2.28 | 0.24 | 0.07 | 0.39 |
    | test | B0 | 0.221 | 58.2 / 59.7 | 0.208 | 2.08 | 0.17 | 0.04 | 0.00 |
    | test | B1 | 0.270 | 63.2 / 75.2 | 0.233 | 2.03 | 0.99 | 1.64 | 1.01 |

  - Kill-and-resume: a seed-42 gloss process was force-killed at epoch 50, then `--resume`
    (`…T134800Z`). Last and best checkpoints are weight-identical to the full run, and the metrics
    are identical.
- Notes:
  - Pilot "pipeline test" only (5 items per split, signer-dependent).
  - Model B and ablation T are about as good as mean motion (B0) on held-out clips and move far
    less than real signing (velocity ratio 0.2–0.3). B1 moves realistically but replays another
    sentence. Gloss vs text input shows no clear difference at this size.
  - DTW-MJE is computed for val/test only (cost).
  - The first seed's predictions for all 50 clips are in `seed42/predictions/` for Day 5.
  - Bugs found and fixed in my own code during the run: a too-coarse time code; hand coordinates not
    wrist-relative.

---

## 2026-10-22 — Day 3 Step 1 — Model A pilot, TEST mode (fake review data; ADR-0025)
> **TEST RUN.** The references are fake: they were derived from the sentence text, and no video was
> watched. None of these numbers is a Model A result. G0 is favoured because the references were
> made by editing its drafts.
- Setup:
  - Environment: desktop CPU, torch 2.14.1+cpu, sacreBLEU 2.6.0, branch `test-run-fake-review`
    (code commit `de6db35`), later merged into `main`.
  - Data: pilot50_v1 (40/5/5), `annotations/pilot50_v1_gloss_v01.csv` with 50 rows `team_reviewed`,
    `is_mock=true`. Command: `train-text2gloss --allow-test-data`.
  - A-GRU: emb 128, BiGRU 256, Bahdanau 256, GRU decoder 256, dropout 0.2, Adam 1e-3, batch 8,
    label smoothing 0.1, patience 30 on val greedy WER, beam 4 at the end.
  - Vocab (train only): src 98, tgt 88 (incl. 4 specials and the tag tokens). 1,713,752 parameters.
- Checks and results:
  - Guard: `gloss-validate` without the option → exit 1 (100 problems: 50 mock, 50 "not
    video-verified"). With the option → exit 0, `usable_for_training` 50. `train-text2gloss` without
    the option → exit 2 "Refusing to train". A split that differs from the manifest is refused
    (unit test).
  - Overfit: 1 sentence → 100% exact (beam) at epoch 4; 40 train sentences → 100% exact at epoch 12
    (`…overfit1…T125750Z`, `…overfit40…T125800Z`).
  - Full run `TEST_text2gloss_pilot50_20261022T125820Z`, 46 s. Seeds 42/43/44 stopped at epochs
    39/50/41 (best 9/20/11). G0 vs A-GRU (mean ± sd over 3 seeds):

    | split | G0 WER | G0 exact | A-GRU WER | A-GRU exact | A-GRU tags | A-GRU BLEU-4 | A-GRU chrF |
    |---|---|---|---|---|---|---|---|
    | train (40) | 34.5 | 15% | 1.4 ± 1.5 | 94% | 99% | 97.2 | 98.8 |
    | val (5) | 33.3 | 20% | 68.3 ± 7.3 | 0% | 87% | 8.4 | 33.8 |
    | test (5) | 33.3 | 0% | 69.8 ± 13.7 | 0% | 87% | 9.7 | 38.6 |

  - Kill-and-resume: a seed-42 process was force-killed after epoch 20, then `--resume`. The last and
    best checkpoints are weight-identical to the uninterrupted run, with identical metrics
    (`…T130107Z`). Resuming with other seeds is refused (exit 2).
  - Labels: 0 files under `work/runs/` lack the `TEST_` prefix. Every JSON file and checkpoint has
    `TEST_RUN: true`, and every log line starts with `[TEST]`.
  - `uv run pytest`: 111 passed.
- Notes:
  - The A-GRU memorises its 40 sentences. On held-out sentences it outputs near-copies of training
    sentences (e.g. 3323 → "তোমার প্রিয় রং কি" for all seeds). With 5 items per split, one item
    moves a score by 20 points.
  - BLEU-4 is 0 for any gloss under 4 tokens, so gloss WER is the main score.
  - Two bugs found and fixed: the overfit stop is now judged with beam search; resume now keeps
    the run's seeds. The superseded folders are `…overfit1…T125651Z`, `…overfit40…T125701Z` and
    `…T125920Z`.

---

## 2026-10-22 — Notebooks — structural check at the end of Session 3 (not executed)
- Setup: new thin notebooks `notebooks/01_manifest.ipynb`, `02_extract.ipynb`, `03_gloss.ipynb`
  (call `bdsl.cli.main` and package functions; paths from config only), plus the existing
  `00_env_check.ipynb`. Checked with nbformat 5.11.1 and Python `ast` in `.venv`; no cell was run, so
  no data was read.
- Metric(s) / checks: valid nbformat; no outputs and no execution counts; every code cell parses;
  imports come from `bdsl`; no absolute machine paths; the CLI commands they call exist; the config keys
  and functions they use exist.
- Result: all 4 notebooks pass.
  - `00_env_check`: 5 cells (3 code).
  - `01_manifest`: 8 cells (6 code): manifest, split, pilot-select; `pilot-copy --confirm` is
    commented out behind the approval note.
  - `02_extract`: 4 cells (3 code): extract (pilot50, VIDEO mode).
  - `03_gloss`: 5 cells (4 code): gloss-draft, gloss-validate.
  pytest: 93 passed (unchanged).
- Notes: running 01–03 would re-read data. The manifest resumes from its hash cache, extraction skips
  finished clips, and gloss-draft rewrites the identical file or refuses if rows are reviewed. Not done
  this session.

## 2026-10-22 — Annotations — Day 2 Step 2: gloss convention v0.1 + G0 drafts (Session 3)
- Setup:
  - `.venv` as before (no new packages).
  - Code: `src/bdsl/text/{gloss_rules,annotations}.py`; `bdsl.cli gloss-draft --data pilot50` and
    `gloss-validate`.
  - Inputs: FinalSheet2.xlsx (sentence text only, for the R5 word list) and
    dataset/pilot50_v1/pilot50_manifest.csv. No video opened.
  - Config hash 1563eb579556.
- Metric(s) / checks: rows and statuses; determinism (re-run SHA-256); validation of the real file;
  validator and overwrite-guard unit tests; input SHA-256 before/after; pytest.
- Result:
  - **Drafts:** `annotations/pilot50_v1_gloss_v01.csv` has 50 rows, all `auto_draft` (annotator
    `auto:G0-v0.1`, is_mock=false, reviewer fields empty). A re-run is byte-identical (SHA-256
    bdacd8355c4a…).
  - **G0 v0.1 over the 219 pilot tokens:**
    - R0 pronoun 46; R1 negation 4; R2 wh-word 1; R2b কি/কী 4;
    - R3 number 1; R4 Latin 1;
    - R5 genitive stem (`~`) 5;
    - R6 no rule (`?`) 157.
  - **gloss-validate:** 0 problems; 0 rows usable for training (no reviewed rows; REVIEWERS.csv is
    header only).
  - **Unit tests:** invalid rows are rejected:
    - a reviewed row with an unregistered reviewer;
    - an expert status from a team-role reviewer;
    - a missing gloss_reviewed; a future review date;
    - a mock row; a wrong sentence_norm; a bad status;
    - reviewer fields on a draft; an unknown index;
    - a rejected row without a note; the reviewer code "MOCK".
    The `gloss-draft` command refuses to overwrite a file with a reviewed row (the file stays
    byte-identical).
  - **Inputs unchanged:** FinalSheet2.xlsx and pilot50_manifest.csv SHA-256 identical before and after.
  - **pytest:** 93 passed (26 new).
- Notes:
  - One bug in my own tests (expected outputs were passed through norm_v1, which strips `?`); fixed
    before the real run.
  - G0 output is a pseudo-gloss. 157 of 219 tokens are left to the reviewer.

## 2026-10-22 — Features — Day 2 Step 1: MediaPipe extraction + QC on pilot50_v1 (Session 3)
- Setup:
  - `.venv` as before (no new packages).
  - Code: `src/bdsl/features/{layout,extract,qc}.py`; `bdsl.cli extract --data pilot50 --mode both`.
  - Inputs: the 50 pilot copies (`dataset/pilot50_v1/videos/`). Originals not opened.
  - Process: OpenCV decode with rotation; nearest-timestamp resampling to 15 fps; a fresh
    HolisticLandmarker per clip; blendshapes on; documented default thresholds; 5 worker processes.
  - Config hash f382a31af899.
- Metric(s) / checks: per-clip QC; VIDEO vs IMAGE comparison; privacy check of every .npz;
  kill-and-resume; pilot-copy SHA-256 and original size + mtime; pytest.
- Result:
  - **Extraction:** VIDEO feat_ver `fa89892d4908` and IMAGE feat_ver `395e878f9861`: 50/50 clips
    each, 0 failures. 4,806 grid frames per mode (from 9,613 source frames).
  - **Run time:** VIDEO 138.8 s, IMAGE 129.2 s; 4 min 33 s in total. Median 84 ms per detection with
    5 processes in parallel (25 ms single-process in the smoke test). About 7.4 MB per mode.
  - **QC, VIDEO mode, mean over clips:**
    - Coverage: pose 99.95%, face 99.4%, left hand 69.7%, right hand 35.7%, both hands 25.9%,
      any hand 79.5%.
    - Longest hand gap: left median 0.67 s (max 4.9 s); right median 1.7 s (max 11.9 s, clip 792).
    - Forearm-length coefficient of variation ≈ 0.15.
    - Wrist jitter: left 15.8 m/s², right 19.0 m/s².
    - ts_cv: max 0.064 (median 0).
    - Hand-side agreement with body wrists: median 0.90, minimum 0.49.
    - Median head |yaw|: 2.4°.
  - **By recording type** (VIDEO, mean coverage left / right / both; median agreement):
    - portrait (38): 0.760 / 0.251 / 0.229; 0.771
    - landscape (9): 0.586 / 0.725 / 0.404; 1.000
    - low-res (3): 0.230 / 0.602 / 0.208; 0.985
    - Left > right in 40 of 50 clips.
  - **VIDEO vs IMAGE** (`compare_pilot50.json`):
    - any hand +0.24 points for VIDEO (18 clips higher, 17 lower, 15 equal); both hands −0.18 points;
    - wrist jitter VIDEO 15.8 / 19.0 vs IMAGE 19.6 / 24.8 m/s² (left / right).
    - Owner chose VIDEO mode (ADR-0023).
  - **Privacy:** 150 .npz files checked (both modes and the resume test). No unexpected keys, no
    478-point face mesh, no image arrays.
  - **Kill-and-resume (VIDEO):** killed with 10 clips done and 0 temp files. The resume extracted 40;
    all 50 clips are array-identical to the uninterrupted run, so the extraction is deterministic.
    No leftover processes.
  - **Data unchanged:** the 50 pilot copies still match `pilot50_manifest.csv` (SHA-256); the 50
    originals' size + mtime are unchanged.
  - **pytest:** 67 passed (13 new: resampling, ts_cv, head rotation, QC maths, privacy check,
    feat_ver, read_meta).
- Notes:
  - QC values are reported without thresholds (open_questions G9).
  - Which real hand MediaPipe calls "left" is unknown (mirroring; open_questions G8).
  - Head rotation is an approximation from 4 face points; signs follow the code's convention.
  - Full-set estimate from the pilot rate (≈ 35 grid frames/s with 5 processes; ≈ 533k grid
    frames): about 4–4.5 h per mode. An estimate, not measured.

## 2026-10-22 — Dataset — Day 1 Step 2: manifest v1, split S1 v0, pilot50_v1 (Session 3)
- Setup:
  - `.venv` as in Day 1 Step 1, plus pandas 3.0.3 and openpyxl 3.1.5 (owner-approved; `uv.lock` now
    91 packages).
  - Code: `src/bdsl/{text,data}/`, `src/bdsl/cli.py`.
  - Commands: `uv run python -m bdsl.cli manifest --data full | split | pilot-select |
    pilot-copy --confirm`.
  - 6 worker processes. All 5,010 videos and the sheet were read-only.
- Metric(s) / checks:
  - ID set vs sheet; decodability; source size + mtime of all 5,010 videos and the sheet SHA-256,
    before and after;
  - exact duplicates; leakage groups; leakage checks on the real split; balance;
  - determinism (re-run hashes); pilot quotas; SHA-256 of the 50 copies; pytest.
- Result:
  - **Manifest v1** (2026-10-22T07:05Z; CSV SHA-256 2ff133cf6bb2…; config hash f7aa5765c6a6):
    - Time: 2 min 23 s wall (probe 138 s).
    - Files: 5,010 rows; ID set equals the sheet; 0 missing, 0 extra, 0 decode failures.
    - Duplicates: 3,456 unique SHA-256 (= representatives).
    - Sentences: 3,378 unique `norm_v1` sentences (NFC + `। . ? ! ,` → space + collapsed whitespace;
      990 rows change under NFC).
    - Leakage groups: 3,376 (size histogram 1:1915, 2:1380, 3:35, 4:30, 5:3, 6:7, 7:2, 8:1, 9:1,
      11:2). 0 label conflicts.
    - Video properties: portrait 4,302 / landscape 708; rotation 0°:3,142, 270°:1,838, 90°:18,
      180°:12; codec h264 2,819, hevc 2,181, VP90 10; 71,206,505,652 B; 1,059,409 declared frames;
      Σ(n_frames/fps) = 35,527 s (9.87 h).
    - Spot checks: 0.mp4 and 2.mp4 stored/display sizes agree with Day 1 Step 1.
  - **Sources unchanged:** size + mtime identical for all 5,010 videos, and the sheet SHA-256
    identical — before the run, after it, and after copying the pilot.
  - **Split S1 v0** (salt S1-v0, 80/10/10 by sha256(salt|group_id); CSV SHA-256 40481a5faedc…):
    - Groups 2,700 / 357 / 319 (80.0 / 10.6 / 9.4%).
    - Representative clips 2,759 / 368 / 329.
    - Leakage problems: none. No group, SHA-256, sentence or known link crosses splits.
    - The colour cluster (group g3456, 6 clips) is entirely in train.
  - **Balance, train / val / test (representatives):**
    - tokens 1–2: 112/13/5; 3–4: 1,619/221/191; 5–6: 953/126/123; 7+: 75/8/10
    - question (indicative): 171/20/15; negation (indicative): 165/25/18
    - landscape: 288/35/31
    - resolution 1080: 2,127/298/268; 720: 484/59/45; low (<500 px): 148/11/16
  - **pilot50_v1** (selection SHA-256 8affc876aace…; config hash 08230f0a1b63):
    - Counts and quotas: 40/5/5 from a pool of 3,378; quotas met (landscape 9, low-res 3, all
      duration quartiles: q1 15, q2 21, q3 6, q4 8); hard share 0.24.
    - Composition: 6 minimal-pair families × 4 train clips, plus 16 diversity train clips.
    - Held-out: chosen after the train clips. Option B (owner, ADR-0022): 6 of 10 held-out clips
      use only pilot-train words; 4 keep unseen words, listed per clip.
    - Copies: 50/50 SHA-256 identical to the manifest and the sources (723 MB).
  - **Determinism:** split and selection re-runs gave byte-identical CSVs.
  - **pytest:** 54 passed.
- Notes:
  - The 2026-10-22 count of 3,379 unique sentences (Phase 1 checks) used no NFC; with NFC it is
    3,378, matching 2026-10-21.
  - Indicative tags are word lists, not annotation: e.g. "সব সময়" ("always") counts as a time
    word. The sheet contains no `?`.
  - Before the first real run, my own code had three bugs, found by the tests or a manual review:
    - a pandas `index` column clashed with the row-tuple method;
    - synthetic test data used Latin digits;
    - stale wording in the generated protocol.
    All are fixed.
  - The first pilot list (option A, family siblings only) gave 1/10 held-out clips with seen words
    only. It was never copied.
  - The manifest meta records an earlier config hash than the pilot: only the `pilot` section
    changed afterwards, and that section is not used by the manifest or the split.
  - Timestamp irregularity (ts_cv) is measured during Day-2 extraction.

## 2026-10-22 — Environment + config — Day 1 Step 1 (Session 3)
- Setup:
  - Machine: desktop DESKTOP-4NDR99B, Windows 11 Pro.
  - Project `.venv` created with uv 0.10.8: CPython 3.12.13. Packages from `uv.lock` (88 resolved):
    mediapipe 0.10.35, opencv-contrib-python 5.0.0.93 (opencv-python absent), numpy 2.4.6,
    PyYAML 6.0.3, torch 2.14.1+cpu, matplotlib 3.11.2, pytest 9.1.1, ipykernel 7.4.0,
    nbclient 0.11.0, nbformat 5.11.1.
  - Model `work/models/holistic_landmarker.task`, downloaded from the official float16/latest URL:
    13,683,609 B, SHA-256 e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8 —
    identical to both copies in the earlier project. The hash is pinned in `configs/base.yaml`.
  - `notebooks/00_env_check.ipynb` executed headless (nbclient) → `work/reports/env_report.json`
    (gitignored).
  - Git at 1809048 plus uncommitted changes.
- Metric(s) / checks: pytest; the 8 env-check checks; an alternate BDSL_WORK_DIR; SHA-256 of the 2
  rotation clips before and after; git diff under dataset/.
- Result:
  - **pytest:** 30 passed.
  - **Env report:** overall pass, 8/8 checks (final run 06:50:41Z, config hash 0f64a5248617):
    - python: 3.12.13 inside `.venv`.
    - packages: all pins match; no OpenCV clash.
    - opencv_rotation:
      - 0.mp4: flag 270°; raw frame 1080×1920 (h×w) → auto-rotated 1920×1080 (portrait), one quarter
        turn, pixel-exact.
      - 2.mp4: flag 0°; frame unchanged at 1080×1920 (landscape).
    - mediapipe_holistic:
      - HolisticLandmarker present; created in 0.15 s.
      - Result fields: face_landmarks, pose_landmarks, pose_world_landmarks, left_hand_landmarks,
        left_hand_world_landmarks, right_hand_landmarks, right_hand_world_landmarks,
        face_blendshapes, segmentation_mask.
      - On 0.mp4 frame 96: 33 pose, 21 + 21 hand (image and world), 478 face, 52 blendshapes.
      - VIDEO mode works.
    - torch_devices: 2.14.1+cpu, 6 threads; CUDA no; MPS no; DirectML not installed.
    - write_permission: pass; no temp files left over.
    - cpu_benchmark:
      - 6 logical CPUs.
      - numpy 512×512 matmul ×20: 0.0187 s ≈ 287.7 GFLOPS (second run: 328.6).
      - MediaPipe IMAGE mode on 1920×1080: 33.4 ms/frame over 5 frames (first 38.3 ms, rest 32.1);
        second run: 36.6 ms/frame. Single-process smoke test only, not a full-dataset estimate.
  - **BDSL_WORK_DIR** pointed outside the project: every derived path moved, the config hash was
    unchanged, and the write test passed.
  - **Clip SHA-256** identical before and after: 0.mp4 ed3713970f46…1bb6, 2.mp4 111ece319ea3…1569.
    No git diff under dataset/.
- Notes:
  - The first notebook run failed `torch_devices` because of a bug in the check, not in torch: the
    expected sum of x @ x.T was hard-coded as 70 (correct: 83). The check now compares with numpy;
    the two later runs passed.
  - Windows-only warnings (zmq Proactor event loop; kernel over TCP) do not affect results.
  - Kaggle and Colab environments are not checked yet; the same notebook will report them.

## 2026-10-22 — Repository + dataset + environment — Phase 1 read-only checks (Session 3)
- Setup: Desktop DESKTOP-4NDR99B, system Python 3.14.4, OpenCV 5.0.0.93, pandas 3.0.3. Scripts in
  the session scratchpad only; nothing written to the project or dataset. Web: PyPI, npm registry,
  MediaPipe docs, GitHub API (unauthenticated).
- Metric(s) / checks: repo visibility; contents of SIGN_LANGUAGE_DATA/; sheet copy identity; Python
  installs; colour-cluster hashes and frame differences; token statistics; sample-clip headers.
- Result:
  - **Repo:** public (`visibility: public`); 50 sample videos in `origin/main`; no LICENSE file.
  - **SIGN_LANGUAGE_DATA/:** 5,012 entries = 5,010 MP4 + SESSION_LOG.md + FinalSheet2.xlsx; the
    copy's SHA-256 equals `initial_dataset/FinalSheet2.xlsx` (prefix 15348b36e11ea8f0); 71.2 GB in
    total.
  - **Python:** 3.14.4 (system) and 3.14.3 (uv); no 3.12; uv present; both opencv-python and
    opencv-contrib-python installed in system Python.
  - **Colour cluster:** 3456=5096, 3457=5100, 3458=5102 by SHA-256; all 1298×720, 30 fps, 181–183
    frames. Mean grey difference at 20 normalised positions:
    - 3456 vs 3458: 0.0 over the first 15 positions, 10.6–13.0 over the last 5;
    - 3456 vs 3457: 0.0–1.9, then 11.1–15.1;
    - 3457 vs 3458: 0.0–1.9, then 9.1–10.7;
    - within-clip reference ≈ 7.1–7.4.
  - **Sheet** (normaliser: `। . ? ! ,` → space, whitespace collapsed): 3,379 unique sentences;
    1,417 tokens; 646 in one sentence only; 2,872 sentences with all tokens seen elsewhere;
    2,588 in 1,086 one-word-difference families (largest 31).
  - **Sample headers:** 0.mp4 rotation 270°, 1.mp4 180°, 2.mp4 0°; fps 23.1–30.2.
- Notes:
  - The 3,379 vs 3,378 difference (2026-10-21) comes from different normalisers; the project
    normaliser will be versioned.
  - The cluster interpretation ("one recording edited onto three endings") is a proposal, not a
    verified fact.


## 2026-10-21 — Dataset + repository + environment — Read-only re-audit (Session 2)
- Setup:
  - Desktop `DESKTOP-4NDR99B`, Windows 11 Pro, system Python 3.14.4, pandas 3.0.3, openpyxl 3.1.5,
    OpenCV 5.0.0.93, PyAV 17.1.0, mediapipe 0.10.35.
  - Scripts lived in the session's temporary scratchpad only. They were not added to the repo and
    wrote nothing to the project or dataset.
  - Data: `dataset/initial_dataset/{FinalSheet2.xlsx, SIGN_LANGUAGE_DATA/, videos/}` and the old CSVs
    `D:\CSE498R\Sign_Language\CSE498R_v2\Sign_Language\outputs\{duplicate_groups,near_duplicate_groups}.csv`.
  - No frames decoded, except 3 single-frame rotation checks.
- Metric(s) / checks: sheet structure and counts; ID ↔ file mapping; sample ↔ full-set identity;
  duplicate-CSV consistency; header metadata of all files; rotation; packet-timestamp regularity;
  hardware/software; MediaPipe API.
- Result:
  - **Sheet:** `Sheet1` has 2 data columns (`Names`, `Index`); 5,010 rows, 5,010 unique Index (0–5460),
    0 blank sentences. Unique sentences: raw 3,414 · stripped 3,395 · punctuation-normalised
    (`। . ? ! ,` removed) 3,378. Vocabulary 1,398 whitespace tokens (20,974 tokens). Words per
    sentence 1–13, mean 4.19. Heuristic counts: 17 rows with Latin letters, 116 with digits, ~538
    question-like, ~264 negation-like (regex; indicative only).
  - **Files:** 5,010 MP4, 71,206,505,652 B; ID set == sheet Index set. All 50 `videos/` clips are
    SHA-256 identical to their `SIGN_LANGUAGE_DATA/` copies.
  - **Exact duplicates:** the old CSV has 1,516 groups / 3,070 files (1,486 pairs, 22 triples,
    8 quads). All groups are same-size, and 25/25 random groups are SHA-256 identical. All 14 same-size
    sets that differ from CSV groups were hashed and split exactly into CSV groups, so the CSV is
    complete for exact duplicates.
  - **After exact dedup:** 3,456 videos; 3,378 unique normalised sentences; 3,324 (98.4%) have one
    video, 41 have 2, 13 have 3–6.
  - **Index structure:** 1,424 of 1,516 second copies are at Index ≥ 4000.
  - **Label mismatches in exact groups:** 3 (3850/3851/5019/5020; 3882/3883/5017/5018; 1515/1569),
    all removed by punctuation normalisation. The colour near-duplicate cluster (old pHash CSV) was not
    re-checked.
  - **Codecs:** h264 2,819 · hevc 2,181 · vp9 10.
  - **Rotation (OpenCV `CAP_PROP_ORIENTATION_META`):** 0° 3,142 · 270° 1,838 · 90° 18 · 180° 12.
    OpenCV auto-applies it (decoded frames of 0.mp4 and 10.mp4 are 1920×1080 h×w). **Displayed:
    portrait 4,302 (85.9%), landscape 708.** 1080×1920: 3,425; 350 low-res clips (short side
    < 500 px), all in Index 3675–5415. PyAV reported rotation 0 for every file, so it is not usable
    for rotation.
  - **Duration:** min 1.30 · median 6.37 · mean 7.10 · p90 11.1 · max 47.73 s; total 9.89 h; declared
    frames 1,059,409.
  - **Frame rate:** average fps ≈30 for 4,686 files, ≈29 for 262, ≈24/23 for 32, ≈60/59 for 16.
    Every file has 1 audio stream.
  - **Packet-timestamp regularity** (80 clips = 50 sample + 30 random, seed 42): 55 constant
    (CV < 1%), 20 near-constant (1–10%), **5 irregular (≥ 10%)**: 3941 (max gap 333 ms), 3947, 3946,
    5451, 3939. This contradicts both the old "all VFR" and the old "0 badly VFR" claims.
  - **Hardware:** Ryzen 5 3500X 6C/6T, 23.9 GB RAM, Radeon RX 570 8 GB (driver 31.0.12027.9001), NVMe
    SSDs; D: 86 GB free.
  - **Software:** mediapipe 0.10.35 imports on Python 3.14; `vision.HolisticLandmarker` and
    `FaceLandmarker` present, `mp.solutions` absent. Not installed: torch, ffmpeg/ffprobe, conda.
  - **Web-checked:** mediapipe latest 1.1.1 (2026-10-14). torch-directml latest 0.2.5.dev240914
    (pre-release), Python 3.8–3.12 wheels only.
  - **Old outputs:** found at `D:\CSE498R\Sign_Language\CSE498R_v2\`. `D:\CSE498R\derived` (old
    features) does not exist; `Sign_Language/data/{keypoints,deduplicated}` are empty.
- Notes:
  - PyAV segfaulted (exit 139) during a long in-process packet-demux loop; it ran fine one file per
    subprocess.
  - Not re-run: pHash near-duplicates, audio content, MediaPipe coverage, signer estimate. Treat those
    old numbers as **reported**.
  - Full SHA-256 of all 5,010 files is deferred to the scale-up stage.

## 2026-09-27 — Repository — Real-folder verification + worktree removal (Session 1)
- Setup: `git rev-parse`, `git worktree list`, `git status`, `git diff --cached -M --name-status`,
  `find`, `grep` in `C:/Workspace/NSU/sign_avatar_cse498r` on branch `main`.
- Metric(s) / checks: session location; dataset files unchanged; analyses cleaned (D3); references to
  the old worktree; worktree removal.
- Result: Session ran in the real folder (`.git` is the main git dir). Dataset: 53 files are 100%
  renames (3 sheets + 50 videos), `videos.txt` deleted, `dataset/README.md` added. Analyses 01–07 were
  edited to remove the medical/dialect context (similarity 87–99%); 08 is a 100% rename. Remaining
  medical/dialect mentions are paper findings, except two "Medical" table rows in 07 (flagged, E3).
  No symlinks, and no project file depends on the worktree. Worktree folder was already empty; its
  branch had no commits beyond `main`. `git worktree prune -v` removed the stale metadata;
  `git worktree list` now shows only the real folder. `rmdir` of the empty folder failed ("Device or
  resource busy").
- Notes: The empty folder can be deleted once the process holding it (likely the old Claude session)
  is closed.

## 2026-09-27 — Repository — Bootstrap reorganization check
- Setup: `git status` / `find` on branch `claude/bangla-sign-avatar-setup-699b03` after the `git mv`
  moves; spreadsheets read with Python's standard library (zipfile + XML).
- Metric(s) / checks: every moved file shows as a rename; file counts per folder; no leftover files in
  the old folders; sheet row counts and video ↔ Index alignment.
- Result: 70 files were moved (6 PDFs + notice README, 8 analyses, reading form, 3 sheets, 50 videos +
  `videos.txt`). 69 are byte-identical renames; the only content edit was the reading form (3 lines
  removed, ADR-0003). The 17 `templates/` files were deleted (git shows one of them as "renamed" to
  `session_protocol.md` only because the content is similar).
  `FinalSheet.xlsx` 3,491 rows; `FinalSheet2.xlsx` 5,010 rows (superset); all 50 videos match an Index
  in `FinalSheet2.xlsx`.
- Notes: The first `git mv` failed with "Permission denied" because the shell's working directory was
  inside the folder being moved. Retrying from the repo root worked.
