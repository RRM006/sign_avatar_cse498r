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
**(TBD — decide with owner.)** The evaluation method is not chosen yet (ADR-0002). Options found in the
literature are listed in `open_questions.md` C5. They are candidates, not decisions.

## Planned test cases
None yet. There is no system to test. Add test cases once the design is chosen.

---

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
