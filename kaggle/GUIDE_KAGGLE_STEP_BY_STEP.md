# Kaggle, step by step (for a first-time user)

This guide takes you from "no Kaggle account" to "results in the paper". Short sentences, one action at a
time. After every step there is a **What you should see** checklist. If what you see is different, stop
and tell Claude what you see (a screenshot or the exact text helps).

Kaggle changes its screens from time to time. If a button has a slightly different name, look for the
closest one. All times marked [ESTIMATE] are guesses until we measure them.

---

## 1. Create an account and verify your phone

You need a verified phone number. Without it, Kaggle does not allow GPU or Internet in notebooks.

1. Open **https://www.kaggle.com** in your browser.
2. Click **Register** (top right). Sign up with Google or with an e-mail address.
3. Confirm your e-mail if Kaggle asks.
4. Click your **profile picture** (top right) → **Settings**.
5. Find **Phone verification**. Click **Not verified** / **Verify**.
6. Choose your country (Bangladesh, +880), type your phone number, and click **Send code**.
7. Type the code from the SMS and confirm.

**What you should see**
- [ ] You are logged in; your profile picture is at the top right.
- [ ] In Settings, Phone verification says **Verified**.

---

## 2. Check your GPU quota and session limit (write the real numbers down)

1. Click **Create** (the **+** button, top left) → **New Notebook**.
2. A notebook editor opens. On the right side there is a panel. Open **Session options** (or the ⋮ / settings
   part of that panel).
3. Look for **Accelerator**. Note which GPUs are offered (for example "GPU T4 x2", "GPU P100").
4. Look for the **GPU quota** line (for example "GPU 0 / 30 h used this week"). Write down the numbers.
5. Look for the **session** or **time limit** information if shown. Write it down.
6. Close this notebook without saving (or delete it later).

**What you should see**
- [ ] At least one GPU accelerator is offered.
- [ ] You wrote down: GPU types, weekly GPU hours, session limit. Send them to Claude (they go into the
      project record, open question G3).

---

## 3. Make the upload file and create a PRIVATE dataset

### 3a. The upload file (already made by the PowerShell script)
`kaggle\tools\run_local_steps.ps1` builds one zip file:
`D:\sign_avatar_cse498r\kaggle\work\upload\bdsl-k400-<commit>.zip` (about 5.95 GB: the 400 source videos total 5.94 GB in manifest_v1).
To see its size again, open **PowerShell** and run:

```powershell
Get-Item D:\sign_avatar_cse498r\kaggle\work\upload\bdsl-k400-*.zip | Select-Object Name, @{n='GB';e={[math]::Round($_.Length/1GB,2)}}
```

The zip contains only: `data/` (400 videos + manifests + report + lock), `code/` (the committed code),
`UPLOAD_MANIFEST.csv` (SHA-256 of every file), `PACKAGE_INFO.json`, `README_UPLOAD.md`. No `.venv`, no `work/`,
no `kaggle.json`, no checkpoints — the script refuses anything outside this list.

### 3b. Create the dataset
1. On Kaggle, click **Datasets** in the left menu.
2. Click **+ New Dataset**.
3. Drag the zip file into the upload area (or click **Browse Files** and choose it).
   Upload time depends on your Internet: about 40 minutes at 20 Mbit/s, about 80 minutes at 10 Mbit/s
   [ESTIMATE]. Keep the tab open.
4. **Title**: `bdsl-k400`. (The URL ending becomes `bdsl-k400`.)
5. **Visibility**: choose **Private**. Check it twice. Never choose Public.
6. Click **Create**. Kaggle now processes the files (several minutes). Kaggle usually unpacks a zip into
   folders; the notebooks also work if it keeps the zip as one file.
7. When it is ready, open the dataset page → **Settings** (or **⋮ → Settings**) → **Sharing** → add your
   team members by Kaggle username. Give them **Can view** (or **Can edit** only if they must change it).

**What you should see**
- [ ] The dataset page says **Private** (a lock symbol).
- [ ] The file browser shows `data/`, `code/`, `UPLOAD_MANIFEST.csv`, `PACKAGE_INFO.json`, `README_UPLOAD.md`
      (or one zip file).
- [ ] Only your team members are listed under Sharing.

---

## 4. Check the upload

Notebook **01** checks every file against `UPLOAD_MANIFEST.csv` (SHA-256). You will run it in step 6.
Until then, check on the dataset page that the size shown is about the size of your zip.

