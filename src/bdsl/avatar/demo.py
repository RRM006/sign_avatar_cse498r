"""Day 5 end-to-end demo: one Bangla sentence → Model B motion and B1 retrieval, side by side.

    sentence → norm_v1 → G0 gloss (+ G0 tag tokens) → Model B (chosen run/seed, predicted length)
                                                  ↘ B1: the real motion of the most similar training clip
    both → smoothing → retargeting → motion_modelB.json, motion_B1.json (browser viewer)
         → skeleton_side_by_side.mp4 (always) + demo_log.json (versions, hashes, round-trip errors)
Model A is not used: it has run in TEST mode only (ADR-0025).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from ..io import atomic_write_json, atomic_write_text, sha256_file
from ..models.baselines import b1_retrieve, g0_gloss
from ..models.gloss2motion import Gloss2Motion
from ..models.text2gloss import Vocab, vocab_hash
from ..models.train_gloss2motion import _git, input_tokens, load_items
from .export import MOTION_FORMAT, build_motion, skeleton_video, write_motion
from .retarget import RETARGET_VER

MODEL_B_LABEL = "Model B (pilot, 40 training clips, G0 gloss input)"
B1_LABEL = "B1 retrieval: replays the real recording of training clip {index}"
LIMITATIONS = """# Day 5 demo — limitations (read before showing this anywhere)

- Pilot "pipeline test" only: Model B was trained on 40 clips; its held-out error is about the same as
  the mean-motion baseline B0, and it moves at about 20–30% of real speed (test_log 2026-10-22).
- The gloss comes from the G0 rule drafter: a pseudo-gloss of the Bangla text, not a BdSL annotation.
  Model A was only run in TEST mode on fake review data (ADR-0025) and is not used.
- B1 is a real recording of a *different* training sentence, chosen by word overlap. It shows real
  signing motion, but not the input sentence.
- Nothing here has been checked by a BdSL-competent person. No claim of correct BdSL grammar,
  comprehensibility or naturalness is made (ADR-0020).
- MediaPipe's left/right labels are used as given; whether some recordings are mirrored is unknown
  (G8). The viewer has a mirror toggle.
- Face: blendshapes are mapped to a few VRM expressions by a rough, unchecked mapping; non-manual
  signals are therefore only approximate.
