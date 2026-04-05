"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

const HELIX_LENGTH = 48;
const BASE_PAIR_COLORS = [
  [0x38bdf8, 0x8b5cf6],
  [0x22d3ee, 0xf472b6],
  [0x67e8f9, 0xa855f7],
  [0x60a5fa, 0xfb7185],
];

const TONE_PALETTES = {
  resistant: {
    glow: 0xfb7185,
    secondary: 0xf97316,
    strandLeft: 0x7dd3fc,
    strandRight: 0xfb7185,
  },
  not_resistant: {
    glow: 0x22d3ee,
    secondary: 0x8b5cf6,
    strandLeft: 0x67e8f9,
    strandRight: 0xa78bfa,
  },
  neutral: {
    glow: 0x67e8f9,
    secondary: 0x8b5cf6,
    strandLeft: 0x38bdf8,
    strandRight: 0xa855f7,
  },
};

function createConnector(start, end, colorHex) {
  const midpoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start);
  const length = direction.length();
  const geometry = new THREE.CylinderGeometry(0.09, 0.09, length, 12);
  const material = new THREE.MeshStandardMaterial({
    color: colorHex,
    emissive: 0x112244,
    emissiveIntensity: 0.18,
    metalness: 0.35,
    roughness: 0.22,
    transparent: true,
    opacity: 0.9,
  });

  const connector = new THREE.Mesh(geometry, material);
  connector.position.copy(midpoint);
  connector.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.clone().normalize()
  );

  return connector;
}