**What you should see**
- [ ] Dataset size ≈ zip size (a few % difference is normal).

---

## 5. Create a notebook, add the dataset, turn on GPU and Internet

You do this once for each of the 10 notebooks (00 to 09).

1. **Create** (+) → **New Notebook**.
2. Load our notebook file: menu **File → Import Notebook** → **Browse** → choose for example
   `D:\sign_avatar_cse498r\kaggle\notebooks\00_env_check_kaggle.ipynb` → **Import**.
3. Give the notebook the same name (click the title at the top left), for example `00_env_check_kaggle`.
4. Right panel → **Input** → **+ Add Input** → **Datasets** / **Your Work** → find `bdsl-k400` → click **+** (Add).
5. From notebook 03 on, also add the previous notebook's output: **+ Add Input** → **Notebooks** /
   **Your Work** → choose the previous notebook (for 03: `02_extract_features`) → **+**.
6. Right panel → **Session options**:
   - **Accelerator**: as the notebook's first cell says (GPU for 00, 04, 05, 06; None for the others).
   - **Internet**: **On** (needed for `pip install`).
7. You do not need to change any path. The first code cell finds the data and the code by itself.

**What you should see**
- [ ] The right panel lists `bdsl-k400` under Input (and the previous notebook from 03 on).
- [ ] Accelerator and Internet are set as the notebook's first cell says.

---

## 6. Run the notebooks 00 to 09, in order

Always run a notebook with **Save Version → Save & Run All** (step 7). It runs every cell in order,
saves all printed outputs inside the notebook, and keeps the output files for the next notebook. After each
notebook, paste the last lines (the PASS/FAIL list) to Claude and wait for "OK, next".

| # | Notebook | Accelerator | Extra Input | Time [ESTIMATE] | Check at the end |
|---|---|---|---|---|---|
| 00 | env check | GPU | — | 3–6 min | `GPU visible` PASS, `MEDIAPIPE: OK` |
| 01 | data/split check | None | — | 3–8 min | `UPLOAD CHECK: PASS`, 10/10 split checks PASS |
| 02 | extract features | None | (own earlier version if it stopped) | 30–90 min | `EXTRACTION COMPLETE`, 400/400, rotation OK |
| 03 | G0 glosses | None | output of 02 | < 2 min | IDENTICAL × 3 |
| 04 | Model B (gloss) | GPU | output of 03 | 20–60 min | dry run on cuda, 3 seeds, resume diff < 1e-3 |
| 05 | ablation T (text) | GPU | output of 04 | 20–60 min | 3 seeds |
| 06 | Model A (G0 refs) | GPU | output of 05 | 10–40 min | 3 seeds, label "agreement with the rule glosser" |
| 07 | freeze + VAL + TEST | None | output of 06 | 10–20 min | lock written; **run only once** |
| 08 | report | None | output of 07 | < 3 min | `final_test_done: true` |
| 09 | avatar | None | output of 08 | < 5 min | 5 skeleton videos |

Total GPU time about 1–3 hours [ESTIMATE]; MediaPipe (02) runs on the CPU and uses no GPU quota.

---

## 7. Save Version: "Save & Run All" vs "Quick Save"

1. Click **Save Version** (top right).
2. Choose **Save & Run All (Commit)**. Give a short name, for example `run 1`. Click **Save**.
   - **Save & Run All** = Kaggle starts a fresh session, runs every cell from the top, and saves the notebook
     **with all outputs** plus the files in `/kaggle/working` (our `k400/` folder). Use this every time.
   - **Quick Save** = saves the notebook text only, without running it. Not useful for results.
3. You can close the tab. Progress: bottom left **View Active Events**, or the notebook page → **Versions** / **Logs**.
4. When it finishes, open the notebook's page. The **Output** tab (or **Data → Output**) shows `k400/`.

**What you should see**
- [ ] The version status is **Complete** (green), not Error.
- [ ] The notebook view shows the printed outputs and the final PASS/FAIL list.
- [ ] The Output tab contains the `k400` folder.

---

## 8. Download the outputs to your PC and check them

