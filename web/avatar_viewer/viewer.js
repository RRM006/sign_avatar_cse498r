// Day 5 viewer: plays motion_modelB.json and motion_B1.json on two VRM avatars side by side.
// The retargeting below is the same algorithm as src/bdsl/avatar/retarget.py (solve), but with the
// loaded model's own rest directions. Quaternions are in VRM 1.0 model space (+X model's left, +Y up,
// +Z front); for VRM 0.x models the x and z parts are negated, as three-vrm's examples do.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

const W = 480, H = 540, HEAD = 64, FOOT = 30;
const VERSIONS = 'three 0.186.1 · three-vrm 3.5.5 · CC0 VRoid Base_Female';
const FINGERS = { Thumb: ['Metacarpal', 'Proximal', 'Distal'], Index: ['Proximal', 'Intermediate', 'Distal'],
  Middle: ['Proximal', 'Intermediate', 'Distal'], Ring: ['Proximal', 'Intermediate', 'Distal'],
  Little: ['Proximal', 'Intermediate', 'Distal'] };
const SIDES = ['left', 'right'];

const params = new URLSearchParams(location.search);
const demoDir = (params.get('demo') || '').replace(/\/?$/, '/');
const vrmUrl = params.get('vrm') || '/work/models/vrm/Base_Female.vrm';
const statusEl = document.getElementById('status');
const out = document.getElementById('out');
const glCanvas = document.getElementById('gl');
const ctx = out.getContext('2d');
const state = { playing: true, mirror: false, t: 0, recorder: null, roundtrip: null, error: null };
window.bdsl = state;

const v3 = (a) => new THREE.Vector3(a[0], a[1], a[2]);
const isHandBone = (name, side) => name.startsWith(side) &&
  (name.endsWith('Hand') || Object.keys(FINGERS).some((f) => name.includes(f)));

function basis(a, b) {
  const x = a.clone();
  if (x.lengthSq() < 1e-18) return null;
  x.normalize();
  const y = b.clone().sub(x.clone().multiplyScalar(b.dot(x)));
  if (y.lengthSq() < 1e-18) return null;
  y.normalize();
  return new THREE.Matrix4().makeBasis(x, y, new THREE.Vector3().crossVectors(x, y));
}

// Directions measured on the avatar (rest pose at load, or the posed avatar for the round-trip check).
// A distal finger bone has no tip bone: at rest it continues its parent's direction; when posed, that
// rest direction is turned by the bone's own world rotation change since rest (restQ).
function measureDirs(vrm, restDirs = null, restQ = null) {
  vrm.scene.updateMatrixWorld(true);
  const node = (n) => vrm.humanoid.getRawBoneNode(n);
  const P = (n) => (node(n) ? node(n).getWorldPosition(new THREE.Vector3()) : null);
  const sub = (a, b) => (a && b ? a.clone().sub(b) : null);
  const d = {};
  const lu = P('leftUpperArm'), ru = P('rightUpperArm');
  d.spine = [sub(lu.clone().add(ru).multiplyScalar(0.5), P('hips')), sub(lu, ru)];
  for (const s of SIDES) {
    d[`${s}UpperArm`] = sub(P(`${s}LowerArm`), P(`${s}UpperArm`));
    d[`${s}LowerArm`] = sub(P(`${s}Hand`), P(`${s}LowerArm`));
    d[`${s}Hand`] = [sub(P(`${s}MiddleProximal`), P(`${s}Hand`)), sub(P(`${s}IndexProximal`), P(`${s}LittleProximal`))];
    for (const [f, segs] of Object.entries(FINGERS)) {
      const n = segs.map((g) => `${s}${f}${g}`);
      d[n[0]] = sub(P(n[1]), P(n[0]));
      d[n[1]] = sub(P(n[2]), P(n[1]));
      d[n[2]] = sub(P(n[2]), P(n[1]));
      if (restDirs && restQ && node(n[2]) && restDirs[n[2]]) {
        const now = node(n[2]).getWorldQuaternion(new THREE.Quaternion());
        d[n[2]] = restDirs[n[2]].clone().applyQuaternion(now.multiply(restQ[n[2]].clone().invert()));
      }
    }
  }
  return d;
}

