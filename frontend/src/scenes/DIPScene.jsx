/**
 * DIPScene.jsx — Futuristic 3D DIP visualization scene.
 *
 * Features:
 *  - Floating input / output image planes with pixel-grid overlay
 *  - 3x3 convolution kernel cubes sweeping across the image
 *  - Particle flow (data processing metaphor)
 *  - Edge-glow outlines
 *  - Full camera orbit + zoom (OrbitControls)
 *  - Dual-theme: dark (neon/holographic) <-> light (soft matte)
 *  - Bloom post-processing, dynamic lighting
 */

import { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Line, Stars } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import * as THREE from 'three'

/* ═══════════════════════════════════════════════════════════
   THEME PALETTE
═══════════════════════════════════════════════════════════ */
const D = {
  bg: '#050a14', plane1: '#0d1b2a', grid: '#4cc9f0',
  kernel: '#b44fff', kernelHi: '#ff3dff', particle: '#4cc9f0',
  edge: '#4361ee', light1: '#4361ee', light2: '#7209b7',
  light3: '#4cc9f0', bloom: 1.8,
}
const L = {
  bg: '#f0f4f8', plane1: '#dce8f5', grid: '#5b8dd9',
  kernel: '#7c3aed', kernelHi: '#9333ea', particle: '#3b82f6',
  edge: '#2563eb', light1: '#60a5fa', light2: '#a78bfa',
  light3: '#34d399', bloom: 0.35,
}
const C = (isDark) => isDark ? D : L

/* ═══════════════════════════════════════════════════════════
   IMAGE PLANE (input / output)
═══════════════════════════════════════════════════════════ */
function ImagePlane({ isDark, isOutput = false }) {
  const meshRef = useRef()
  const p = C(isDark)

  const texture = useMemo(() => {
    const size = 128
    const data = new Uint8Array(size * size * 4)
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const i = (y * size + x) * 4
        const v = isDark
          ? Math.floor(10 + (Math.random() * 20) + ((x + y) % 16 < 1 ? 30 : 0))
          : Math.floor(200 + (Math.random() * 30) - ((x + y) % 16 < 1 ? 20 : 0))
        data[i]     = v
        data[i + 1] = v + (isDark ? 20 : -10)
        data[i + 2] = v + (isDark ? 40 : 10)
        data[i + 3] = 255
      }
    }
    const tex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat)
    tex.needsUpdate = true
    return tex
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDark])

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = Math.sin(clock.elapsedTime * 0.2) * 0.06
      meshRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.15) * 0.04
    }
  })

  const borderColor = isOutput ? p.kernel : p.grid

  return (
    <group position={[0, 0, isOutput ? -0.7 : 0]}>
      <mesh ref={meshRef}>
        <planeGeometry args={[5, 3.5]} />
        <meshStandardMaterial
          map={texture}
          color={p.plane1}
          roughness={isDark ? 0.05 : 0.65}
          metalness={isDark ? 0.9 : 0.05}
          transparent
          opacity={isOutput ? (isDark ? 0.55 : 0.6) : (isDark ? 0.85 : 0.88)}
          emissive={isDark ? new THREE.Color(p.plane1) : new THREE.Color('#ffffff')}
          emissiveIntensity={isDark ? 0.08 : 0}
        />
      </mesh>

      {/* Border outline via Line from drei */}
      <Line
        points={[[-2.5, -1.75, 0.01], [2.5, -1.75, 0.01], [2.5, 1.75, 0.01], [-2.5, 1.75, 0.01], [-2.5, -1.75, 0.01]]}
        color={borderColor}
        lineWidth={1.5}
        transparent
        opacity={isDark ? 0.7 : 0.4}
      />

      {/* Corner accent squares */}
      {[[-2.4, 1.6], [2.4, 1.6], [-2.4, -1.6], [2.4, -1.6]].map(([cx, cy], i) => (
        <mesh key={i} position={[cx, cy, 0.02]}>
          <planeGeometry args={[0.22, 0.22]} />
          <meshStandardMaterial
            color={borderColor}
            emissive={borderColor}
            emissiveIntensity={isDark ? 1.2 : 0.2}
            transparent
            opacity={isDark ? 0.9 : 0.6}
          />
        </mesh>
      ))}
    </group>
  )
}

