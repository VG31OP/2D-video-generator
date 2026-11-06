"""
3D Procedural Scene Builder (Three.js WebGL / Playwright Runner)
Dynamically builds topic-synchronized 3D scenes with active physical props,
microscopic cutaways, particle streams, sparks, and Apple Fluid camera easing.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.config import TEMPLATES_DIR, find_node_modules


class SceneBuilder:
    def setup_project(self, project_dir: Path) -> None:
        """
        Initializes the self-contained Three.js environment in the reel directory.
        """
        project_dir.mkdir(parents=True, exist_ok=True)

        # Copy template files
        for item in TEMPLATES_DIR.iterdir():
            if item.name == "node_modules":
                continue
            dst = project_dir / item.name
            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)

        # Cross-platform link to node_modules
        dst_modules = project_dir / "node_modules"
        if not dst_modules.exists():
            src_modules = find_node_modules()
            if src_modules and src_modules.exists():
                try:
                    if sys.platform == "win32":
                        subprocess.run(["cmd", "/c", "mklink", "/J", str(dst_modules), str(src_modules)], check=True, capture_output=True)
                    else:
                        os.symlink(src_modules, dst_modules)
                except Exception:
                    shutil.copytree(src_modules, dst_modules)
            else:
                subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=str(project_dir), check=True)

    def build_shots_file(
        self,
        project_dir: Path,
        captions: List[List[Any]],
        duration: float,
        meta_lines: List[Dict[str, Any]] = None,
        topic: str = ""
    ) -> Path:
        """
        Generates src/shots.js with 8 shots mapped to the 8-sentence viral formula,
        synchronizing 3D props, microscopic cutaways, particles, and character animations.
        """
        shots_file = project_dir / "src" / "shots.js"
        shots_file.parent.mkdir(parents=True, exist_ok=True)
        t_lower = topic.lower()

        # Calculate shot boundaries based on duration or meta_lines
        if meta_lines and len(meta_lines) == 8:
            t1 = round(meta_lines[1]["start"], 2)
            t2 = round(meta_lines[2]["start"], 2)
            t3 = round(meta_lines[3]["start"], 2)
            t4 = round(meta_lines[4]["start"], 2)
            t5 = round(meta_lines[5]["start"], 2)
            t6 = round(meta_lines[6]["start"], 2)
            t7 = round(meta_lines[7]["start"], 2)
            twist_fade_start = round(t2 - 0.15, 2)
            twist_fade_end = round(t2 + 0.05, 2)
        else:
            seg = duration / 8.0
            t1 = round(seg * 1, 2)
            t2 = round(seg * 2, 2)
            t3 = round(seg * 3, 2)
            t4 = round(seg * 4, 2)
            t5 = round(seg * 5, 2)
            t6 = round(seg * 6, 2)
            t7 = round(seg * 7, 2)
            twist_fade_start = round(t2 - 0.15, 2)
            twist_fade_end = round(t2 + 0.05, 2)

        # Domain selection
        if "rice" in t_lower:
            shots_code = self._generate_rice_phone_shots(t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions)
        elif any(w in t_lower for w in ["battery", "puncture", "explode"]):
            shots_code = self._generate_battery_puncture_shots(t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions)
        elif any(w in t_lower for w in ["gum", "swallow", "stomach", "digest", "gut"]):
            shots_code = self._generate_digestion_shots(t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions)
        else:
            shots_code = self._generate_tech_gadget_shots(t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions, topic)

        shots_file.write_text(shots_code, encoding="utf-8")
        return shots_file

    def _generate_rice_phone_shots(self, t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions) -> str:
        return f"""import * as THREE from 'three';
import {{ makeHuman }} from './human.js';
import {{
  modernPhone,
  riceBowl,
  microscopicPortCutaway,
  starchDustStream,
  corrosionSludge,
  motherboardPCB,
  sparks,
  misconceptionBadge
}} from './props.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration + 0.4:.2f};

export const CAPTIONS = {json.dumps(captions, indent=2)};

export const FADES = [[{twist_fade_start}, {round(twist_fade_start+0.06, 2)}, {round(twist_fade_start+0.14, 2)}, {twist_fade_end}]];

