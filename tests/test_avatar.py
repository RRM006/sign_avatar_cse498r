"""Day 5: smoothing, hand weights, quaternion maths, retargeting round trip, export and skeleton video."""

import cv2
import numpy as np
import pytest

from bdsl.avatar.export import EXPRESSIONS, build_motion, skeleton_video
from bdsl.avatar.postprocess import one_euro, presence_weights
from bdsl.avatar.retarget import (BONES, HAND_BONES, IDENT, canonical_rest, frame_targets, head_quat, q_angle,
                                  q_from_mat, q_from_two, q_mul, q_rot, roundtrip_errors, solve)

NAMES = [f"bs{i}" for i in range(52)]
for i, n in enumerate(sorted({n for v in EXPRESSIONS.values() for n in v})):
    NAMES[i] = n


def test_one_euro_keeps_constants_and_reduces_noise():
    x = np.full((30, 2), 3.0)
    assert np.allclose(one_euro(x, 15), 3.0)
    rng = np.random.default_rng(0)
    noisy = 1.0 + rng.normal(0, 0.1, (200, 1))
    assert one_euro(noisy, 15).std() < 0.5 * noisy.std()


def test_presence_weights_ramp_into_gaps():
    w = presence_weights(np.array([1, 1] + [0] * 10 + [1], dtype=bool), ramp=3)
    assert w[0] == 1 and w[12] == 1 and w[6] == 0
    assert np.allclose(w[2:5], [0.75, 0.5, 0.25]) and np.allclose(w[9:12], [0.25, 0.5, 0.75])


def test_quaternion_helpers():
    u, v = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    assert np.allclose(q_rot(q_from_two(u, v), u), v)
    assert np.allclose(q_rot(q_from_two(u, -u), u), -u)
    assert np.allclose(q_from_mat(np.eye(3)), IDENT)
    rz = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1.0]])
    assert np.allclose(q_rot(q_from_mat(rz), u), v)
    assert q_angle(head_quat(0, 0, 0), IDENT) < 1e-6


def _frame(rng, left_arm_mp=(0.3, 0.0, 0.0)):
    raw = rng.normal(0, 0.05, 208)
    body = np.zeros((9, 3))
    body[1], body[2] = [0.5, 0, 0], [-0.5, 0, 0]          # shoulders (MediaPipe axes, shoulder widths)
    body[3] = body[1] + np.array(left_arm_mp)                 # left elbow
    body[5] = body[3] + [0.3, 0, 0]
    body[4], body[6] = body[2] + [-0.3, 0.2, 0], body[2] + [-0.3, 0.5, 0]
    body[7], body[8] = [0.3, 1.5, 0], [-0.3, 1.5, 0]           # hips below (y down)
    raw[0:27] = body.ravel()
    raw[205:208] = [10, -5, 3]
    return raw


def test_axes_mediapipe_to_vrm():
    t = frame_targets(_frame(np.random.default_rng(1), left_arm_mp=(0.0, 0.3, 0.0)))
    assert t["leftUpperArm"][1] < 0 and abs(t["leftUpperArm"][0]) < 1e-9   # y down in MediaPipe → −Y in VRM
    assert t["spine"][0][1] > 0 and t["spine"][1][0] > 0                   # torso up, left shoulder at +X


def test_solve_round_trip_is_exact_and_hand_weight_blends_to_rest():
    rest = canonical_rest()
    rng = np.random.default_rng(2)
    for _ in range(5):
        tg = frame_targets(_frame(rng))
        model, local = solve(tg, rest)
        errs = roundtrip_errors(tg, model, rest)
        assert max(max(v) for v in errs.values() if v) < 1e-3
        assert all(abs(np.linalg.norm(q) - 1) < 1e-9 for q in local.values())
    _, local = solve(tg, rest, {"left": 0.0, "right": 1.0})
    assert all(q_angle(local[b], IDENT) < 1e-9 for b in HAND_BONES["left"])
    assert {b for b, _, _ in BONES} >= {"leftThumbMetacarpal", "rightLittleDistal", "head", "spine"}
    assert len(HAND_BONES["left"]) == 16


def test_child_follows_parent():
    rest = canonical_rest()
    tg = frame_targets(_frame(np.random.default_rng(3)))
    model, local = solve(tg, rest)
    assert np.allclose(q_mul(model["leftUpperArm"], local["leftLowerArm"]), model["leftLowerArm"])


def test_build_motion_and_skeleton_video(tmp_path):
    rng = np.random.default_rng(4)
    raw = np.stack([_frame(rng) for _ in range(6)])
    raw[:, 153:205] = rng.uniform(-0.5, 1.5, (6, 52))
    mask = np.ones((6, 4), dtype=bool)
    mask[2:4, 2] = False
    motion, rt = build_motion(raw, mask, 15.0, NAMES, "label", {"k": 1}, {"min_cutoff": 1.0, "beta": 0.3, "d_cutoff": 1.0})
    assert motion["n_frames"] == 6 and set(motion["expressions"]) == set(EXPRESSIONS)
    assert all(0 <= v <= 1 for arr in motion["expressions"].values() for v in arr)
    assert motion["hand_weight"]["right"][2] < 1 and motion["hand_weight"]["left"][2] == 1
    assert len(motion["targets"]["leftHand"]["values"][0]) == 2 and len(motion["targets"]["head"]["values"][0]) == 4
    assert rt["fingers"]["max_deg"] < 1e-3
    n = skeleton_video(tmp_path / "s.mp4", [{"raw": raw, "mask": mask, "title": "A", "subtitle": "a"},
                                            {"raw": raw[:3], "mask": mask[:3], "title": "B", "subtitle": "b"}], 15.0, 0.32, "f")
    cap = cv2.VideoCapture(str(tmp_path / "s.mp4"))
    assert n == 6 and int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == 6 and int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == 960
    cap.release()


@pytest.mark.parametrize("bone", ["leftUpperArm", "rightIndexDistal", "leftThumbMetacarpal"])
def test_canonical_rest_is_unit_and_sided(bone):
    d = canonical_rest()[bone]
    assert abs(np.linalg.norm(d) - 1) < 1e-9
    assert (d[0] > 0) == bone.startswith("left")