/* ═══════════════════════════════════════════════════════════
   PIXEL GRID OVERLAY
═══════════════════════════════════════════════════════════ */
function PixelGrid({ isDark }) {
  const meshGroupRef = useRef()
  const p = C(isDark)
  const cols = 10, rows = 7

  const pixels = useMemo(() => {
    const arr = []
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        arr.push({
          x: (c - cols / 2 + 0.5) * 0.5,
          y: (r - rows / 2 + 0.5) * 0.5,
          v: Math.random(),
        })
      }
    }
    return arr
  }, [])

  // Build grid line points with drei <Line>
  const vertLines = useMemo(() => {
    const lines = []
    for (let i = 0; i <= cols; i++) {
      const x = (i - cols / 2) * 0.5
      lines.push([[x, -rows * 0.25, 0], [x, rows * 0.25, 0]])
    }
    return lines
  }, [])
  const horizLines = useMemo(() => {
    const lines = []
    for (let i = 0; i <= rows; i++) {
      const y = (i - rows / 2) * 0.5
      lines.push([[-cols * 0.25, y, 0], [cols * 0.25, y, 0]])
    }
    return lines
  }, [])

  useFrame(({ clock }) => {
    if (!meshGroupRef.current) return
    meshGroupRef.current.children.forEach((child, i) => {
      if (!child.material) return
      const t = clock.elapsedTime * 0.8 + i * 0.31
      child.material.opacity = isDark
        ? 0.15 + Math.abs(Math.sin(t)) * 0.3
        : 0.08 + Math.abs(Math.sin(t)) * 0.15
    })
  })

  return (
    <group position={[0, 0, 0.05]}>
      {/* Pixel cells — separate group for animation */}
      <group ref={meshGroupRef}>
        {pixels.map((px, i) => (
          <mesh key={i} position={[px.x, px.y, 0]}>
            <planeGeometry args={[0.46, 0.46]} />
            <meshStandardMaterial
              color={p.grid}
              emissive={p.grid}
              emissiveIntensity={isDark ? px.v * 0.8 : px.v * 0.1}
              transparent
              opacity={0.2}
            />
          </mesh>
        ))}
      </group>

      {/* Vertical grid lines */}
      {vertLines.map((pts, i) => (
        <Line key={`v${i}`} points={pts} color={p.grid} lineWidth={0.8} transparent opacity={isDark ? 0.25 : 0.12} />
      ))}
      {/* Horizontal grid lines */}
      {horizLines.map((pts, i) => (
        <Line key={`h${i}`} points={pts} color={p.grid} lineWidth={0.8} transparent opacity={isDark ? 0.25 : 0.12} />
      ))}
    </group>
  )
}

/* ═══════════════════════════════════════════════════════════
   3x3 CONVOLUTION KERNEL — sweeping cubes
═══════════════════════════════════════════════════════════ */
const KERNEL_VALUES = [
  [-1, -1, -1],
  [-1,  8, -1],
  [-1, -1, -1],
]

function KernelCubes({ isDark }) {
  const groupRef = useRef()
  const cubeRefs = useRef([])
  const p = C(isDark)

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    const cycleT = (t * 0.18) % 1
    const sweepX = -2.0 + cycleT * 4.0
    const row    = Math.floor(cycleT * 4) % 3
    const sweepY = 0.9 - row * 0.9

    if (groupRef.current) {
      groupRef.current.position.set(sweepX, sweepY, 0.2)
      groupRef.current.rotation.x = Math.sin(t * 0.4) * 0.1
      groupRef.current.rotation.y = Math.sin(t * 0.3) * 0.08
    }

    cubeRefs.current.forEach((mesh, i) => {
      if (!mesh) return
      const isCentre = i === 4
      const pulse = 0.5 + Math.abs(Math.sin(t * 3 + i * 0.5)) * 0.5
      mesh.material.emissiveIntensity = isCentre
        ? (isDark ? 1.5 + pulse : 0.25 + pulse * 0.15)
        : (isDark ? 0.3 + pulse * 0.3 : 0.05)
      mesh.scale.setScalar(isCentre ? 1 + pulse * 0.08 : 1)
    })
  })

  return (
    <group ref={groupRef}>
      {KERNEL_VALUES.flat().map((val, i) => {
        const col = i % 3
        const row = Math.floor(i / 3)
        const isCentre = i === 4
        const baseColor = isCentre ? p.kernelHi : p.kernel
        return (
          <mesh
            key={i}
            ref={el => (cubeRefs.current[i] = el)}
            position={[(col - 1) * 0.26, -(row - 1) * 0.26, 0]}
          >
            <boxGeometry args={[0.22, 0.22, isDark ? 0.16 : 0.08]} />
            <meshStandardMaterial
              color={baseColor}
              emissive={baseColor}
              emissiveIntensity={isDark ? 0.8 : 0.1}
              roughness={isDark ? 0.05 : 0.6}
              metalness={isDark ? 0.95 : 0.1}
              transparent
              opacity={isDark ? 0.92 : 0.78}
            />
          </mesh>
        )
      })}

      {/* Kernel value labels (small planes) */}
      {KERNEL_VALUES.flat().map((val, i) => {
        const col = i % 3
        const row = Math.floor(i / 3)
        return (
          <mesh key={`lbl-${i}`} position={[(col - 1) * 0.26, -(row - 1) * 0.26, 0.12]}>
            <planeGeometry args={[0.18, 0.12]} />
            <meshStandardMaterial
              color={isDark ? '#ffffff' : '#1e1b4b'}
              emissive={isDark ? '#ffffff' : '#000000'}
              emissiveIntensity={isDark ? 0.5 : 0}
              transparent
              opacity={isDark ? 0.6 : 0.4}
            />
          </mesh>
        )
      })}
    </group>
  )
}