function idle(t, k = 1) {{ return Math.sin(t * 1.6) * 0.012 * k; }}
const STAND = {{ lSh: [0.05, 0, 0.16], rSh: [0.05, 0, -0.16], lEl: [-0.25, 0, 0], rEl: [-0.25, 0, 0] }};

function standPose(h, t, extra = {{}}) {{
  const p = {{ ...STAND, ...extra }};
  p.chest = [idle(t) + (extra.chest?.[0] || 0), extra.chest?.[1] || 0, extra.chest?.[2] || 0];
  h.setPose(p);
}}

// ============ SHOT 1: Hook — Dropping Wet Phone in Rice Bowl (0 - {t1}s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const phone = modernPhone({{ wet: true }}); scene.add(phone);
  const bowl = riceBowl({{ withPhone: false }});
  bowl.position.set(0.12, 0.88, 0.42); scene.add(bowl);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [lerp(0.4, 0.82, range(lt, 0, 1.8)), -0.15, 0.25],
        rEl: [-0.85, 0, 0],
        head: [0.22, 0, 0]
      }});
      // Phone drops into rice bowl
      const py = lerp(1.28, 0.94, range(lt, 0.4, 2.2));
      phone.position.set(0.12, py, 0.42);
      phone.rotation.set(0.35, -0.15, lerp(0, 0.25, range(lt, 0.4, 2.2)));

      c.position.set(0.24, 1.36, 1.75);
      c.lookAt(0.12, 1.05, 0.42);
    }}
  }};
}}

// ============ SHOT 2: Misconception — Rice Sucking Water Myth ({t1}s - {t2}s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const bowl = riceBowl({{ withPhone: true }});
  bowl.position.set(0, 1.10, 0); scene.add(bowl);
  const badge = misconceptionBadge("GRAINS SUCK WATER?");
  badge.position.set(0, 1.48, 0.05); scene.add(badge);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      badge.position.y = 1.48 + Math.sin(lt * 2.5) * 0.015;
      bowl.rotation.y = lt * 0.15;
      c.position.set(0, 1.42, lerp(1.4, 1.15, range(lt, 0, 3.0)));
      c.lookAt(0, 1.25, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! — Shock & Dive Into Phone ({t2}s - {t3}s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const phone = modernPhone({{ wet: true }});
  phone.position.set(0.08, 1.25, 0.35); scene.add(phone);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ head: [0.15, Math.sin(lt * 3.5) * 0.06, 0] }});
      phone.rotation.x = lt * 0.3;
      c.position.set(0.15, 1.35, lerp(1.5, 0.95, range(lt, 0, 2.5)));
      c.lookAt(0.08, 1.25, 0.35);
    }}
  }};
}}

// ============ SHOT 4: Step 1 — Microscopic USB-C Port & Trapped Water ({t3}s - {t4}s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const port = microscopicPortCutaway();
  port.position.set(0, 1.35, 0); scene.add(port);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      port.rotation.y = Math.sin(lt * 0.4) * 0.2;
      c.position.set(Math.sin(lt * 0.5) * 0.3, 1.38, 0.72);
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 5: Step 2 — Air Moisture vs Trapped Surface Tension ({t4}s - {t5}s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const port = microscopicPortCutaway();
  port.position.set(0, 1.35, 0); scene.add(port);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      c.position.set(0, 1.35, lerp(0.68, 0.46, range(lt, 0, 3.0)));
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 6: Step 3 — Starch Dust Stream Infiltration ({t5}s - {t6}s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const port = microscopicPortCutaway();
  port.position.set(0, 1.32, 0); scene.add(port);
  const dust = starchDustStream(95);
  dust.position.set(0, 1.32, 0); scene.add(dust);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      dust.update(lt);
      c.position.set(0.12, 1.38, 0.62);
      c.lookAt(0, 1.32, 0);
    }}
  }};
}}

