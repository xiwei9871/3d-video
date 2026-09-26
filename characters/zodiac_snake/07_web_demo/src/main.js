import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const ASSET_URL = './public/zodiac_snake_character_v1_runtime.glb';
const EXPECTED_SEMANTICS = ['idle', 'head_shake', 'head_tilt', 'body_sway', 'bounce', 'tail_wag', 'tongue_flick'];
const canvas = document.querySelector('#viewport');
const statusEl = document.querySelector('#status');
const auditEl = document.querySelector('#audit');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d131d);

const camera = new THREE.PerspectiveCamera(32, 1, 0.01, 100);
camera.position.set(1.55, 0.9, 2.55);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = false;
renderer.info.autoReset = true;

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.target.set(0, 0.48, 0);
controls.minDistance = 1.2;
controls.maxDistance = 4.5;

scene.add(new THREE.HemisphereLight(0xffffff, 0x50545a, 1.0));
const key = new THREE.DirectionalLight(0xffffff, 2.0);
key.position.set(-2.5, 4, 3.5);
scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.45);
fill.position.set(3, 1.5, 2.5);
scene.add(fill);

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let model = null;
let mixer = null;
let clips = [];
let clipMap = new Map();
let currentAction = null;
let currentSemantic = 'idle';
let hoverActive = false;
let hoverTimer = null;
let firstVisibleMs = null;
const clock = new THREE.Clock();
const metricState = {
  asset: { url: ASSET_URL },
  load: {},
  scene: {},
  clips: {},
  interactions: [],
  benchmark: { plan: [], results: [], complete_ms: null, active: null },
  frameSamples: [],
  idleLoop: { started_ms: null, elapsed_ms: 0, root_baseline: null, max_root_drift: 0, root_position_track_count: null },
};

function normalize(name) {
  return String(name).toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
}

function semanticForClip(name) {
  const n = normalize(name);
  if (n.includes('idle')) return 'idle';
  if (n.includes('head') && (n.includes('shake') || n.includes('look'))) return 'head_shake';
  if (n.includes('head') && n.includes('tilt')) return 'head_tilt';
  if (n.includes('body') && n.includes('sway')) return 'body_sway';
  if (n.includes('bounce')) return 'bounce';
  if (n.includes('tail') && n.includes('wag')) return 'tail_wag';
  if (n.includes('tongue') && n.includes('flick')) return 'tongue_flick';
  return null;
}

function fitModel(root) {
  const box = new THREE.Box3().setFromObject(root);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  root.position.sub(center);
  root.position.y += size.y * 0.5;
  controls.target.set(0, size.y * 0.42, 0);
  // Whole-character review framing target: roughly 50–70% of canvas height.
  camera.position.set(size.x * 2.23, size.y * 1.22, size.z * 3.65);
  camera.near = Math.max(size.length() / 100, 0.001);
  camera.far = size.length() * 20;
  camera.updateProjectionMatrix();
}

function sceneAudit(root, gltfAnimations, transferBytes) {
  const meshes = [];
  const materials = new Set();
  const textures = new Set();
  const boneNames = [];
  let triangles = 0;
  let skinnedMeshes = 0;
  let bones = 0;
  root.traverse((object) => {
    if (object.isMesh) {
      meshes.push(object);
      if (object.isSkinnedMesh) skinnedMeshes += 1;
      const geometry = object.geometry;
      if (geometry.index) triangles += geometry.index.count / 3;
      else if (geometry.attributes.position) triangles += geometry.attributes.position.count / 3;
      const slots = Array.isArray(object.material) ? object.material : [object.material];
      slots.filter(Boolean).forEach((material) => {
        materials.add(material.name || '(unnamed)');
        for (const key of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap']) {
          if (material[key]) textures.add(material[key].uuid);
        }
      });
    }
    if (object.isBone) {
      bones += 1;
      boneNames.push(object.name);
    }
  });
  metricState.scene = {
    mesh_count: meshes.length,
    skinned_mesh_count: skinnedMeshes,
    bones,
    bone_names: boneNames.sort(),
    triangles: Math.round(triangles),
    materials: [...materials].sort(),
    texture_count: textures.size,
    glb_size_bytes: transferBytes,
  };
  clips = gltfAnimations;
  clipMap = new Map();
  clips.forEach((clip) => {
    const semantic = semanticForClip(clip.name);
    if (semantic) clipMap.set(semantic, clip);
  });
  metricState.clips = {
    three_revision: THREE.REVISION,
    count: clips.length,
    names: clips.map((clip) => clip.name),
    details: clips.map((clip) => ({ name: clip.name, duration_seconds: Number(clip.duration.toFixed(6)), tracks: clip.tracks.length })),
    semantic_map: Object.fromEntries([...clipMap].map(([semantic, clip]) => [semantic, clip.name])),
    track_names: Object.fromEntries(clips.map((clip) => [clip.name, clip.tracks.map((track) => track.name)])),
  };
  const idleClip = clipMap.get('idle');
  const rootTrackCount = idleClip?.tracks.filter((track) => /(^|[/.])ROOT([/.]|$)/i.test(track.name) && /\.position$/.test(track.name)).length ?? 0;
  metricState.idleLoop.root_position_track_count = rootTrackCount;
}

