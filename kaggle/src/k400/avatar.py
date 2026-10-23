"""Notebook 09: avatar motion JSON + skeleton videos for a few TEST sentences (after the test lock only).

For each chosen test sentence, three versions side by side: Model B (G0 gloss input, first seed of the
frozen run), B1 retrieval (the real recording of a different, most similar training sentence) and the
real recording of the sentence itself. The motions come from the single final evaluation
(`outputs/predictions/test_motion/`); nothing here changes or re-scores a result.
Output: outputs/avatar/<Index>/ motion_modelB.json, motion_B1.json, motion_real.json (bdsl-motion-v1),
demo_log.json (the fields web/avatar_viewer reads), skeleton_modelB_B1_real.mp4, info.json, LIMITATIONS.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bdsl.data import kaggle400 as k4
from bdsl.io import atomic_write_json, atomic_write_text

LIMITATIONS = """# Avatar export — limitations (read before showing this anywhere)

- kaggle400 is small-scale (320 training clips) and signer-dependent. Model B's motion is a model output
  from G0 pseudo-gloss input; it has NOT been checked by a BdSL-competent person.
- B1 replays the real recording of a DIFFERENT training sentence (most similar by gloss words).
- "Real" is the MediaPipe reconstruction of the actual test recording (noisy hands, monocular depth).
- No claim of correct BdSL grammar, comprehensibility or naturalness is made. Hand sides are MediaPipe's
  labels as given (mirroring unknown, G8). The face mapping to avatar expressions is rough and unchecked.
"""


def export(cfg: dict, n: int | None = None) -> dict:
    from bdsl.avatar.export import build_motion, skeleton_video, write_motion
    from bdsl.features.normalize import clip_motion

    p = k4.paths(cfg)
    if not p["final_lock"].is_file():
        raise k4.TestSplitLocked("Notebook 09 runs only after the final test evaluation (FINAL_TEST_LOCK.json missing).")
    lock = json.loads(p["final_lock"].read_text(encoding="utf-8"))
    n = n or int(cfg["kaggle400"]["avatar_test_sentences"])
    fps = float(cfg["features"]["fps"])
    smooth = cfg["avatar"]["smooth"]
    per_item = pd.read_csv(p["predictions"] / "test_modelB_per_item.csv", encoding="utf-8-sig")
    seed = cfg["kaggle400"]["seed"]
    order = sorted(per_item["index"].astype(int), key=lambda i: hashlib.sha256(f"{seed}|avatar|{i}".encode()).hexdigest())[:n]
    out = []
    with k4.final_test_access("avatar export after the final lock (no scoring)"):
        man = k4.read_split_manifest(cfg, "test").set_index("index")
        train_man = k4.read_split_manifest(cfg, "train").set_index("index")
        g0_test = k4.read_g0(cfg, "test").set_index("index")
        for i in order:
            row = per_item[per_item["index"] == i].iloc[0]
            gt = clip_motion(p["features"]["test"] / f"{i}.npz", cfg["gloss2motion"]["max_gap"])
            with np.load(p["features"]["test"] / f"{i}.npz") as z:
                names = [str(x) for x in z["blendshape_names"]]

            def load(method):
                with np.load(p["predictions"] / "test_motion" / method / f"{i}.npz") as z:
                    return z["x"]

            raw = {"modelB": load("model_b_gloss"), "B1": load("B1"), "real": load("real_recording")}
            masks = {"modelB": np.ones((len(raw["modelB"]), 4), bool), "B1": np.ones((len(raw["B1"]), 4), bool),
                     "real": gt["mask"]}
            d = p["avatar"] / str(i)
            d.mkdir(parents=True, exist_ok=True)
            b1_src = int(row["B1_source_index"])
            labels = {"modelB": "Model B (kaggle400, G0 gloss input) - model output",
                      "B1": f"B1 retrieval: real recording of training clip {b1_src} (a different sentence)",
                      "real": f"real recording of test clip {i} (MediaPipe reconstruction)"}
            rt = {}
            for k in raw:
                motion, rt[k] = build_motion(raw[k], masks[k], fps, names, labels[k],
                                             {"index": i, "sentence_norm": man.loc[i, "sentence_norm"], "source": k,
                                              "final_eval": lock["results"]}, smooth)
                write_motion(d / f"motion_{k}.json", motion)
            frames = skeleton_video(
                d / "skeleton_modelB_B1_real.mp4",
                [{"raw": raw["modelB"], "mask": masks["modelB"], "title": "Model B", "subtitle": "G0 gloss input"},
                 {"raw": raw["B1"], "mask": masks["B1"], "title": f"B1: clip {b1_src}", "subtitle": "different sentence"},
                 {"raw": raw["real"], "mask": masks["real"], "title": f"Real: clip {i}", "subtitle": "MediaPipe"}],
                fps, gt["shoulder_width_m"], "kaggle400 test sentence - not checked by a BdSL signer")
            info = {"index": i, "sentence_raw": man.loc[i, "sentence_raw"], "sentence_norm": man.loc[i, "sentence_norm"],
                    "b1_source_index": b1_src, "b1_source_sentence": train_man.loc[b1_src, "sentence_norm"],
                    "frames": {k: int(len(v)) for k, v in raw.items()}, "video_frames": frames,
                    "roundtrip_deg": rt, "final_eval": lock["results"], "labels": labels}
            atomic_write_json(d / "info.json", info)
            # the fields web/avatar_viewer reads (it shows motion_modelB.json and motion_B1.json side by side)
            atomic_write_json(d / "demo_log.json", {
                "label": "kaggle400 test sentence export - not checked by a BdSL-competent person",
                "sentence": info["sentence_raw"], "sentence_norm": info["sentence_norm"],
                "g0_gloss": g0_test.loc[str(i), "gloss_auto"], "b1": {"index": b1_src, "sentence_norm": info["b1_source_sentence"]},
                "final_eval": lock["results"]})
            atomic_write_text(d / "LIMITATIONS.md", LIMITATIONS)
            out.append({"index": i, "sentence": info["sentence_norm"], "b1_source": b1_src, "folder": str(d)})
    atomic_write_text(p["avatar"] / "README.md", "# Avatar exports (test sentences)\n\n" + LIMITATIONS + "\n" + "\n".join(
        f"- `{o['index']}/`: {o['sentence']} (B1 source {o['b1_source']})" for o in out) + "\n")
    return {"exported": out, "viewer": "web/avatar_viewer/ on the desktop: copy a folder into work/demo/ and open "
                                       "?demo=/work/demo/<folder>/ (see kaggle/GUIDE_KAGGLE_STEP_BY_STEP.md)"}
