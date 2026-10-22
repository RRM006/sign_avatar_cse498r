"""Our own direction-based retargeter: motion frames → VRM 1.0 humanoid bone rotations (ADR-0019).

Coordinates. MediaPipe world (pilot data, checked 2026-10-22): x towards the person's left as
labelled (G8), y down, z away from the camera; the hand world points share this frame. VRM 1.0 model
space: +X = the model's left, +Y up, +Z = the model's front (towards the viewer). So v_vrm = S·v_mp with
S = diag(1, −1, −1), a proper rotation. The avatar therefore appears like the unmirrored video.

Solving, parent bone first, all in model space (normalised VRM bones have identity rest rotations):
- "dir" bones swing their rest direction (already moved by the parent) onto the target direction;
- "frame" bones (spine, hands) map a rest pair of directions (main, side) onto the target pair;
- the head takes an absolute rotation from the stored yaw/pitch/roll;
- "follow" bones keep their parent's rotation (identity local rotation).
The local rotation is inverse(parent) · bone. Hands and fingers blend towards their rest pose by the
hand-presence weight. The browser viewer runs the same algorithm with the loaded model's own rest
directions (web/avatar_viewer/viewer.js); the canonical rest directions here serve the round-trip test
and the exported reference quaternions.
"""

from __future__ import annotations

import numpy as np

RETARGET_VER = "rt-v1"
S = np.array([1.0, -1.0, -1.0])
FINGERS = {"Thumb": ("Metacarpal", "Proximal", "Distal"), "Index": ("Proximal", "Intermediate", "Distal"),
           "Middle": ("Proximal", "Intermediate", "Distal"), "Ring": ("Proximal", "Intermediate", "Distal"),
           "Little": ("Proximal", "Intermediate", "Distal")}
FINGER_BASE = {"Thumb": 1, "Index": 5, "Middle": 9, "Ring": 13, "Little": 17}   # MediaPipe hand landmarks
BODY = {"nose": 0, "lsh": 1, "rsh": 2, "lel": 3, "rel": 4, "lwr": 5, "rwr": 6, "lhip": 7, "rhip": 8}


def _bones() -> list[tuple[str, str | None, str]]:
    """(bone, parent, kind) in parent-first order."""
    out = [("hips", None, "follow"), ("spine", "hips", "frame"), ("chest", "spine", "follow"),
           ("upperChest", "chest", "follow"), ("neck", "upperChest", "follow"), ("head", "neck", "quat")]
    for side in ("left", "right"):
        out += [(f"{side}Shoulder", "upperChest", "follow"), (f"{side}UpperArm", f"{side}Shoulder", "dir"),
                (f"{side}LowerArm", f"{side}UpperArm", "dir"), (f"{side}Hand", f"{side}LowerArm", "frame")]
        for f, segs in FINGERS.items():
            parent = f"{side}Hand"
            for s in segs:
                out.append((f"{side}{f}{s}", parent, "dir"))
                parent = f"{side}{f}{s}"
    return out


BONES = _bones()
HAND_BONES = {side: {b for b, _, _ in BONES if b.startswith(side) and (b.endswith("Hand") or any(f in b for f in FINGERS))}
              for side in ("left", "right")}


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else None