function auditText() {
  const s = metricState.scene;
  const c = metricState.clips;
  const missing = EXPECTED_SEMANTICS.filter((name) => !c.semantic_map?.[name]);
  const lines = [
    `GLB: ${metricState.load.transfer_bytes ?? '…'} bytes`,
    `mesh objects: ${s.mesh_count ?? '…'} · skinned: ${s.skinned_mesh_count ?? '…'} · bones: ${s.bones ?? '…'}`,
    `triangles: ${s.triangles ?? '…'} · materials: ${(s.materials || []).join(', ') || '…'} · textures: ${s.texture_count ?? '…'}`,
    `clips: ${c.count ?? '…'} · ${c.names?.join(', ') || '…'}`,
    `semantic map: ${c.semantic_map ? JSON.stringify(c.semantic_map) : '…'}`,
    missing.length ? `missing semantics: ${missing.join(', ')}` : 'semantic actions: complete',
  ];
  auditEl.textContent = lines.join('\n');
}

function playSemantic(semantic, options = {}) {
  if (!mixer || !model) return false;
  const clip = clipMap.get(semantic) || clipMap.get('idle');
  if (!clip) return false;
  const next = mixer.clipAction(clip, model);
  const previous = currentAction;
  if (previous && previous !== next) next.crossFadeFrom(previous, options.fade ?? 0.2, false);
  next.reset();
  if (semantic === 'idle') {
    next.setLoop(THREE.LoopRepeat, Infinity);
    next.clampWhenFinished = false;
  } else {
    next.setLoop(THREE.LoopOnce, 1);
    next.clampWhenFinished = true;
  }
  next.play();
  currentAction = next;
  currentSemantic = semantic;
  metricState.interactions.push({ type: options.type || 'button', semantic, clip: clip.name, time_ms: performance.now() });
  return true;
}

function returnToIdle() {
  if (currentSemantic !== 'idle') playSemantic('idle', { fade: 0.18, type: 'auto_return' });
}

function captureBonePose() {
  const pose = {};
  model?.traverse((object) => {
    if (object.isBone) {
      pose[object.name] = {
        position: object.position.toArray(),
        quaternion: object.quaternion.toArray(),
      };
    }
  });
  return pose;
}

function auditIdleBoundary() {
  const clip = clipMap.get('idle');
  if (!clip || !mixer || !model) return null;
  mixer.stopAllAction();
  const action = mixer.clipAction(clip, model);
  action.reset();
  action.setLoop(THREE.LoopOnce, 1);
  action.clampWhenFinished = true;
  action.play();
  mixer.update(1e-5);
  const start = captureBonePose();
  const steps = 120;
  const duration = Math.max(clip.duration - 2e-5, 0);
  for (let i = 0; i < steps; i += 1) mixer.update(duration / steps);
  const end = captureBonePose();
  let maxPositionDelta = 0;
  let maxRotationDeltaRadians = 0;
  for (const name of Object.keys(start)) {
    if (!end[name]) continue;
    maxPositionDelta = Math.max(maxPositionDelta, Math.hypot(...start[name].position.map((value, i) => value - end[name].position[i])));
    const a = start[name].quaternion;
    const b = end[name].quaternion;
    const dot = Math.min(1, Math.abs(a.reduce((sum, value, i) => sum + value * b[i], 0)));
    maxRotationDeltaRadians = Math.max(maxRotationDeltaRadians, 2 * Math.acos(dot));
  }
  const rootStart = start.ROOT?.position ?? null;
  const rootEnd = end.ROOT?.position ?? null;
  const rootDrift = rootStart && rootEnd ? Math.hypot(...rootStart.map((value, i) => value - rootEnd[i])) : null;
  metricState.idleLoop.boundary = {
    duration_seconds: clip.duration,
    max_position_delta: Number(maxPositionDelta.toFixed(7)),
    max_rotation_delta_degrees: Number((maxRotationDeltaRadians * 180 / Math.PI).toFixed(5)),
    root_start: rootStart,
    root_end: rootEnd,
    root_boundary_drift: rootDrift === null ? null : Number(rootDrift.toFixed(7)),
    pass: maxPositionDelta < 1e-4 && maxRotationDeltaRadians < Math.PI / 180,
  };
  playSemantic('idle', { fade: 0, type: 'idle_boundary_audit_restore' });
  return metricState.idleLoop.boundary;
}

