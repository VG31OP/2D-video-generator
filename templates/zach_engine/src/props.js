import * as THREE from 'three';
import { materials } from './materials.js';
import { glowTexture, rng } from './textures.js';

const shadow = o => { o.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } }); return o; };
const box = (w, h, d, mat, p = [0, 0, 0], r = [0, 0, 0]) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(...p); m.rotation.set(...r); return m;
};

// ---------- pistol (barrel along +x, muzzle at .muzzle) ----------
export function pistol() {
  const M = materials();
  const g = new THREE.Group();
  g.add(box(0.19, 0.036, 0.03, M.gun, [0, 0.03, 0]));
  for (let i = 0; i < 7; i++) g.add(box(0.003, 0.03, 0.031, M.gunDark, [-0.085 + i * 0.007, 0.032, 0]));
  g.add(box(0.05, 0.012, 0.031, M.gunDark, [0.02, 0.03, 0])); // ejection port
  g.add(box(0.17, 0.022, 0.026, M.gunDark, [0.005, 0.003, 0]));
  const grip = box(0.04, 0.115, 0.03, M.gunDark, [-0.065, -0.052, 0], [0, 0, 0.22]); g.add(grip);
  const tg = new THREE.Mesh(new THREE.TorusGeometry(0.022, 0.004, 8, 20, Math.PI), M.gunDark);
  tg.rotation.z = Math.PI; tg.position.set(-0.012, -0.008, 0); g.add(tg);
  g.add(box(0.004, 0.018, 0.006, M.gunDark, [-0.014, -0.015, 0], [0, 0, 0.3]));
  g.add(box(0.008, 0.008, 0.006, M.gunDark, [0.088, 0.052, 0]));
  g.add(box(0.012, 0.008, 0.02, M.gunDark, [-0.088, 0.052, 0]));
  const bore = new THREE.Mesh(new THREE.CylinderGeometry(0.0055, 0.0055, 0.004, 16), M.mouth);
  bore.rotation.z = Math.PI / 2; bore.position.set(0.0955, 0.03, 0); g.add(bore);
  g.muzzle = new THREE.Vector3(0.1, 0.03, 0);
  return shadow(g);
}

// first person arm holding the pistol (pistol frame = arm frame)
export function gunArm() {
  const M = materials();
  const g = new THREE.Group();
  const gun = pistol(); g.add(gun);
  const hand = new THREE.Group(); g.add(hand);
  const palm = new THREE.Mesh(new THREE.SphereGeometry(0.05, 32, 24), M.skin);
  palm.scale.set(0.95, 1.1, 0.8); palm.position.set(-0.075, -0.06, 0); hand.add(palm);
  for (let i = 0; i < 4; i++) {
    const f = new THREE.Mesh(new THREE.CapsuleGeometry(0.0115, 0.035, 4, 10), M.skin);
    f.rotation.x = Math.PI / 2; f.position.set(-0.045 - i * 0.004, -0.03 - i * 0.022, 0.026); hand.add(f);
  }
  const th = new THREE.Mesh(new THREE.CapsuleGeometry(0.012, 0.05, 4, 10), M.skin);
  th.rotation.set(0, 0, -1.2); th.position.set(-0.04, 0.0, -0.022); hand.add(th);
  const fa = new THREE.Mesh(new THREE.CapsuleGeometry(0.042, 0.45, 8, 20), M.skin);
  fa.rotation.z = 1.05; fa.position.set(-0.29, -0.2, 0); hand.add(fa);
  g.muzzle = gun.muzzle;
  return shadow(g);
}

