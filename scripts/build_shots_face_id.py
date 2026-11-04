import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REEL_DIR = ROOT_DIR / "storage" / "reels" / "zach_face_id"
WORDS_FILE = REEL_DIR / "audio" / "vo.words.json"
SHOTS_FILE = REEL_DIR / "src" / "shots.js"

words = json.load(open(WORDS_FILE, "r", encoding="utf-8"))
small = {'a', 'an', 'the', 'at', 'to', 'of', 'in', 'on', 'and', 'or', 'but', 'for', 'with', 'by', 'it', 'is', 'like', 'as', 'so'}
captions = []
cur = []
for j, w in enumerate(words):
    cur.append(w)
    text = ' '.join(x['w'] for x in cur)
    stop = any(w['w'].endswith(p) for p in ['.', ',', '?', '!', ';', ':'])
    dangling = w['w'].lower() in small and j + 1 < len(words) and len(cur) < 4
    if stop or ((len(cur) >= 3 or len(text) >= 18) and not dangling):
        c_text = ' '.join(x['w'] for x in cur).rstrip('.,;:').replace("'", "\\'")
        captions.append([round(cur[0]['s'], 2), c_text])
        cur = []
if cur:
    c_text = ' '.join(x['w'] for x in cur).rstrip('.,;:').replace("'", "\\'")
    captions.append([round(cur[0]['s'], 2), c_text, round(cur[-1]['e'] + 0.3, 2)])

duration = round(words[-1]["e"] + 0.5, 2)

