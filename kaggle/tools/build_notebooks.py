"""Regenerate kaggle/notebooks/00–09 (outputs empty). Run: `uv run python kaggle/tools/build_notebooks.py`.

The notebooks are thin: every real step is a command of `bdsl.cli` or `kaggle/src/k400_run.py`, run as a
subprocess whose output is printed into the notebook (and therefore saved inside the .ipynb by Kaggle's
"Save & Run All"). Editing a notebook by hand is fine; re-running this script overwrites it.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parents[1] / "notebooks"

SETUP = '''# Cell 1 - Setup (the same in every notebook). Finds the data and the code, sets the paths, and copies the
# outputs of earlier notebooks (added with "Add Input") into /kaggle/working/k400 so results accumulate.
import os, sys, zipfile, pathlib, json
NOTEBOOK = "{name}"

def _find_root():
    base = pathlib.Path("/kaggle/input")
    if base.is_dir():
        for dirpath, dirnames, filenames in os.walk(base):
            if "UPLOAD_MANIFEST.csv" in filenames and "PACKAGE_INFO.json" in filenames:
                return pathlib.Path(dirpath)
            depth = len(pathlib.Path(dirpath).relative_to(base).parts)
            dirnames[:] = [] if depth >= 4 else [d for d in dirnames if d not in ("videos", "k400")]
        zips = sorted(base.rglob("bdsl-k400-*.zip"))
        if zips:  # Kaggle kept the upload as one zip file: unpack it once (a few minutes)
            dest = pathlib.Path("/tmp/k400_dataset")   # /tmp is not saved as Output
            if not (dest / "UPLOAD_MANIFEST.csv").is_file():
                print("Unpacking", zips[0], "->", dest)
                zipfile.ZipFile(zips[0]).extractall(dest)
            return dest
        raise FileNotFoundError("The private dataset is not attached. Right panel: Add Input -> Your Datasets -> bdsl-k400.")
    here = pathlib.Path.cwd().resolve()
    for c in [here, *here.parents]:
        if (c / "pyproject.toml").is_file() and (c / "kaggle" / "src" / "k400").is_dir():
            return c
    raise FileNotFoundError("Open this notebook inside the project folder, or on Kaggle with the dataset attached.")

DATASET_ROOT = _find_root()
CODE_ROOT = DATASET_ROOT / "code" if (DATASET_ROOT / "code" / "pyproject.toml").is_file() else DATASET_ROOT
for _p in (CODE_ROOT / "kaggle" / "src", CODE_ROOT / "src"):
    sys.path.insert(0, str(_p))
from k400.setup import setup
S = setup(DATASET_ROOT, CODE_ROOT, NOTEBOOK)'''


def header(title, purpose, kaggle, inputs, outputs, time, checks, extra=""):
    return new_markdown_cell(f"""# {title}

**Purpose.** {purpose}

**Kaggle settings.** {kaggle}

**Inputs.** {inputs}

**Outputs** (under `/kaggle/working/k400/`, saved by *Save Version → Save & Run All*). {outputs}

**Expected run time** [ESTIMATE, not measured yet]. {time}

**What to check.** {checks}
{extra}
> Honesty rules: label every number measured or estimated; results are small-scale and signer-dependent;
> the test split is used once (notebook 07); low coordinate error is not proof of correct sign language;
> G0 glosses are pseudo-glosses, not BdSL annotation; no human or expert validation exists.""")


def md(text):
    return new_markdown_cell(text)


def code(text):
    return new_code_cell(text)


def finish(checks: str) -> str:
    return f"S.finish(checks=[\n{checks}\n])"


NB = {}

TEST_TABLE = """import pandas as pd
from IPython.display import display
m = json.load(open(S.state_root / "outputs/eval" / lock["results"] / "metrics.json"))
b = m["model_b_and_baselines"]["methods"]
KEYS = ("mpjpe_body", "dtw_body", "mpjpe_lhand", "mpjpe_rhand")
rows = []
for k, v in b.items():
    vals = {x: v["mean_sd_over_seeds"][x]["mean"] for x in KEYS} if "mean_sd_over_seeds" in v else {x: v["summary"][x] for x in KEYS}
    rows.append({"method": k, **{x: round(y, 3) for x, y in vals.items()}})
