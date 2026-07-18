'use client';

import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, MeshDistortMaterial, Sphere } from '@react-three/drei';
import { useTheme } from 'next-themes';
import * as THREE from 'three';

import dynamic from 'next/dynamic';

const DynamicCanvas = dynamic(() => import('@react-three/fiber').then(mod => mod.Canvas), {
  ssr: false,
});

function AmbientSphere() {
  const mesh = useRef<THREE.Mesh>(null);
  const { theme } = useTheme();
  
  const isReducedMotion = typeof window !== 'undefined' && window.matchMedia(`(prefers-reduced-motion: reduce)`).matches === true;

  useFrame((state) => {
    if (mesh.current && !isReducedMotion) {
      mesh.current.rotation.x = state.clock.getElapsedTime() * 0.1;
      mesh.current.rotation.y = state.clock.getElapsedTime() * 0.15;
    }
  });

  const isDark = theme === 'dark';
  const color = isDark ? "#2a3a5a" : "#cde4fa";

  return (
    <Sphere ref={mesh} args={[1, 64, 64]} scale={2}>
      <MeshDistortMaterial
        color={color}
        envMapIntensity={0.8}
        clearcoat={1}
        clearcoatRoughness={0.1}
        metalness={0.1}
        roughness={0.4}
        distort={isReducedMotion ? 0 : 0.4}
        speed={isReducedMotion ? 0 : 1.5}
      />
    </Sphere>
  );
}

export function HeroBackground() {
  return (
    <div className="absolute top-0 right-0 w-[600px] h-[500px] pointer-events-none opacity-40 mix-blend-screen overflow-hidden -z-10" aria-hidden="true">
      <DynamicCanvas camera={{ position: [0, 0, 4], fov: 45 }} gl={{ alpha: true }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <AmbientSphere />
        <Environment preset="city" />
      </DynamicCanvas>
    </div>
  );
}
