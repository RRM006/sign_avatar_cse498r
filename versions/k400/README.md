# k400

## বর্তমান canonical layout — 2026-11-11

এটি active canonical version folder। Owner PC-তে pytest 238 passed (46.03s), দুইটি real-checkpoint demo তৈরি হয়েছে এবং দুইটি viewer browser-এ লোড হয়েছে। Reviewed 2,053 redundant files সরানো হয়েছে; retained hashes/counts মেলে। Assistant Python চালায়নি। বর্তমান commands: [RUN_AND_SHOW.md](../RUN_AND_SHOW.md)। নিচের Gate 4 copy counts historical snapshots।


তারিখ: 2026-11-11। 400 clips: 320 train / 40 val / 40 test। Folder/display name `k400`; CLI/config identifier `kaggle400`।

## কী কোথায়

এই canonical folder-এ `processed/features/{train,val,test}/`-এ 320/40/40 NPZ, সঙ্গে QC, vocab ও G0 glosses আছে। `data/`-তে manifests, selection metadata ও split lock আছে; raw videos নেই। `outputs/`-এ মূল runs, saved eval, tables, figures, predictions ও avatar exports আছে।

Historical download source ছিল kaggle/work/downloads/run1/k400/; পুরোনো download/summaries consolidation শেষে সরানো হয়েছে। Active metadata/state: versions/k400/। Desktop demo config:

- `paths.demo_data_root = ${project_root}/versions/k400`
- `paths.demo_state_root = ${project_root}/versions/k400`

Demo ও training দুটির data/state roots এখন `versions/k400/`; metadata ও processed/runs সেখানেই। Raw videos আলাদা `paths.k400_video_root` দিয়ে আগের `kaggle/data/` থেকে পাওয়া যায়। শুধু paths পরিবর্তন; experiment settings অপরিবর্তিত।

Gate 4 measured snapshot: 1,694 files, 620,021,009 bytes; সব source/copy SHA-256 identical। এই README ও ভবিষ্যৎ outputs ওই count-এর বাইরে।

## মূল runs ও seeds

| Run ID | ভূমিকা | Seeds |
|---|---|---|
| `gloss2motion_gloss_kaggle400_20261023T135437Z` | মূল trained Model B; G0 gloss input; এই run দিয়ে demo | 42, 43, 44 |
| `gloss2motion_text_kaggle400_20261023T141059Z` | Trained text ablation | 42, 43, 44 |
| `G0REF_text2gloss_kaggle400_20261023T142908Z` | Trained A-GRU against G0 references; rule-glosser agreement only | 42, 43, 44 |

Selection ও bootstrap seed: 20261023। Features: `fa89892d4908`, VIDEO mode, 15 fps। Model B gloss vocab 408 tokens; text vocab 420। Predicted-length cap 360 frames। Demo seed 42; saved mean results তিনটি seed-এর।

প্রতি copied run-এ `run.json`, `env.json`, `metrics.json`, per-item/curves ও checkpoints আছে; Model B runs-এ `standardizer.npz` ও predictions আছে। মোট 18 checkpoint। Training provenance: package commit `933e9032ac3a3664e447c4e658a335f0ed621ffa`, clean package; Python 3.13.15 / Torch 2.11.0+cu128। Owner PC-তে Torch 2.14.1+cpu দিয়ে এই real checkpoint-এর demo output পাওয়া ও hashes মিলেছে। Assistant Python চালায়নি।

Saved training config hash: `83e62cae0fe05fcd092bbd50ad93a3d6143b4e82b9d833b172d2d499e5f5d453`। নতুন demo keys শুধু `paths`-এ; config hash function এই section বাদ দেয়। Owner PC full test suite: **238 passed**।

## চালানোর commands — owner PC-তে যাচাই করা

Validation Index 912: “আমার নানা অনেক ভালো”; stored gloss-input tokens train vocab-এ আছে।

```powershell
Set-Location -LiteralPath 'D:/sign_avatar_cse498r'
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'

uv run python -m bdsl.cli --env local demo --data kaggle400 --sentence "আমার নানা অনেক ভালো" --model-run gloss2motion_gloss_kaggle400_20261023T135437Z --seed 42 --out-root ./versions/k400/demo
```

