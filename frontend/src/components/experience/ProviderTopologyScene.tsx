"use client";

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Float, Text, Line } from '@react-three/drei';
import * as THREE from 'three';
import { useExperienceContext } from '@/contexts/ExperienceContext';
import { useProviders } from '@/hooks/useProviders';

function ProviderNode({ position, name, status, index }: { position: [number, number, number], name: string, status: string, index: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.5 + index;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.2 + index;
    }
  });

  const color = status === 'connected' ? '#00E676' : '#FF1744';

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1} position={position}>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[0.5, 1]} />
        <meshStandardMaterial color={color} wireframe opacity={0.8} transparent />
      </mesh>
      <Text position={[0, -0.8, 0]} fontSize={0.2} color="white" anchorX="center" anchorY="middle">
        {name}
      </Text>
    </Float>
  );
}

function Connections({ nodes }: { nodes: [number, number, number][] }) {
  const lines = useMemo(() => {
    const arr = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        // connect nodes randomly for topology look
        if (Math.random() > 0.5) {
          arr.push([nodes[i], nodes[j]]);
        }
      }
    }
    return arr;
  }, [nodes]);

  return (
    <>
      {lines.map((line, idx) => (
        <Line key={idx} points={line} color="#00E676" opacity={0.2} transparent lineWidth={1} />
      ))}
    </>
  );
}

export function ProviderTopologyScene() {
  const { reducedMotion, performanceMode } = useExperienceContext();
  const { providers } = useProviders();

  if (reducedMotion || performanceMode === 'battery-saver') {
    return <div className="h-full w-full flex items-center justify-center text-text-muted text-sm border border-glass-border bg-surface rounded-lg">3D Topology Disabled (Performance Mode)</div>;
  }

  const positions = useMemo(() => {
    return providers.map((_, i) => [
      Math.cos((i / providers.length) * Math.PI * 2) * 3,
      Math.sin(i * 1.5) * 1.5,
      Math.sin((i / providers.length) * Math.PI * 2) * 3
    ] as [number, number, number]);
  }, [providers]);

  return (
    <div className="w-full h-full rounded-lg overflow-hidden border border-glass-border bg-void relative shadow-glow">
      <Canvas camera={{ position: [0, 2, 8], fov: 45 }} dpr={performanceMode === 'ultra' ? [1, 2] : 1}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        {performanceMode !== 'low' && <Stars radius={10} depth={50} count={1000} factor={4} saturation={0} fade speed={1} />}
        
        {providers.map((p, idx) => (
          <ProviderNode key={p.id} index={idx} position={positions[idx] || [0,0,0]} name={p.name} status={p.status} />
        ))}
        
        <Connections nodes={positions} />
        
        <OrbitControls enableZoom={true} enablePan={false} autoRotate={!reducedMotion} autoRotateSpeed={0.5} />
      </Canvas>
    </div>
  );
}
