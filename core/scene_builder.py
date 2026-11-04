"""
3D Procedural Scene Builder (Three.js WebGL / Playwright Runner)
Sets up Three.js project, generates shots.js with Apple Fluid camera easing,
and ensures comfortable zoomed-out 9:16 framing (FOV 42°-45°, Z=1.6m-2.4m).
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List

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

    def build_shots_file(self, project_dir: Path, captions: List[List[Any]], duration: float, meta_lines: List[Dict[str, Any]] = None) -> Path:
        """
        Generates src/shots.js with 8 shots mapped to the 8-sentence viral formula,
        including dip-to-black twist and comfortable zoomed-out camera framing.
        """
        shots_file = project_dir / "src" / "shots.js"

        # Calculate shot boundaries based on duration or meta_lines
        if meta_lines and len(meta_lines) == 8:
            t0 = 0.0
            t1 = meta_lines[1]["start"] + meta_lines[1]["dur"]
            t2 = meta_lines[2]["start"] + meta_lines[2]["dur"]
            t3 = meta_lines[3]["start"] + meta_lines[3]["dur"]
            t4 = meta_lines[4]["start"] + meta_lines[4]["dur"]
            t5 = meta_lines[5]["start"] + meta_lines[5]["dur"]
            t6 = meta_lines[6]["start"] + meta_lines[6]["dur"]
            t7 = duration
            twist_fade_start = round(t2 - 0.20, 2)
            twist_fade_end = round(t2, 2)
        else:
            seg = duration / 8.0
            t1 = round(seg * 1, 2)
            t2 = round(seg * 2, 2)
            t3 = round(seg * 3, 2)
            t4 = round(seg * 4, 2)
            t5 = round(seg * 5, 2)
            t6 = round(seg * 6, 2)
            t7 = duration
            twist_fade_start = round(t2 - 0.20, 2)
            twist_fade_end = round(t2, 2)

        code = f"""import * as THREE from 'three';
import {{ makeHuman }} from './human.js';
import {{ materials }} from './materials.js';
import {{ kf, lerp, smooth, easeOut, easeIn, easeInOut, range, clamp, V, cam, place, shake }} from './anim.js';

export const DURATION = {duration + 0.4:.2f};

export const CAPTIONS = {json.dumps(captions, indent=2)};

// Dip to black after misconception twist
export const FADES = [[{twist_fade_start}, {round(twist_fade_start+0.06, 2)}, {round(twist_fade_start+0.14, 2)}, {twist_fade_end}]];

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

// ============ SHOT 1: Hook / Scenario (0.00s - {t1}s) ============
function shot1({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(43); // Comfortable zoomed-out FOV
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [lerp(0.3, 0.75, range(lt, 0, 1.5)), -0.2, 0.3],
        head: [0.05, Math.sin(lt * 0.8) * 0.05, 0]
      }});
      c.position.set(0.12, 1.45, 1.95);
      c.lookAt(0, 1.35, 0.1);
    }}
  }};
}}

// ============ SHOT 2: Misconception ({t1}s - {t2}s) ============
function shot2({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.4 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(42);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        lSh: [0.35, 0.2, -0.2], rSh: [0.35, -0.2, 0.2],
        head: [0.08, 0, 0]
      }});
      c.position.set(0, 1.48, lerp(1.7, 1.4, range(lt, 0, 3.0)));
      c.lookAt(0, 1.38, 0);
    }}
  }};
}}

// ============ SHOT 3: Twist! ({t2}s - {t3}s) ============
function shot3({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.2 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(42);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ head: [0.12, Math.sin(lt * 2) * 0.08, 0] }});
      c.position.set(0.08, 1.42, 1.35);
      c.lookAt(0, 1.40, 0);
    }}
  }};
}}

// ============ SHOT 4: Step 1 Mechanism ({t3}s - {t4}s) ============
function shot4({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(43);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ rSh: [0.6, -0.2, 0.35], rEl: [-1.1, 0, 0] }});
      c.position.set(0.18, 1.48, 1.85);
      c.lookAt(0.02, 1.38, 0);
    }}
  }};
}}

// ============ SHOT 5: Step 2 Microscopic/Physics ({t4}s - {t5}s) ============
function shot5({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.6 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(42);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ head: [0.04, 0, 0] }});
      c.position.set(0, 1.45, 1.25);
      c.lookAt(0, 1.40, 0);
    }}
  }};
}}

// ============ SHOT 6: Step 3 Forces & Interaction ({t5}s - {t6}s) ============
function shot6({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.5 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(43);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ head: [0.05, Math.sin(lt * 0.7) * 0.06, 0] }});
      c.position.set(0.15, 1.46, 1.75);
      c.lookAt(0, 1.38, 0);
    }}
  }};
}}

// ============ SHOT 7: Step 4 Secondary Reaction ({t6}s - {t7}s) ============
function shot7({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.4 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(42);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{ head: [0.08, 0, 0] }});
      c.position.set(0, 1.45, 1.45);
      c.lookAt(0, 1.38, 0);
    }}
  }};
}}

// ============ SHOT 8: Payoff & Resolution ({t7}s - End) ============
function shot8({{ makeStage }}) {{
  const scene = makeStage({{ shadowSize: 2.8 }});
  const man = makeHuman('casual'); scene.add(man.root);
  const c = cam(43);
  return {{
    scene, camera: c,
    update(lt, gt) {{
      standPose(man, lt, {{
        rSh: [0.55, -0.15, 0.25], lSh: [0.55, 0.15, -0.25],
        head: [0.02, 0, 0]
      }});
      c.position.set(0.12, 1.46, 1.95);
      c.lookAt(0.02, 1.38, 0.1);
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
        shots_file.write_text(code, encoding="utf-8")
        return shots_file


scene_builder = SceneBuilder()