def canonical_rest() -> dict:
    """VRM 1.0 T-pose rest directions (arms along ±X, palms down, thumbs 45° forward)."""
    rest = {"spine": (np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0]))}
    for side, sx in (("left", 1.0), ("right", -1.0)):
        rest[f"{side}UpperArm"] = rest[f"{side}LowerArm"] = np.array([sx, 0.0, 0.0])
        rest[f"{side}Hand"] = (np.array([sx, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        for f, segs in FINGERS.items():
            d = _unit(np.array([sx, 0.0, 1.0])) if f == "Thumb" else np.array([sx, 0.0, 0.0])
            for s in segs:
                rest[f"{side}{f}{s}"] = d
    return rest


# ---- quaternions (x, y, z, w), as in three.js ----
IDENT = np.array([0.0, 0.0, 0.0, 1.0])


def q_mul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


def q_inv(q):
    return np.array([-q[0], -q[1], -q[2], q[3]])


def q_rot(q, v):
    return q_mul(q_mul(q, np.array([*v, 0.0])), q_inv(q))[:3]


def q_from_two(u, v):
    """Shortest rotation taking unit vector u onto unit vector v."""
    d = float(np.dot(u, v))
    if d < -1 + 1e-9:
        axis = _unit(np.cross(u, [1.0, 0.0, 0.0])) if abs(u[0]) < 0.9 else _unit(np.cross(u, [0.0, 1.0, 0.0]))
        return np.array([*axis, 0.0])
    q = np.array([*np.cross(u, v), 1.0 + d])
    return q / np.linalg.norm(q)


def q_from_mat(m):
    t = np.trace(m)
    if t > 0:
        s = 2 * np.sqrt(t + 1)
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, s / 4]
    else:
        i = int(np.argmax(np.diag(m)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = 2 * np.sqrt(1 + m[i, i] - m[j, j] - m[k, k])
        q = [0.0, 0.0, 0.0, (m[k, j] - m[j, k]) / s]
        q[i] = s / 4
        q[j] = (m[j, i] + m[i, j]) / s
        q[k] = (m[k, i] + m[i, k]) / s
    q = np.array(q)
    return q / np.linalg.norm(q)


def q_slerp_identity(q, t: float):
    """Rotation from identity towards q by fraction t."""
    if t >= 1:
        return q
    if q[3] < 0:
        q = -q
    angle = 2 * np.arccos(np.clip(q[3], -1, 1))
    axis = _unit(q[:3])
    if axis is None or t <= 0:
        return IDENT.copy()
    return np.array([*(axis * np.sin(angle * t / 2)), np.cos(angle * t / 2)])


def q_angle(a, b) -> float:
    return float(np.degrees(2 * np.arccos(np.clip(abs(np.dot(a, b)), 0, 1))))


def _basis(a, b):
    """Orthonormal frame [a, b⊥, a×b⊥]; None when a or b is degenerate (e.g. a missing hand)."""
    a = _unit(np.asarray(a, dtype=float))
    if a is None:
        return None
    b = _unit(np.asarray(b, dtype=float) - np.dot(b, a) * a)
    if b is None:
        return None
    return np.stack([a, b, np.cross(a, b)], axis=1)


def head_quat(yaw: float, pitch: float, roll: float) -> np.ndarray:
    """extract.head_rotation's angles (rel = Ry·Rx·Rz in image axes) → model-space rotation S·rel·S."""
    y, p, r = np.radians([yaw, pitch, roll])
    ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
    rz = np.array([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0], [0, 0, 1]])
    sm = np.diag(S)
    return q_from_mat(sm @ (ry @ rx @ rz) @ sm)


def frame_targets(raw: np.ndarray) -> dict:
    """Target directions in VRM model space for one 208-value frame (features.normalize layout)."""
    body = raw[0:27].reshape(9, 3) * S
    hands = {"left": raw[27:90].reshape(21, 3) * S, "right": raw[90:153].reshape(21, 3) * S}
    yaw, pitch, roll = raw[205:208]
    sh_mid = (body[BODY["lsh"]] + body[BODY["rsh"]]) / 2
    hip_mid = (body[BODY["lhip"]] + body[BODY["rhip"]]) / 2
    t = {"spine": (sh_mid - hip_mid, body[BODY["lsh"]] - body[BODY["rsh"]]), "head": head_quat(yaw, pitch, roll)}
    for side, k in (("left", "l"), ("right", "r")):
        t[f"{side}UpperArm"] = body[BODY[f"{k}el"]] - body[BODY[f"{k}sh"]]
        t[f"{side}LowerArm"] = body[BODY[f"{k}wr"]] - body[BODY[f"{k}el"]]
        h = hands[side]
        t[f"{side}Hand"] = (h[9] - h[0], h[5] - h[17])
        for f, segs in FINGERS.items():
            base = FINGER_BASE[f]
            for n, s in enumerate(segs):
                t[f"{side}{f}{s}"] = h[base + n + 1] - h[base + n]
    return t


def solve(targets: dict, rest: dict, hand_weight: dict | None = None) -> tuple[dict, dict]:
    """(model-space rotations, local rotations) per bone for one frame."""
    hand_weight = hand_weight or {"left": 1.0, "right": 1.0}
    model, local = {}, {}
    for bone, parent, kind in BONES:
        qp = model[parent] if parent else IDENT
        qb = qp
        if kind == "dir":
            d = _unit(np.asarray(targets[bone], dtype=float))
            r = q_rot(qp, rest[bone])
            if d is not None:
                qb = q_mul(q_from_two(_unit(r), d), qp)
        elif kind == "frame":
            bt, br = _basis(*targets[bone]), _basis(*rest[bone])
            if bt is not None:
                qb = q_from_mat(bt @ br.T)
        elif kind == "quat":
            qb = np.asarray(targets[bone], dtype=float)
        loc = q_mul(q_inv(qp), qb)
        for side in ("left", "right"):
            if bone in HAND_BONES[side]:
                loc = q_slerp_identity(loc, hand_weight[side])
        local[bone] = loc / np.linalg.norm(loc)
        model[bone] = q_mul(qp, local[bone])
    return model, local


def roundtrip_errors(targets: dict, model: dict, rest: dict, hand_ok: dict | None = None) -> dict:
    """Angle (degrees) between each rebuilt bone direction and its target, by group. Hands with
    hand_ok[side] False (blended towards rest) are skipped."""
    hand_ok = hand_ok or {"left": True, "right": True}
    out = {"body": [], "hands": [], "fingers": [], "head": []}
    for bone, _, kind in BONES:
        if any(bone in HAND_BONES[s] and not hand_ok[s] for s in hand_ok):
            continue
        if kind == "dir":
            d = _unit(np.asarray(targets[bone], dtype=float))
            if d is None:
                continue
            got = q_rot(model[bone], rest[bone])
            ang = float(np.degrees(np.arccos(np.clip(np.dot(_unit(got), d), -1, 1))))
            out["fingers" if any(f in bone for f in FINGERS) else "body"].append(ang)
        elif kind == "frame":
            bt = _basis(*targets[bone])
            if bt is None:
                continue
            got = np.stack([q_rot(model[bone], c) for c in _basis(*rest[bone]).T], axis=1)
            ang = max(float(np.degrees(np.arccos(np.clip(np.dot(got[:, i], bt[:, i]), -1, 1)))) for i in range(2))
            out["hands" if bone.endswith("Hand") else "body"].append(ang)
        elif kind == "quat":
            out["head"].append(q_angle(model[bone], targets[bone]))
    return out