shots_js = f"""import * as THREE from 'three';
import {{ makeHuman }} from './human.js';
import {{
  modernPhone,
  explodedNotchSensors,
  infraredFloodCone,
  dotProjectorGrid,
  biometricFaceMesh,
  floatingUnlockBadge,
  cameraOffBadge,
  bedroomEnvironment
}} from './props.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration};

export const CAPTIONS = {json.dumps(captions, indent=2)};

// Dip to black after misconception twist (9.65s - 9.85s)
export const FADES = [[9.65, 9.72, 9.78, 9.85]];

function idle(t, k = 1) {{ return Math.sin(t * 1.6) * 0.012 * k; }}

const STAND = {{
  lSh: [0.05, 0, 0.16], rSh: [0.05, 0, -0.16], lEl: [-0.25, 0, 0], rEl: [-0.25, 0, 0],
  lHip: [0, 0, 0.07], rHip: [0, 0, -0.07], lAn: [0, 0, -0.07], rAn: [0, 0, 0.07],
}};

function standPose(h, t, extra = {{}}) {{
  const p = {{ ...STAND, ...extra }};
  p.chest = [idle(t) + (extra.chest?.[0] || 0), extra.chest?.[1] || 0, extra.chest?.[2] || 0];
  h.setPose(p);
}}

// ============ SHOT 1: Zack unlocks phone in dark bedroom (0.00 - 2.34s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const env = bedroomEnvironment(); scene.add(env);

  const man = makeHuman('casual');
  man.root.position.set(0, 0, 0);
  scene.add(man.root);

  const phone = modernPhone();
  scene.add(phone);

  // Zoomed-out camera framing FOV 43, distance Z=1.85m
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      // Zack lifts phone towards face
      const lift = range(lt, 0.0, 1.4);
      standPose(man, lt, {{
        rSh: [lerp(0.3, 0.75, lift), -0.2, lerp(0.2, 0.35, lift)],
        rEl: [lerp(-0.5, -1.2, lift), 0, 0],
        head: [0.08, 0, 0],
      }});

      phone.position.set(0.08, 1.35 + idle(lt, 0.5), 0.35);
      phone.rotation.set(-0.35, -0.2, 0.05);

      // Camera glides smoothly
      c.position.set(0.12, 1.42, 1.85);
      c.lookAt(0.04, 1.38, 0.1);
    }}
  }};
}}

// ============ SHOT 2: Misconception: Does camera take a photo? (2.34 - 6.86s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const phone = modernPhone();
  phone.position.set(0, 1.4, 0);
  scene.add(phone);

  const noCam = cameraOffBadge();
  noCam.position.set(0.18, 1.48, 0.12);
  scene.add(noCam);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      const p = range(lt, 0, 3.5);
      phone.rotation.y = lerp(-0.25, 0.15, p);
      phone.rotation.x = 0.05;

      // Red X pulses
      const pulse = 1.0 + Math.sin(lt * 6) * 0.06;
      noCam.scale.set(pulse, pulse, pulse);

      c.position.set(0.05, 1.42, 0.95);
      c.lookAt(0, 1.4, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! Camera isn't on (6.86 - 9.85s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.0 }});
  const phone = modernPhone();
  phone.position.set(0, 1.4, 0);
  scene.add(phone);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      // Pull-in into notch
      const push = range(lt, 0, 2.5);
      phone.position.y = 1.4;
      c.position.set(0, 1.46 - push * 0.02, lerp(0.85, 0.52, push));
      c.lookAt(0, 1.46, 0);
    }}
  }};
}}

// ============ SHOT 4: Step 1: Invisible Flood Illuminator (9.85 - 14.46s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const man = makeHuman('casual');
  man.root.position.set(0, 0, -0.1);
  scene.add(man.root);

  const phone = modernPhone();
  phone.position.set(0.06, 1.36, 0.38);
  phone.rotation.set(-0.35, -0.15, 0.02);
  scene.add(phone);

  const flood = infraredFloodCone();
  flood.position.set(0.06, 1.42, 0.38);
  flood.rotation.set(0.35, 0.15, 0);
  scene.add(flood);

  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.75, -0.2, 0.35], rEl: [-1.2, 0, 0], head: [0.06, 0, 0]
      }});

      // Soft infrared flood wave expands
      const pulse = 0.8 + Math.sin(lt * 4.5) * 0.2;
      flood.scale.set(pulse, pulse, pulse);

      c.position.set(0.18, 1.46, 1.82);
      c.lookAt(0.02, 1.38, 0);
    }}
  }};
}}

// ============ SHOT 5: Step 2: Dot Projector fires 30,000 laser beams (14.46 - 21.37s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});

  // Macro view of dot projector firing
  const sensors = explodedNotchSensors();
  sensors.position.set(0, 1.4, 0);
  scene.add(sensors);

  const dots = dotProjectorGrid(500);
  dots.position.set(0.10, 1.4, 0.03);
  scene.add(dots);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      const beamProgress = range(lt, 0.2, 2.0);
      dots.scale.set(beamProgress, beamProgress, beamProgress);

      // Rotate slightly to see 3D cone
      sensors.rotation.y = Math.sin(lt * 0.8) * 0.15;
      dots.rotation.y = sensors.rotation.y;

      c.position.set(0.08, 1.42, 0.78);
      c.lookAt(0.06, 1.4, 0);
    }}
  }};
}}

// ============ SHOT 6: Step 3: Dots contour over nose, eyes & cheekbones (21.37 - 27.00s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const man = makeHuman('casual');
  man.root.position.set(0, 0, 0);
  scene.add(man.root);

  const faceMesh = biometricFaceMesh();
  faceMesh.position.set(0, 1.58, 0.02);
  scene.add(faceMesh);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ head: [0.04, Math.sin(lt * 0.7) * 0.08, 0] }});
      faceMesh.rotation.y = Math.sin(lt * 0.7) * 0.08;

      // Contour points oscillate with scanning pulse
      const scanPhase = (lt * 2.5) % 1;
      faceMesh.landmarks.children.forEach((dot, idx) => {{
        dot.scale.setScalar(1.0 + Math.sin(lt * 6 + idx) * 0.25);
      }});

      c.position.set(0, 1.62, 0.78);
      c.lookAt(0, 1.58, 0);
    }}
  }};
}}

// ============ SHOT 7: Step 4: Converting into Mathematical Mesh (27.00 - 33.95s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const mesh = biometricFaceMesh();
  mesh.position.set(0, 1.4, 0);
  scene.add(mesh);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      // Full 3D rotating mathematical mesh
      mesh.rotation.y = lt * 0.6;
      mesh.rotation.x = Math.sin(lt * 0.4) * 0.12;

      const p = range(lt, 0.0, 3.0);
      mesh.scale.setScalar(lerp(0.9, 1.15, p));

      c.position.set(0, 1.42, 0.82);
      c.lookAt(0, 1.4, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff: Instant Millisecond Unlock! (33.95 - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const env = bedroomEnvironment(); scene.add(env);

  const man = makeHuman('casual');
  man.root.position.set(0, 0, 0);
  scene.add(man.root);

  const phone = modernPhone();
  phone.position.set(0.06, 1.38, 0.38);
  phone.rotation.set(-0.32, -0.15, 0.02);
  scene.add(phone);

  const badge = floatingUnlockBadge();
  badge.position.set(0.08, 1.68, 0.32);
  scene.add(badge);

  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.75, -0.2, 0.35], rEl: [-1.2, 0, 0], head: [0.04, 0, 0]
      }});

      // Spring bounce unlock at lt ~ 0.5s
      const unlockT = range(lt, 0.2, 0.9);
      badge.shackle.position.y = lerp(0.04, 0.075, unlockT);
      badge.shackle.rotation.y = lerp(0, 0.6, unlockT);

      // Ripple ring expands
      const ringT = range(lt, 0.5, 2.5);
      badge.ring.scale.setScalar(lerp(0.5, 3.5, ringT));
      badge.ring.material.opacity = lerp(0.8, 0.0, ringT);

      // Phone screen turns bright green
      if (lt > 0.6) {{
        phone.screen.material = materials().phoneScreenUnlock;
      }}

      c.position.set(0.12, 1.46, 1.85);
      c.lookAt(0.04, 1.40, 0.1);
    }}
  }};
}}

export const SHOTS = [
  {{ start: 0.00, end: 2.34, build: shot1 }},
  {{ start: 2.34, end: 6.86, build: shot2 }},
  {{ start: 6.86, end: 9.85, build: shot3 }},
  {{ start: 9.85, end: 14.46, build: shot4 }},
  {{ start: 14.46, end: 21.37, build: shot5 }},
  {{ start: 21.37, end: 27.00, build: shot6 }},
  {{ start: 27.00, end: 33.95, build: shot7 }},
  {{ start: 33.95, end: {duration}, build: shot8 }},
];
"""

with open(SHOTS_FILE, "w", encoding="utf-8") as f:
    f.write(shots_js)

print(f"Generated shots.js successfully! Duration: {duration}s, Shots: 8, Captions: {len(captions)}")