function worldQuats(vrm) {
  vrm.scene.updateMatrixWorld(true);
  const q = {};
  for (const name of Object.keys(vrm.humanoid.humanBones)) {
    const n = vrm.humanoid.getRawBoneNode(name);
    if (n) q[name] = n.getWorldQuaternion(new THREE.Quaternion());
  }
  return q;
}

function frameTargets(motion, t, mirror) {
  const ft = {};
  for (const [name, { kind, values }] of Object.entries(motion.targets)) ft[name] = { kind, v: values[t] };
  const w = { left: motion.hand_weight.left[t], right: motion.hand_weight.right[t] };
  if (!mirror) return { ft, w };
  // Mirror across the model's YZ plane: negate x, swap left/right; a rotation q becomes (x, −y, −z, w).
  const swap = (n) => n.replace(/^left/, '@').replace(/^right/, 'left').replace(/^@/, 'right');
  const mx = (a) => [-a[0], a[1], a[2]];
  const m = {};
  for (const [name, { kind, v }] of Object.entries(ft)) {
    m[swap(name)] = { kind, v: kind === 'dir' ? mx(v) : kind === 'frame' ? [mx(v[0]), mx(v[1])] : [v[0], -v[1], -v[2], v[3]] };
  }
  return { ft: m, w: { left: w.right, right: w.left } };
}

function solve(bones, ft, rest, w) {
  const model = {}, local = {};
  for (const { name, parent, kind } of bones) {
    const qp = parent ? model[parent] : new THREE.Quaternion();
    let qb = qp.clone();
    const t = ft[name];
    if (kind === 'dir' && rest[name]) {
      const d = v3(t.v);
      if (d.lengthSq() > 1e-18) {
        const r = rest[name].clone().applyQuaternion(qp).normalize();
        qb = new THREE.Quaternion().setFromUnitVectors(r, d.normalize()).multiply(qp);
      }
    } else if (kind === 'frame' && rest[name] && rest[name][0] && rest[name][1]) {
      const bt = basis(v3(t.v[0]), v3(t.v[1])), br = basis(rest[name][0], rest[name][1]);
      if (bt && br) qb = new THREE.Quaternion().setFromRotationMatrix(bt.multiply(br.transpose()));
    } else if (kind === 'quat') {
      qb = new THREE.Quaternion(...t.v).normalize();
    }
    let loc = qp.clone().invert().multiply(qb);
    for (const s of SIDES) if (isHandBone(name, s)) loc = new THREE.Quaternion().slerp(loc, w[s]);
    local[name] = loc.normalize();
    model[name] = qp.clone().multiply(local[name]);
  }
  return local;
}