// ---------- bullet (nose along +y) with mushroom morph ----------
export function bullet(scale = 1) {
  const M = materials();
  const A = [[0, 0], [0.0052, 0], [0.0057, 0.0015], [0.0057, 0.006], [0.0057, 0.0105], [0.0052, 0.0135], [0.0042, 0.016], [0.0026, 0.0178], [0, 0.0186]];
  const B = [[0, 0.001], [0.0052, 0.001], [0.006, 0.0025], [0.0068, 0.006], [0.0095, 0.0085], [0.0125, 0.0098], [0.0118, 0.0108], [0.006, 0.0112], [0, 0.0112]];
  const smoothP = (P) => { const c = new THREE.SplineCurve(P.map(([r, y]) => new THREE.Vector2(r, y))); return c.getPoints(28); };
  const mk = (P) => new THREE.LatheGeometry(smoothP(P), 64);
  const ga = mk(A), gb = mk(B);
  // jagged splatter on the mushroom
  const p = gb.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), z = p.getZ(i), y = p.getY(i);
    const rad = Math.hypot(x, z);
    if (rad > 0.0065) { const a = Math.atan2(z, x); const k = 1 + (Math.sin(a * 6) * 0.09 + Math.sin(a * 11 + 1.3) * 0.05) * ((rad - 0.0065) / 0.006); p.setX(i, x * k); p.setZ(i, z * k); }
  }
  ga.morphAttributes.position = [gb.attributes.position];
  ga.computeVertexNormals();
  const m = new THREE.Mesh(ga, M.copper.clone());
  m.material.emissive = new THREE.Color(0x7a2408);
  m.scale.setScalar(scale);
  m.morphTargetInfluences = [0];
  m.castShadow = true;
  return m;
}

// ---------- sword (blade along +y, origin at grip) ----------
export function sword() {
  const M = materials();
  const g = new THREE.Group();
  const bg = new THREE.BoxGeometry(0.05, 0.85, 0.008, 1, 16, 1);
  const p = bg.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const y = p.getY(i) + 0.425, t = y / 0.85;
    const w = t > 0.88 ? (1 - t) / 0.12 : 1 - t * 0.25;
    p.setX(i, p.getX(i) * w); p.setZ(i, p.getZ(i) * (Math.abs(p.getX(i)) > 0.015 ? 0.35 : 1));
  }
  bg.translate(0, 0.425 + 0.09, 0); bg.computeVertexNormals();
  g.add(new THREE.Mesh(bg, M.steelBright));
  g.add(box(0.008, 0.6, 0.0095, M.steelDark, [0, 0.4, 0]));
  g.add(box(0.2, 0.022, 0.03, M.steelDark, [0, 0.08, 0]));
  const gr = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.14, 12), M.leather); g.add(gr);
  const pm = new THREE.Mesh(new THREE.SphereGeometry(0.026, 16, 12), M.steelDark); pm.position.y = -0.08; g.add(pm);
  g.tip = new THREE.Vector3(0, 0.94, 0);
  return shadow(g);
}

// ---------- heater shield (front +z) ----------
export function shield() {
  const M = materials();
  const s = new THREE.Shape();
  s.moveTo(-0.27, 0.32); s.lineTo(0.27, 0.32);
  s.bezierCurveTo(0.29, 0.0, 0.2, -0.25, 0, -0.42);
  s.bezierCurveTo(-0.2, -0.25, -0.29, 0.0, -0.27, 0.32);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.02, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.014, bevelSegments: 3, curveSegments: 32 });
  // curve it a bit
  const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setZ(i, p.getZ(i) - x * x * 0.5); }
  geo.computeVertexNormals();
  const g = new THREE.Group();
  g.add(new THREE.Mesh(geo, M.steel));
  const pts = s.getSpacedPoints(26);
  for (const q of pts) { const r = new THREE.Mesh(new THREE.SphereGeometry(0.008, 10, 8), M.steelDark); r.position.set(q.x * 0.9, q.y * 0.9, 0.034 - q.x * q.x * 0.45); g.add(r); }
  return shadow(g);
}

