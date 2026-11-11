"""Day 5 end-to-end demo: one Bangla sentence → Model B motion and B1 retrieval, side by side.

    sentence → norm_v1 → G0 gloss (+ G0 tag tokens) → Model B (chosen run/seed, predicted length)
                                                  ↘ B1: the real motion of the most similar training clip
    both → smoothing → retargeting → motion_modelB.json, motion_B1.json (browser viewer)
         → skeleton_side_by_side.mp4 (always) + demo_log.json (versions, hashes, round-trip errors)
Model A is not used: the demo uses G0 pseudo-glosses, without claiming BdSL validation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from ..io import atomic_write_json, atomic_write_text, sha256_file
from ..models.baselines import b1_retrieve, g0_gloss
from ..models.gloss2motion import Gloss2Motion
from ..models.train_gloss2motion import RESUME_KEYS, _git, input_tokens
from .demo_inputs import load_demo_inputs
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


def _new_output(out_root: Path, stamp: str) -> Path:
    """Reserve a fresh folder, including when two demos start in the same second."""
    out_root.mkdir(parents=True, exist_ok=True)
    suffix = 1
    while True:
        out = out_root / (f"demo_{stamp}" + (f"_{suffix}" if suffix > 1 else ""))
        try:
            out.mkdir(exist_ok=False)
            return out
        except FileExistsError:
            suffix += 1


def run_demo(cfg: dict, sentence: str, out_root: Path, model_run: str, seed: int) -> dict:
    from ..models.train_gloss2motion import b1_pool
    from ..text.gloss_rules import g0
    from ..text.normalize import NORM_VER, normalize

    ctx = load_demo_inputs(cfg, model_run, seed)
    run_dir, run_meta = ctx.run_dir, ctx.meta
    df, items, train, vocab = ctx.rows, ctx.items, ctx.train, ctx.vocab
    mean, sd, checks, blend_names = ctx.mean, ctx.sd, dict(ctx.checks), ctx.blend_names
    pilot = ctx.paths["layout"] == "pilot"
    acfg = cfg["avatar"]
    fps = float(cfg["features"]["fps"])
    model_run = run_dir.name
    model_label = MODEL_B_LABEL if pilot else f"Model B ({ctx.paths['data']}, {len(train)} training clips, G0 gloss input)"

    # Text → gloss (G0), exactly as gloss-draft builds its drafts.
    norm = normalize(sentence)
    gloss_auto, tags_auto, _ = g0(norm, ctx.corpus)
    toks = input_tokens({"gloss_auto": gloss_auto, "tags_auto": tags_auto, "sentence_norm": norm}, "gloss")

    # Model B.
    ckpt = run_dir / f"seed{seed}" / "ckpt_best.pt"
    checkpoint = torch.load(ckpt, weights_only=True, map_location="cpu")
    wanted = {k: run_meta[k] for k in RESUME_KEYS}
    different = [k for k, v in wanted.items() if checkpoint["meta"].get(k) != v]
    if different or checkpoint["meta"].get("seed") != seed:
        raise ValueError(f"checkpoint does not belong to this run/seed: {different or ['seed']}")
    checks["checkpoint_meta"] = True
    model = Gloss2Motion(len(vocab), **run_meta["gloss2motion_config"]["model"])
    model.load_state_dict(checkpoint["model"])
    pred_z = model.generate(torch.tensor([vocab.encode(toks)]), run_meta["gloss2motion_config"]["max_frames"])[0].numpy()
    raw_b = pred_z * sd + mean
    mask_b = np.ones((len(raw_b), 4), dtype=bool)
    unknown = [t for t in toks if t not in vocab.stoi]

    # B1: the most similar training clip (gloss-token Jaccard), its real recorded motion.
    pool = train
    if not pilot:
        # A matched train/val query keeps the same copy/shared-segment exclusions as training.
        matched_indices = set(df.loc[df["sentence_norm"] == norm, "index"].astype(int))
        matches = [it for it in items if it["index"] in matched_indices]
        for query in matches:
            pool = b1_pool(query, pool)
        if matches and any(t["index"] == q["index"] or (q.get("sha256") and t.get("sha256") == q["sha256"])
                           or (q["link_group"] >= 0 and t["link_group"] == q["link_group"]) for q in matches for t in pool):
            raise ValueError("no unrelated training motion is available for B1 retrieval")
    src = pool[b1_retrieve(g0_gloss(gloss_auto), [t["gloss"] for t in pool], [t["index"] for t in pool])]
    by_index = {int(r["index"]): r for r in df.to_dict("records")}
    pilot_match = [int(r["index"]) for r in df.to_dict("records") if r["sentence_norm"] == norm]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = _new_output(Path(out_root), stamp)
    common = {"sentence": sentence, "sentence_norm": norm, "g0_gloss": gloss_auto, "g0_tags": tags_auto}
    b1_label = B1_LABEL.format(index=src["index"])
    motion_b, rt_b = build_motion(raw_b, mask_b, fps, blend_names, model_label,
                                  common | {"source": "model_b", "run": model_run, "seed": seed}, acfg["smooth"])
    motion_1, rt_1 = build_motion(src["x"], src["mask"], fps, blend_names, b1_label,
                                  common | {"source": "b1", "b1_index": src["index"],
                                            "b1_sentence": by_index[src["index"]]["sentence_norm"]}, acfg["smooth"])
    write_motion(out / "motion_modelB.json", motion_b)
    write_motion(out / "motion_B1.json", motion_1)
    sw = float(np.mean([it["shoulder_width_m"] for it in train]))
    n_video = skeleton_video(out / "skeleton_side_by_side.mp4",
                             [{"raw": raw_b, "mask": mask_b, "title": "Model B (pilot)" if pilot else f"Model B ({ctx.paths['data']})",
                               "subtitle": f"{len(train)} training clips, G0 gloss input"},
                              {"raw": src["x"], "mask": src["mask"], "title": f"B1 retrieval: clip {src['index']}",
                               "subtitle": "real recording of a different sentence"}],
                             fps, sw, "Pipeline test - not checked by a BdSL signer. Sentence: see demo_log.json")

    # Preserve the old pilot round trip. Split demos check only their selected B1 source;
    # this is an inference/export check, not another evaluation of the dataset.
    rt_all = {"body": [], "hands": [], "fingers": [], "head": []}
    for it in (items if pilot else [src]):
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
                    "hash_checks": checks, "label": model_label},
        "b1": {"index": src["index"], "split": src["split"], "sentence_norm": by_index[src["index"]]["sentence_norm"],
               "g0_gloss": by_index[src["index"]]["gloss_auto"], "frames": len(src["x"]),
               "hand_coverage": {"left": float(src["mask"][:, 1].mean()), "right": float(src["mask"][:, 2].mean())},
               "label": b1_label},
        "pilot_match": pilot_match, "feat_ver": run_meta["feat_ver"], "fps": fps,
        "post_processing": {"one_euro": acfg["smooth"], "hand_rest_blend_frames": 3},
        "retarget_ver": RETARGET_VER, "motion_format": MOTION_FORMAT,
        "data": ctx.paths["data"], "roundtrip_demo_deg": {"model_b": rt_b, "b1": rt_1},
        "roundtrip_pilot50_deg" if pilot else "roundtrip_b1_source_deg": roundtrip_pilot,
        "skeleton_video": {"file": "skeleton_side_by_side.mp4", "frames": n_video},
        "viewer": {"page": "web/avatar_viewer/index.html", **acfg["viewer"],
                   "vrm_sha256": sha256_file(vrm) if vrm.exists() else None},
        "versions": {"torch": torch.__version__, "numpy": np.__version__}, "git": _git(cfg["_meta"]["project_root"]),
    }
    if not pilot:
        log["label"] = f"{ctx.paths['data']} demo — G0 pseudo-glosses; not checked by a BdSL-competent person"
        log["version_match"] = log.pop("pilot_match")
        log["roundtrip_source_index"] = src["index"]
        log["input_splits"] = ["train", "val"]
        log["input_paths"] = {"runs": str(ctx.paths["runs"]), "data": str(ctx.paths["data_dir"]),
                              "state": str(ctx.paths["state_root"])}
    atomic_write_json(out / "demo_log.json", log)
    limitations = LIMITATIONS if pilot else f"""# {ctx.paths['data']} demo — limitations

- Model B used {len(train)} training clips. This is a small-scale, signer-dependent demo.
- Glosses are G0 pseudo-glosses; Model A is not used. G0REF scores measure rule-glosser agreement only.
- B0 mean motion is a strong baseline. Read the saved evaluation with its motion-energy limitations;
  low coordinate error does not prove correct BdSL.
- B1 replays a different training recording, not a translation of the requested sentence.
- Unknown input tokens map to <unk>; their motion is not a validated sign or fingerspelling fallback.
- No BdSL expert validation exists. Hand sides, monocular depth and facial-expression mapping remain limited.
- Demo input checks use train/val only; no final test evaluation or test-lock update is performed.
"""
    atomic_write_text(out / "LIMITATIONS.md", limitations)
    return {"out_dir": str(out), "log": log}
