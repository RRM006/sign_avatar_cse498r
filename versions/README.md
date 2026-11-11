# Versions — বর্তমান project map

তারিখ: 2026-11-11। Root: `D:/sign_avatar_cse498r`।

এই folders-ই model-এর canonical inputs ও outputs। Consolidation ও reviewed duplicate cleanup শেষ। Raw data ও প্রয়োজনীয় historical/provenance artifacts তাদের নির্ধারিত জায়গায় আছে।

| Version | Clip / split | নিজের files | চালানোর পরিচয় | অবস্থা |
|---|---|---|---|---|
| pilot50 | 50; 40 train / 5 val / 5 test | [pilot50/](pilot50/README.md): features, annotations, runs, demo, notebooks, engineering checks | `--data pilot50` (default) | PC pytest **238 passed**; demo artifacts ও viewer যাচাই হয়েছে |
| k400 | 400; 320 train / 40 val / 40 test | [k400/](k400/README.md): processed, data metadata, outputs, notebooks, helper src/tools, engineering checks | `--data kaggle400` | PC pytest **238 passed**; demo artifacts ও viewer যাচাই হয়েছে |
| k600 | Selection / split TBD | এখন folder/data/config নেই; [guide](HOW_TO_ADD_NEW_VERSION.md) আছে | ভবিষ্যতে `kaggle600` | **not started** |

Shared engine একবারই আছে: root `src/bdsl/`, `configs/`, `tests/`, `web/`, `pyproject.toml`, `uv.lock`। এগুলো শুধু pilot50-এর নয়। `shared/models/`-এ MediaPipe/VRM assets; `shared/dataset_index/`-এ full-set manifest ও split index। Shared reviewer register/convention root `annotations/`-এ থাকে।

Raw videos নিজেদের আগের জায়গায় আছে: `dataset/` ও `kaggle/data/{train,val,test}/videos/`। Raw-video upload ZIP আগের `kaggle/work/upload/`-এ আছে; versions-এ নেওয়া হয়নি। Source manifests-এ pilot50/k400-এর চারটি train clip Index একই (2224, 2906, 2958, 2973); তাদের experiment state আলাদা রাখা হয়েছে।

Migration measured: 1,388 files / 1,227,494,033 bytes move। এরপর reviewed 2,053 redundant files / 911,823,762 bytes ও 194 empty directories সরানো হয়েছে। Retained 1,931 file SHA-256, 127 critical hashes এবং file-count/byte reduction মেলে; mismatch 0। Gate 4 copy counts historical evidence।

চালানো, output ও viewer: [RUN_AND_SHOW.md](RUN_AND_SHOW.md)। পুরোনো work/kaggle paths ধরে নতুন কাজ করবেন না। CLI-তে explicit `--out-root` থাকলে সেই override ব্যবহার হবে।

Honest facts: pilot gloss annotations FAKE (`is_mock=true`); human-reviewed BdSL references দিয়ে Model A-এর real result নেই। G0REF কেবল rule-glosser agreement। B0 শক্ত baseline: pilot body MPJPE-তে Model B প্রায় 0.224, B0 প্রায় 0.221। k400-এ কিছু coordinate gain আছে, কিন্তু motion বাস্তব recording-এর চেয়ে অনেক ছোট। Results small-scale, signer-dependent; expert validation নেই; low coordinate error সঠিক BdSL প্রমাণ করে না। Pilot report scope শেষ 2026-10-22।

Public repo: heavy features/checkpoints/videos/state commit করা যাবে না। Owner 2026-11-11-এ selective ignore policy অনুমোদন করেছেন: version-এর source, docs ও notebooks publish হতে পারে; version training/data artifacts, features, checkpoints, run/history/engineering/demo state এবং shared dataset indexes/model assets local থাকবে। `.gitignore` এই scope enforce করে; পুরো `/versions/` ignore করা হয়নি।
