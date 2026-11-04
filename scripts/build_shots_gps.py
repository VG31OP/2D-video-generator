import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REEL_DIR = ROOT_DIR / "storage" / "reels" / "zach_gps_satellites"
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
  mapsPhone,
  stylizedEarth,
  gpsSatellite,
  orbitalConstellation,
  trilaterationVisual,
  locationPinDrop,
  mountainPedestal,
  spySatelliteBadge
}} from './props.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration};

export const CAPTIONS = {json.dumps(captions, indent=2)};

// Dip to black after misconception twist (12.45s - 12.62s)
export const FADES = [[12.45, 12.52, 12.58, 12.62]];

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

// ============ SHOT 1: Zack lost on cliff opens Google Maps (0.00 - 4.39s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const ped = mountainPedestal(); scene.add(ped);

  const man = makeHuman('casual');
  man.root.position.set(0, 0, 0);
  scene.add(man.root);

  const phone = mapsPhone();
  scene.add(phone);

  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      const lookDown = range(lt, 0.2, 1.8);
      standPose(man, lt, {{
        rSh: [lerp(0.3, 0.8, lookDown), -0.2, lerp(0.2, 0.35, lookDown)],
        rEl: [lerp(-0.5, -1.25, lookDown), 0, 0],
        head: [lerp(0.02, 0.18, lookDown), 0, 0],
      }});

      phone.position.set(0.08, 1.34 + idle(lt, 0.5), 0.38);
      phone.rotation.set(-0.45, -0.18, 0.05);

      // Pulse radar ring on screen
      const rScale = 1.0 + Math.sin(lt * 5) * 0.3;
      phone.radarRing.scale.set(rScale, rScale, 1);

      c.position.set(0.16, 1.45, 1.95);
      c.lookAt(0.02, 1.35, 0.1);
    }}
  }};
}}

// ============ SHOT 2: Misconception: Are satellites actively spying? (4.39 - 8.70s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const spySat = spySatelliteBadge();
  spySat.position.set(0, 1.45, 0);
  scene.add(spySat);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      spySat.rotation.y = Math.sin(lt * 0.8) * 0.25;
      spySat.rotation.x = 0.12;

      // Camera pulls out dramatically
      const push = range(lt, 0, 3.5);
      c.position.set(0, 1.48, lerp(0.9, 1.25, push));
      c.lookAt(0, 1.42, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! GPS satellites don't know you exist (8.70 - 12.62s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 3.0 }});
  const earth = stylizedEarth(0.75);
  earth.position.set(0, 0.6, -0.6);
  scene.add(earth);

  const sat = gpsSatellite();
  sat.position.set(0.35, 1.4, 0.1);
  sat.scale.setScalar(1.2);
  scene.add(sat);

  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      earth.rotation.y = lt * 0.15;
      sat.rotation.y = -lt * 0.2;

      c.position.set(0.2, 1.45, 1.85);
      c.lookAt(0.1, 1.1, -0.2);
    }}
  }};
}}

// ============ SHOT 4: Phone sends ZERO signal back to space (12.62 - 16.21s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const phone = mapsPhone();
  phone.position.set(0, 1.4, 0);
  scene.add(phone);

  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      phone.rotation.y = Math.sin(lt * 1.2) * 0.2;
      phone.rotation.x = -0.15;

      c.position.set(0, 1.42, 0.95);
      c.lookAt(0, 1.4, 0);
    }}
  }};
}}

// ============ SHOT 5: 31 Satellites Constellation & Atomic Clocks (16.21 - 23.64s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 3.5 }});
  const earth = stylizedEarth(0.65);
  earth.position.set(0, 1.35, 0);
  scene.add(earth);

  const constell = orbitalConstellation(0.65);
  constell.position.set(0, 1.35, 0);
  scene.add(constell);

  const c = cam(44);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      earth.rotation.y = lt * 0.12;
      constell.rotation.y = lt * 0.08;

      // Cinematic orbit camera push
      const orbitAngle = lt * 0.18;
      c.position.set(Math.sin(orbitAngle) * 2.3, 1.65, Math.cos(orbitAngle) * 2.3);
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 6: 4 Satellites sending Radio Waves (23.64 - 29.92s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const trilateral = trilaterationVisual();
  trilateral.position.set(0, 1.2, 0);
  scene.add(trilateral);

  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      trilateral.rotation.y = lt * 0.22;

      // Satellites pulse timed radio waves
      trilateral.nodes.forEach((n, idx) => {{
        n.scale.setScalar(1.0 + Math.sin(lt * 5 + idx * 1.5) * 0.15);
      }});

      c.position.set(0.15, 1.55, 1.88);
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 7: Trilateration: 4 Intersecting Spheres Lock In (29.92 - 36.81s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const trilateral = trilaterationVisual();
  trilateral.position.set(0, 1.3, 0);
  scene.add(trilateral);

  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      trilateral.rotation.y = lt * 0.35;

      // 4 spheres expand and intersect
      const sphereScale = lerp(0.6, 1.35, range(lt, 0, 4.0));
      trilateral.spheres.forEach(sp => {{
        sp.scale.setScalar(sphereScale);
      }});

      // Target point flashes
      const flash = (Math.sin(lt * 8) > 0) ? 1.4 : 0.8;
      trilateral.target.scale.setScalar(flash);

      c.position.set(0.08, 1.48, 1.65);
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff: Blue Pin Drops with Bounce! (36.81 - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const ped = mountainPedestal(); scene.add(ped);

  const man = makeHuman('casual');
  man.root.position.set(-0.25, 0, 0);
  scene.add(man.root);

  const pinDrop = locationPinDrop();
  pinDrop.position.set(0.22, 0.05, 0.15);
  scene.add(pinDrop);

  const phone = mapsPhone();
  phone.position.set(-0.16, 1.32, 0.35);
  phone.rotation.set(-0.4, 0.1, 0.05);
  scene.add(phone);

  const c = cam(44);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.75, -0.2, 0.35], rEl: [-1.2, 0, 0], head: [0.08, -0.15, 0]
      }});

      // Pin drops with spring bounce at lt ~ 0.4s
      const pinFall = range(lt, 0.2, 0.8);
      // Damped harmonic bounce
      const bounce = Math.sin(pinFall * Math.PI * 2.5) * Math.exp(-pinFall * 3) * 0.15;
      pinDrop.pin.position.y = lerp(0.65, 0, pinFall) + Math.max(0, bounce);

      // Radar rings expand on the ground
      const ringT = range(lt, 0.7, 3.5);
      pinDrop.ring.scale.setScalar(lerp(0.5, 4.2, ringT));
      pinDrop.ring.material.opacity = lerp(0.7, 0, ringT);

      c.position.set(0.08, 1.45, 2.05);
      c.lookAt(0, 1.30, 0.1);
    }}
  }};
}}

export const SHOTS = [
  {{ start: 0.00, end: 4.39, build: shot1 }},
  {{ start: 4.39, end: 8.70, build: shot2 }},
  {{ start: 8.70, end: 12.62, build: shot3 }},
  {{ start: 12.62, end: 16.21, build: shot4 }},
  {{ start: 16.21, end: 23.64, build: shot5 }},
  {{ start: 23.64, end: 29.92, build: shot6 }},
  {{ start: 29.92, end: 36.81, build: shot7 }},
  {{ start: 36.81, end: {duration}, build: shot8 }},
];
"""

with open(SHOTS_FILE, "w", encoding="utf-8") as f:
    f.write(shots_js)

print(f"Generated GPS shots.js successfully! Duration: {duration}s, Shots: 8, Captions: {len(captions)}")