class Panel {
  constructor(vrm, motion) {
    // Rest directions and rotations are measured once, before any pose is applied.
    this.vrm = vrm; this.motion = motion; this.rest = measureDirs(vrm); this.restQ = worldQuats(vrm);
    this.isV0 = vrm.meta?.metaVersion === '0';
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xffffff);
    this.scene.add(new THREE.AmbientLight(0xffffff, 1.2));
    const light = new THREE.DirectionalLight(0xffffff, 2.2);
    light.position.set(1, 1.5, 2);
    this.scene.add(light, vrm.scene);
    this.camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 20);
    this.camera.position.set(0, 1.15, 2.3);
    this.camera.lookAt(0, 1.12, 0);
  }

  pose(t, mirror) {
    const { ft, w } = frameTargets(this.motion, t, mirror);
    const local = solve(this.motion.bones, ft, this.rest, w);
    for (const [name, q] of Object.entries(local)) {
      const node = this.vrm.humanoid.getNormalizedBoneNode(name);
      if (node) node.quaternion.set(this.isV0 ? -q.x : q.x, q.y, this.isV0 ? -q.z : q.z, q.w);
    }
    const em = this.vrm.expressionManager;
    if (em) {
      for (const [k, arr] of Object.entries(this.motion.expressions)) {
        const name = mirror ? (k === 'blinkLeft' ? 'blinkRight' : k === 'blinkRight' ? 'blinkLeft' : k) : k;
        if (em.getExpression(name)) em.setValue(name, arr[t]);
      }
    }
    return ft;
  }

  // Round-trip on the real avatar: angle between each posed bone and its target (hands only where present).
  roundtrip() {
    const errs = { body: [], hands: [], fingers: [] };
    const angle = (a, b) => THREE.MathUtils.radToDeg(a.clone().normalize().angleTo(b.clone().normalize()));
    for (let t = 0; t < this.motion.n_frames; t++) {
      const ft = this.pose(t, false);
      this.vrm.humanoid.update();
      const got = measureDirs(this.vrm, this.rest, this.restQ);
      for (const { name, kind } of this.motion.bones) {
        const side = SIDES.find((s) => isHandBone(name, s));
        if (side && this.motion.hand_weight[side][t] < 1) continue;
        if (kind === 'dir' && got[name] && v3(ft[name].v).lengthSq() > 1e-18) {
          errs[Object.keys(FINGERS).some((f) => name.includes(f)) ? 'fingers' : 'body'].push(angle(got[name], v3(ft[name].v)));
        } else if (kind === 'frame' && got[name] && got[name][0] && v3(ft[name].v[0]).lengthSq() > 1e-18) {
          errs[name.endsWith('Hand') ? 'hands' : 'body'].push(angle(got[name][0], v3(ft[name].v[0])));
        }
      }
    }
    const summ = (v) => (v.length ? { n: v.length, mean_deg: v.reduce((a, b) => a + b, 0) / v.length, max_deg: Math.max(...v) } : null);
    return Object.fromEntries(Object.entries(errs).map(([k, v]) => [k, summ(v)]));
  }
}

async function loadVRM() {
  const loader = new GLTFLoader();
  loader.register((p) => new VRMLoaderPlugin(p));
  const gltf = await loader.loadAsync(vrmUrl);
  const vrm = gltf.userData.vrm;
  VRMUtils.removeUnnecessaryVertices(gltf.scene);
  VRMUtils.rotateVRM0(vrm);
  vrm.scene.traverse((o) => { o.frustumCulled = false; });
  return vrm;
}

function wrapText(text, x, y, maxW, lineH) {
  let line = '';
  for (const word of text.split(' ')) {
    const test = line ? `${line} ${word}` : word;
    if (ctx.measureText(test).width > maxW && line) { ctx.fillText(line, x, y); line = word; y += lineH; } else line = test;
  }
  ctx.fillText(line, x, y);
}

