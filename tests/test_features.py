"""Feature extraction helpers, QC maths, privacy check and versioning (no MediaPipe needed)."""

import json

import numpy as np
import pytest

from bdsl.features.extract import head_rotation, resample_nearest, timestamp_cv
from bdsl.features.layout import N_BLEND, N_HAND, N_POSE, feat_ver, privacy_problems, read_meta
from bdsl.features.qc import longest_run, qc_row

FCFG = {"layout": "feat_layout_v1", "fps": 15, "landmarker": {"min_hand_landmarks_confidence": 0.5}}


def test_resample_regular_and_irregular():
    regular = [0, 33.3, 66.7, 100, 133.3, 166.7, 200]
    assert [j for _, j in resample_nearest(regular, 15)] == [0, 2, 4, 6]
    irregular = [0, 30, 120, 150]
    plan = resample_nearest(irregular, 15)
    assert [j for _, j in plan] == [0, 1, 2] and plan[-1][0] == pytest.approx(133.333, abs=0.01)
    assert resample_nearest([], 15) == []


def test_timestamp_cv():
    assert timestamp_cv([0, 33, 66, 99, 132]) == pytest.approx(0.0)
    assert timestamp_cv([0, 33, 200, 233, 266]) > 0.5
    assert timestamp_cv([0, 33]) is None


def _face_points(R):
    canonical = np.array([[-1, 0, 0], [1, 0, 0], [0, 1.2, 0], [0, -1.5, 0]], float)  # eyes, forehead, chin
    r0 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], float)
    return (r0 @ R @ canonical.T).T * 50 + np.array([300, 400, 0])


@pytest.mark.parametrize("deg", [-30, 0, 20])
def test_head_rotation_recovers_yaw_and_roll(deg):
    t = np.radians(deg)
    ry = np.array([[np.cos(t), 0, np.sin(t)], [0, 1, 0], [-np.sin(t), 0, np.cos(t)]])
    rz = np.array([[np.cos(t), -np.sin(t), 0], [np.sin(t), np.cos(t), 0], [0, 0, 1]])
    assert head_rotation(_face_points(ry)) == pytest.approx([deg, 0, 0], abs=1e-3)
    assert head_rotation(_face_points(rz)) == pytest.approx([0, 0, deg], abs=1e-3)


def test_longest_run():
    assert longest_run(np.array([1, 1, 0, 1, 1, 1, 0], bool)) == 3
    assert longest_run(np.zeros(4, bool)) == 0


def _fake_npz(path, T=10, extra=None):
    nan = np.nan
    pose = np.zeros((T, N_POSE, 3), np.float32)
    pose[:, 13] = [0.0, -0.3, 0]    # elbows / wrists / shoulders at fixed spots → zero bone variation
    pose[:, 15] = [0.0, -0.55, 0]
    pose[:, 11] = [0.2, 0, 0]
    mask = np.ones((T, 4), np.uint8)
    mask[3:7, 2] = 0                # right hand missing for 4 frames
    hand = np.full((T, N_HAND, 3), nan, np.float32)
    arrays = {
        "t_ms": np.arange(T, dtype=np.float32) * 66.7, "src_t_ms": np.arange(T, dtype=np.float32) * 66.7,
        "src_frame": np.arange(T, dtype=np.int32), "pose_world": pose, "pose_img": np.zeros((T, N_POSE, 3), np.float32),
        "pose_vis": np.ones((T, N_POSE), np.float32), "lhand_world": hand, "rhand_world": hand, "lhand_img": hand,
        "rhand_img": hand, "blendshapes": np.zeros((T, N_BLEND), np.float32), "blendshape_names": np.array(["b"] * N_BLEND),
        "head_rot": np.zeros((T, 3), np.float32), "mask": mask,
        "meta": np.array(json.dumps({"index": 7, "feat_ver": "abc", "mode": "video", "fps": 15, "frames": T,
                                     "src_frames": 20, "src_fps": 30.0, "ts_cv": 0.01, "detect_ms_per_frame": 30.0,
                                     "seconds": 1.0, "frame_hw": [1920, 1080]})),
    }
    arrays.update(extra or {})
    np.savez_compressed(path, **arrays)
    return path


def test_qc_row_on_synthetic_clip(tmp_path):
    row = qc_row(_fake_npz(tmp_path / "7.npz"))
    assert row["index"] == 7 and row["cov_pose"] == 1.0 and row["cov_right_hand"] == pytest.approx(0.6)
    assert row["longest_gap_right_hand_s"] == pytest.approx(4 / 15, abs=1e-3)
    assert row["cv_forearm_left"] == pytest.approx(0.0, abs=1e-6)
    assert row["jitter_wrist_left"] == pytest.approx(0.0, abs=1e-6)


def test_privacy_check(tmp_path):
    assert privacy_problems(_fake_npz(tmp_path / "ok.npz")) == []
    mesh = _fake_npz(tmp_path / "mesh.npz", extra={"face_mesh": np.zeros((10, 478, 3), np.float32)})
    assert any("unexpected keys" in p for p in privacy_problems(mesh))
    assert any("478" in p for p in privacy_problems(mesh))
    img = _fake_npz(tmp_path / "img.npz", extra={"pose_img": np.zeros((4, 8, 8, 3), np.uint8)})
    assert any("image" in p for p in privacy_problems(img))


def test_feat_ver_and_read_meta(tmp_path):
    a = feat_ver(FCFG, "video", "0.10.35", "e2dab6")
    assert a == feat_ver(dict(FCFG), "video", "0.10.35", "e2dab6") and len(a) == 12
    assert a != feat_ver(FCFG, "image", "0.10.35", "e2dab6")
    assert a != feat_ver({**FCFG, "fps": 30}, "video", "0.10.35", "e2dab6")
    assert read_meta(_fake_npz(tmp_path / "7.npz"))["feat_ver"] == "abc"
    broken = tmp_path / "broken.npz"
    broken.write_bytes(b"not a zip")
    assert read_meta(broken) is None
