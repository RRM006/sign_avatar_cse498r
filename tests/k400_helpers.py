"""Test helpers: a tiny kaggle400 layout (manifests, dummy videos, synthetic features, G0 glosses, lock)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

WORDS = ["আমি", "তুমি", "স্কুল", "অফিস", "বাসা", "যাব", "খাব", "ভাত", "না", "কেন", "আজ", "কাল"]
FEAT_VER = "fa89892d4908"
BLEND = ["_neutral", "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight", "cheekPuff",
         "cheekSquintLeft", "cheekSquintRight", "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
         "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight", "eyeLookUpLeft", "eyeLookUpRight",
         "eyeSquintLeft", "eyeSquintRight", "eyeWideLeft", "eyeWideRight", "jawForward", "jawLeft", "jawOpen", "jawRight",
         "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft", "mouthFrownRight", "mouthFunnel",
         "mouthLeft", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthPressLeft", "mouthPressRight", "mouthPucker",
         "mouthRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper", "mouthSmileLeft",
         "mouthSmileRight", "mouthStretchLeft", "mouthStretchRight", "mouthUpperUpLeft", "mouthUpperUpRight",
         "noseSneerLeft", "noseSneerRight"]   # MediaPipe's 52 face blendshape names
TINY_B = ["gloss2motion.model.d=16", "gloss2motion.model.heads=2", "gloss2motion.model.enc_layers=1",
          "gloss2motion.model.dec_layers=1", "gloss2motion.model.ff=32", "gloss2motion.train.max_epochs=3",
          "gloss2motion.train.batch_size=4", "gloss2motion.seeds=[1,2]", "gloss2motion.max_frames=40"]
TINY_A = ["text2gloss.model.emb=8", "text2gloss.model.enc_hidden=8", "text2gloss.model.dec_hidden=8",
          "text2gloss.model.attn=8", "text2gloss.train.max_epochs=3", "text2gloss.seeds=[1,2]", "text2gloss.beam=2"]


def fake_features(path: Path, index: int, t: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    pose = rng.normal(0, 0.1, (t, 33, 3)).astype(np.float32)
    pose[:, 11] = [0.15, 0, 0]
    pose[:, 12] = [-0.15, 0, 0]
    lh = rng.normal(0, 0.05, (t, 21, 3)).astype(np.float32)
    rh = rng.normal(0, 0.05, (t, 21, 3)).astype(np.float32)
    mask = np.ones((t, 4), dtype=np.uint8)
    rh[2:5] = np.nan
    mask[2:5, 2] = 0
    meta = {"index": index, "feat_ver": FEAT_VER, "frames": t, "fps": 15, "frame_hw": [1920, 1080]}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, pose_world=pose, pose_img=pose, pose_vis=np.ones((t, 33), np.float32), lhand_world=lh, rhand_world=rh,
             lhand_img=lh, rhand_img=rh, blendshapes=rng.uniform(0, 1, (t, 52)).astype(np.float32),
             blendshape_names=np.array(BLEND), head_rot=rng.normal(0, 5, (t, 3)).astype(np.float32),
             mask=mask, t_ms=np.arange(t, dtype=np.float32), src_t_ms=np.arange(t, dtype=np.float32),
             src_frame=np.arange(t, dtype=np.int32), meta=np.array(json.dumps(meta)))


def make_layout(root: Path, counts=None, with_videos=True, with_features=True) -> dict:
    """root = the k400 data root AND state root. Returns {"subset": DataFrame}."""
    from bdsl.text.normalize import normalize

    counts = counts or {"train": 12, "val": 3, "test": 3}
    rng = np.random.default_rng(0)
    rows, idx = [], 100
    for sp, n in counts.items():
        for _ in range(n):
            words = list(rng.choice(WORDS, size=int(rng.integers(2, 5)), replace=False))
            sent = " ".join(words)
            while normalize(sent) in {r["sentence_norm"] for r in rows}:
                sent += " " + str(rng.choice(WORDS))
            video = f"video-{idx}".encode() * 10
            h = hashlib.sha256(video).hexdigest()
            rows.append({"index": idx, "filename": f"{idx}.mp4", "split": sp, "s1_split": sp, "sentence_raw": sent,
                         "sentence_norm": normalize(sent), "sha256": h, "orientation": "portrait", "duration_s": 1.0,
                         "fps": 30.0, "resolution_bucket": "1080", "display_w": 1080, "display_h": 1920, "codec": "h264",
                         "bytes": len(video), "sentence_length": len(normalize(sent).split()), "length_bucket": "3-4",
                         "duration_quartile": "q1", "tags": "", "question": False, "negation": "না" in sent,
                         "group_id": f"g{idx}", "mp_family": "", "mp_role": "", "mp_partner": "",
                         "has_train_minimal_pair_sibling": False, "all_words_in_train": True, "oov_words": "",
                         "in_pilot50": False, "source_relpath": f"SIGN_LANGUAGE_DATA/{idx}.mp4", "reason": "test fixture",
                         "_video": video})
            idx += 1
    df = pd.DataFrame(rows)
    from k400.select import MANIFEST_COLUMNS

    data = root / "data"
    for sp in counts:
        part = df[df["split"] == sp]
        (data / sp / "videos").mkdir(parents=True, exist_ok=True)
        (data / sp / f"{sp}_manifest.csv").write_bytes(("\ufeff" + part[MANIFEST_COLUMNS].to_csv(index=False, lineterminator="\n")).encode("utf-8"))
        for r in part.to_dict("records"):
            if with_videos:
                (data / sp / "videos" / r["filename"]).write_bytes(r["_video"])
            if with_features:
                fake_features(root / "processed" / "features" / sp / f"{r['index']}.npz", r["index"], 12 + r["index"] % 7,
                              r["index"])
    sub = df[MANIFEST_COLUMNS].copy()
    sub.insert(MANIFEST_COLUMNS.index("sha256") + 1, "sha256_source", sub["sha256"])
    sub.insert(MANIFEST_COLUMNS.index("sha256") + 2, "sha256_copy", sub["sha256"])
    (data / "subset_manifest.csv").write_bytes(("\ufeff" + sub.to_csv(index=False, lineterminator="\n")).encode("utf-8"))
    return {"subset": df, "source_videos": {r["source_relpath"]: r["_video"] for r in rows}}


def make_glosses(root: Path) -> None:
    from bdsl.text.normalize import tokens
    from k400.gloss import make_glosses as mk

    sub = pd.read_csv(root / "data" / "subset_manifest.csv", encoding="utf-8-sig")
    corpus = {t for s in sub["sentence_raw"] for t in tokens(s)}
    (root / "processed" / "glosses").mkdir(parents=True, exist_ok=True)
    mk(root / "data", root / "processed" / "glosses", corpus, "G0-v0.1")


def full_layout(root: Path, **kw) -> dict:
    from k400.lock import write_lock

    info = make_layout(root, **kw)
    make_glosses(root)
    write_lock(root, {"test_fixture": True})
    return info


def k400_env(monkeypatch, root: Path) -> None:
    monkeypatch.setenv("K400_DATA_ROOT", str(root))
    monkeypatch.setenv("K400_STATE_ROOT", str(root))
    monkeypatch.setenv("BDSL_ENV", "local")