export default function DNAHelix3D({
  highlightPositions = [7, 21, 35],
  predictionTone = "neutral",
  focusLabel = "Awaiting sequence lock",
  confidence = 0.5,
}) {
  const containerRef = useRef(null);
  const sceneStateRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!containerRef.current) {
      return undefined;
    }

    const container = containerRef.current;
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x040816, 0.026);

    const width = container.clientWidth || 640;
    const height = container.clientHeight || 520;

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 120);
    camera.position.set(0, 0.5, 27);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    if ("outputColorSpace" in renderer) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0x92a5ff, 0.42);
    const keyLight = new THREE.PointLight(0x67e8f9, 8, 100, 2.2);
    keyLight.position.set(0, 2, 16);

    const rimLight = new THREE.PointLight(0x8b5cf6, 6, 80, 2.1);
    rimLight.position.set(-18, 7, -4);

    const fillLight = new THREE.PointLight(0xfb7185, 3.8, 70, 1.8);
    fillLight.position.set(16, -10, 8);

    scene.add(ambientLight, keyLight, rimLight, fillLight);

    const helixGroup = new THREE.Group();
    helixGroup.rotation.x = 0.34;
    helixGroup.rotation.z = 0.14;
    scene.add(helixGroup);

    const strandPointsLeft = [];
    const strandPointsRight = [];
    const nodes = [];

    const sphereGeometry = new THREE.SphereGeometry(0.38, 20, 20);
    const glowGeometry = new THREE.SphereGeometry(0.92, 22, 22);

    for (let index = 0; index < HELIX_LENGTH; index += 1) {
      const angle = index * 0.42;
      const radius = 6.3 + Math.sin(index * 0.18) * 0.24;
      const y = (index - HELIX_LENGTH / 2) * 0.92;

      const leftPosition = new THREE.Vector3(
        Math.cos(angle) * radius,
        y,
        Math.sin(angle) * radius
      );
      const rightPosition = new THREE.Vector3(-leftPosition.x, y, -leftPosition.z);
      const midpoint = leftPosition.clone().add(rightPosition).multiplyScalar(0.5);

      strandPointsLeft.push(leftPosition.clone());
      strandPointsRight.push(rightPosition.clone());

      const pairColors = BASE_PAIR_COLORS[index % BASE_PAIR_COLORS.length];
      const leftMaterial = new THREE.MeshStandardMaterial({
        color: pairColors[0],
        emissive: pairColors[0],
        emissiveIntensity: 0.26,
        metalness: 0.28,
        roughness: 0.18,
      });
      const rightMaterial = new THREE.MeshStandardMaterial({
        color: pairColors[1],
        emissive: pairColors[1],
        emissiveIntensity: 0.22,
        metalness: 0.28,
        roughness: 0.18,
      });

      const leftSphere = new THREE.Mesh(sphereGeometry, leftMaterial);
      leftSphere.position.copy(leftPosition);

      const rightSphere = new THREE.Mesh(sphereGeometry, rightMaterial);
      rightSphere.position.copy(rightPosition);

      const connector = createConnector(leftPosition, rightPosition, 0x86a4ff);
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: 0x67e8f9,
        transparent: true,
        opacity: 0.05,
        depthWrite: false,
      });
      const glow = new THREE.Mesh(glowGeometry, glowMaterial);
      glow.position.copy(midpoint);

      helixGroup.add(leftSphere, rightSphere, connector, glow);

      nodes.push({
        leftMaterial,
        rightMaterial,
        connectorMaterial: connector.material,
        glowMaterial,
        glow,
        midpoint,
        baseColors: pairColors,
        highlighted: false,
        pulseOffset: index * 0.22,
      });
    }

    const leftTube = new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(strandPointsLeft), 280, 0.13, 12, false),
      new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        emissive: 0x38bdf8,
        emissiveIntensity: 0.24,
        transparent: true,
        opacity: 0.95,
        metalness: 0.3,
        roughness: 0.26,
      })
    );

    const rightTube = new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(strandPointsRight), 280, 0.13, 12, false),
      new THREE.MeshStandardMaterial({
        color: 0xa855f7,
        emissive: 0xa855f7,
        emissiveIntensity: 0.2,
        transparent: true,
        opacity: 0.92,
        metalness: 0.3,
        roughness: 0.26,
      })
    );

    helixGroup.add(leftTube, rightTube);

    const particleCount = 320;
    const particlePositions = new Float32Array(particleCount * 3);
    const particleColors = new Float32Array(particleCount * 3);
    for (let index = 0; index < particleCount; index += 1) {
      particlePositions[index * 3] = (Math.random() - 0.5) * 42;
      particlePositions[index * 3 + 1] = (Math.random() - 0.5) * 36;
      particlePositions[index * 3 + 2] = (Math.random() - 0.5) * 36;

      const color = new THREE.Color(index % 2 === 0 ? 0x67e8f9 : 0x8b5cf6);
      particleColors[index * 3] = color.r;
      particleColors[index * 3 + 1] = color.g;
      particleColors[index * 3 + 2] = color.b;
    }

    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
    particleGeometry.setAttribute("color", new THREE.BufferAttribute(particleColors, 3));

    const particleField = new THREE.Points(
      particleGeometry,
      new THREE.PointsMaterial({
        size: 0.09,
        transparent: true,
        opacity: 0.75,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        vertexColors: true,
      })
    );
    scene.add(particleField);

    const pointerTarget = { x: 0.34, y: 0.14 };
    const pointerCurrent = { x: 0.34, y: 0.14 };
    let frameId = 0;

    const handlePointerMove = (event) => {
      const rect = container.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      pointerTarget.y = x * 0.42;
      pointerTarget.x = 0.32 + y * 0.36;
    };

    const handlePointerLeave = () => {
      pointerTarget.x = 0.34;
      pointerTarget.y = 0.14;
    };

    const handleResize = () => {
      if (!container) {
        return;
      }

      const nextWidth = container.clientWidth || 640;
      const nextHeight = container.clientHeight || 520;
      camera.aspect = nextWidth / nextHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(nextWidth, nextHeight);
    };

    container.addEventListener("pointermove", handlePointerMove);
    container.addEventListener("pointerleave", handlePointerLeave);
    window.addEventListener("resize", handleResize);

    const animate = (time) => {
      const elapsed = time * 0.001;

      pointerCurrent.x += (pointerTarget.x - pointerCurrent.x) * 0.03;
      pointerCurrent.y += (pointerTarget.y - pointerCurrent.y) * 0.03;

      helixGroup.rotation.y += 0.005;
      helixGroup.rotation.x += (pointerCurrent.x - helixGroup.rotation.x) * 0.02;
      helixGroup.rotation.z += (pointerCurrent.y - helixGroup.rotation.z) * 0.03;
      helixGroup.position.y = Math.sin(elapsed * 0.9) * 0.35;

      nodes.forEach((node) => {
        const pulse = 0.5 + Math.sin(elapsed * 3 + node.pulseOffset) * 0.5;
        node.glow.scale.setScalar(node.highlighted ? 1.15 + pulse * 0.32 : 0.86 + pulse * 0.08);
        node.glowMaterial.opacity = node.highlighted ? 0.18 + pulse * 0.12 : 0.035 + pulse * 0.015;
      });

      particleField.rotation.y = -elapsed * 0.03;
      particleField.rotation.x = Math.sin(elapsed * 0.25) * 0.06;

      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(animate);
    };

    sceneStateRef.current = {
      renderer,
      scene,
      keyLight,
      rimLight,
      leftTubeMaterial: leftTube.material,
      rightTubeMaterial: rightTube.material,
      nodes,
      pointerTarget,
      frameId,
    };

    frameId = window.requestAnimationFrame(animate);
    setIsReady(true);

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", handleResize);
      container.removeEventListener("pointermove", handlePointerMove);
      container.removeEventListener("pointerleave", handlePointerLeave);

      scene.traverse((object) => {
        if (object.geometry) {
          object.geometry.dispose();
        }
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((material) => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });

      renderer.dispose();
      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
      sceneStateRef.current = null;
    };
  }, []);

  useEffect(() => {
    const state = sceneStateRef.current;
    if (!state) {
      return;
    }

    const palette = TONE_PALETTES[predictionTone] || TONE_PALETTES.neutral;
    const normalizedHighlights = new Set(
      (highlightPositions || []).map((value) =>
        Math.min(HELIX_LENGTH - 1, Math.max(0, Number(value) || 0))
      )
    );

    state.keyLight.color.setHex(palette.glow);
    state.rimLight.color.setHex(palette.secondary);
    state.leftTubeMaterial.color.setHex(palette.strandLeft);
    state.leftTubeMaterial.emissive.setHex(palette.strandLeft);
    state.rightTubeMaterial.color.setHex(palette.strandRight);
    state.rightTubeMaterial.emissive.setHex(palette.strandRight);

    state.nodes.forEach((node, index) => {
      const highlighted = normalizedHighlights.has(index);
      node.highlighted = highlighted;

      node.leftMaterial.color.setHex(highlighted ? palette.glow : node.baseColors[0]);
      node.leftMaterial.emissive.setHex(highlighted ? palette.glow : node.baseColors[0]);
      node.leftMaterial.emissiveIntensity = highlighted ? 0.75 : 0.26;

      node.rightMaterial.color.setHex(highlighted ? palette.secondary : node.baseColors[1]);
      node.rightMaterial.emissive.setHex(highlighted ? palette.secondary : node.baseColors[1]);
      node.rightMaterial.emissiveIntensity = highlighted ? 0.72 : 0.22;

      node.connectorMaterial.color.setHex(highlighted ? palette.glow : 0x86a4ff);
      node.connectorMaterial.emissive.setHex(highlighted ? palette.secondary : 0x112244);
      node.connectorMaterial.emissiveIntensity = highlighted ? 0.55 : 0.18;

      node.glowMaterial.color.setHex(highlighted ? palette.glow : 0x67e8f9);
      node.glow.scale.setScalar(highlighted ? 1.2 + confidence * 0.35 : 0.86);
    });
  }, [highlightPositions, predictionTone, confidence]);

  return (
    <section className="neon-panel relative overflow-hidden rounded-[34px] p-4 sm:p-5">
      <div
        ref={containerRef}
        className="relative h-[520px] overflow-hidden rounded-[28px] border border-white/10 bg-[#040816]"
      >
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(103,232,249,0.12),transparent_24%),radial-gradient(circle_at_bottom,rgba(168,85,247,0.12),transparent_28%)]" />
        <div className="pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-cyan-300/10 to-transparent" />

        <div className="absolute left-4 top-4 z-10 rounded-2xl border border-white/10 bg-black/30 px-4 py-3 backdrop-blur-xl">
          <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
            3D Molecular View
          </p>
          <p className="mt-2 text-sm font-medium text-white">Interactive DNA helix</p>
        </div>

        <div className="absolute bottom-4 left-4 z-10 max-w-xs rounded-2xl border border-white/10 bg-black/35 px-4 py-3 backdrop-blur-xl">
          <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Focus Label</p>
          <p className="mt-2 text-sm font-medium text-white">{focusLabel}</p>
          <p className="mt-1 text-xs text-slate-400">
            {Math.round(confidence * 100)}% visual confidence lock
          </p>
        </div>

        <div className="absolute bottom-4 right-4 z-10 rounded-2xl border border-white/10 bg-black/35 px-4 py-3 text-right backdrop-blur-xl">
          <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Mutation Tracking</p>
          <p className="mt-2 text-sm font-medium text-white">
            {highlightPositions.length} highlighted loci
          </p>
        </div>

        {!isReady && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-[#040816]/80">
            <div className="flex flex-col items-center gap-4">
              <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300" />
              <p className="text-sm text-slate-300">Rendering DNA helix...</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