- MediaPipe landmarks are noisy (monocular depth, missing hands); all results are signer-dependent.
- The avatar is the CC0 VRoid "Base_Female" sample (VRM 0.x); retargeting is direction-based.
"""


def run_demo(cfg: dict, sentence: str, out_root: Path, model_run: str, seed: int) -> dict:
    from ..cli import check_model_b_inputs
    from ..data.manifest import read_sheet
    from ..text.gloss_rules import g0
    from ..text.normalize import NORM_VER, normalize, tokens

    acfg, gcfg_now = cfg["avatar"], cfg["gloss2motion"]
    fps = float(cfg["features"]["fps"])
    run_dir = Path(cfg["paths"]["runs_dir"]) / model_run
    run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    if run_meta["input"] != "gloss":
        raise ValueError(f"{model_run} is a {run_meta['input']!r} run; the demo uses a gloss run")

    # Text → gloss (G0), exactly as gloss-draft builds its drafts.
    norm = normalize(sentence)
    corpus = {t for s in read_sheet(cfg)["sentence_raw"] for t in tokens(s)}
    gloss_auto, tags_auto, _ = g0(norm, corpus)
    toks = input_tokens({"gloss_auto": gloss_auto, "tags_auto": tags_auto, "sentence_norm": norm}, "gloss")

    # Rebuild the run's vocabulary and standardiser from the same inputs and check their hashes.
    df, problems, inputs_sha = check_model_b_inputs(cfg)
    if problems:
        raise RuntimeError(f"Model B inputs failed the checks: {problems[:3]}")
    features_dir = Path(cfg["paths"]["features_dir"]) / run_meta["feat_ver"]
    items = load_items(df, features_dir, "gloss", run_meta["gloss2motion_config"]["max_gap"])
    train = [it for it in items if it["split"] == "train"]
    vocab = Vocab([t for it in train for t in it["tokens"]])
    checks = {"inputs_sha256": inputs_sha == run_meta["inputs_sha256"],
              "vocab_sha256": vocab_hash(vocab, vocab) == run_meta["vocab_sha256"]}
    with np.load(run_dir / "standardizer.npz") as z:
        mean, sd = z["mean"], z["sd"]
    checks["standardizer_sha256"] = hashlib.sha256(mean.tobytes() + sd.tobytes()).hexdigest() == run_meta["standardizer_sha256"]
    if not all(checks.values()):
        raise RuntimeError(f"the run's inputs changed since training: {checks}")

    # Model B.
    ckpt = run_dir / f"seed{seed}" / "ckpt_best.pt"
    model = Gloss2Motion(len(vocab), **run_meta["gloss2motion_config"]["model"])
    model.load_state_dict(torch.load(ckpt, weights_only=True)["model"])
    pred_z = model.generate(torch.tensor([vocab.encode(toks)]), gcfg_now["max_frames"])[0].numpy()
    raw_b = pred_z * sd + mean
    mask_b = np.ones((len(raw_b), 4), dtype=bool)
    unknown = [t for t in toks if t not in vocab.stoi]

    # B1: the most similar training clip (gloss-token Jaccard), its real recorded motion.
    src = train[b1_retrieve(g0_gloss(gloss_auto), [t["gloss"] for t in train], [t["index"] for t in train])]
    by_index = {int(r["index"]): r for r in df.to_dict("records")}
    pilot_match = [int(r["index"]) for r in df.to_dict("records") if r["sentence_norm"] == norm]

    with np.load(next(features_dir.glob("*.npz"))) as z:
        blend_names = [str(n) for n in z["blendshape_names"]]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = out_root / f"demo_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    common = {"sentence": sentence, "sentence_norm": norm, "g0_gloss": gloss_auto, "g0_tags": tags_auto}
    b1_label = B1_LABEL.format(index=src["index"])
    motion_b, rt_b = build_motion(raw_b, mask_b, fps, blend_names, MODEL_B_LABEL,
                                  common | {"source": "model_b", "run": model_run, "seed": seed}, acfg["smooth"])
    motion_1, rt_1 = build_motion(src["x"], src["mask"], fps, blend_names, b1_label,
                                  common | {"source": "b1", "b1_index": src["index"],
                                            "b1_sentence": by_index[src["index"]]["sentence_norm"]}, acfg["smooth"])
    write_motion(out / "motion_modelB.json", motion_b)
    write_motion(out / "motion_B1.json", motion_1)
    sw = float(np.mean([it["shoulder_width_m"] for it in train]))
    n_video = skeleton_video(out / "skeleton_side_by_side.mp4",
                             [{"raw": raw_b, "mask": mask_b, "title": "Model B (pilot)",
                               "subtitle": "40 training clips, G0 gloss input"},
                              {"raw": src["x"], "mask": src["mask"], "title": f"B1 retrieval: clip {src['index']}",
                               "subtitle": "real recording of a different sentence"}],
                             fps, sw, "Pipeline test - not checked by a BdSL signer. Sentence: see demo_log.json")

    # Round-trip check of the retargeter on every recorded pilot clip (canonical T-pose).
    rt_all = {"body": [], "hands": [], "fingers": [], "head": []}
    for it in items:
        _, s = build_motion(it["x"], it["mask"], fps, blend_names, "roundtrip", {}, acfg["smooth"])
        for k in rt_all:
            if s[k]["n"]:
                rt_all[k].append((s[k]["n"], s[k]["mean_deg"], s[k]["max_deg"]))
    roundtrip_pilot = {k: {"frames_bones": int(sum(n for n, _, _ in v)),
                           "mean_deg": float(sum(n * m for n, m, _ in v) / max(sum(n for n, _, _ in v), 1)),
                           "max_deg": float(max((mx for _, _, mx in v), default=0.0))} for k, v in rt_all.items()}

    vrm = Path(cfg["paths"]["vrm_file"])
    log = {
        "label": "Day 5 demo - pipeline test; not checked by a BdSL-competent person",
        "created_utc": stamp, **common, "g0_ver": cfg["annotations"]["g0_ver"], "norm_ver": NORM_VER,
        "model_b": {"run": model_run, "seed": seed, "checkpoint": ckpt.relative_to(run_dir).as_posix(),
                    "checkpoint_sha256": sha256_file(ckpt), "run_json_sha256": sha256_file(run_dir / "run.json"),
                    "input_tokens": toks, "unknown_tokens": unknown, "predicted_frames": len(raw_b),
                    "hash_checks": checks, "label": MODEL_B_LABEL},
        "b1": {"index": src["index"], "split": src["split"], "sentence_norm": by_index[src["index"]]["sentence_norm"],
               "g0_gloss": by_index[src["index"]]["gloss_auto"], "frames": len(src["x"]),
               "hand_coverage": {"left": float(src["mask"][:, 1].mean()), "right": float(src["mask"][:, 2].mean())},
               "label": b1_label},
        "pilot_match": pilot_match, "feat_ver": run_meta["feat_ver"], "fps": fps,
        "post_processing": {"one_euro": acfg["smooth"], "hand_rest_blend_frames": 3},
        "retarget_ver": RETARGET_VER, "motion_format": MOTION_FORMAT,
        "roundtrip_demo_deg": {"model_b": rt_b, "b1": rt_1}, "roundtrip_pilot50_deg": roundtrip_pilot,
        "skeleton_video": {"file": "skeleton_side_by_side.mp4", "frames": n_video},
        "viewer": {"page": "web/avatar_viewer/index.html", **acfg["viewer"],
                   "vrm_sha256": sha256_file(vrm) if vrm.exists() else None},
        "versions": {"torch": torch.__version__, "numpy": np.__version__}, "git": _git(cfg["_meta"]["project_root"]),
    }
    atomic_write_json(out / "demo_log.json", log)
    atomic_write_text(out / "LIMITATIONS.md", LIMITATIONS)
    return {"out_dir": str(out), "log": log}
