import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ToolWebcam() {
  const navigate = useNavigate()
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const [active, setActive] = useState(false)
  const [filter, setFilter] = useState('none')
  const [snapshots, setSnapshots] = useState([])
  const [error, setError] = useState('')

  const FILTERS = [
    { key: 'none', label: '🎨 Normal', css: '' },
    { key: 'gray', label: '⬛ Grayscale', css: 'grayscale(100%)' },
    { key: 'sepia', label: '🟤 Sepia', css: 'sepia(100%)' },
    { key: 'invert', label: '🔄 Invert', css: 'invert(100%)' },
    { key: 'contrast', label: '⚡ High Contrast', css: 'contrast(200%)' },
    { key: 'bright', label: '☀️ Bright', css: 'brightness(150%)' },
    { key: 'blur', label: '🌫️ Blur', css: 'blur(4px)' },
    { key: 'saturate', label: '🌈 Saturate', css: 'saturate(300%)' },
  ]

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      streamRef.current = stream
      videoRef.current.srcObject = stream
      setActive(true); setError('')
    } catch (e) { setError('Camera access denied or not available.') }
  }

  const stop = () => {
    streamRef.current?.getTracks().forEach(t => t.stop())
    setActive(false)
  }

  useEffect(() => () => { streamRef.current?.getTracks().forEach(t => t.stop()) }, [])

  const snap = () => {
    if (!videoRef.current || !canvasRef.current) return
    const v = videoRef.current; const c = canvasRef.current
    c.width = v.videoWidth; c.height = v.videoHeight
    const ctx = c.getContext('2d')
    const css = FILTERS.find(f => f.key === filter)?.css || ''
    if (css) ctx.filter = css
    ctx.drawImage(v, 0, 0)
    setSnapshots(prev => [{ url: c.toDataURL('image/jpeg', 0.9), filter, ts: new Date().toLocaleTimeString() }, ...prev].slice(0, 12))
  }

  const curFilter = FILTERS.find(f => f.key === filter)?.css || ''

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>📷</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Live Webcam Filters</h1>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
          <div>
            <div style={{ background: '#000', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', position: 'relative', boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5)', overflow: 'hidden' }}>
              <video ref={videoRef} autoPlay playsInline muted
                style={{ width: '100%', borderRadius: '16px', display: 'block', filter: curFilter, boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }} />
              
              {!active && (
                 <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.8)', zIndex: 5 }}>
                    <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎥</div>
                    <p style={{ fontWeight: 800, color: 'white', letterSpacing: '0.1em' }}>CAMERA SIGNAL OFFLINE</p>
                    <button onClick={start} style={{ background: 'var(--blue)', color: 'white', border: 'none', padding: '12px 32px', borderRadius: '12px', fontWeight: 800, cursor: 'pointer', marginTop: '16px' }}>INITIALIZE LINK</button>
                 </div>
              )}

              {active && (
                 <div style={{ position: 'absolute', top: '40px', right: '40px', display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,51,102,0.2)', padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--pink)' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--pink)', animation: 'pulse 1s infinite' }} />
                    <span style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--pink)', letterSpacing: '0.1em' }}>LIVE FEED</span>
                 </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '16px', marginTop: '24px' }}>
              {active && (
                <>
                  <button onClick={snap} style={{ background: 'var(--green)', color: 'white', border: 'none', padding: '14px 40px', borderRadius: '12px', fontWeight: 800, cursor: 'pointer', flex: 1, boxShadow: '0 10px 20px rgba(6, 214, 160, 0.2)' }}>📸 CAPTURE FRAME</button>
                  <button onClick={stop} style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--pink)', border: '1px solid rgba(255,51,102,0.2)', padding: '14px 24px', borderRadius: '12px', fontWeight: 800, cursor: 'pointer' }}>STOP</button>
                </>
              )}
            </div>
            {error && <div style={{ marginTop: '16px', color: 'var(--pink)', fontSize: '0.85rem', fontWeight: 700, padding: '12px', background: 'rgba(255,51,102,0.05)', borderRadius: '12px', border: '1px solid rgba(255,51,102,0.2)' }}>⚠️ {error.toUpperCase()}</div>}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
              <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)', fontSize: '0.9rem', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '20px' }}>FORENSIC FILTERS</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
                {FILTERS.map(f => (
                  <button 
                    key={f.key} 
                    onClick={() => setFilter(f.key)} 
                    style={{ 
                      padding: '12px 16px', border: '1px solid ' + (filter === f.key ? 'var(--blue)' : 'transparent'), 
                      borderRadius: '12px', cursor: 'pointer', textAlign: 'left', fontWeight: 700, transition: 'all 0.2s', 
                      background: filter === f.key ? 'rgba(67,97,238,0.1)' : 'rgba(255,255,255,0.02)', 
                      color: filter === f.key ? 'var(--blue)' : 'var(--text-dim)',
                      fontSize: '0.85rem'
                    }}
                  >
                    {f.label.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {snapshots.length > 0 && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', marginTop: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
               <div>
                  <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)', fontSize: '1.2rem' }}>Captured Sequences</h3>
                  <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-dim)' }}>Snapshot history for forensic analysis and comparison.</p>
               </div>
               <button onClick={() => setSnapshots([])} style={{ background: 'rgba(255,51,102,0.1)', color: 'var(--pink)', border: 'none', padding: '8px 20px', borderRadius: '10px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 800 }}>PURGE ALL</button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '20px' }}>
              {snapshots.map((s, i) => (
                <div key={i} style={{ borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border)', position: 'relative', background: 'rgba(0,0,0,0.2)' }}>
                  <img src={s.url} alt={`snap ${i}`} style={{ width: '100%', display: 'block' }} />
                  <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(0,0,0,0.7)', padding: '10px 16px', fontSize: '0.7rem', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 800 }}>{s.filter.toUpperCase()}</span>
                    <a href={s.url} download={`webcam_snap_${i}.jpg`} style={{ background: 'var(--green)', color: 'white', width: '24px', height: '24px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', textDecoration: 'none', fontSize: '10px' }}>⬇</a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  )
}
