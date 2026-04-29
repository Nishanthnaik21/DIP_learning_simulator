/**
 * HeroScene.jsx — Full Three.js 3D scene for the Home page hero section.
 *
 * Contains:
 *  - Animated icosahedron core with MeshDistortMaterial (blue/purple)
 *  - Two glowing orbit rings (cyan & purple)
 *  - 100 scattered spherical particles orbiting the core
 *  - 6 floating coloured micro-orbs
 *  - Starfield background (5 000 stars)
 *  - Bloom post-processing
 */

import { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Stars, Float, MeshDistortMaterial } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'

/* ─── Animated icosahedron + orbit rings ──────────────── */
function AnimatedCore() {
  const coreRef  = useRef()
  const ring1Ref = useRef()
  const ring2Ref = useRef()

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    if (coreRef.current)  { coreRef.current.rotation.x  = t * 0.08; coreRef.current.rotation.y  = t * 0.12 }
    if (ring1Ref.current) { ring1Ref.current.rotation.x = t * 0.40; ring1Ref.current.rotation.z = t * 0.25 }
    if (ring2Ref.current) { ring2Ref.current.rotation.y = t * 0.35; ring2Ref.current.rotation.z = -t * 0.18 }
  })

  return (
    <group>
      {/* Distorted core */}
      <Float speed={1.4} rotationIntensity={0.25} floatIntensity={0.6}>
        <mesh ref={coreRef}>
          <icosahedronGeometry args={[1.3, 4]} />
          <MeshDistortMaterial
            color="#4361ee" emissive="#4361ee" emissiveIntensity={0.5}
            distort={0.25} speed={2} roughness={0.08} metalness={0.85}
          />
        </mesh>
      </Float>

      {/* Orbit ring 1 — cyan */}
      <mesh ref={ring1Ref} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.3, 0.018, 16, 140]} />
        <meshStandardMaterial color="#4cc9f0" emissive="#4cc9f0" emissiveIntensity={1.3} transparent opacity={0.85} />
      </mesh>

      {/* Orbit ring 2 — purple */}
      <mesh ref={ring2Ref} rotation={[Math.PI / 3.5, Math.PI / 5, 0]}>
        <torusGeometry args={[2.85, 0.013, 16, 140]} />
        <meshStandardMaterial color="#b44fff" emissive="#b44fff" emissiveIntensity={1.3} transparent opacity={0.75} />
      </mesh>
    </group>
  )
}

/* ─── Rotating particle cloud ─────────────────────────── */
function ParticleCloud({ count = 100 }) {
  const ref = useRef()

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2
      const phi   = Math.acos(2 * Math.random() - 1)
      const r     = 3.6 + Math.random() * 3.5
      arr[i * 3]     = r * Math.sin(phi) * Math.cos(theta)
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      arr[i * 3 + 2] = r * Math.cos(phi)
    }
    return arr
  }, [count])

  useFrame(({ clock }) => {
    if (ref.current) ref.current.rotation.y = clock.elapsedTime * 0.04
  })

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" array={positions} count={count} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.045} color="#4cc9f0" transparent opacity={0.65} sizeAttenuation />
    </points>
  )
}

/* ─── Floating micro-orbs ─────────────────────────────── */
const ORB_CONFIGS = [
  { pos: [-4.5,  1.5, -2.0], color: '#4361ee', scale: 0.22, speed: 0.55 },
  { pos: [ 4.6, -1.2, -2.0], color: '#7209b7', scale: 0.28, speed: 0.42 },
  { pos: [-3.0, -2.6, -1.2], color: '#4cc9f0', scale: 0.16, speed: 0.80 },
  { pos: [ 3.8,  2.4, -1.5], color: '#06d6a0', scale: 0.18, speed: 0.65 },
  { pos: [ 0.4,  3.8, -2.5], color: '#f8961e', scale: 0.20, speed: 0.48 },
  { pos: [-1.0, -4.0, -2.0], color: '#ff3366', scale: 0.14, speed: 1.00 },
]

function FloatingOrb({ pos, color, scale, speed }) {
  const ref   = useRef()
  const phase = useMemo(() => pos[0] * 0.5 + pos[1] * 0.3, [pos])

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.position.y = pos[1] + Math.sin(clock.elapsedTime * speed + phase) * 0.35
      ref.current.rotation.y = clock.elapsedTime * speed * 0.5
    }
  })

  return (
    <mesh ref={ref} position={pos} scale={scale}>
      <sphereGeometry args={[1, 14, 14]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} roughness={0.1} metalness={0.9} transparent opacity={0.88} />
    </mesh>
  )
}

/* ─── Scene root (inside Canvas) ─────────────────────── */
function SceneContent() {
  return (
    <>
      <color attach="background" args={['#0d1117']} />

      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 5]}  intensity={2.5} color="#4361ee" />
      <pointLight position={[-10, -5, -5]} intensity={1.5} color="#7209b7" />
      <pointLight position={[0, 8, 0]}    intensity={0.8} color="#4cc9f0" />

      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0.15} fade speed={0.4} />

      <AnimatedCore />
      <ParticleCloud count={110} />

      {ORB_CONFIGS.map((cfg, i) => <FloatingOrb key={i} {...cfg} />)}

      <EffectComposer>
        <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.85} intensity={1.8} height={300} />
      </EffectComposer>
    </>
  )
}

/* ─── Exported canvas component ───────────────────────── */
export default function HeroScene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 6.5], fov: 60 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
      performance={{ min: 0.5 }}
    >
      <Suspense fallback={null}>
        <SceneContent />
      </Suspense>
    </Canvas>
  )
}