// ---------- spiked mace (handle along +y, origin at grip) ----------
export function mace() {
  const M = materials();
  const g = new THREE.Group();
  const h = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.02, 0.62, 16), M.steelDark); h.position.y = 0.2; g.add(h);
  const wrap = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.16, 16), M.leather); g.add(wrap);
  const head = new THREE.Group(); head.position.y = 0.53; g.add(head);
  head.add(new THREE.Mesh(new THREE.SphereGeometry(0.065, 32, 24), M.steel));
  const N = 22;
  for (let i = 0; i < N; i++) {
    const y = 1 - (i / (N - 1)) * 2, rr = Math.sqrt(1 - y * y), th = i * 2.39996;
    const dir = new THREE.Vector3(Math.cos(th) * rr, y, Math.sin(th) * rr);
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.016, 0.06, 12), M.steelBright);
    c.position.copy(dir.clone().multiplyScalar(0.085));
    c.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    head.add(c);
  }
  g.head = head;
  return shadow(g);
}

// ---------- arrow (points +z, tip at origin) ----------
export function arrow() {
  const M = materials();
  const g = new THREE.Group();
  const sh = new THREE.Mesh(new THREE.CylinderGeometry(0.0055, 0.0055, 0.74, 10), M.wood);
  sh.rotation.x = Math.PI / 2; sh.position.z = -0.42; g.add(sh);
  const hd = new THREE.Mesh(new THREE.ConeGeometry(0.011, 0.055, 4), M.steelDark);
  hd.rotation.x = Math.PI / 2; hd.position.z = -0.027; g.add(hd);
  for (let i = 0; i < 3; i++) {
    const f = new THREE.Mesh(new THREE.PlaneGeometry(0.02, 0.1), M.feather);
    const a = i * Math.PI * 2 / 3;
    f.rotation.set(0, 0, a); f.rotateX(Math.PI / 2); f.position.set(Math.cos(a) * 0.014, Math.sin(a) * 0.014, -0.72);
    g.add(f);
  }
  return shadow(g);
}

// ---------- bow (vertical, faces +z, grip at origin), dynamic draw ----------
export function bow() {
  const M = materials();
  const g = new THREE.Group();
  const L = 0.72;
  const limbMesh = new THREE.Mesh(new THREE.BufferGeometry(), M.woodDark); g.add(limbMesh);
  const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.12, 12), M.leather); g.add(grip);
  const s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.0018, 0.0018, 1, 6), M.string);
  const s2 = s1.clone(); g.add(s1, s2);
  const tmp = new THREE.Vector3();
  function seg(m, a, b) {
    m.position.copy(a).add(b).multiplyScalar(0.5);
    tmp.subVectors(b, a); m.scale.set(1, tmp.length(), 1);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), tmp.normalize());
  }
  g.nock = new THREE.Vector3();
  g.update = (draw) => {
    const k = 0.1 + 0.16 * draw;
    const ys = L * (1 - 0.06 * draw);
    const pts = [];
    for (let i = 0; i <= 24; i++) {
      const t = i / 24 * 2 - 1;
      pts.push(new THREE.Vector3(0, t * ys, -k * t * t - 0.02 * Math.abs(t) ** 4 * (1 - draw)));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    limbMesh.geometry.dispose();
    limbMesh.geometry = new THREE.TubeGeometry(curve, 48, 0.011, 8, false);
    const top = pts[24], bot = pts[0];
    g.nock.set(0, 0.035, -k - 0.02 - 0.58 * draw);
    seg(s1, top, g.nock); seg(s2, bot, g.nock);
  };
  g.update(0);
  return shadow(g);
}

// ---------- wooden armor stand ----------
export function stand() {
  const M = materials();
  const g = new THREE.Group();
  g.add(box(0.075, 1.5, 0.075, M.wood, [0, 0.75, 0]));
  g.add(box(0.4, 0.06, 0.07, M.wood, [0, 1.38, 0]));
  for (let i = 0; i < 3; i++) {
    const a = i * Math.PI * 2 / 3 + 0.5;
    const leg = box(0.06, 0.55, 0.06, M.wood);
    leg.position.set(Math.cos(a) * 0.2, 0.2, Math.sin(a) * 0.2);
    leg.lookAt(Math.cos(a) * 2, 0.2, Math.sin(a) * 2); leg.rotateX(Math.PI / 2 - 0.65);
    g.add(leg);
    g.add(box(0.12, 0.05, 0.09, M.wood, [Math.cos(a) * 0.38, 0.025, Math.sin(a) * 0.38], [0, -a, 0]));
  }
  return shadow(g);
}

