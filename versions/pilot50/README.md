# pilot50

## বর্তমান canonical layout — 2026-11-11

এটি active canonical version folder। Owner PC-তে pytest 238 passed (46.03s), দুইটি real-checkpoint demo তৈরি হয়েছে এবং দুইটি viewer browser-এ লোড হয়েছে। Reviewed 2,053 redundant files সরানো হয়েছে; retained hashes/counts মেলে। Assistant Python চালায়নি। বর্তমান commands: [RUN_AND_SHOW.md](../RUN_AND_SHOW.md)। নিচের Gate 4 copy counts historical snapshots।


তারিখ: 2026-11-11। এটি 50-clip **pipeline test**; split 40 train / 5 val / 5 test।

## কী আছে

- `features/fa89892d4908/`: 50 NPZ, QC ও extraction metadata; VIDEO mode, 15 fps।
- Full-set manifest/split index এখন shared/dataset_index/; pilot/-এ এই version-এর selection ও manifest metadata।
- annotations/: FAKE pilot CSV; shared convention root annotations/GLOSS_CONVENTION_v0.1.md-এ। Real review নয়।
- runs/: নিচের দুইটি current main run-এর canonical files।
- `demo/`: complete exports `demo_20261022T141520Z` ও `demo_20261026T034134Z`।
- reports/: historical environment/executed-notebook evidence; features/-এ mode-comparison report।
- notebooks/: 7টি pilot-workflow notebook; engineering_checks/ ও history/: non-result checks।

Gate 4 measured snapshot: 205 files, 287,080,095 bytes; 205/205 source/copy SHA-256 identical। এই README ও ভবিষ্যৎ outputs ওই count-এর বাইরে। Raw videos copy হয়নি।

## প্রধান runs ও seeds

| Run ID | ভূমিকা | Seeds |
|---|---|---|
| `gloss2motion_gloss_pilot50_20261022T133822Z` | Current Model B; G0 pseudo-gloss input; demo-তে এই run | 42, 43, 44 |
| `gloss2motion_text_pilot50_20261022T133822Z` | Text-input ablation; gloss demo-তে ব্যবহার হবে না | 42, 43, 44 |

Selection seed: 20261022। `feat_ver=fa89892d4908`; gloss vocab size 100; predicted-length cap 300 frames। Demo seed 42 একটি model দেখায়; saved Model B mean metrics তিনটি seed-এর।

প্রতি run-এ checkpoints, `metrics.json`, `run.json`, `per_item.csv`, `standardizer.npz`, curves ও predictions আছে। দুই run মিলে 12 checkpoint। পুরোনো run metadata-তে `dirty=true` আছে। Per-run `env.json` পাওয়া যায়নি; `reports/env_report.json` পুরোনো shared environment report, তার বিকল্প training-time provenance দাবি নয়।

## চালানোর commands — owner PC-তে যাচাই করা

Project root-এর PowerShell-এ, existing environment ব্যবহার করে:

```powershell
Set-Location -LiteralPath 'D:/sign_avatar_cse498r'
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'

uv run python -m bdsl.cli --env local demo --data pilot50 --sentence "আমি স্কুল যাই" --model-run gloss2motion_gloss_pilot50_20261022T133822Z --seed 42 --out-root ./versions/pilot50/demo
```

নতুন output: `versions/pilot50/demo/demo_<UTC timestamp>/`; একই timestamp থাকলে নতুন suffix। নতুন default output-ও `versions/pilot50/demo/`; `--out-root` explicit override। `--data`-র default `pilot50`।

Inputs এখন `versions/pilot50/runs/`, `features/`, `annotations/` ও `pilot/pilot50_manifest.csv` থেকে পড়া হয়। Corpus-এর sheet reference আগের `dataset/initial_dataset/FinalSheet2.xlsx`; raw video inference-এ খোলা হয় না। Shared models/reviewer register/full-set index আলাদা canonical shared paths-এ।

Viewer-এর জন্য অন্য terminal-এ project root থেকে:

```powershell
uv run python -m http.server 8765 --bind 127.0.0.1
```

[Copied পুরোনো pilot export](http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/pilot50/demo/demo_20261022T141520Z/)। নতুন export-এর URL-এ তার actual folder দিন। নতুন pilot50 validation export browser-এ দেখা হয়েছে। Original `shared/models/vrm/Base_Female.vrm` ও pinned jsDelivr libraries-এর জন্য browser internet লাগে।

## engineering checks / not results

নিচের checks মূল results নয়। এগুলো এখন এই version-এর engineering_checks/, history/ অথবা historical demo subfolders-এ রাখা হয়েছে:

| বর্তমান relative location | কেন মূল result নয় |
|---|---|
| `engineering_checks/runs/TEST_text2gloss_*` — 7 runs | Fake review data; TEST only; Model A performance নয় |
| `engineering_checks/runs/gloss2motion_gloss_overfit1_pilot50_20261022T133821Z` ও `...overfit40_pilot50_20261022T134024Z` | Memorisation checks |
| `history/runs/gloss2motion_gloss_pilot50_20261022T134800Z` | Kill-and-resume check |
| `engineering_checks/runs/_superseded_day4_hand_offset/` — 6 runs | পুরোনো ভুল hand-coordinate implementation |
| `engineering_checks/features/395e878f9861/`, `engineering_checks/features_resume_test/` | IMAGE comparison / resume check; chosen training features নয় |
| `demo/_superseded/`, `demo_20261026T034304Z` | পুরোনো অথবা অসম্পূর্ণ exports; শেষটির demo log/limitations নেই |

## যা সৎভাবে বলতে হবে

Annotation CSV-র 50/50 row `is_mock=true`; `status=team_reviewed` লেখা থাকলেও বাস্তবে video review হয়নি। Model A-এর real reviewed-BdSL result নেই। Demo-তে G0 ব্যবহৃত হয়। Model B G0 columns ও real-recording-derived features নেয়; mock review labels-কে real BdSL review বলা যায় না। k400-এর G0REF-ও rule-glosser agreement মাত্র।

Saved pilot test body MPJPE: Model B 0.22394, B0 0.22107; body unit shoulder widths। B0 শক্ত baseline; এই metric-এ Model B তাকে ছাড়ায়নি। k400-এ কিছু coordinate gain থাকলেও তার motion অনেক ছোট—pilot-এর ফল দিয়ে k400 ব্যাখ্যা করা যাবে না।

Small-scale, signer-dependent ফল; কোনো BdSL expert validation নেই। Low coordinate error সঠিক grammar, comprehensibility বা natural signing প্রমাণ করে না। Hands missing/mirroring, monocular depth ও coarse facial mapping-এর সীমা আছে; unseen tokens `<unk>` হয়।

`research/reports/PILOT_TEST_VERSION_COMPLETE_REPORT.md`-এর scope 2026-10-22 পর্যন্ত। তার পুরোনো Kaggle-status statements বর্তমান k400 status নয়। Owner PC pytest 238 passed; pilot motion regression byte-identical এবং নতুন viewer browser-এ দেখা হয়েছে।
