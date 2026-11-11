# কোন model চালাবেন, output কোথায়, কীভাবে দেখাবেন

তারিখ: 2026-11-11। **নতুন canonical paths দিয়ে Python/pytest/demo: not run by assistant।** নিচের commands আপনার PC-তে চালাতে হবে। কোনো command fail করলে থামুন এবং সম্পূর্ণ output দিন।

## যাচাই করা বর্তমান অবস্থা — 2026-11-11

- Owner PC: `uv run pytest -q` → **238 passed in 46.03s** (cleanup-এর আগে)। Cleanup-এর পরে Python tests assistant চালায়নি।
- pilot50: `demo_validation/demo_20261111T150500Z/`; Model B 91 frames, B1 train Index 3225; দুইটি motion JSON পুরোনো reference-এর সঙ্গে byte-identical।
- k400: `demo_validation/demo_20261111T151556Z/`; validation Index 912, Model B 135 frames, B1 train Index 903; unknown tokens নেই, logged hash checks true। Saved checkpoint/run/VRM hashes independently মিলেছে।
- দুইটি canonical viewer browser-এ দেখা হয়েছে। এটি rendering/engineering check; BdSL correctness বা expert validation নয়।
- Cleanup: **2,053 files / 911,823,762 bytes**, 194 verified-empty directories সরানো হয়েছে। Retained 1,931 files-এর SHA-256 ও 127 unique checkpoint/metrics/run hashes মেলে; mismatch 0। Counts/byte reduction approved list-এর সঙ্গে মেলে। Raw videos/ZIP, ভিন্ন line-ending corpus variant ও k600 অক্ষত।

নতুন যাচাই করা exports দেখার URLs:

- [pilot50](http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/pilot50/demo_validation/demo_20261111T150500Z/)
- [k400](http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/k400/demo_validation/demo_20261111T151556Z/)

## Project root ও existing environment

```powershell
Set-Location -LiteralPath 'D:/sign_avatar_cse498r'
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:BDSL_WORK_DIR = ''
$env:BDSL_DATA_ROOT = ''
$env:K400_DATA_ROOT = ''
$env:K400_STATE_ROOT = ''
$env:K400_VIDEO_ROOT = ''

uv run pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; share the full output.' }
```

এটি নতুন dependencies install/download করতে দেবে না। Assistant tests চালায়নি। পুরোনো TEMP demo evidence নতুন path acceptance নয়।

## pilot50 model — seed 42

```powershell
uv run python -m bdsl.cli --env local demo --data pilot50 --sentence "আমি স্কুল যাই" --model-run gloss2motion_gloss_pilot50_20261022T133822Z --seed 42
if ($LASTEXITCODE -ne 0) { throw 'Pilot demo failed; share the full output.' }
```

Input checkpoint: `versions/pilot50/runs/gloss2motion_gloss_pilot50_20261022T133822Z/seed42/ckpt_best.pt`।

Default output: `versions/pilot50/demo/demo_<UTC timestamp>/`। `--data` বাদ দিলেও pilot50; নতুন default আর `work/demo/` নয়। Explicit আলাদা test output চাইলে `--out-root ./versions/pilot50/demo_validation` যোগ করুন।

Regression reference এখন `versions/pilot50/demo/demo_20261022T141520Z/`। একই sentence/seed-এর আগের PC artifacts-এ দুইটি motion JSON byte-identical ছিল; migration-এর পরের pilot export-এর দুইটি JSON-ও byte-identical মেলানো হয়েছে।

## k400 model — validation Index 912, seed 42

```powershell
uv run python -m bdsl.cli --env local demo --data kaggle400 --sentence "আমার নানা অনেক ভালো" --model-run gloss2motion_gloss_kaggle400_20261023T135437Z --seed 42
if ($LASTEXITCODE -ne 0) { throw 'k400 demo failed; share the full output.' }
```

Input checkpoint: `versions/k400/outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/seed42/ckpt_best.pt`। Metadata/vocab/glosses/features এই version-এর `data/` ও `processed/` থেকে আসে; B1 শুধু train pool থেকে আসে।

Default output: `versions/k400/demo/demo_<UTC timestamp>/`। Explicit test output চাইলে `--out-root ./versions/k400/demo_validation` যোগ করুন। CLI যে `out_dir` print করবে সেটিই actual folder; নাম আগে থেকে জানা নেই।