// ---------- effects ----------
let _glow;
export function glowSprite(color = 0xffffff, size = 1) {
  _glow = _glow || glowTexture();
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: _glow, color, blending: THREE.AdditiveBlending, transparent: true, depthWrite: false, toneMapped: false }));
  s.scale.setScalar(size);
  return s;
}

// deterministic spark burst: update(dt since burst)
export function sparks(count = 60, { speed = 2.5, spread = 1, gravity = -6, life = 0.6, color = [1, 0.75, 0.3], size = 0.02, seed = 9, dir = new THREE.Vector3(0, 0, 1) } = {}) {
  const r = rng(seed);
  _glow = _glow || glowTexture();
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3), col = new Float32Array(count * 3);
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({ size, map: _glow, vertexColors: true, blending: THREE.AdditiveBlending, transparent: true, depthWrite: false, toneMapped: false });
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false;
  const V = [], Lf = [];
  const d = dir.clone().normalize();
  for (let i = 0; i < count; i++) {
    const v = new THREE.Vector3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(spread).add(d).normalize().multiplyScalar(speed * (0.3 + r() * 0.9));
    V.push(v); Lf.push(life * (0.4 + r() * 0.8));
  }
  pts.update = (t) => {
    for (let i = 0; i < count; i++) {
      const tt = Math.max(0, t), v = V[i];
      pos[i * 3] = v.x * tt; pos[i * 3 + 1] = v.y * tt + 0.5 * gravity * tt * tt; pos[i * 3 + 2] = v.z * tt;
      const a = t < 0 ? 0 : Math.max(0, 1 - tt / Lf[i]);
      col[i * 3] = color[0] * a * 3; col[i * 3 + 1] = color[1] * a * 3; col[i * 3 + 2] = color[2] * a * 3;
    }
    geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true;
  };
  pts.update(-1);
  return pts;
}

// glowing tracer streak between two points
export function streak(color = 0xfff2dd) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1, 8, 1, true), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
  const tmp = new THREE.Vector3();
  m.set = (a, b, r = 0.003, op = 0.7) => {
    m.position.copy(a).add(b).multiplyScalar(0.5);
    tmp.subVectors(b, a); const L = tmp.length();
    m.scale.set(r, Math.max(L, 1e-4), r);
    if (L > 1e-5) m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), tmp.normalize());
    m.material.opacity = op; m.visible = op > 0.001 && L > 1e-4;
  };
  return m;
}