/* ═══════════════════════════════════════════════════════════
   PARTICLE FLOW
═══════════════════════════════════════════════════════════ */
function ParticleFlow({ isDark, count = 180 }) {
  const ref = useRef()
  const p = C(isDark)

  const { positions, velocities } = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const vel = new Float32Array(count)
    for (let i = 0; i < count; i++) {
      pos[i * 3]     = (Math.random() - 0.5) * 8
      pos[i * 3 + 1] = (Math.random() - 0.5) * 6
      pos[i * 3 + 2] = (Math.random() - 0.5) * 3
      vel[i] = 0.005 + Math.random() * 0.012
    }
    return { positions: pos, velocities: vel }
  }, [count])

  useFrame(() => {
    if (!ref.current) return
    const arr = ref.current.geometry.attributes.position.array
    for (let i = 0; i < count; i++) {
      arr[i * 3] += velocities[i]
      if (arr[i * 3] > 4) arr[i * 3] = -4
    }
    ref.current.geometry.attributes.position.needsUpdate = true
  })

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={positions}
          count={count}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={isDark ? 0.05 : 0.035}
        color={p.particle}
        transparent
        opacity={isDark ? 0.7 : 0.45}
        sizeAttenuation
      />
    </points>
  )
}

/* ═══════════════════════════════════════════════════════════
   EDGE GLOW OUTLINE
═══════════════════════════════════════════════════════════ */
function EdgeGlowPlane({ isDark }) {
  const ref = useRef()
  const p = C(isDark)

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.material.opacity = isDark
        ? 0.4 + Math.abs(Math.sin(clock.elapsedTime * 1.5)) * 0.5
        : 0.12 + Math.abs(Math.sin(clock.elapsedTime * 1.2)) * 0.1
    }
  })

  return (
    <mesh ref={ref} position={[0, 0, 0.03]}>
      <planeGeometry args={[5.15, 3.65]} />
      <meshStandardMaterial
        color={p.edge}
        emissive={p.edge}
        emissiveIntensity={isDark ? 1.5 : 0.2}
        transparent
        opacity={0.4}
        wireframe
      />
    </mesh>
  )
}

/* ═══════════════════════════════════════════════════════════
   FREQUENCY WAVE GRID — uses imperative geometry via ref
═══════════════════════════════════════════════════════════ */
function FrequencyWaveGrid({ isDark }) {
  const meshRef = useRef()
  const cols = 16, rows = 10

  // Build a PlaneGeometry that we animate on each frame
  const geo = useMemo(() => {
    const g = new THREE.PlaneGeometry(7, 4.5, cols, rows)
    return g
  }, [])

  useFrame(({ clock }) => {
    if (!meshRef.current) return
    const posArr = meshRef.current.geometry.attributes.position.array
    const t = clock.elapsedTime * 1.2
    for (let i = 0; i < posArr.length; i += 3) {
      const x = posArr[i]
      const y = posArr[i + 1]
      posArr[i + 2] = Math.sin(x * 0.6 + t + y * 0.8) * (isDark ? 0.22 : 0.1)
    }
    meshRef.current.geometry.attributes.position.needsUpdate = true
  })

  return (
    <mesh ref={meshRef} position={[0, 0, -1.5]} rotation={[0.25, 0, 0]}>
      <primitive object={geo} attach="geometry" />
      <meshStandardMaterial
        color={isDark ? '#4cc9f0' : '#93c5fd'}
        emissive={isDark ? '#4cc9f0' : '#93c5fd'}
        emissiveIntensity={isDark ? 0.15 : 0.03}
        wireframe
        transparent
        opacity={isDark ? 0.3 : 0.18}
      />
    </mesh>
  )
}