## Avatar দেখানো

আলাদা PowerShell terminal-এ:

```powershell
Set-Location -LiteralPath 'D:/sign_avatar_cse498r'
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'
uv run python -m http.server 8765 --bind 127.0.0.1
```

নতুন run-এর actual folder name দিয়ে browser-এ খুলুন:

- pilot50: `http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/pilot50/demo/<actual-folder>/`
- k400: `http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/k400/demo/<actual-folder>/`

Explicit `--out-root` দিলে URL-তেও সেই folder দিতে হবে। আগে থেকে থাকা historical files দেখার URLs:

- [pilot50 পুরোনো reference](http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/pilot50/demo/demo_20261022T141520Z/)
- [k400 পুরোনো export, Index 1255](http://127.0.0.1:8765/web/avatar_viewer/?demo=/versions/k400/outputs/avatar/1255/)

Viewer এখন shared `shared/models/vrm/Base_Female.vrm` ব্যবহার করে। Pinned jsDelivr libraries-এর জন্য browser internet লাগে। Server বন্ধ করতে Ctrl+C। Migration-এর পরের দুইটি validation export এই canonical URLs-এ browser-এ দেখা হয়েছে।

## Output files

| File | কী আছে |
|---|---|
| `motion_modelB.json` | Model B-এর generated motion ও retargeted avatar targets |
| `motion_B1.json` | শব্দের overlap দিয়ে বাছা ভিন্ন training recording-এর derived motion |
| `skeleton_side_by_side.mp4` | Generated skeleton comparison; raw video নয় |
| `demo_log.json` | Version, sentence, seed/run/checkpoint hashes, input checks ও unknown tokens |
| `LIMITATIONS.md` | Demo দেখানোর সময় জানাতে হবে এমন সীমা |

## Notebooks ও future work

pilot workflow-এর 7টি notebook `versions/pilot50/notebooks/`-এ; k400-এর 10টি `versions/k400/notebooks/`-এ। Shared executable code root `src/bdsl/`-এ। নিজের notebook editor-এ existing Python 3.12 .venv kernel ব্যবহার করুন। Historical notebook outputs নতুন validation নয়; k400 notebook 07/final TEST আবার চালাবেন না।

নতুন pilot training runs যাবে `versions/pilot50/runs/`-এ। k400 training/eval/report outputs-এর root `versions/k400/outputs/`; preprocessing root `versions/k400/processed/`। এগুলো storage mapping, নতুন training/evaluation চালানোর অনুমোদন নয়। Existing completed run resume করতে migration test-এর সঙ্গে code-provenance/resume checks-ও লাগবে।

k600 এখন নেই। Compatible future demo-এর আলাদা config/state-root লাগবে; বর্তমান full training CLI এখনও pilot50/kaggle400-specific। সম্পূর্ণ k600 training-কে এখন config-only বলবেন না। [HOW_TO_ADD_NEW_VERSION.md](HOW_TO_ADD_NEW_VERSION.md) দেখুন।

## Supervisor-কে কী বলবেন

Version map, seed-42 avatar comparison ও saved k400 tables/figures দেখান। Model B main run ব্যবহার করুন; TEST/DRYRUN/NFP/superseded checks-কে result বলবেন না।

বলুন: “Bangla থেকে G0 pseudo-gloss, তারপর learned motion ও VRM avatar-এর prototype। Pilot gloss annotations fake। Human-reviewed BdSL references দিয়ে Model A result নেই; G0REF শুধু rule-glosser agreement।”

বলুন: “B0 শক্ত baseline: pilot test body MPJPE Model B প্রায় 0.224, B0 প্রায় 0.221। k400-এ কিছু coordinate gain আছে, কিন্তু gloss-model velocity প্রায় 0.14 ও hand energy প্রায় 0.03 of real। সব results ছোট scale-এর ও signer-dependent।”

বলুন: “Expert validation নেই; low coordinate error সঠিক বা বোধগম্য BdSL প্রমাণ করে না। B1 একটি ভিন্ন training sentence replay করে।” Pilot report scope শেষ 2026-10-22; k400 notebook 07-এর documented failed first attempt-ও report করতে হবে।
