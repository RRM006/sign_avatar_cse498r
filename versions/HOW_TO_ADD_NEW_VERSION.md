# নতুন version যোগ করার পদ্ধতি

তারিখ: 2026-11-11। **Future work only; commands not run।** এখন কোনো `k600/` folder, dataset বা `configs/data/kaggle600.yaml` তৈরি হয়নি।

এই guide একই split/G0/208-value motion schema-তে compatible trained run পাওয়া গেলে demo ও overview যোগ করার জন্য। নতুন clip selection, feature extraction ও training-এর আলাদা owner approval লাগবে। বর্তমান training CLI-তে `--data` choices `pilot50` ও `kaggle400`; তাই সম্পূর্ণ k600 training workflow-কে এখন config-only বলা হচ্ছে না। Generic demo resolver ও তার future-config tests লেখা হয়েছে; Owner PC full pytest suite 238 passed; real k600 experiment/demo এখনো not started।

## Naming ও layout contract

Display/folder name হবে `k600`; CLI/config name `kaggle600`; data subset name `kaggle600_v1`।

ভবিষ্যৎ নিজস্ব state-এ এই relative paths প্রয়োজন:

- `versions/k600/data/SPLIT_LOCK.json`, `subset_manifest.csv` ও `{train,val,test}/<split>_manifest.csv`
- `versions/k600/processed/features/{train,val,test}/<Index>.npz`
- `versions/k600/processed/glosses/gloss_g0_<split>.csv` ও `g0_corpus_v1.txt`
- `versions/k600/processed/vocab/vocab_modelB_gloss_input.json` ও নিজস্ব QC/vocab reports
- `versions/k600/outputs/runs/<approved run ID>/`: run/metrics/env JSON, checkpoints, curves, per-item data ও standardizer
- ভবিষ্যৎ fresh demo outputs: `versions/k600/demo/demo_<UTC timestamp>/`

এখানে raw videos যাবে না। pilot50/k400-এর features, vocab, standardizer বা runs-এর সঙ্গে shared path, junction বা hardlink ব্যবহার করবেন না। Source selection/split ও training artifacts নতুন experiment-এর নিজস্ব সত্য provenance বহন করবে। এই guide সেই experiment শুরু করার অনুমোদন নয়।

## ধাপগুলো

1. Owner-এর সঙ্গে clip selection, split, seeds, evaluation protocol ও data-sharing scope নির্ধারণ করুন। এগুলো এখন TBD।
2. নিজস্ব approved metadata, G0 drafts, features ও trained gloss-input run প্রস্তুত করুন। Train-only vocab/standardizer/B1 pool রাখুন; test lock অক্ষত রাখুন।
3. শুরু থেকেই একটি canonical versions/k600/ state ব্যবহার করুন। Existing state import/move করার আগে -WhatIf, source/target SHA-256 ও collision checks করুন; overwrite নয়। Checkpoints/metrics/run JSON, file count ও byte totals শেষে মিলিয়ে নিন। একই state-এর আরেকটি archive copy রাখবেন না।
4. নতুন data config তৈরি করুন। শুধু নাম/path যোগ করলেই demo নতুন schema আবিষ্কার করে না: উপরের একই layout এবং সত্য run fingerprints প্রয়োজন।
5. Tests চালান; validation-এর একটি বাক্যে seed নির্বাচন করে demo চালান; output/error সংরক্ষণ করুন। Test split দিয়ে smoke demo নির্বাচন করবেন না।
6. নিজের README-তে measured/reported/unknown, limitations ও provenance লিখুন। Owner-এর দেখার পরে version map-এ নতুন row যোগ করুন; পুরোনো version বদলাবেন না।

## Config তৈরি করার future command — not run

Compatible future run উপস্থিত হওয়ার পরে `REPLACE_WITH_APPROVED_RUN_ID` বদলে project root থেকে নিচের block চালানোর কথা। এটি existing config overwrite করবে না; model settings ও fps সত্য run metadata থেকে নেয়। এখন এটি চালাবেন না।

```powershell
Set-Location -LiteralPath 'D:/sign_avatar_cse498r'
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'

@'
import json
from pathlib import Path
import yaml

root = Path("D:/sign_avatar_cse498r")
run_id = "REPLACE_WITH_APPROVED_RUN_ID"
run = root / "versions/k600/outputs/runs" / run_id
meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
if meta.get("data") != "kaggle600" or meta.get("input") != "gloss":
    raise ValueError("A genuine kaggle600 gloss-input run is required")
cfg = {
    "data": {"name": "kaggle600", "subset": "kaggle600_v1"},
    "paths": {
        "demo_data_root": "${project_root}/versions/k600",
        "demo_state_root": "${project_root}/versions/k600",
        "demo_dir": "${paths.demo_state_root}/demo",
        "work_dir": "${paths.demo_state_root}/work",
    },
    "features": {"fps": meta["fps"]},
    "gloss2motion": meta["gloss2motion_config"],
}
target = root / "configs/data/kaggle600.yaml"
with target.open("x", encoding="utf-8") as handle:
    yaml.safe_dump(cfg, handle, allow_unicode=True, sort_keys=False)
print(target)
'@ | uv run python -
```

এই template বর্তমান G0-v0.1/norm_v1 ও feature schema ধরে। Representation/normalisation বদলালে আলাদা design/code review প্রয়োজন। Settings/hash মেলাতে run metadata নিজে বদলাবেন না। Split-layout run-এর legacy `pilot_manifest_sha256` field-এও সেই experiment-এর split-lock hash লাগে; সত্য training process সেটি লিখবে।

`paths` section config hash-এর বাইরে; অন্য settings training metadata-এর সঙ্গে মিলতে হবে। `--data kaggle600`-এর জন্য নতুন demo code branch যোগের পরিকল্পনা নেই; runtime acceptance এখনো **not run**।

## Future validation/demo commands — not run

Future experiment ও config owner-approved হয়ে উপস্থিত হলে, project root থেকে:

```powershell
Set-Location -LiteralPath 'D:/sign_avatar_cse498r'
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'

uv run pytest -q
uv run python -m bdsl.cli --env local demo --data kaggle600 --sentence "REPLACE_WITH_VALIDATION_SENTENCE" --model-run REPLACE_WITH_APPROVED_RUN_ID --seed REPLACE_WITH_RECORDED_SEED --out-root ./versions/k600/demo
```

Viewer path হবে `/versions/k600/demo/<actual folder>/`, বর্তমান `web/avatar_viewer/` page-এ। Shared project code/viewer ও shared/models/vrm/Base_Female.vrm dependency থাকবে; experimental data ও run folders আলাদা থাকবে। Package/model install, download বা upload-এর অনুমতি এই guide দেয় না।
