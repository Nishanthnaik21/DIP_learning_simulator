/**
 * LoginScene.jsx — Three.js background for the Login page.
 *
 * A rotating icosahedron with wireframe overlay, three glowing orbit rings,
 * and a starfield — positioned to the right so the login card on the left
 * doesn't overlap the core geometry.
 */

import { useRef, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Stars } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'

function RotatingCore() {
  const coreRef  = useRef()
  const ring1Ref = useRef()
  const ring2Ref = useRef()
  const ring3Ref = useRef()

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    if (coreRef.current)  { coreRef.current.rotation.x  = t * 0.20; coreRef.current.rotation.z = t * 0.08 }
    if (ring1Ref.current) ring1Ref.current.rotation.x = t * 0.45
    if (ring2Ref.current) ring2Ref.current.rotation.y = t * 0.30
    if (ring3Ref.current) ring3Ref.current.rotation.z = t * 0.20
  })

  return (
    <group position={[3.0, 0, -1]}>
      {/* Core */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[1.25, 3]} />
        <meshStandardMaterial color="#4361ee" emissive="#4361ee" emissiveIntensity={0.55} roughness={0.1} metalness={0.9} transparent opacity={0.8} />
      </mesh>

      {/* Wireframe shell */}
      <mesh>
        <icosahedronGeometry args={[1.30, 3]} />
        <meshBasicMaterial color="#4cc9f0" wireframe transparent opacity={0.18} />
      </mesh>

      {/* Ring — cyan */}
      <mesh ref={ring1Ref} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.0, 0.016, 16, 120]} />
        <meshStandardMaterial color="#4cc9f0" emissive="#4cc9f0" emissiveIntensity={1.3} />
      </mesh>

      {/* Ring — purple */}
      <mesh ref={ring2Ref} rotation={[Math.PI / 3, 0, 0]}>
        <torusGeometry args={[2.55, 0.011, 16, 120]} />
        <meshStandardMaterial color="#b44fff" emissive="#b44fff" emissiveIntensity={1.2} />
      </mesh>

      {/* Ring — green */}
      <mesh ref={ring3Ref} rotation={[0, Math.PI / 4, 0]}>
        <torusGeometry args={[1.75, 0.013, 16, 120]} />
        <meshStandardMaterial color="#06d6a0" emissive="#06d6a0" emissiveIntensity={1.1} transparent opacity={0.8} />
      </mesh>
    </group>
  )
}

function SceneContent() {
  return (
    <>
      <color attach="background" args={['#0d1117']} />
      <ambientLight intensity={0.2} />
      <pointLight position={[6, 5, 5]}   intensity={2.2} color="#4361ee" />
      <pointLight position={[-5, -3, -3]} intensity={1.2} color="#7209b7" />
      <Stars radius={100} depth={50} count={4000} factor={4} saturation={0.1} fade speed={0.5} />
      <RotatingCore />
      <EffectComposer>
        <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.9} intensity={1.6} height={300} />
      </EffectComposer>
    </>
  )
}

export default function LoginScene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 7], fov: 60 }}
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