// ============ SHOT 7: Step 4 — Toxic Corrosion Sludge Bubbling ({t6}s - {t7}s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.4 }});
  const sludge = corrosionSludge();
  sludge.position.set(0, 1.34, 0); scene.add(sludge);
  const sp = sparks(45, {{ color: [0.3, 1.0, 0.4], speed: 1.8 }});
  sp.position.set(0, 1.35, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sludge.update(lt);
      sp.update(lt);
      c.position.set(0, 1.38, lerp(0.55, 0.38, range(lt, 0, 3.0)));
      c.lookAt(0, 1.34, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff — Fried Motherboard with Blinding Sparks ({t7}s - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const pcb = motherboardPCB({{ fried: true }});
  pcb.position.set(0, 1.25, 0); scene.add(pcb);
  const sp = sparks(80, {{ color: [1.0, 0.4, 0.1], speed: 3.2 }});
  sp.position.set(0, 1.28, 0); scene.add(sp);
  const man = makeHuman('casual');
  man.root.position.set(-0.32, 0, -0.15); scene.add(man.root);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      standPose(man, lt, {{
        rSh: [0.95, -0.3, 0.4], lSh: [0.95, 0.3, -0.4],
        head: [0.18, 0, 0]
      }});
      c.position.set(0.10, 1.42, 1.75);
      c.lookAt(0, 1.28, 0);
    }}
  }};
}}

export const SHOTS = [
  {{ start: 0.00, end: {t1}, build: shot1 }},
  {{ start: {t1}, end: {t2}, build: shot2 }},
  {{ start: {t2}, end: {t3}, build: shot3 }},
  {{ start: {t3}, end: {t4}, build: shot4 }},
  {{ start: {t4}, end: {t5}, build: shot5 }},
  {{ start: {t5}, end: {t6}, build: shot6 }},
  {{ start: {t6}, end: {t7}, build: shot7 }},
  {{ start: {t7}, end: {duration + 0.4:.2f}, build: shot8 }},
];
"""

    def _generate_battery_puncture_shots(self, t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions) -> str:
        return f"""import * as THREE from 'three';
import {{ makeHuman }} from './human.js';
import {{
  lithiumBatteryPouch,
  sharpSteelNail,
  batteryLayeredCutaway,
  fireBlowtorchJet,
  sparks,
  misconceptionBadge
}} from './props.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration + 0.4:.2f};

export const CAPTIONS = {json.dumps(captions, indent=2)};

export const FADES = [[{twist_fade_start}, {round(twist_fade_start+0.06, 2)}, {round(twist_fade_start+0.14, 2)}, {twist_fade_end}]];

function idle(t, k = 1) {{ return Math.sin(t * 1.6) * 0.012 * k; }}
const STAND = {{ lSh: [0.05, 0, 0.16], rSh: [0.05, 0, -0.16], lEl: [-0.25, 0, 0], rEl: [-0.25, 0, 0] }};

function standPose(h, t, extra = {{}}) {{
  const p = {{ ...STAND, ...extra }};
  p.chest = [idle(t) + (extra.chest?.[0] || 0), extra.chest?.[1] || 0, extra.chest?.[2] || 0];
  h.setPose(p);
}}

// ============ SHOT 1: Hook — Puncturing Smartphone Battery (0 - {t1}s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const battery = lithiumBatteryPouch({{ swollen: false }});
  battery.position.set(0.10, 1.20, 0.45); scene.add(battery);
  const nail = sharpSteelNail();
  nail.position.set(0.10, 1.48, 0.45); scene.add(nail);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.72, -0.2, 0.35], rEl: [-0.95, 0, 0],
        head: [0.22, 0, 0]
      }});
      nail.position.y = lerp(1.48, 1.25, range(lt, 0.5, 2.5));
      c.position.set(0.24, 1.38, 1.65);
      c.lookAt(0.10, 1.25, 0.45);
    }}
  }};
}}

// ============ SHOT 2: Misconception — "Gasoline Fire?" ({t1}s - {t2}s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const battery = lithiumBatteryPouch({{ swollen: false }});
  battery.position.set(0, 1.20, 0); scene.add(battery);
  const nail = sharpSteelNail();
  nail.position.set(0, 1.35, 0); scene.add(nail);
  const badge = misconceptionBadge("GASOLINE EXPLOSION?");
  badge.position.set(0, 1.55, 0.05); scene.add(badge);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      badge.position.y = 1.55 + Math.sin(lt * 2.5) * 0.015;
      c.position.set(0, 1.45, lerp(1.35, 1.10, range(lt, 0, 3.0)));
      c.lookAt(0, 1.30, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! — Internal Thermal Runaway Piercing ({t2}s - {t3}s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const battery = lithiumBatteryPouch({{ swollen: false }});
  battery.position.set(0, 1.25, 0); scene.add(battery);
  const nail = sharpSteelNail();
  nail.position.set(0, 1.26, 0); scene.add(nail);
  const sp = sparks(40, {{ color: [0.2, 0.8, 1.0], speed: 2.5 }});
  sp.position.set(0, 1.26, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      c.position.set(0.08, 1.32, lerp(1.3, 0.85, range(lt, 0, 2.5)));
      c.lookAt(0, 1.25, 0);
    }}
  }};
}}