function hitCharacter(event) {
  if (!model) return false;
  const rect = canvas.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  return raycaster.intersectObject(model, true).length > 0;
}

function onPointerMove(event) {
  if (!hitCharacter(event)) {
    hoverActive = false;
    return;
  }
  if (!hoverActive) {
    hoverActive = true;
    clearTimeout(hoverTimer);
    playSemantic('head_tilt', { type: 'hover', fade: 0.2 });
    hoverTimer = setTimeout(returnToIdle, 900);
  }
}

function onPointerClick(event) {
  if (!hitCharacter(event)) return;
  playSemantic('bounce', { type: 'click', fade: 0.2 });
}

function collectFrameSample(now) {
  if (!renderer.info) return;
  const rootBone = model?.getObjectByName('ROOT');
  const rootPosition = rootBone?.position.toArray().map((value) => Number(value.toFixed(6))) ?? null;
  metricState.frameSamples.push({
    t_ms: now,
    semantic: currentSemantic,
    calls: renderer.info.render.calls,
    triangles: renderer.info.render.triangles,
    points: renderer.info.render.points,
    lines: renderer.info.render.lines,
    geometries: renderer.info.memory.geometries,
    textures: renderer.info.memory.textures,
    root_position: rootPosition,
  });
  if (metricState.frameSamples.length > 1200) metricState.frameSamples.shift();
  if (currentSemantic === 'idle') {
    const rootBone = model?.getObjectByName('ROOT');
    if (rootBone) {
      const position = rootBone.position.toArray().map((value) => Number(value.toFixed(5)));
      const idle = metricState.idleLoop;
      if (idle.root_baseline === null) {
        idle.root_baseline = position;
        idle.started_ms = now;
      }
      idle.elapsed_ms = now - idle.started_ms;
      const drift = Math.hypot(...position.map((value, index) => value - idle.root_baseline[index]));
      idle.max_root_drift = Math.max(idle.max_root_drift, drift);
    }
  }
}

function resize() {
  const width = canvas.clientWidth || canvas.parentElement.clientWidth;
  const height = canvas.clientHeight || canvas.parentElement.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}

async function loadRuntime() {
  const loadStart = performance.now();
  const response = await fetch(ASSET_URL, { cache: 'no-store' });
  const bodyReadStart = performance.now();
  const arrayBuffer = await response.arrayBuffer();
  const fetchToArrayBufferMs = performance.now() - loadStart;
  const resourceTiming = performance.getEntriesByName(response.url).at(-1);
  metricState.load = {
    response_status: response.status,
    transfer_bytes: arrayBuffer.byteLength,
    fetch_to_arraybuffer_ms: Number(fetchToArrayBufferMs.toFixed(3)),
    body_read_ms: Number((performance.now() - bodyReadStart).toFixed(3)),
    resource_network_ms: resourceTiming ? Number((resourceTiming.responseEnd - resourceTiming.responseStart).toFixed(3)) : null,
    encoded_body_bytes: resourceTiming?.encodedBodySize ?? null,
    transfer_size_bytes: resourceTiming?.transferSize ?? null,
  };
  const loader = new GLTFLoader();
  const parseStart = performance.now();
  const gltf = await new Promise((resolve, reject) => loader.parse(arrayBuffer, '', resolve, reject));
  metricState.load.parse_ms = Number((performance.now() - parseStart).toFixed(3));
  model = gltf.scene;
  fitModel(model);
  scene.add(model);
  mixer = new THREE.AnimationMixer(model);
  mixer.addEventListener('finished', (event) => {
    if (event.action === currentAction && currentSemantic !== 'idle') returnToIdle();
  });
  sceneAudit(model, gltf.animations, arrayBuffer.byteLength);
  playSemantic('idle', { fade: 0, type: 'autoplay' });
  resize();
  renderer.render(scene, camera);
  firstVisibleMs = performance.now() - loadStart;
  metricState.load.first_visible_ms = Number(firstVisibleMs.toFixed(3));
  statusEl.textContent = 'Runtime asset loaded · benchmark ready';
  statusEl.className = 'ok';
  auditText();
  return gltf;
}