// ---------- red impact ripple overlay ----------
const NOISE = `
float h3(vec3 p){ p = fract(p*0.3183099+.1); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
float n3(vec3 x){ vec3 i=floor(x), f=fract(x); f=f*f*(3.-2.*f);
  return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z); }
`;
export function rippleOverlay(target) {
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uCenter: { value: new THREE.Vector3() }, uRadius: { value: 0 }, uAmp: { value: 0 },
      uTime: { value: 0 }, uRings: { value: 160 }, uSpot: { value: 0.04 }, uBlot: { value: 0 }, uSpotAmp: { value: 1 },
    },
    vertexShader: `varying vec3 vPos; void main(){ vPos = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: NOISE + `
      uniform vec3 uCenter; uniform float uRadius,uAmp,uTime,uRings,uSpot,uBlot,uSpotAmp; varying vec3 vPos;
      void main(){
        float d = distance(vPos,uCenter);
        float front = 1.0 - smoothstep(uRadius*0.75, uRadius, d);
        float wob = n3(vPos*30.0)*0.012;
        float rings = pow(0.5+0.5*sin((d+wob*0.4)*uRings - uTime*9.0), 7.0);
        float fall = mix(1.0, 0.45, clamp(d/max(uRadius,1e-3),0.,1.));
        float bl = smoothstep(0.55, 0.8, n3(vPos*22.0 + vec3(0.,uTime*0.3,0.))*0.7 + n3(vPos*60.0)*0.3);
        float core = exp(-d*d/(uSpot*uSpot));
        float a = (rings*0.85*fall)*front*uAmp + bl*uBlot*front + core*uSpotAmp*uAmp;
        a = clamp(a,0.,1.);
        vec3 c = mix(vec3(0.9,0.05,0.06), vec3(1.0,0.45,0.42), core*0.6 + rings*0.25);
        gl_FragColor = vec4(c*(1.0+core*0.8), a*0.88);
      }`,
    transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -4, side: THREE.FrontSide,
  });
  const m = new THREE.Mesh(target.geometry, mat);
  m.renderOrder = 5;
  target.add(m);
  return m;
}

// ============================================================================
// TECH, PHONE, RICE, BATTERY & CIRCUIT 3D PROCEDURAL PROPS
// ============================================================================

// 1. Modern Smartphone with detailed screen, chassis & USB-C port
export function modernPhone({ wet = false, screenOn = true } = {}) {
  const M = materials();
  const g = new THREE.Group();
  const frame = box(0.082, 0.168, 0.0085, M.phoneBody);
  const screen = box(0.076, 0.160, 0.001, screenOn ? M.phoneScreenOn : M.phoneScreen, [0, 0, 0.0048]);
  g.add(frame, screen);

  // USB-C bottom port
  const port = box(0.016, 0.004, 0.006, M.steelDark, [0, -0.084, 0]);
  g.add(port);

  // Floating water droplets on surface if wet
  if (wet) {
    const drops = new THREE.Group();
    for (let i = 0; i < 18; i++) {
      const drop = new THREE.Mesh(new THREE.SphereGeometry(0.002 + (i % 3) * 0.0015, 8, 8), M.water);
      drop.scale.set(1.2, 1.2, 0.5);
      drop.position.set((Math.sin(i * 1.7) * 0.03), (Math.cos(i * 2.3) * 0.06), 0.0055);
      drops.add(drop);
    }
    g.add(drops);
    g.drops = drops;
  }
  return shadow(g);
}

// 2. Ceramic Bowl Filled with Detailed 3D Rice Grains
export function riceBowl({ withPhone = true } = {}) {
  const M = materials();
  const g = new THREE.Group();

  // Ceramic white bowl
  const bowlGeo = new THREE.CylinderGeometry(0.18, 0.10, 0.14, 32, 1, true);
  const bowlOuter = new THREE.Mesh(bowlGeo, M.ceramic);
  const bowlBase = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.10, 0.015, 32), M.ceramic);
  bowlBase.position.y = -0.07;
  g.add(bowlOuter, bowlBase);

  // 3D Rice Grains cluster
  const riceCluster = new THREE.Group();
  const grainGeo = new THREE.CapsuleGeometry(0.003, 0.012, 4, 8);
  for (let i = 0; i < 220; i++) {
    const grain = new THREE.Mesh(grainGeo, M.riceGrain);
    const radius = Math.sqrt(Math.random()) * 0.16;
    const theta = Math.random() * Math.PI * 2;
    grain.position.set(Math.cos(theta) * radius, -0.01 + Math.random() * 0.04, Math.sin(theta) * radius);
    grain.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    riceCluster.add(grain);
  }
  g.add(riceCluster);

  // Submerged phone sticking out diagonally
  if (withPhone) {
    const phone = modernPhone({ wet: true });
    phone.position.set(0.02, 0.03, -0.01);
    phone.rotation.set(0.4, -0.2, 0.3);
    g.add(phone);
    g.phone = phone;
  }
  return shadow(g);
}

// 3. Exploded Macro Cutaway of USB-C Port with Trapped Water
export function microscopicPortCutaway() {
  const M = materials();
  const g = new THREE.Group();

  // Giant exploded outer port tunnel
  const portShell = box(0.35, 0.16, 0.45, M.phoneBody);
  g.add(portShell);

  // Inner cavity
  const cavity = box(0.31, 0.12, 0.40, M.steelDark, [0, 0, 0.02]);
  g.add(cavity);

  // Gold connector pins inside
  const pins = new THREE.Group();
  for (let i = 0; i < 12; i++) {
    const pin = box(0.012, 0.008, 0.28, M.goldTrace, [-0.12 + i * 0.022, 0.025, 0]);
    pins.add(pin);
    const pinBot = box(0.012, 0.008, 0.28, M.goldTrace, [-0.12 + i * 0.022, -0.025, 0]);
    pins.add(pinBot);
  }
  g.add(pins);

  // Trapped surface-tension water droplets
  const droplets = new THREE.Group();
  for (let i = 0; i < 8; i++) {
    const drop = new THREE.Mesh(new THREE.SphereGeometry(0.035 + (i % 3) * 0.015, 16, 16), M.water);
    drop.scale.set(1.4, 0.9, 1.2);
    drop.position.set(-0.09 + i * 0.026, (i % 2 === 0 ? 0.02 : -0.02), -0.05 + Math.sin(i) * 0.08);
    droplets.add(drop);
  }
  g.add(droplets);
  g.droplets = droplets;

  return shadow(g);
}

// 4. Starch Dust Cloud particles streaming inward
export function starchDustStream(count = 70) {
  const M = materials();
  const g = new THREE.Group();
  const dustGeo = new THREE.SphereGeometry(0.008, 6, 6);
  const particles = [];
  for (let i = 0; i < count; i++) {
    const p = new THREE.Mesh(dustGeo, M.riceGrain);
    p.position.set((Math.random() - 0.5) * 0.5, 0.2 + Math.random() * 0.4, (Math.random() - 0.5) * 0.4);
    g.add(p);
    particles.push({ mesh: p, speed: 0.2 + Math.random() * 0.3, offset: Math.random() * Math.PI * 2 });
  }
  g.update = (lt) => {
    particles.forEach((item, idx) => {
      item.mesh.position.y -= item.speed * 0.016;
      item.mesh.position.x += Math.sin(lt * 3 + item.offset) * 0.002;
      if (item.mesh.position.y < -0.1) item.mesh.position.y = 0.4;
    });
  };
  return g;
}

// 5. Bubbling Green Toxic Corrosion Sludge over circuits
export function corrosionSludge() {
  const M = materials();
  const g = new THREE.Group();
  const base = box(0.26, 0.02, 0.22, M.sludge);
  g.add(base);

  // Bubbles
  const bubbles = [];
  for (let i = 0; i < 14; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.015 + (i % 4) * 0.008, 12, 12), M.sludge);
    b.position.set((Math.sin(i * 1.8) * 0.1), 0.02, (Math.cos(i * 2.1) * 0.08));
    g.add(b);
    bubbles.push({ mesh: b, baseScale: 1.0, speed: 2 + (i % 3) });
  }
  g.update = (lt) => {
    bubbles.forEach(b => {
      const s = Math.max(0.2, Math.sin(lt * b.speed) * 1.4);
      b.mesh.scale.set(s, s * 0.8, s);
    });
  };
  return shadow(g);
}

// 6. High-Detail Motherboard Circuit Board with Fried Components
export function motherboardPCB({ fried = false } = {}) {
  const M = materials();
  const g = new THREE.Group();

  // Green substrate
  const pcb = box(0.38, 0.015, 0.42, fried ? M.steelDark : M.pcbGreen);
  g.add(pcb);

  // Gold circuit traces
  for (let i = 0; i < 16; i++) {
    const trace = box(0.004, 0.018, 0.12 + (i % 5) * 0.04, M.goldTrace, [-0.14 + (i * 0.02), 0.002, (i % 2 === 0 ? 0.05 : -0.05)]);
    g.add(trace);
  }

  // Microchips
  const mainCPU = box(0.09, 0.025, 0.09, M.siliconChip, [0, 0.01, 0]);
  const ram1 = box(0.045, 0.02, 0.07, M.siliconChip, [0.08, 0.008, 0.04]);
  const ram2 = box(0.045, 0.02, 0.07, M.siliconChip, [-0.08, 0.008, 0.04]);
  g.add(mainCPU, ram1, ram2);

  // Capacitors
  for (let i = 0; i < 8; i++) {
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.022, 12), M.steelBright);
    cap.position.set(-0.12 + (i * 0.035), 0.015, 0.12);
    g.add(cap);
  }

  // Burnt scorched black overlay if fried
  if (fried) {
    const scorch = new THREE.Mesh(new THREE.CircleGeometry(0.12, 24), M.steelDark);
    scorch.rotation.x = -Math.PI / 2;
    scorch.position.set(0, 0.026, 0);
    g.add(scorch);
  }
  return shadow(g);
}

// 7. Lithium-Ion Smartphone Battery Pouch
export function lithiumBatteryPouch({ swollen = false } = {}) {
  const M = materials();
  const g = new THREE.Group();

  // Silver foil pouch
  const pouchGeo = new THREE.BoxGeometry(0.09, 0.14, swollen ? 0.045 : 0.012, 8, 8, 8);
  const pouch = new THREE.Mesh(pouchGeo, M.batteryFoil);
  g.add(pouch);

  // Black terminal ribbon at top
  const ribbon = box(0.05, 0.012, 0.006, M.siliconChip, [0, 0.074, 0]);
  const termPos = box(0.008, 0.015, 0.003, M.goldTrace, [-0.018, 0.082, 0]);
  const termNeg = box(0.008, 0.015, 0.003, M.steelBright, [0.018, 0.082, 0]);
  g.add(ribbon, termPos, termNeg);

  // Warning label
  const label = box(0.065, 0.08, 0.001, M.steelDark, [0, -0.01, swollen ? 0.023 : 0.0065]);
  g.add(label);

  return shadow(g);
}

// 8. Sharp Steel Puncture Nail
export function sharpSteelNail() {
  const M = materials();
  const g = new THREE.Group();

  // Shaft
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.005, 0.16, 16), M.steelBright);
  shaft.position.y = 0.08;
  g.add(shaft);

  // Flat head
  const head = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.006, 16), M.steelBright);
  head.position.y = 0.16;
  g.add(head);

  // Sharp tip
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.005, 0.024, 16), M.steelBright);
  tip.rotation.x = Math.PI;
  tip.position.y = -0.012;
  g.add(tip);

  return shadow(g);
}

// 9. Exploded Layer Cutaway of Battery (Cathode, Separator, Anode)
export function batteryLayeredCutaway() {
  const M = materials();
  const g = new THREE.Group();

  // Cathode (Blue foil)
  const cathode = box(0.18, 0.008, 0.22, M.batteryCathode, [0, 0.06, 0]);
  // Separator (Porous White membrane)
  const sep = box(0.19, 0.004, 0.23, M.separator, [0, 0.0, 0]);
  // Anode (Copper foil)
  const anode = box(0.18, 0.008, 0.22, M.batteryAnode, [0, -0.06, 0]);

  g.add(cathode, sep, anode);
  g.sep = sep;
  g.cathode = cathode;
  g.anode = anode;

  return shadow(g);
}

// 10. Volumetric Jet Blowtorch Flame
export function fireBlowtorchJet() {
  const M = materials();
  const g = new THREE.Group();

  // Multiple nested glowing flame cones
  const core = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.35, 16), M.electricArc);
  core.position.y = 0.17;
  const flameOuter = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.45, 16), M.flame);
  flameOuter.position.y = 0.22;

  g.add(flameOuter, core);
  g.update = (lt) => {
    const s = 1.0 + Math.sin(lt * 25) * 0.15;
    g.scale.set(s, s * 1.1, s);
  };
  return g;
}

// 11. 3D Floating Misconception Badge
export function misconceptionBadge(text = "MISCONCEPTION") {
  const M = materials();
  const g = new THREE.Group();

  // Pill badge
  const badge = new THREE.Mesh(new THREE.CapsuleGeometry(0.04, 0.24, 8, 16), M.steelDark);
  badge.rotation.z = Math.PI / 2;
  g.add(badge);

  // Red border ring
  const border = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.006, 8, 24), M.flame);
  border.position.set(-0.10, 0, 0.02);
  g.add(border);

  // Large question mark icon / exclamation
  const bar = box(0.008, 0.05, 0.008, M.goldTrace, [-0.10, 0.01, 0.02]);
  const dot = box(0.008, 0.008, 0.008, M.goldTrace, [-0.10, -0.025, 0.02]);
  g.add(bar, dot);

  return shadow(g);
}

// 12. Deformed 3D Chewing Gum Wad
export function chewingGumWad(scale = 1.0) {
  const M = materials();
  const geo = new THREE.DodecahedronGeometry(0.045 * scale, 2);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const v = new THREE.Vector3().fromBufferAttribute(pos, i);
    const n = Math.sin(v.x * 40) * Math.cos(v.y * 30) * 0.005;
    v.addScaledVector(v.clone().normalize(), n);
    pos.setXYZ(i, v.x, v.y, v.z);
  }
  geo.computeVertexNormals();
  const mesh = new THREE.Mesh(geo, M.gumPink);
  mesh.castShadow = true;
  return mesh;
}

// 13. Anatomical Stomach Chamber with Gastric Acid Pool
export function stomachChamber() {
  const M = materials();
  const g = new THREE.Group();

  const stomachOuter = new THREE.Mesh(
    new THREE.TorusGeometry(0.18, 0.08, 16, 32, Math.PI * 1.3),
    M.organInternal
  );
  stomachOuter.rotation.z = -0.4;
  g.add(stomachOuter);

  const acid = new THREE.Mesh(
    new THREE.CylinderGeometry(0.11, 0.11, 0.04, 24),
    M.acidGreen
  );
  acid.position.set(0.05, -0.06, 0);
  g.add(acid);

  const bubbleGroup = new THREE.Group();
  for (let i = 0; i < 8; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.008 + (i % 3) * 0.004, 12, 12), M.acidGreen);
    b.position.set((Math.random() - 0.5) * 0.14 + 0.05, -0.04 + Math.random() * 0.05, (Math.random() - 0.5) * 0.1);
    b.baseY = b.position.y;
    b.spd = 0.5 + Math.random() * 0.8;
    bubbleGroup.add(b);
  }
  g.add(bubbleGroup);

  g.update = (lt) => {
    bubbleGroup.children.forEach(b => {
      b.position.y = b.baseY + ((lt * b.spd) % 0.06);
    });
    acid.scale.y = 1.0 + Math.sin(lt * 4) * 0.08;
  };

  return shadow(g);
}

// 14. Pulsing Intestinal Peristalsis Tube
export function peristalsisTube() {
  const M = materials();
  const g = new THREE.Group();

  const rings = [];
  const count = 14;
  for (let i = 0; i < count; i++) {
    const r = new THREE.Mesh(
      new THREE.TorusGeometry(0.065, 0.018, 12, 24),
      M.organInternal
    );
    const t = (i / (count - 1)) * 2 - 1;
    r.position.set(Math.sin(t * 1.5) * 0.08, -t * 0.22, 0);
    r.rotation.x = Math.PI / 2;
    rings.push(r);
    g.add(r);
  }

  g.update = (lt) => {
    rings.forEach((r, idx) => {
      const wave = Math.sin(lt * 5 - idx * 0.5);
      const s = 1.0 + wave * 0.22;
      r.scale.set(s, s, 1.0);
    });
  };

  return shadow(g);
}
