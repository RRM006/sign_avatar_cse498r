"""Pilot selection on a synthetic manifest: counts, quotas, uniqueness, determinism."""

import copy

import pandas as pd
import pytest

from bdsl.config import load_config
from bdsl.data.groups import assign_groups
from bdsl.data.pilot import minimal_pair_families, select_pilot
from bdsl.data.split import assign_split

# Made-up words use Bangla letters, not digits (digits would make every sentence "number_time").
_L = "কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশসহ"
NOUNS = [f"বস্তু{c}" for c in _L[:12]]
TEMPLATES = [f"আমার প্রিয় {{}} রঙ{c}" for c in _L[:30]] + [f"সে {{}} খায় পাতা{c}" for c in _L[:10]]
EXTRA = ["তুমি কোথায় যাও", "সে কে", "তুমি কেমন আছ", "এটা কী", "তুমি কেন এলে", "তার নাম কি",
         "আমি যাব না", "এটা ভালো নয়", "বাড়িতে কেউ নেই", "আমি খাই না", "সে আসে নি", "এটা আমার নয়",
         "আমার ২টা বই", "আজ বৃষ্টি", "সকাল ৭টা", "আমি এক দুই তিন চার পাঁচ ছয় সাত গুনি",
         "ধন্যবাদ", "স্বাগতম", "আমরা স্কুলে যাই প্রতিদিন সকালে হেঁটে হেঁটে"]


def _synthetic_manifest():
    sentences = [t.format(n) for t in TEMPLATES for n in NOUNS] + EXTRA
    sentences += [f"{e} {k}" for e in EXTRA for k in ("এখন", "আবার", "তখন", "সেখানে")]
    rows = []
    for i, s in enumerate(sentences):
        landscape = i % 9 == 0
        low = i % 23 == 0
        w, h = (1920, 1080) if landscape else (1080, 1920)
        if low:
            w, h = (w // 4, h // 4)
        rows.append({"index": i, "sha256": f"h{i}", "sentence_norm": s, "sentence_raw": s, "decode_ok": True,
                     "orientation": "landscape" if landscape else "portrait", "display_w": w, "display_h": h,
                     "duration_s": 2.0 + (i % 40) * 0.25, "fps_avg": 30.0, "relpath": f"V/{i}.mp4"})
    return assign_groups(pd.DataFrame(rows))


@pytest.fixture(scope="module")
def setup():
    cfg = load_config(env="local")
    manifest = _synthetic_manifest()
    split = assign_split(manifest, cfg["split"]["salt"], cfg["split"]["ratios"])
    return cfg["pilot"], manifest, split


def test_selection_meets_counts_quotas_and_is_deterministic(setup):
    pcfg, manifest, split = setup
    sel, report = select_pilot(manifest, split, pcfg)
    assert report["ok"], report
    assert report["counts"] == {"train": 40, "val": 5, "test": 5}
    assert sel["index"].is_unique and sel["sentence_norm"].is_unique
    merged = sel.merge(split[["index", "split"]], on="index", suffixes=("", "_s1"))
    assert (merged["split"] == merged["split_s1"]).all()          # pilot splits are S1 splits
    assert (sel["part"] == "core").sum() == 30 and (sel["part"] == "diversity").sum() == 20
    again, _ = select_pilot(manifest, split, copy.deepcopy(pcfg))
    assert again["index"].tolist() == sel["index"].tolist()


def test_unmet_quota_is_reported_not_relaxed(setup):
    pcfg, manifest, split = setup
    strict = copy.deepcopy(pcfg)
    strict["quotas"]["landscape_min"] = 49
    _, report = select_pilot(manifest, split, strict)
    assert not report["ok"] and any("landscape" in q for q in report["quotas_unmet"])


def test_in_vocab_preference_helps_and_is_recorded(setup):
    pcfg, manifest, split = setup
    on = copy.deepcopy(pcfg)
    on["heldout_prefer_in_vocab"] = True
    off = copy.deepcopy(pcfg)
    off["heldout_prefer_in_vocab"] = False
    sel_on, rep_on = select_pilot(manifest, split, on)
    _, rep_off = select_pilot(manifest, split, off)
    assert rep_on["ok"] and rep_off["ok"]
    assert rep_on["heldout_all_words_seen"] >= rep_off["heldout_all_words_seen"]
    assert rep_on["heldout_all_words_seen"] > 0
    train_vocab = {w for s in sel_on.loc[sel_on["split"] == "train", "sentence_norm"] for w in s.split()}
    for row in sel_on[sel_on["split"] != "train"].to_dict("records"):
        expected = " ".join(w for w in row["sentence_norm"].split() if w not in train_vocab)
        assert row["unseen_in_pilot_train"] == expected


def test_minimal_pair_families_differ_in_one_word():
    pool = pd.DataFrame({"index": [1, 2, 3], "tokens": [["a", "b"], ["a", "c"], ["d", "e"]]})
    fams = minimal_pair_families(pool)
    assert fams == {"2|a _": [1, 2]}