1. Open the last notebook's page (09; it contains everything from 00–09) → **Output** → **Download** (all files as a zip).
2. Unzip into a new folder, for example `D:\kaggle_downloads\run1\`. You get a `k400\` folder.
3. Check the files against the hash list Kaggle wrote (PowerShell, project root):

```powershell
cd D:\sign_avatar_cse498r
uv run python kaggle\src\k400_run.py verify-download D:\kaggle_downloads\run1\k400
```

4. Download each notebook **with its outputs**: open the notebook's version page → **⋮** → **Download**
   (or in the editor **File → Download Notebook**). Save them over `kaggle\notebooks\` only when Claude says
   so (they then contain the real outputs for the paper).
5. Copy the small result files into the project (Claude will give the exact command): `outputs\tables`,
   `outputs\figures`, `outputs\RESULTS_SUMMARY.md`, `outputs\registry.csv`, `outputs\eval\*\*.json/csv`,
   `outputs\runs\*\*.json/csv/log`. Never copy `.pt` checkpoints or `.npz` files into Git.

**What you should see**
- [ ] `DOWNLOAD CHECK: PASS`.

---

## 9. If a session stops (timeout, quota end) — resume

- **Notebook 02 (extraction):** it stops starting new clips after `MAX_MINUTES` (300) and saves what it has.
  Make a **new version** of 02: **+ Add Input** → **Notebooks** → `02_extract_features` (its earlier output),
  then **Save & Run All** again. Finished clips are skipped.
- **Training (04–06):** every epoch saves `ckpt_last.pt`. In a new version, add the stopped version's
  output as Input, then replace the training cell's command with
  `S.bdsl(*B, "--resume", "/kaggle/working/k400/outputs/runs/<run folder>")` (Claude will give you the
  exact line). Changed inputs are refused automatically.
- **Weekly GPU quota used up:** wait for the weekly reset, or ask Claude about continuing on the desktop CPU.

---

## 10. Common errors and fixes

| What you see | Cause | Fix |
|---|---|---|
| `GPU visible ... FAIL`, device `cpu` | Accelerator is None | Session options → Accelerator → GPU; run again |
| `pip ... could not resolve` / `Temporary failure in name resolution` | Internet is Off | Session options → Internet On (needs phone verification) |
| `The private dataset is not attached` | dataset not added | + Add Input → `bdsl-k400` |
| `CUDA out of memory` | GPU memory too small | tell Claude; fix: `--set gloss2motion.train.batch_size=4` |
| `MEDIAPIPE: FAILED on both routes` | install problem | stop; paste the output to Claude |
| `MODEL FILE SHA-256 DIFFERS` | Google changed the model at the URL | stop; tell Claude (fallback: upload our model file as a small private dataset) |
| `SPLIT_LOCK.json ... changed` | a manifest was edited | never edit manifests; re-upload the original package |
| `Refusing a result run: the code is not a clean commit` | code changed after packaging | rebuild the package from a clean commit |
| `The final test evaluation already ran` | 07 ran before | correct behaviour; do not run the test again |
| Session ended / "Notebook timed out" | time limit | see section 9 |
| Version status **Error** | a cell failed | open the version → Logs; paste the last 30 lines to Claude |

---

## 11. Putting the results into the paper

- **Numbers:** only from `outputs/RESULTS_SUMMARY.md` (each number has its run ID and source file).
- **Tables (LaTeX):** `outputs/tables/T1_split.tex` (data), `T2_feature_coverage.tex` (MediaPipe coverage),
  `T3_training.tex` (epochs, time, GPU), `T4_modelB_test.tex` (main result), `T5_paired_test.tex`
  (Model B minus baselines, 95% CI), `T6_modelA_test.tex` (agreement with G0), `T7_error_analysis_test.tex`,
  `T8_train_val_test.tex` (over-fitting). Same names with `.csv` (data) and `.md` (reading).
- **Figures (PNG):** `F1_split_summary.png`, `F2/F3/F4_curves_*.png` (learning curves), `F5_methods_test.png`
  (main comparison with CIs), `F6_error_analysis_test.png`.
- **Wording you must keep:** small-scale and signer-dependent; test evaluated once after freezing; low
  coordinate error is not proof of correct sign language; Model A = agreement with the rule glosser
  (G0 pseudo-gloss); no human or expert validation.

---

## 12. What NOT to do

- **Never make the dataset public.** Never share the videos outside the team.
- **Never put `kaggle.json`** (your API token) or any password in the project folder or in Git.
- **Never tune on test.** Never run notebook 07 a second time to "see if it gets better".
- Never edit a manifest or move a video between `train/ val/ test/`.
- Never `git push` without the owner's decision (the GitHub repository is public).
- Never present G0 or Model A numbers as BdSL correctness.