function updateBenchmark() {
  const now = performance.now();
  const benchmark = metricState.benchmark;
  if (!benchmark.active || benchmark.complete_ms) return;
  const active = benchmark.active;
  if (!active.started_ms) active.started_ms = now;
  const windowStart = active.started_ms;
  const samples = metricState.frameSamples.filter((sample) => sample.t_ms >= windowStart && sample.t_ms <= now);
  if (now - windowStart >= active.duration_ms) {
    if (samples.length) {
      const avg = (key) => samples.reduce((sum, sample) => sum + sample[key], 0) / samples.length;
      const roots = samples.map((sample) => sample.root_position).filter(Boolean);
      const rootBaseline = roots[0] || [0, 0, 0];
      const maxRootDrift = roots.length ? Math.max(...roots.map((position) => Math.hypot(...position.map((value, index) => value - rootBaseline[index])))) : null;
      benchmark.results.push({
        semantic: active.semantic,
        duration_ms: Number((now - windowStart).toFixed(3)),
        samples: samples.length,
        average_fps: Number((samples.length / ((now - windowStart) / 1000)).toFixed(3)),
        average_frame_time_ms: Number((((now - windowStart) / Math.max(samples.length, 1))).toFixed(3)),
        average_draw_calls: Number(avg('calls').toFixed(3)),
        average_triangles: Number(avg('triangles').toFixed(3)),
        average_points: Number(avg('points').toFixed(3)),
        average_lines: Number(avg('lines').toFixed(3)),
        max_root_position_drift: maxRootDrift === null ? null : Number(maxRootDrift.toFixed(7)),
        geometries: samples.at(-1).geometries,
        textures: samples.at(-1).textures,
      });
    }
    const nextIndex = benchmark.results.length;
    if (nextIndex < benchmark.plan.length) {
      const nextSemantic = benchmark.plan[nextIndex];
      playSemantic(nextSemantic, { type: 'benchmark', fade: 0.12 });
      benchmark.active = { semantic: nextSemantic, duration_ms: benchmark.duration_ms, started_ms: now };
    } else {
      benchmark.complete_ms = now;
      statusEl.textContent = 'Runtime benchmark complete';
      statusEl.className = 'ok';
    }
  }
}

function startBenchmark() {
  if (!mixer || metricState.benchmark.complete_ms) return metricState.benchmark;
  metricState.benchmark = {
    plan: ['idle', 'head_shake', 'body_sway', 'tail_wag', 'bounce'],
    duration_ms: 1400,
    results: [],
    complete_ms: null,
    active: { semantic: 'idle', duration_ms: 1400, started_ms: performance.now() },
  };
  playSemantic('idle', { type: 'benchmark', fade: 0 });
  return metricState.benchmark;
}

window.__snakeRuntime = {
  play: playSemantic,
  startBenchmark,
  getMetrics: () => ({ ...metricState, load: { ...metricState.load }, scene: { ...metricState.scene }, clips: { ...metricState.clips }, browser: { user_agent: navigator.userAgent, viewport_width: window.innerWidth, viewport_height: window.innerHeight, device_pixel_ratio: window.devicePixelRatio }, renderer: { calls: renderer.info.render.calls, triangles: renderer.info.render.triangles, points: renderer.info.render.points, lines: renderer.info.render.lines, geometries: renderer.info.memory.geometries, textures: renderer.info.memory.textures, canvas_width: renderer.domElement.width, canvas_height: renderer.domElement.height } }),
  getState: () => ({ currentSemantic, ready: Boolean(model && mixer), firstVisibleMs }),
  getPose: () => ({ currentAction: currentAction?.getClip().name ?? null, bones: model ? model.children.flatMap((root) => { const found = []; root.traverse((object) => { if (object.isBone) found.push({ name: object.name, position: object.position.toArray().map((value) => Number(value.toFixed(5))), quaternion: object.quaternion.toArray().map((value) => Number(value.toFixed(5))) }); }); return found; }) : [] }),
  auditIdleBoundary,
};

document.querySelectorAll('[data-action]').forEach((button) => {
  button.addEventListener('click', () => playSemantic(button.dataset.action, { type: 'button', fade: 0.2 }));
});
canvas.addEventListener('pointermove', onPointerMove);
canvas.addEventListener('click', onPointerClick);
window.addEventListener('resize', resize);

loadRuntime().catch((error) => {
  console.error(error);
  statusEl.textContent = `Runtime load failed: ${error.message}`;
  statusEl.className = 'fail';
  auditEl.textContent = String(error.stack || error);
});

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  if (mixer) mixer.update(delta);
  controls.update();
  renderer.render(scene, camera);
  collectFrameSample(performance.now());
  updateBenchmark();
}
animate();