// ============ SHOT 4: Step 1 — Separator Membrane Tears ({t3}s - {t4}s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const cut = batteryLayeredCutaway();
  cut.position.set(0, 1.35, 0); scene.add(cut);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      cut.sep.scale.set(lerp(1, 0.3, range(lt, 0.5, 2.5)), 1, 1);
      c.position.set(Math.sin(lt * 0.4) * 0.25, 1.38, 0.75);
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 5: Step 2 — Cathode & Anode Direct Touch Short Circuit ({t4}s - {t5}s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const cut = batteryLayeredCutaway();
  cut.position.set(0, 1.35, 0); scene.add(cut);
  const sp = sparks(90, {{ color: [0.3, 0.8, 1.0], speed: 3.5 }});
  sp.position.set(0, 1.35, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      cut.cathode.position.y = lerp(0.06, 0.01, range(lt, 0, 1.2));
      cut.anode.position.y = lerp(-0.06, -0.01, range(lt, 0, 1.2));
      sp.update(lt);
      c.position.set(0, 1.35, lerp(0.72, 0.48, range(lt, 0, 2.8)));
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 6: Step 3 — Thermal Runaway: 600°C Heat Surge ({t5}s - {t6}s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const battery = lithiumBatteryPouch({{ swollen: true }});
  battery.position.set(0, 1.32, 0); scene.add(battery);
  const sp = sparks(50, {{ color: [1.0, 0.5, 0.1], speed: 2.8 }});
  sp.position.set(0, 1.32, 0); scene.add(sp);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      const sw = 1.0 + Math.sin(lt * 8) * 0.08;
      battery.scale.set(sw, sw, sw);
      c.position.set(0.12, 1.38, 0.65);
      c.lookAt(0, 1.32, 0);
    }}
  }};
}}

// ============ SHOT 7: Step 4 — Explosive Internal Pressure Venting ({t6}s - {t7}s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.4 }});
  const battery = lithiumBatteryPouch({{ swollen: true }});
  battery.position.set(0, 1.34, 0); scene.add(battery);
  const sp = sparks(70, {{ color: [1.0, 0.3, 0.05], speed: 3.5 }});
  sp.position.set(0, 1.34, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      c.position.set(0, 1.38, lerp(0.58, 0.40, range(lt, 0, 3.0)));
      c.lookAt(0, 1.34, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff — Violent Blowtorch Jet Fire Eruption ({t7}s - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const fire = fireBlowtorchJet();
  fire.position.set(0.08, 1.25, 0.2); scene.add(fire);
  const sp = sparks(95, {{ color: [1.0, 0.45, 0.1], speed: 4.2 }});
  sp.position.set(0.08, 1.30, 0.2); scene.add(sp);
  const man = makeHuman('casual');
  man.root.position.set(-0.35, 0, -0.2); scene.add(man.root);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      fire.update(lt);
      sp.update(lt);
      standPose(man, lt, {{
        rSh: [0.95, -0.3, 0.4], lSh: [0.95, 0.3, -0.4],
        head: [-0.15, 0, 0]
      }});
      c.position.set(0.12, 1.45, 1.85);
      c.lookAt(0, 1.30, 0.1);
    }}
  }};
}}

export const SHOTS = [
  {{ start: 0.00, end: {t1}, build: shot1 }},
  {{ start: {t1}, end: {t2}, build: shot2 }},
  {{ start: {t2}, end: {t3}, build: shot3 }},
  {{ start: {t3}, end: {t4}, build: shot4 }},
  {{ start: {t4}, end: {t5}, build: shot5 }},
  {{ start: {t5}, end: {t6}, build: shot6 }},
  {{ start: {t6}, end: {t7}, build: shot7 }},
  {{ start: {t7}, end: {duration + 0.4:.2f}, build: shot8 }},
];
"""

    def _generate_digestion_shots(self, t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions) -> str:
        return f"""import * as THREE from 'three';