display(pd.DataFrame(rows))
for comp, d in m["model_b_and_baselines"]["paired_differences"].items():
    x = d["dtw_body"]
    print(f"{comp:30s} DTW body diff {x['estimate']:+.3f} [{x['low']:+.3f}, {x['high']:+.3f}] excludes 0: {x['excludes_zero']}")
print("Model A (agreement with the rule glosser, G0 pseudo-gloss):", {k: round(v["mean"], 1) for k, v in m["model_a"]["mean_sd_over_seeds"].items()})"""

NB["00_env_check_kaggle"] = [
    header("00 — Environment check on Kaggle",
           "Record the real machine (GPU name, Python, PyTorch, CUDA, disk) and prove that MediaPipe 0.10.35 installs "
           "and runs on a real frame of one of our videos — before any long run.",
           "Accelerator **GPU** (T4 or P100, whichever is offered) · Internet **On**.",
           "The private dataset `bdsl-k400` only.",
           "`outputs/env/env_report.json`, `outputs/env/mediapipe_route.json`.",
           "about 3–6 minutes (pip install + model download + one frame).",
           "The last cell says **NOTEBOOK RESULT: PASS**; `GPU visible` is PASS; `MEDIAPIPE: OK via main` (or via "
           "fallback). If MediaPipe FAILS on both routes, stop and paste the output to Claude before going on."),
    code(SETUP.format(name="00_env_check_kaggle")),
    md("## Step 1 — GPU, Python, CUDA, disk (real values, saved to `outputs/env/env_report.json`)"),
    code('import subprocess\ntry:\n    print(subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout or "nvidia-smi: no output")\n'
         'except FileNotFoundError:\n    print("nvidia-smi not found: no NVIDIA GPU in this session")\nrc_env = S.k400("env-report")'),
    md("## Step 2 — MediaPipe 0.10.35: install and run on one real video frame\n"
       "Main route: `pip install mediapipe==0.10.35 opencv-contrib-python==5.0.0.93` into this Python. If that fails, "
       "the pinned **fallback** is tried automatically: a separate Python 3.12 made with `uv`, with the desktop's exact "
       "versions. Notebook 02 uses whichever route works."),
    code('rc_mp = S.k400("mp-setup")'),
    md("## Step 3 — Verdict"),
    code('env = json.load(open(S.state_root / "outputs/env/env_report.json"))\n'
         'mp = json.load(open(S.state_root / "outputs/env/mediapipe_route.json"))\n'
         'gpus = env["device"]["gpu_names"]\n'
         'print("Python        :", env["python"])\nprint("PyTorch / CUDA:", env["device"]["torch"], "/", env["device"]["torch_cuda_version"])\n'
         'print("GPU           :", gpus or "NONE - turn on the GPU accelerator (GUIDE step 5)")\n'
         'print("Free disk     :", env["disk_free_gb_working"], "GB in /kaggle/working")\n'
         'print("MediaPipe     :", mp["route"], "->", mp.get("python"))\n'
         'print("Probe         :", mp.get("probe"))\n'
         'if not mp["ok"]:\n    print("\\nBOTH ROUTES FAILED. Do not run notebook 02. Paste this whole output to Claude. Backup option: '
         'extract features on the desktop (kaggle/README.md, section Local extraction).")'),
    code(finish('    ("GPU visible to PyTorch", bool(gpus)),\n    ("MediaPipe 0.10.35 runs on a real frame", mp["ok"]),\n'
                '    ("model file SHA-256 equals configs/base.yaml", mp["model"]["ok"]),')),
]

NB["01_data_split_check"] = [
    header("01 — Data and split check",
           "Prove that the upload arrived complete and unchanged (SHA-256 of all 400 videos and every code file), that "
           "the split is leakage-free, and show the train / val / test tables and charts.",
           "Accelerator **None** (CPU is enough) · Internet Off is fine.",
           "The private dataset `bdsl-k400`.",
           "`outputs/data_check/` (verification output saved in this notebook).",
           "about 3–8 minutes (hashing about 5.9 GB).",
           "`UPLOAD CHECK: PASS`, `RESULT: PASS (10 passed, 0 failed, 0 skipped)`, counts 320 / 40 / 40."),
    code(SETUP.format(name="01_data_split_check")),
    md("## Step 1 — Every uploaded file against `UPLOAD_MANIFEST.csv`"),
    code('rc_upload = S.k400("verify-upload", "--root", str(DATASET_ROOT))'),
    md("## Step 2 — Leakage and consistency tests (the same as `kaggle/src/verify_split.py`)"),
    code('rc_split = S.k400("verify", "--require-videos")'),
    md("## Step 3 — Tables per split (from the manifests)"),
    code('import pandas as pd\nfrom IPython.display import Image, Markdown, display\n'
         'sub = pd.read_csv(DATASET_ROOT / "data/subset_manifest.csv", encoding="utf-8-sig")\n'
         'display(sub.groupby("split").agg(clips=("index", "size"), groups=("group_id", "nunique"), '
         'mean_duration_s=("duration_s", "mean"), minimal_pair_heldout=("mp_role", lambda s: (s == "heldout").sum())))\n'
         'for col in ["length_bucket", "question", "negation", "orientation", "resolution_bucket", "duration_quartile"]:\n'
         '    display(pd.crosstab(sub[col], sub["split"], margins=True))\n'
         'meta = json.load(open(DATASET_ROOT / "data/SELECTION_META.json", encoding="utf-8"))\n'
         'display(pd.DataFrame(meta["oov"]).drop(columns="train_vocabulary_size", errors="ignore"))\n'
         'print("train vocabulary:", meta["oov"]["train_vocabulary_size"], "word types")'),
    md("## Step 4 — Chart and the split report"),
    code('display(Image(filename=str(DATASET_ROOT / "data/SPLIT_SUMMARY.png")))\n'
         'display(Markdown((DATASET_ROOT / "data/SPLIT_REPORT.md").read_text(encoding="utf-8")))'),
    code('(S.state_root / "outputs/data_check").mkdir(parents=True, exist_ok=True)\n'
         'json.dump({"upload_check_exit": rc_upload, "split_check_exit": rc_split}, open(S.state_root / "outputs/data_check/result.json", "w"))\n'
         + finish('    ("every uploaded file identical (SHA-256)", rc_upload == 0),\n    ("all 10 split checks pass", rc_split == 0),\n'
                  '    ("counts 320/40/40", sub["split"].value_counts().to_dict() == {"train": 320, "val": 40, "test": 40}),')),
]

NB["02_extract_features"] = [
    header("02 — MediaPipe Holistic feature extraction (Kaggle CPU)",
           "Extract the same features as the pilot (VIDEO mode, 15 fps grid, `feat_layout_v1`, no face mesh or image "
           "stored) for all 400 clips, one folder per split, with QC, failures and hand coverage. Resume-safe.",
           "Accelerator **None** (MediaPipe runs on the CPU here; this saves GPU quota) · Internet **On** (pip + model).",
           "Dataset `bdsl-k400`. **If a previous version of this notebook stopped early:** also *Add Input* → that "
           "version's Output; finished clips are then skipped.",
           "`processed/features/{train,val,test}/<Index>.npz`, `processed/qc/qc.csv`, `failures.csv`, "
           "`hand_coverage_summary.csv`, `extract_run.json`.",
           "30–90 minutes for 400 clips (≈ 42,000 frames; desktop pilot rate 34.6 frames/s with 5 processes; Kaggle "
           "CPU speed unknown — `extract_run.json` records the real time).",
           "`EXTRACTION COMPLETE`, 400/400 clips, failures 0, privacy OK True, rotation OK True. If it says NOT COMPLETE "
           "because of the time budget: Save Version, then run a new version with this version's Output added as Input."),
    code(SETUP.format(name="02_extract_features")),
    md("## Settings"),
    code("MAX_MINUTES = 300   # no new clip is started after this; the version then finishes and saves\nWORKERS = None      # None = one process per CPU core"),
    md("## Step 1 — MediaPipe 0.10.35 (main route, else the pinned fallback)"),
    code('rc_mp = S.k400("mp-setup")\nmp = json.load(open(S.state_root / "outputs/env/mediapipe_route.json"))\n'
         'assert mp["ok"], "MediaPipe failed on both routes: stop and paste the output to Claude"\nEXTRACT_PY = mp["python"]\nprint("extraction runs with:", EXTRACT_PY)'),
    md("## Step 2 — Extraction (prints progress; safe to resume)"),
    code('args = ["extract", "--max-minutes", str(MAX_MINUTES)] + (["--workers", str(WORKERS)] if WORKERS else [])\n'
         'rc_extract = S.k400(*args, python=EXTRACT_PY)'),
    md("## Step 3 — Quality control"),
    code('import pandas as pd\nfrom IPython.display import display\nrun = json.load(open(S.state_root / "processed/qc/extract_run.json"))\n'
         'print(json.dumps({k: run[k] for k in ("feat_ver", "mediapipe", "platform", "clips_with_features", "clips_expected", '
         '"failures_or_missing", "privacy_ok_all", "rotation_ok_all", "seconds_this_run", "stopped_by_time_budget")}, indent=1))\n'
         'display(pd.read_csv(S.state_root / "processed/qc/hand_coverage_summary.csv"))\n'
         'fails = pd.read_csv(S.state_root / "processed/qc/failures.csv")\nprint("failures / missing:", len(fails))\ndisplay(fails.head(20))'),
    code(finish('    ("all 400 clips have features", run["clips_with_features"] == 400),\n    ("no failures", run["failures_or_missing"] == 0),\n'
                '    ("privacy check: no face mesh / image stored", run["privacy_ok_all"]),\n'
                '    ("rotation: decoded size = manifest display size", run["rotation_ok_all"]),\n'
                '    ("feat_ver equals the pilot (same MediaPipe, model, settings)", run["feat_ver"] == "fa89892d4908"),')),
]

NB["03_gloss_g0"] = [
    header("03 — G0 pseudo-glosses and TRAIN-only vocabularies",
           "Write G0 v0.1 drafts for all 400 sentences (status `auto_draft`). These are **pseudo-glosses made by a rule "
           "from the Bangla text — NOT BdSL annotation**, nobody checked them against the videos. Build the vocabularies "
           "from TRAIN only.",
           "Accelerator **None** · Internet Off is fine.",
           "Dataset `bdsl-k400` + **Add Input → Output of notebook 02** (carries the features forward).",
           "`processed/glosses/gloss_g0_{train,val,test}.csv`, `processed/vocab/*.json`, `vocab_report.json`.",
           "under 2 minutes.",
           "`compare_with_committed`: IDENTICAL for train, val and test (the same drafts as the desktop made)."),
    code(SETUP.format(name="03_gloss_g0")),
    code('rc_gloss = S.k400("gloss", "--compare-with", str(CODE_ROOT / "kaggle/processed/glosses"))'),
    code('import pandas as pd\nfrom IPython.display import display\n'
         'g = pd.read_csv(S.state_root / "processed/glosses/gloss_g0_train.csv", encoding="utf-8-sig")\n'
         'print("LABEL: G0 pseudo-gloss (auto_draft) - NOT a BdSL annotation")\n'
         'display(g[["index", "sentence_norm", "gloss_auto", "tags_auto", "status"]].head(10))\n'
         'print(json.dumps(json.load(open(S.state_root / "processed/vocab/vocab_report.json")), indent=1, ensure_ascii=False))'),
    code(finish('    ("G0 files identical to the committed copies", rc_gloss == 0),\n'
                '    ("320 + 40 + 40 rows, all auto_draft", all(len(pd.read_csv(S.state_root / f"processed/glosses/gloss_g0_{s}.csv")) == n '
                'for s, n in (("train", 320), ("val", 40), ("test", 40)))),')),
]

TRAIN_B_EXTRA = """
**How training works.** Model B (non-autoregressive Transformer, 2.7 M parameters on the pilot vocabulary) learns
G0 gloss tokens → 208 motion values per frame. Max 600 epochs, early stopping on **VAL** masked position L1
(patience 60), seeds 42 / 43 / 44, AdamW 5e-4. Training reads only train + val; reading test raises an error.
If the session stops: *Save Version*, then a new version with this Output as Input and run
`S.bdsl("train-gloss2motion", "--data", "kaggle400", "--input", INPUT, "--resume", "<run folder>")`."""


def train_b(name, inp, title, purpose, prev, resume_test):
    cells = [
        header(title, purpose, "Accelerator **GPU** · Internet On (not strictly needed).",
               f"Dataset `bdsl-k400` + **Add Input → Output of notebook {prev}**.",
               f"`outputs/runs/gloss2motion_{inp}_kaggle400_<time>/` (run.json, env.json, train.log, metrics.json, "
               "per_item.csv, seed*/curves.csv, checkpoints), `outputs/registry.csv`.",
               "20–60 minutes on a GPU for 3 seeds" + (" + about 5 minutes for the dry run and resume test." if resume_test else "."),
               "Dry run: `device cuda`, finite loss. Training: 3 seeds finished, curves fall, best epochs printed. "
               "Compare Model B with B0/B1 on VAL — if Model B is not better, that is a result, report it.",
               TRAIN_B_EXTRA),
        code(SETUP.format(name=name)),
        code(f'INPUT = "{inp}"\nB = ["train-gloss2motion", "--data", "kaggle400", "--input", INPUT]'),
        md("## Step 1 — Dry run: one optimiser step on the GPU (never a result, named DRYRUN_)"),
        code('rc_dry = S.bdsl(*B, "--max-steps", "1")\nimport glob\ndry = sorted(glob.glob(str(S.state_root / f"outputs/runs/DRYRUN_gloss2motion_{INPUT}_*")))[-1]\n'
             'dry_meta = json.load(open(pathlib.Path(dry) / "run.json"))\nprint("device:", dry_meta["device"], "|", dry_meta["device_note"])\nprint(dry_meta["dry_run"])'),
    ]
    if resume_test:
        cells += [
            md("## Step 2 — Resume test (engineering check, not for the paper): 4 epochs straight vs 2 + resume 2"),
            code('R = [*B, "--not-for-paper", "--set", "gloss2motion.train.max_epochs=4", "--set", "gloss2motion.seeds=[42]"]\n'
                 'S.bdsl(*R)\nstraight = sorted(glob.glob(str(S.state_root / "outputs/runs/NFP_gloss2motion_gloss_*")))[-1]\n'
                 'S.bdsl(*R, "--stop-after-epochs", "2")\nstopped = sorted(glob.glob(str(S.state_root / "outputs/runs/NFP_gloss2motion_gloss_*")))[-1]\n'
                 'S.bdsl(*R, "--resume", stopped)\nimport torch\n'
                 'wa = torch.load(pathlib.Path(straight) / "seed42/ckpt_last.pt", map_location="cpu", weights_only=True)["model"]\n'
                 'wb = torch.load(pathlib.Path(stopped) / "seed42/ckpt_last.pt", map_location="cpu", weights_only=True)["model"]\n'
                 'max_diff = max(float((wa[k] - wb[k]).abs().max()) for k in wa)\n'
                 'print("max |weight difference| straight vs resumed:", max_diff, "(0 = identical; values far below 1e-3 can come '
                 'from GPU non-determinism; a resume bug gives large differences)")'),
        ]
    cells += [
        md("## Step 3 — Real training: 3 seeds, early stopping on VAL"),
        code('rc_train = S.bdsl(*B)\nrun_dir = pathlib.Path(sorted(d for d in glob.glob(str(S.state_root / f"outputs/runs/gloss2motion_{INPUT}_kaggle400_*")) '
             'if (pathlib.Path(d) / "metrics.json").is_file())[-1])\nprint("run:", run_dir.name)'),
        md("## Step 4 — Curves (train vs val) and VAL comparison with B0 / B1 (measured)"),
        code('import pandas as pd, matplotlib.pyplot as plt\nfrom IPython.display import display\n'
             'mets = json.load(open(run_dir / "metrics.json"))\nmeta = json.load(open(run_dir / "run.json"))\nenv = json.load(open(run_dir / "env.json"))\n'
             'print("GPU:", env["device"]["gpu_names"], "| device:", meta["device"], "| seeds:", meta["seeds"])\n'
             'fig, ax = plt.subplots(1, len(meta["seeds"]), figsize=(5 * len(meta["seeds"]), 3.2))\n'
             'for a, s in zip(ax, meta["seeds"]):\n    c = pd.read_csv(run_dir / f"seed{s}/curves.csv")\n'
             '    a.plot(c["epoch"], c["train_pos"], label="train (pos L1)"); a.plot(c["epoch"], c["monitor_pos_l1"], "--", label="val (pos L1)")\n'
             '    a.set_title(f"seed {s}: best epoch {mets[\'model_b\'][str(s)][\'best_epoch\']}"); a.set_xlabel("epoch"); a.legend()\n'
             'plt.tight_layout(); plt.show()\n'
             'rows = []\nfor sp in ("train", "val"):\n    for name, m in (("Model B (mean of seeds)", {k: v["mean"] for k, v in mets["model_b_mean_sd"][sp].items()}), ("B0", mets["B0"][sp]), ("B1", mets["B1"][sp])):\n'
             '        rows.append({"split": sp, "method": name, **{k: round(m[k], 3) for k in ("mpjpe_body", "mpjpe_lhand", "mpjpe_rhand", "velocity_ratio", "diversity_ratio")}})\n'
             'display(pd.DataFrame(rows))\nprint({s: (mets["model_b"][s]["best_epoch"], mets["model_b"][s]["epochs"], mets["train_seconds"][s]) for s in mets["model_b"]}, "(best epoch, epochs run, seconds)")'),
        code(finish('    ("dry run ran on the GPU (cuda)", dry_meta["device"].startswith("cuda")),\n    ("dry-run loss finite", all(d["finite"] for d in dry_meta["dry_run"].values())),\n'
                    '    ("3 seeds finished", len(mets["model_b"]) == 3),\n    ("run is marked for the paper (clean code)", meta["for_paper"]),'
                    + ('\n    ("resume reproduces the weights (max |diff| < 1e-3)", max_diff < 1e-3),' if resume_test else ''))),
    ]
    return cells


NB["04_train_model_b"] = train_b("04_train_model_b", "gloss", "04 — Model B: G0 gloss → motion (3 seeds)",
                                 "Train the main motion model on G0 pseudo-gloss input with real epochs and early stopping on VAL; "
                                 "dry run and resume test first.", "03", True)
NB["05_train_ablation_text"] = train_b("05_train_ablation_text", "text", "05 — Ablation T: Bangla words → motion (3 seeds)",
                                       "The same model with the normalised Bangla words as input instead of glosses (ablation T).",
                                       "04", False)

NB["06_train_model_a"] = [
    header("06 — Model A (A-GRU) on G0 references: agreement with the rule glosser",
           "Train text → gloss on G0 pseudo-glosses. **Be honest about what this measures:** the references are the "
           "outputs of the G0 rule, so the scores say how well the network reproduces the rule glosser — **not BdSL "
           "correctness**. Every table and figure is labelled \"agreement with the rule glosser (G0 pseudo-gloss)\".",
           "Accelerator **GPU** · Internet **On** (pip install sacrebleu).",
           "Dataset `bdsl-k400` + **Add Input → Output of notebook 05**.",
           "`outputs/runs/G0REF_text2gloss_kaggle400_<time>/` (+ overfit checks `G0REF_text2gloss_overfit*`).",
           "10–40 minutes on a GPU.",
           "Overfit 1 and 40 reach 100% / high exact match (the code can learn); 3 seeds finished. Val WER vs G0 is "
           "mostly unseen words (they become `<unk>`)."),
    code(SETUP.format(name="06_train_model_a")),
    code('S.pip_install("sacrebleu==2.6.0")\nA = ["train-text2gloss", "--data", "kaggle400", "--reference", "g0"]\nimport glob'),
    md("## Step 1 — Dry run and overfit checks (engineering checks, never results)"),
    code('rc_dry = S.bdsl(*A, "--max-steps", "1")\nrc_o1 = S.bdsl(*A, "--overfit", "1")\nrc_o40 = S.bdsl(*A, "--overfit", "40")'),
    md("## Step 2 — Real training: 3 seeds, early stopping on VAL WER vs G0"),
    code('rc_train = S.bdsl(*A)\nrun_dir = pathlib.Path(sorted(d for d in glob.glob(str(S.state_root / "outputs/runs/G0REF_text2gloss_kaggle400_*")) '
         'if (pathlib.Path(d) / "metrics.json").is_file())[-1])\nprint("run:", run_dir.name)'),
    md("## Step 3 — Curves and scores (label: agreement with the rule glosser, G0 pseudo-gloss)"),
    code('import pandas as pd, matplotlib.pyplot as plt\nfrom IPython.display import display\nmets = json.load(open(run_dir / "metrics.json"))\nmeta = json.load(open(run_dir / "run.json"))\n'
         'print("LABEL:", mets["label"])\nfig, ax = plt.subplots(1, 2, figsize=(10, 3.2))\n'
         'for s in meta["seeds"]:\n    c = pd.read_csv(run_dir / f"seed{s}/curves.csv")\n    ax[0].plot(c["epoch"], c["train_loss"], label=f"seed {s}"); ax[1].plot(c["epoch"], c["monitor_wer"], label=f"seed {s}")\n'
         'ax[0].set_title("training loss"); ax[1].set_title("val WER vs G0 references (%)"); [a.legend() for a in ax]; plt.tight_layout(); plt.show()\n'
         'display(pd.DataFrame({sp: {k: round(v["mean"], 1) for k, v in mets["agru_mean_sd"][sp].items()} for sp in mets["agru_mean_sd"]}))'),
    code(finish('    ("3 seeds finished", len(mets["agru"]) == 3),\n    ("run is marked for the paper (clean code)", meta["for_paper"]),\n'
                '    ("labelled as agreement with G0, not BdSL", "agreement with the rule glosser" in mets["label"]),')),
]

NB["07_baselines_eval"] = [
    header("07 — Freeze, evaluate on VAL, then ONCE on TEST",
           "Freeze the configuration (the three runs and their checkpoint hashes), evaluate Model B (gloss), Model B (text), "
           "B0 and B1 and Model A on **VAL** with bootstrap 95% intervals and error analysis, then run the single **final "
           "TEST** evaluation, which writes `outputs/FINAL_TEST_LOCK.json`.",
           "Accelerator **None or GPU** (evaluation is light) · Internet **On** (sacrebleu).",
           "Dataset `bdsl-k400` + **Add Input → Output of notebook 06**.",
           "`outputs/frozen_config.json`, `outputs/eval/val_<time>/`, `outputs/eval/FINAL_test_<time>/`, "
           "`outputs/predictions/`, `outputs/FINAL_TEST_LOCK.json`.",
           "10–20 minutes.",
           "The frozen runs are the ones from 04/05/06 (no NFP_, no DRYRUN_, no overfit). The final cell runs once and "
           "prints `lock_written: true`. **Run this notebook only once** (see the warning below).",
           "\n> ⚠️ **Never re-run this notebook after a successful version.** A new version starts without the lock unless "
           "you add this notebook's Output as Input; then a second test run is refused. Re-running the test means "
           "the test is no longer clean."),
    code(SETUP.format(name="07_baselines_eval")),
    code('# Safety stop (added 2026-10-23: Version 1 ran without Internet, sacrebleu was missing, and the notebook\n'
         '# went on to the freeze and the final test). If sacrebleu cannot be installed, stop HERE: before the\n'
         '# freeze and before any access to the test split.\n'
         'import subprocess\n'
         'rc_pip = S.pip_install("sacrebleu==2.6.0")\n'
         'ok = rc_pip == 0 and subprocess.run([sys.executable, "-c", "import sacrebleu"]).returncode == 0\n'
         'assert ok, "STOP: sacrebleu is not installed (turn Internet On). Nothing was frozen; the test split was not touched."\n'
         'print("sacrebleu OK")\n'
         'rc_list = S.bdsl("list-runs")'),
    md("## Step 1 — Freeze (newest finished, for-paper run of each kind)"),
    code('rc_freeze = S.bdsl("freeze")\nfrozen = json.load(open(S.state_root / "outputs/frozen_config.json"))\nprint(json.dumps({r: v["run_id"] for r, v in frozen["runs"].items()}, indent=1))'),
    md("## Step 2 — VAL evaluation (bootstrap 95% CI, paired differences, error analysis)"),
    code('rc_val = S.bdsl("evaluate", "--split", "val")'),
    md("## Step 3 — The single FINAL TEST evaluation\nThe configuration is frozen above. This cell reads the test split for the first and only time."),
    code('rc_final = S.bdsl("evaluate", "--final")\nlock = json.load(open(S.state_root / "outputs/FINAL_TEST_LOCK.json"))\nprint("lock:", lock["created_utc"], lock["results"])'),
    md("## Step 4 — Test results (measured; small-scale, signer-dependent)"),
    code(TEST_TABLE),
    code(finish('    ("configuration frozen before the test", rc_freeze == 0),\n    ("VAL evaluation done", rc_val == 0),\n'
                '    ("final TEST evaluation done once, lock written", rc_final == 0 and not lock.get("history")),')),
]

NB["08_report_figures"] = [
    header("08 — Paper tables, figures and RESULTS_SUMMARY.md",
           "Turn the saved results into paper-ready tables (CSV + Markdown + LaTeX) and figures (PNG), and list every "
           "number with its run ID, source file and label in `outputs/RESULTS_SUMMARY.md`.",
           "Accelerator **None** · Internet Off is fine.",
           "Dataset `bdsl-k400` + **Add Input → Output of notebook 07**.",
           "`outputs/tables/` (T1–T8, per-item tables, RESULTS_LEDGER.csv), `outputs/figures/` (F1–F6), `outputs/RESULTS_SUMMARY.md`.",
           "under 3 minutes.",
           "`final_test_done: true`; `missing` is empty; figures look right (curves, method bars with CIs, error analysis)."),
    code(SETUP.format(name="08_report_figures")),
    code('rc_report = S.k400("report")'),
    code('from IPython.display import Image, Markdown, display\nimport glob\nfor f in sorted(glob.glob(str(S.state_root / "outputs/figures/*.png"))):\n    print(pathlib.Path(f).name); display(Image(filename=f))\n'
         'display(Markdown((S.state_root / "outputs/RESULTS_SUMMARY.md").read_text(encoding="utf-8")[:6000]))'),
    code(finish('    ("report built", rc_report == 0),\n    ("final test results present", (S.state_root / "outputs/FINAL_TEST_LOCK.json").is_file()),')),
]

NB["09_avatar_export"] = [
    header("09 — Avatar export for a few TEST sentences",
           "After the single test evaluation: motion JSON (for the browser VRM viewer) and side-by-side skeleton videos "
           "(Model B vs B1 vs the real recording) for 5 test sentences. Nothing is re-scored.",
           "Accelerator **None** · Internet **On** (pip install OpenCV if missing).",
           "Dataset `bdsl-k400` + **Add Input → Output of notebook 08**.",
           "`outputs/avatar/<Index>/` (motion_modelB.json, motion_B1.json, motion_real.json, demo_log.json, "
           "skeleton_modelB_B1_real.mp4, info.json, LIMITATIONS.md).",
           "under 5 minutes.",
           "Refuses to run without `FINAL_TEST_LOCK.json` (correct). Five folders written; the video plays below."),
    code(SETUP.format(name="09_avatar_export")),
    code('try:\n    import cv2  # noqa: F401\nexcept ImportError:\n    S.pip_install("opencv-contrib-python==5.0.0.93")\n'
         'assert (S.state_root / "outputs/FINAL_TEST_LOCK.json").is_file(), "Run notebook 07 first (and add its output as Input)"\nrc_avatar = S.k400("avatar")'),
    code('from IPython.display import Video, display\nimport glob\nvids = sorted(glob.glob(str(S.state_root / "outputs/avatar/*/skeleton_modelB_B1_real.mp4")))\n'
         'print(len(vids), "videos")\nif vids:\n    display(Video(vids[0], embed=True, width=720))'),
    code(finish('    ("avatar export done", rc_avatar == 0),\n    ("5 skeleton videos", len(vids) == 5),')),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, cells in NB.items():
        nb = new_notebook(cells=cells, metadata={
            "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
            "language_info": {"name": "python"}, "kaggle400": {"generated_by": "kaggle/tools/build_notebooks.py"}})
        nbformat.validate(nb)
        nbformat.write(nb, OUT / f"{name}.ipynb")
        print("wrote", OUT / f"{name}.ipynb")


if __name__ == "__main__":
    main()