নতুন output: `versions/k400/demo/demo_<UTC timestamp>/`। `--out-root` বাদ দিলে default `work/demo/`। Input checks train+val মিলিয়ে হয়; vocab ও saved standardizer train-only, B1-ও train থেকে আসে। Test evaluation পুনরায় চালানো এই command-এর কাজ নয়।

Viewer server project root থেকে:

```powershell
uv run python -m http.server 8765 --bind 127.0.0.1
```

[Copied পুরোনো k400 export, Index 1255](http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/k400/outputs/avatar/1255/)। এটি saved test-sentence export; validation Index 912-এর নতুন demo নয়। অন্য copied exports: 1863, 2513, 3061, 3232। নতুন output হলে URL-এ `/versions/k400/demo/<actual folder>/` দিন। নতুন validation Index 912 export browser-এ দেখা হয়েছে। Original VRM asset ও CDN internet প্রয়োজন।

## engineering checks / not results

এগুলো এখন engineering_checks/runs/-এ; main results-এর outputs/runs/ থেকে আলাদা:

| Pattern | সংখ্যা | ভূমিকা |
|---|---:|---|
| `DRYRUN_*` | 3 | এক-step checks |
| `NFP_gloss2motion_gloss_kaggle400_*` | 2 | Resume checks; not for paper |
| `G0REF_text2gloss_overfit1_*`, `G0REF_text2gloss_overfit40_*` | 2 | Memorisation checks |

Historical registry.csv-তে engineering runs-এর পুরোনো path references অপরিবর্তিত আছে। Overfit metadata-তেও `for_paper=true` পাওয়া গিয়েছিল; সেই flag একা result নির্বাচন করে না। Main roles দেখুন `outputs/frozen_config.json`-এ।

## Saved results ও সীমা

এগুলো পুরোনো saved results; নতুন evaluation চালানো হয়নি। Model B gloss TEST body DTW প্রায় 0.181, B0 0.199, B1 0.198 shoulder widths। কিছু coordinate metric-এ gain আছে। পাশাপাশি velocity ratio প্রায় 0.14 ও hand-energy ratio প্রায় 0.03 of real: motion strongly damped। Text ablation-এর coordinate ফল কাছাকাছি। বিস্তারিত `outputs/tables/T4_modelB_test.md`, `outputs/tables/T5_paired_test.md` ও `outputs/RUN1_NOTES.md`।

Model A-এর human-reviewed BdSL result নেই; G0REF WER 19.7 হলো G0 rule-glosser agreement। Pilot annotations FAKE (`is_mock=true`); pilot test body MPJPE-তে Model B প্রায় 0.224, B0 প্রায় 0.221। B0 শক্ত baseline।

সব ফল small-scale, signer-dependent; expert validation নেই। Low coordinate error সঠিক BdSL প্রমাণ করে না। `<unk>`, missing hands, mirroring ও coarse facial mapping-এর সীমা আছে। Pilot report-এর scope শেষ 2026-10-22।

## Test lock ও provenance

Final lock: `outputs/FINAL_TEST_LOCK.json`, created 20261023T151119Z; result `FINAL_test_20261023T151119Z`। Successful final evaluation একবার হয়েছে। Notebook 07-এর আগের failed attempt-এ test rows memory-তে পড়া হয়েছিল, কিন্তু কোনো result print/save হয়নি; owner-approved দ্বিতীয় attempt-এর কথা `outputs/RUN1_NOTES.md`-এ আছে। Notebook 07 / final evaluation পুনরায় চালাবেন না।

`provenance/STATE.json` source ও copy দুইটিই 3,057 bytes, একই SHA-256। Historical manifest-এ 2,869 bytes আছে: hash লেখার পরে finish event যোগ হওয়ার পরিচিত issue; file অপরিবর্তিত রাখা হয়েছে। `provenance/OUTPUT_HASHES.csv` পুরো original download-এর historical তালিকা; তার relative paths historical download layout-এর; engineering files এখন আলাদা location-এ। Current move-verification manifest দিয়ে migration যাচাই করুন।

Owner PC pytest 238 passed; k400 demo log/files ও browser viewer যাচাই হয়েছে। Assistant Python চালায়নি; cleanup-এর পরে full pytest আবার চালানো হয়নি।