import {{ makeHuman }} from './human.js';
import {{
  chewingGumWad,
  stomachChamber,
  peristalsisTube,
  sparks,
  misconceptionBadge
}} from './props.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration + 0.4:.2f};

export const CAPTIONS = {json.dumps(captions, indent=2)};

export const FADES = [[{twist_fade_start}, {round(twist_fade_start+0.06, 2)}, {round(twist_fade_start+0.14, 2)}, {twist_fade_end}]];

function idle(t, k = 1) {{ return Math.sin(t * 1.6) * 0.012 * k; }}
const STAND = {{ lSh: [0.05, 0, 0.16], rSh: [0.05, 0, -0.16], lEl: [-0.25, 0, 0], rEl: [-0.25, 0, 0] }};

function standPose(h, t, extra = {{}}) {{
  const p = {{ ...STAND, ...extra }};
  p.chest = [idle(t) + (extra.chest?.[0] || 0), extra.chest?.[1] || 0, extra.chest?.[2] || 0];
  h.setPose(p);
}}

// ============ SHOT 1: Hook — Character Swallowing Chewing Gum (0 - {t1}s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const gum = chewingGumWad(0.8); scene.add(gum);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [lerp(0.3, 0.88, range(lt, 0, 1.6)), -0.22, 0.35],
        rEl: [-1.1, 0, 0],
        head: [lerp(0.05, -0.12, range(lt, 0.8, 2.0)), 0, 0]
      }});
      const gy = lerp(1.22, 1.48, range(lt, 0.2, 1.8));
      const gz = lerp(0.35, 0.12, range(lt, 0.2, 1.8));
      gum.position.set(0.06, gy, gz);
      c.position.set(0.18, 1.44, 1.75);
      c.lookAt(0.05, 1.38, 0.1);
    }}
  }};
}}

// ============ SHOT 2: Misconception — Trapped for 7 Years? ({t1}s - {t2}s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const stomach = stomachChamber();
  stomach.position.set(0, 1.25, 0); scene.add(stomach);
  const badge = misconceptionBadge("TRAPPED 7 YEARS?");
  badge.position.set(0, 1.55, 0.05); scene.add(badge);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      stomach.update(lt);
      badge.position.y = 1.55 + Math.sin(lt * 2.5) * 0.015;
      c.position.set(0, 1.42, lerp(1.4, 1.15, range(lt, 0, 3.0)));
      c.lookAt(0, 1.25, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! — Dive Into Internal Anatomy ({t2}s - {t3}s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const stomach = stomachChamber();
  stomach.position.set(0, 1.28, 0); scene.add(stomach);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      stomach.update(lt);
      c.position.set(0.05, 1.32, lerp(1.25, 0.72, range(lt, 0, 2.5)));
      c.lookAt(0, 1.28, 0);
    }}
  }};
}}

// ============ SHOT 4: Step 1 — Stomach Acid Dissolving Sugars ({t3}s - {t4}s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const stomach = stomachChamber();
  stomach.position.set(0, 1.32, 0); scene.add(stomach);
  const gum = chewingGumWad(1.1);
  gum.position.set(0.05, 1.26, 0); scene.add(gum);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      stomach.update(lt);
      gum.rotation.y = lt * 0.3;
      c.position.set(Math.sin(lt * 0.3) * 0.2, 1.35, 0.65);
      c.lookAt(0.05, 1.26, 0);
    }}
  }};
}}

// ============ SHOT 5: Step 2 — Synthetic Gum Base Resisting Acid ({t4}s - {t5}s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const gum = chewingGumWad(1.4);
  gum.position.set(0, 1.34, 0); scene.add(gum);
  const sp = sparks(40, {{ color: [0.5, 0.9, 0.2], speed: 1.6 }});
  sp.position.set(0, 1.34, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      gum.rotation.x = lt * 0.2;
      gum.rotation.y = lt * 0.4;
      c.position.set(0, 1.35, lerp(0.65, 0.42, range(lt, 0, 3.0)));
      c.lookAt(0, 1.34, 0);
    }}
  }};
}}