/* ═══════════════════════════════════════════════════════════
   FLOATING ORBIT RINGS (visual flair)
═══════════════════════════════════════════════════════════ */
function OrbitRings({ isDark }) {
  const ring1 = useRef()
  const ring2 = useRef()

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    if (ring1.current) { ring1.current.rotation.x = t * 0.3; ring1.current.rotation.z = t * 0.2 }
    if (ring2.current) { ring2.current.rotation.y = t * 0.25; ring2.current.rotation.z = -t * 0.15 }
  })

  return (
    <>
      <mesh ref={ring1} rotation={[Math.PI / 2.5, 0, 0]}>
        <torusGeometry args={[3.6, 0.015, 16, 120]} />
        <meshStandardMaterial
          color={isDark ? '#4cc9f0' : '#60a5fa'}
          emissive={isDark ? '#4cc9f0' : '#60a5fa'}
          emissiveIntensity={isDark ? 1.3 : 0.2}
          transparent
          opacity={isDark ? 0.65 : 0.35}
        />
      </mesh>
      <mesh ref={ring2} rotation={[Math.PI / 3.5, Math.PI / 5, 0]}>
        <torusGeometry args={[4.2, 0.012, 16, 120]} />
        <meshStandardMaterial
          color={isDark ? '#b44fff' : '#a78bfa'}
          emissive={isDark ? '#b44fff' : '#a78bfa'}
          emissiveIntensity={isDark ? 1.2 : 0.15}
          transparent
          opacity={isDark ? 0.55 : 0.3}
        />
      </mesh>
    </>
  )
}

/* ═══════════════════════════════════════════════════════════
   SCENE LIGHTING
═══════════════════════════════════════════════════════════ */
function SceneLighting({ isDark }) {
  const p = C(isDark)
  return (
    <>
      <ambientLight intensity={isDark ? 0.15 : 0.65} color={isDark ? '#0d1b2a' : '#e8f4fc'} />
      <pointLight position={[6, 6, 4]}   intensity={isDark ? 3.5 : 1.5} color={p.light1} />
      <pointLight position={[-6, -4, -2]} intensity={isDark ? 2.0 : 1.0} color={p.light2} />
      <pointLight position={[0, 6, 2]}   intensity={isDark ? 1.2 : 0.6} color={p.light3} />
      <directionalLight
        position={[5, 8, 3]}
        intensity={isDark ? 0.4 : 1.2}
        color={isDark ? p.light1 : '#ffffff'}
      />
      {isDark && (
        <spotLight position={[0, 0, 6]} angle={0.45} penumbra={0.8} intensity={2.5} color="#4361ee" distance={12} />
      )}
    </>
  )
}

/* ═══════════════════════════════════════════════════════════
   SCENE CONTENT
═══════════════════════════════════════════════════════════ */
function SceneContent({ isDark }) {
  return (
    <>
      <color attach="background" args={[C(isDark).bg]} />
      {isDark && <Stars radius={80} depth={40} count={4000} factor={3.5} saturation={0.2} fade speed={0.3} />}

      <SceneLighting isDark={isDark} />

      {/* Particle data flow */}
      <ParticleFlow isDark={isDark} count={isDark ? 200 : 120} />

      {/* Bloom post-processing */}
      <EffectComposer>
        <Bloom
          luminanceThreshold={isDark ? 0.12 : 0.5}
          luminanceSmoothing={0.85}
          intensity={C(isDark).bloom}
          height={300}
        />
      </EffectComposer>

      {/* Camera controls */}
      <OrbitControls
        enablePan={false}
        enableZoom
        zoomSpeed={0.5}
        minDistance={3.5}
        maxDistance={14}
        autoRotate
        autoRotateSpeed={isDark ? 0.35 : 0.2}
        maxPolarAngle={Math.PI * 0.72}
        minPolarAngle={Math.PI * 0.25}
      />
    </>
  )
}

/* ═══════════════════════════════════════════════════════════
   EXPORTED CANVAS
═══════════════════════════════════════════════════════════ */
export default function DIPScene({ isDark = true }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 7.5], fov: 58 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
      performance={{ min: 0.5 }}
    >
      <Suspense fallback={null}>
        <SceneContent isDark={isDark} />
      </Suspense>
    </Canvas>
  )
}