async function main() {
  if (!params.get('demo')) throw new Error('add ?demo=/work/demo/<demo folder>/ to the address');
  const get = async (f) => { const r = await fetch(demoDir + f); if (!r.ok) throw new Error(`${f}: HTTP ${r.status}`); return r.json(); };
  const [log, mB, m1] = await Promise.all([get('demo_log.json'), get('motion_modelB.json'), get('motion_B1.json')]);
  const vrms = [await loadVRM(), await loadVRM()];
  const panels = [mB, m1].map((m, i) => new Panel(vrms[i], m));
  const subtitles = ['predicted from the G0 gloss (pilot model)', `replays: ${log.b1.sentence_norm}`];

  state.roundtrip = { modelB: panels[0].roundtrip(), B1: panels[1].roundtrip() };
  const renderer = new THREE.WebGLRenderer({ canvas: glCanvas, antialias: true });
  renderer.setPixelRatio(1);
  renderer.setSize(2 * W, H, false);
  out.width = 2 * W; out.height = HEAD + H + FOOT;
  const fps = mB.fps;
  const total = Math.max(mB.n_frames, m1.n_frames) + Math.round(fps);   // hold ~1 s at the end
  let last = performance.now();

  const fmt = (r) => (r ? `${r.mean_deg.toFixed(2)}° (max ${r.max_deg.toFixed(1)}°)` : '–');
  statusEl.textContent = `Sentence: ${log.sentence}   G0 gloss: ${log.g0_gloss}\n` +
    `Round-trip on this avatar, mean (max): Model B body ${fmt(state.roundtrip.modelB.body)}, hands ${fmt(state.roundtrip.modelB.hands)}, fingers ${fmt(state.roundtrip.modelB.fingers)}; ` +
    `B1 body ${fmt(state.roundtrip.B1.body)}, hands ${fmt(state.roundtrip.B1.hands)}, fingers ${fmt(state.roundtrip.B1.fingers)}\n` +
    `Demo folder: ${demoDir}   VRM ${vrms[0].meta?.metaVersion === '0' ? '0.x' : '1.0'}`;

  function frame(now) {
    const dt = Math.max(0, (now - last) / 1000); last = now;
    if (state.playing) state.t += dt;
    let f = Math.floor(state.t * fps);
    if (f >= total) {
      if (state.recorder) { state.recorder.stop(); state.recorder = null; }
      state.t = 0; f = 0;
    }
    renderer.setScissorTest(true);
    panels.forEach((p, i) => {
      const k = Math.min(f, p.motion.n_frames - 1);
      p.pose(k, state.mirror);
      p.vrm.update(dt);
      renderer.setViewport(i * W, 0, W, H);
      renderer.setScissor(i * W, 0, W, H);
      renderer.render(p.scene, p.camera);
    });
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, out.width, out.height);
    ctx.drawImage(glCanvas, 0, HEAD);
    ctx.fillStyle = '#1d1d1b'; ctx.font = '600 17px system-ui, "Nirmala UI", sans-serif';
    ctx.fillText(`“${log.sentence}”`, 12, 24);
    ctx.font = '13px system-ui, "Nirmala UI", sans-serif'; ctx.fillStyle = '#55554f';
    ctx.fillText(`G0 gloss: ${log.g0_gloss}${state.mirror ? '   ·   MIRRORED' : ''}`, 12, 46);
    panels.forEach((p, i) => {
      const k = Math.min(f, p.motion.n_frames - 1);
      ctx.fillStyle = '#1d1d1b'; ctx.font = '600 14px system-ui, "Nirmala UI", sans-serif';
      wrapText(p.motion.label, i * W + 10, HEAD + 20, W - 20, 17);
      ctx.font = '12px system-ui, "Nirmala UI", sans-serif'; ctx.fillStyle = '#55554f';
      ctx.fillText(subtitles[i], i * W + 10, HEAD + 58);
      ctx.fillText(`frame ${k + 1}/${p.motion.n_frames}${f >= p.motion.n_frames ? ' (ended)' : ''}`, i * W + 10, HEAD + H - 10);
    });
    ctx.strokeStyle = '#d4d4cf'; ctx.beginPath(); ctx.moveTo(W, HEAD); ctx.lineTo(W, HEAD + H); ctx.stroke();
    ctx.fillStyle = '#f4f4f2'; ctx.fillRect(0, HEAD + H, out.width, FOOT);
    ctx.fillStyle = '#55554f'; ctx.font = '12px system-ui, sans-serif';
    ctx.fillText(`Pipeline test — not checked by a BdSL-competent person · ${VERSIONS}`, 12, HEAD + H + 20);
    state.frame = f;
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  document.getElementById('play').onclick = (e) => { state.playing = !state.playing; e.target.textContent = state.playing ? 'Pause' : 'Play'; };
  document.getElementById('restart').onclick = () => { state.t = 0; };
  document.getElementById('mirror').onchange = (e) => { state.mirror = e.target.checked; };
  document.getElementById('record').onclick = () => {
    if (state.recorder) return;
    const type = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
    const rec = new MediaRecorder(out.captureStream(30), { mimeType: type });
    const chunks = [];
    rec.ondataavailable = (e) => chunks.push(e.data);
    rec.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      state.lastRecordingBytes = blob.size;
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `bdsl_demo_${log.created_utc}${state.mirror ? '_mirrored' : ''}.webm`;
      a.textContent = `Save recording (${(blob.size / 1e6).toFixed(1)} MB)`;
      statusEl.append('\n', a);
    };
    state.t = 0; state.playing = true;
    rec.start(); state.recorder = rec;
  };
}

main().catch((e) => { state.error = String(e); statusEl.textContent = `Error: ${e.message || e}`; console.error(e); });
