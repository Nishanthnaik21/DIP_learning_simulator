import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Text3D, Environment } from '@react-three/drei'
import { EffectComposer, Bloom, DepthOfField } from '@react-three/postprocessing'
import * as THREE from 'three'

// Clean glass-like material with subtle blue glow
const glassMaterial = new THREE.MeshPhysicalMaterial({
  color: "#e6f2ff", // subtle blue tint
  transmission: 0.98,
  opacity: 1,
  metalness: 0.1,
  roughness: 0.02,
  ior: 1.5,
  thickness: 0.6,
  specularIntensity: 1,
  specularColor: new THREE.Color("#44bbff"),
  envMapIntensity: 1.5,
  clearcoat: 1,
  clearcoatRoughness: 0.1
})

const text = "DIP Learning Simulator"

// Estimated kerning widths for helvetiker_regular at size 0.6
const charWidths = {
  'D': 0.65, 'I': 0.25, 'P': 0.6, ' ': 0.5,
  'L': 0.55, 'e': 0.5, 'a': 0.5, 'r': 0.35, 'n': 0.5, 'i': 0.25, 'g': 0.55,
  'S': 0.55, 'm': 0.8, 'u': 0.5, 'l': 0.25, 't': 0.35, 'o': 0.55
}

function AnimatedLetter({ char, targetPosition, startPosition, rotStart, rotTarget, delay }) {
  const mesh = useRef()
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (t > delay) {
       // Smooth cubic ease out
       const progress = Math.min((t - delay) * 0.4, 1) // slower animation
       const ease = 1 - Math.pow(1 - progress, 4) // Quartic easing for softer finish
       
       mesh.current.position.lerpVectors(startPosition, targetPosition, ease)
       mesh.current.quaternion.slerpQuaternions(rotStart, rotTarget, ease)
    }
  })

  if (char === ' ') return null

  return (
    <Text3D
      ref={mesh}
      font="https://threejs.org/examples/fonts/helvetiker_regular.typeface.json"
      size={0.6}
      height={0.1}
      curveSegments={32}
      bevelEnabled
      bevelThickness={0.02}
      bevelSize={0.01}
      bevelOffset={0}
      bevelSegments={8}
      material={glassMaterial}
      position={startPosition}
      quaternion={rotStart}
    >
      {char}
    </Text3D>
  )
}

function AnimatedTitle() {
  const group = useRef()
  
  const charData = useMemo(() => {
    let currentX = 0
    const data = text.split('').map((char) => {
       // Calculate width, adding slight extra spacing
       const width = (charWidths[char] || 0.5) * 0.6 * 1.05 
       const x = currentX
       currentX += width
       return { char, targetX: x }
    })
    
    const totalWidth = currentX
    
    data.forEach(d => {
       // Center the title
       d.targetPosition = new THREE.Vector3(d.targetX - totalWidth / 2, 0, 0)
       
       // Start softly scattered behind and around
       d.startPosition = new THREE.Vector3(
          d.targetPosition.x + (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 15,
          (Math.random() * 10) - 30 // coming from the background
       )
       
       // Random starting rotations
       const axis = new THREE.Vector3(Math.random(), Math.random(), Math.random()).normalize()
       d.rotStart = new THREE.Quaternion().setFromAxisAngle(axis, Math.random() * Math.PI * 4)
       d.rotTarget = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0), 0)
       
       // Stagger animation onset softly
       d.delay = Math.random() * 1.5 
    })
    return data
  }, [])

  useFrame((state) => {
    // Subtle 3D parallax
    group.current.rotation.y = THREE.MathUtils.lerp(group.current.rotation.y, (state.mouse.x * Math.PI) / 30, 0.05)
    group.current.rotation.x = THREE.MathUtils.lerp(group.current.rotation.x, -(state.mouse.y * Math.PI) / 30, 0.05)
  })

  return (
    <group ref={group}>
      {charData.map((d, i) => (
        <AnimatedLetter key={i} {...d} />
      ))}
    </group>
  )
}

export default function CinematicTitle() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: 'radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%)', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
        {/* Clean, soft lighting setup */}
        <ambientLight intensity={0.6} color="#e2e8f0" />
        <directionalLight position={[5, 10, 5]} intensity={1} color="#bae6fd" />
        <pointLight position={[-5, -5, -5]} intensity={2} color="#38bdf8" distance={20} />
        
        {/* Realistic studio reflections */}
        <Environment preset="studio" blur={0.6} />

        <AnimatedTitle />

        <EffectComposer disableNormalPass>
          <Bloom luminanceThreshold={0.8} luminanceSmoothing={0.9} height={300} intensity={0.5} />
          <DepthOfField focusDistance={0.0} focalLength={0.02} bokehScale={1.2} height={480} />
        </EffectComposer>
      </Canvas>
    </div>
  )
}
