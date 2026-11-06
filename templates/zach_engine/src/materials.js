import * as THREE from 'three';
import { steelTextures, chainmailTextures, woodTexture, fabricTexture, skinTexture } from './textures.js';

let M = null;
export function materials() {
  if (M) return M;
  const steel = steelTextures(3);
  const steel2 = steelTextures(9);
  const fab = fabricTexture();
  const skinN = skinTexture();
  M = {
    skin: new THREE.MeshPhysicalMaterial({ color: 0xd99b7a, roughness: 0.52, sheen: 0.6, sheenColor: new THREE.Color(0xffc8b0), sheenRoughness: 0.5, bumpMap: skinN, bumpScale: 0.6, clearcoat: 0.08 }),
    lip: new THREE.MeshStandardMaterial({ color: 0xa85e52, roughness: 0.45 }),
    hair: new THREE.MeshStandardMaterial({ color: 0x3a2618, roughness: 0.85, bumpMap: fab, bumpScale: 2 }),
    beard: new THREE.MeshStandardMaterial({ color: 0x5c4434, roughness: 0.95, bumpMap: fab, bumpScale: 3 }),
    eyeWhite: new THREE.MeshPhysicalMaterial({ color: 0xf2eee8, roughness: 0.15, clearcoat: 1 }),
    iris: new THREE.MeshPhysicalMaterial({ color: 0x4a3322, roughness: 0.2, clearcoat: 1 }),
    mouth: new THREE.MeshStandardMaterial({ color: 0x2a0d0b, roughness: 0.9 }),
    teeth: new THREE.MeshStandardMaterial({ color: 0xf0ece0, roughness: 0.4 }),
    cloth: new THREE.MeshStandardMaterial({ color: 0x1d1d20, roughness: 0.92, bumpMap: fab, bumpScale: 1.2 }),
    clothGrey: new THREE.MeshStandardMaterial({ color: 0x3e4044, roughness: 0.9, bumpMap: fab, bumpScale: 1.2 }),
    leather: new THREE.MeshStandardMaterial({ color: 0x3a2618, roughness: 0.6 }),
    steel: new THREE.MeshPhysicalMaterial({ color: 0xc4c6ca, map: steel.color, metalness: 1, roughness: 0.42, roughnessMap: steel.rough, clearcoat: 0.25, clearcoatRoughness: 0.4 }),
    steelDark: new THREE.MeshPhysicalMaterial({ color: 0x4a4c50, map: steel2.color, metalness: 1, roughness: 0.28, roughnessMap: steel2.rough }),
    steelBright: new THREE.MeshPhysicalMaterial({ color: 0xd0d2d6, metalness: 1, roughness: 0.22, roughnessMap: steel2.rough }),
    gun: new THREE.MeshPhysicalMaterial({ color: 0xb8bcc2, metalness: 1, roughness: 0.3, roughnessMap: steel.rough, clearcoat: 0.3 }),
    gunDark: new THREE.MeshStandardMaterial({ color: 0x2a2b2e, metalness: 0.4, roughness: 0.5 }),
    copper: new THREE.MeshPhysicalMaterial({ color: 0xd9733f, metalness: 1, roughness: 0.25, emissive: 0x6a1d05, emissiveIntensity: 0.3, clearcoat: 0.6 }),
    wood: new THREE.MeshStandardMaterial({ map: woodTexture(), roughness: 0.75 }),
    woodDark: new THREE.MeshStandardMaterial({ map: woodTexture(21), color: 0x8a6a50, roughness: 0.8 }),
    rivet: new THREE.MeshStandardMaterial({ color: 0x8b5a2b, metalness: 0.8, roughness: 0.35 }),
    feather: new THREE.MeshStandardMaterial({ color: 0xe8e2d0, roughness: 0.8, side: THREE.DoubleSide }),
    string: new THREE.MeshStandardMaterial({ color: 0xe0d8c0, roughness: 0.6 }),
    // ---------- Modern Tech & Physics Materials ----------
    phoneBody: new THREE.MeshPhysicalMaterial({ color: 0x1e2229, metalness: 0.85, roughness: 0.32, clearcoat: 0.2 }),
    phoneScreen: new THREE.MeshPhysicalMaterial({ color: 0x08090a, metalness: 0.2, roughness: 0.08, clearcoat: 1.0 }),
    phoneScreenOn: new THREE.MeshPhysicalMaterial({ color: 0x0f172a, emissive: 0x1e3a8a, emissiveIntensity: 0.8, roughness: 0.1, clearcoat: 1.0 }),
    pcbGreen: new THREE.MeshStandardMaterial({ color: 0x064e3b, roughness: 0.55 }),
    goldTrace: new THREE.MeshPhysicalMaterial({ color: 0xf59e0b, metalness: 0.95, roughness: 0.18 }),
    siliconChip: new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.25, metalness: 0.3 }),
    water: new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.72, roughness: 0.05, transmission: 0.6, ior: 1.33 }),
    riceGrain: new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.75 }),
    ceramic: new THREE.MeshPhysicalMaterial({ color: 0xf1f5f9, roughness: 0.18, clearcoat: 0.85 }),
    sludge: new THREE.MeshStandardMaterial({ color: 0x65a30d, emissive: 0x365314, emissiveIntensity: 0.6, roughness: 0.4 }),
    batteryFoil: new THREE.MeshPhysicalMaterial({ color: 0xcbd5e1, metalness: 0.92, roughness: 0.28, clearcoat: 0.4 }),
    batteryCathode: new THREE.MeshPhysicalMaterial({ color: 0x1d4ed8, metalness: 0.75, roughness: 0.35 }),
    batteryAnode: new THREE.MeshPhysicalMaterial({ color: 0xb45309, metalness: 0.85, roughness: 0.3 }),
    separator: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85, transparent: true, opacity: 0.88 }),
    flame: new THREE.MeshBasicMaterial({ color: 0xff5500, transparent: true, opacity: 0.95 }),
    electricArc: new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.9 }),
    smoke: new THREE.MeshStandardMaterial({ color: 0x334155, transparent: true, opacity: 0.45, roughness: 0.9 }),
    // ---------- Biology & Anatomy Materials ----------
    gumPink: new THREE.MeshPhysicalMaterial({ color: 0xf472b6, roughness: 0.35, clearcoat: 0.6 }),
    organInternal: new THREE.MeshPhysicalMaterial({ color: 0x991b1b, roughness: 0.42, clearcoat: 0.3 }),
    acidGreen: new THREE.MeshPhysicalMaterial({ color: 0x84cc16, roughness: 0.1, transparent: true, opacity: 0.8, transmission: 0.7, emissive: 0x365314, emissiveIntensity: 0.5, ior: 1.34 }),
    // ---------- Character Wardrobe & Styling Materials ----------
    clothNavy: new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.88, bumpMap: fab, bumpScale: 1.2 }),
    clothCharcoal: new THREE.MeshStandardMaterial({ color: 0x27272a, roughness: 0.85, bumpMap: fab, bumpScale: 1.2 }),
    clothCrimson: new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.85, bumpMap: fab, bumpScale: 1.2 }),
    clothEmerald: new THREE.MeshStandardMaterial({ color: 0x065f46, roughness: 0.85, bumpMap: fab, bumpScale: 1.2 }),
    clothLabCoat: new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.68, bumpMap: fab, bumpScale: 1.0 }),
    clothTeal: new THREE.MeshStandardMaterial({ color: 0x0e7490, roughness: 0.85, bumpMap: fab, bumpScale: 1.2 }),
    clothKhaki: new THREE.MeshStandardMaterial({ color: 0x78716c, roughness: 0.90, bumpMap: fab, bumpScale: 1.2 }),
    sneakerWhite: new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.32 }),
    shoeLeather: new THREE.MeshPhysicalMaterial({ color: 0x451a03, roughness: 0.45, clearcoat: 0.35 }),
    hairBlack: new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.85, bumpMap: fab, bumpScale: 2 }),
    hairAuburn: new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.85, bumpMap: fab, bumpScale: 2 }),
    hairGrey: new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.85, bumpMap: fab, bumpScale: 2 }),
    glassesFrame: new THREE.MeshPhysicalMaterial({ color: 0x09090b, metalness: 0.6, roughness: 0.2, clearcoat: 0.8 }),
    glassesLens: new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.32, roughness: 0.05, transmission: 0.9, ior: 1.5 }),
  };
  const cm = chainmailTextures([14, 9]);
  M.chainmail = new THREE.MeshPhysicalMaterial({
    color: 0xb8b8bc, map: cm.color, metalness: 1, metalnessMap: cm.bump, roughness: 0.42,
    bumpMap: cm.bump, bumpScale: 6, clearcoat: 0.3,
  });
  M._cmTex = cm;
  return M;
}