// ============ SHOT 6: Step 3 — Peristalsis Muscular Contractions ({t5}s - {t6}s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const canal = peristalsisTube();
  canal.position.set(0, 1.38, 0); scene.add(canal);
  const gum = chewingGumWad(0.85);
  gum.position.set(0, 1.48, 0); scene.add(gum);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      canal.update(lt);
      gum.position.y = lerp(1.48, 1.26, range(lt, 0, 3.0));
      c.position.set(0.12, 1.38, 0.62);
      c.lookAt(0, 1.36, 0);
    }}
  }};
}}

// ============ SHOT 7: Step 4 — Rhythmic Intestinal Traversal ({t6}s - {t7}s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.4 }});
  const canal = peristalsisTube();
  canal.position.set(0, 1.36, 0); scene.add(canal);
  const gum = chewingGumWad(0.85);
  gum.position.set(0, 1.28, 0); scene.add(gum);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      canal.update(lt);
      gum.position.y = lerp(1.28, 1.10, range(lt, 0, 3.0));
      c.position.set(0.12, 1.35, lerp(0.58, 0.40, range(lt, 0, 3.0)));
      c.lookAt(0, 1.24, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff — Completely Safe & Intact Payoff ({t7}s - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.72, -0.3, 0.35], rEl: [-0.65, 0, 0],
        lSh: [0.15, 0.1, -0.15],
        head: [0.08, 0, 0]
      }});
      c.position.set(0.10, 1.45, 1.85);
      c.lookAt(0, 1.32, 0.1);
    }}
  }};
}}

export const SHOTS = [
  {{ start: 0.00, end: {t1}, build: shot1 }},
  {{ start: {t1}, end: {t2}, build: shot2 }},
  {{ start: {t2}, end: {t3}, build: shot3 }},
  {{ start: {t3}, end: {t4}, build: shot4 }},
  {{ start: {t4}, end: {t5}, build: shot5 }},
  {{ start: {t5}, end: {t6}, build: shot6 }},
  {{ start: {t6}, end: {t7}, build: shot7 }},
  {{ start: {t7}, end: {duration + 0.4:.2f}, build: shot8 }},
];
"""

    def _generate_tech_gadget_shots(self, t1, t2, t3, t4, t5, t6, t7, duration, twist_fade_start, twist_fade_end, captions, topic: str) -> str:
        return f"""import * as THREE from 'three';
import {{ makeHuman }} from './human.js';
import {{
  modernPhone,
  motherboardPCB,
  microscopicPortCutaway,
  sparks,
  misconceptionBadge
}} from './props.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration + 0.4:.2f};

export const CAPTIONS = {json.dumps(captions, indent=2)};

export const FADES = [[{twist_fade_start}, {round(twist_fade_start+0.06, 2)}, {round(twist_fade_start+0.14, 2)}, {twist_fade_end}]];

function idle(t, k = 1) {{ return Math.sin(t * 1.6) * 0.012 * k; }}
const STAND = {{ lSh: [0.05, 0, 0.16], rSh: [0.05, 0, -0.16], lEl: [-0.25, 0, 0], rEl: [-0.25, 0, 0] }};

function standPose(h, t, extra = {{}}) {{
  const p = {{ ...STAND, ...extra }};
  p.chest = [idle(t) + (extra.chest?.[0] || 0), extra.chest?.[1] || 0, extra.chest?.[2] || 0];
  h.setPose(p);
}}

// ============ SHOT 1: Hook — Character Demonstrating Device (0 - {t1}s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const phone = modernPhone({{ screenOn: true }});
  phone.position.set(0.10, 1.30, 0.42); scene.add(phone);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.65, -0.15, 0.28], rEl: [-0.85, 0, 0],
        head: [0.18, 0, 0]
      }});
      phone.rotation.y = Math.sin(lt * 0.8) * 0.2;
      c.position.set(0.22, 1.42, 1.75);
      c.lookAt(0.10, 1.30, 0.42);
    }}
  }};
}}

// ============ SHOT 2: Misconception — Floating Question & Analysis ({t1}s - {t2}s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const phone = modernPhone({{ screenOn: true }});
  phone.position.set(0, 1.25, 0); scene.add(phone);
  const badge = misconceptionBadge("HOW IT REALLY WORKS");
  badge.position.set(0, 1.55, 0.05); scene.add(badge);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      badge.position.y = 1.55 + Math.sin(lt * 2.5) * 0.015;
      phone.rotation.y = lt * 0.2;
      c.position.set(0, 1.45, lerp(1.35, 1.10, range(lt, 0, 3.0)));
      c.lookAt(0, 1.30, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! — Dive Into Internal Micro-Architecture ({t2}s - {t3}s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const phone = modernPhone({{ screenOn: true }});
  phone.position.set(0, 1.30, 0); scene.add(phone);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      phone.rotation.x = lt * 0.35;
      c.position.set(0.06, 1.35, lerp(1.3, 0.82, range(lt, 0, 2.5)));
      c.lookAt(0, 1.30, 0);
    }}
  }};
}}

// ============ SHOT 4: Step 1 — Exploded Microscopic Component Cutaway ({t3}s - {t4}s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const pcb = motherboardPCB({{ fried: false }});
  pcb.position.set(0, 1.35, 0); scene.add(pcb);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      pcb.rotation.y = Math.sin(lt * 0.4) * 0.25;
      c.position.set(Math.sin(lt * 0.4) * 0.25, 1.40, 0.75);
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 5: Step 2 — Microscopic Signals & Electrical Flow ({t4}s - {t5}s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const pcb = motherboardPCB({{ fried: false }});
  pcb.position.set(0, 1.35, 0); scene.add(pcb);
  const sp = sparks(50, {{ color: [0.2, 0.8, 1.0], speed: 2.2 }});
  sp.position.set(0, 1.36, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      c.position.set(0, 1.36, lerp(0.72, 0.50, range(lt, 0, 3.0)));
      c.lookAt(0, 1.35, 0);
    }}
  }};
}}

// ============ SHOT 6: Step 3 — High-Speed Processor Probability Calculation ({t5}s - {t6}s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const pcb = motherboardPCB({{ fried: false }});
  pcb.position.set(0, 1.32, 0); scene.add(pcb);
  const sp = sparks(65, {{ color: [1.0, 0.8, 0.2], speed: 2.8 }});
  sp.position.set(0, 1.33, 0); scene.add(sp);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      c.position.set(0.12, 1.38, 0.65);
      c.lookAt(0, 1.32, 0);
    }}
  }};
}}

// ============ SHOT 7: Step 4 — Electromagnetic Chain Reaction ({t6}s - {t7}s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.4 }});
  const pcb = motherboardPCB({{ fried: false }});
  pcb.position.set(0, 1.34, 0); scene.add(pcb);
  const sp = sparks(75, {{ color: [0.2, 0.9, 1.0], speed: 3.2 }});
  sp.position.set(0, 1.35, 0); scene.add(sp);
  const c = cam(42);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      sp.update(lt);
      c.position.set(0, 1.38, lerp(0.60, 0.42, range(lt, 0, 3.0)));
      c.lookAt(0, 1.34, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff — Working Miracle & Complete Payoff ({t7}s - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const phone = modernPhone({{ screenOn: true }});
  phone.position.set(0.08, 1.30, 0.35); scene.add(phone);
  const man = makeHuman('casual');
  man.root.position.set(-0.25, 0, -0.15); scene.add(man.root);
  const c = cam(43);

  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.55, -0.15, 0.25], lSh: [0.55, 0.15, -0.25],
        head: [0.05, 0, 0]
      }});
      phone.rotation.y = Math.sin(lt * 1.2) * 0.3;
      c.position.set(0.12, 1.45, 1.85);
      c.lookAt(0, 1.30, 0.1);
    }}
  }};
}}

export const SHOTS = [
  {{ start: 0.00, end: {t1}, build: shot1 }},
  {{ start: {t1}, end: {t2}, build: shot2 }},
  {{ start: {t2}, end: {t3}, build: shot3 }},
  {{ start: {t3}, end: {t4}, build: shot4 }},
  {{ start: {t4}, end: {t5}, build: shot5 }},
  {{ start: {t5}, end: {t6}, build: shot6 }},
  {{ start: {t6}, end: {t7}, build: shot7 }},
  {{ start: {t7}, end: {duration + 0.4:.2f}, build: shot8 }},
];
"""


scene_builder = SceneBuilder()
