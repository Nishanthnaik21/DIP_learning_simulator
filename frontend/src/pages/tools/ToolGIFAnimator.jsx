import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ToolGIFAnimator() {
  const navigate = useNavigate()
  const [frames, setFrames] = useState([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentFrame, setCurrentFrame] = useState(0)
  const [fps, setFps] = useState(5)
  const fileInputRef = useRef(null)
  const timerRef = useRef(null)

  const handleFiles = (e) => {
    const files = Array.from(e.target.files || [])
    const newFrames = files.map(f => ({
      url: URL.createObjectURL(f),
      name: f.name,
      id: Math.random().toString(36).substr(2, 9)
    }))
    setFrames(prev => [...prev, ...newFrames])
  }

  useEffect(() => {
    if (isPlaying && frames.length > 0) {
      timerRef.current = setInterval(() => {
        setCurrentFrame(prev => (prev + 1) % frames.length)
      }, 1000 / fps)
    } else {
      clearInterval(timerRef.current)
    }
    return () => clearInterval(timerRef.current)
  }, [isPlaying, frames.length, fps])

  const removeFrame = (id) => {
    setFrames(prev => prev.filter(f => f.id !== id))
    if (currentFrame >= frames.length - 1) setCurrentFrame(0)
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🎞️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>GIF / Frame Animator</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)' }}>Animation Controls</h3>
          <input type="file" ref={fileInputRef} onChange={handleFiles} accept="image/*" multiple style={{ display: 'none' }} />
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr auto auto', gap: '24px', alignItems: 'end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 600 }}>SOURCE FRAMES</label>
              <button onClick={() => fileInputRef.current.click()} style={{ width: '100%', background: 'var(--blue)', color: 'white', padding: '10px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
                {frames.length > 0 ? `Add More (${frames.length})` : 'Choose Frames'}
              </button>
            </div>
            
            <div>
               <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>PLAYBACK SPEED (FPS)</label>
                  <span style={{ color: 'var(--cyan)', fontWeight: 800 }}>{fps} FPS</span>
               </div>
               <input type="range" min="1" max="30" value={fps} onChange={(e) => setFps(parseInt(e.target.value))} />
            </div>

            <button 
              onClick={() => setIsPlaying(!isPlaying)} 
              disabled={frames.length === 0}
              style={{ background: isPlaying ? 'var(--pink)' : 'var(--green)', color: 'white', border: 'none', padding: '10px 32px', borderRadius: '10px', fontWeight: 700, cursor: 'pointer', height: '42px', minWidth: '120px' }}
            >
              {isPlaying ? '⏸ PAUSE' : '▶ PLAY'}
            </button>
            
            {frames.length > 0 && (
              <button onClick={() => {setFrames([]); setIsPlaying(false); setCurrentFrame(0)}} style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-dim)', border: '1px solid var(--border)', padding: '10px 20px', borderRadius: '10px', cursor: 'pointer', height: '42px' }}>
                RESET
              </button>
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
          <div style={{ background: '#000', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '500px', position: 'relative', boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5)' }}>
            {frames.length > 0 ? (
              <div style={{ textAlign: 'center', width: '100%' }}>
                <img src={frames[currentFrame].url} alt="Current Frame" style={{ maxWidth: '100%', maxHeight: '440px', borderRadius: '12px', boxShadow: '0 20px 40px rgba(0,0,0,0.6)' }} />
                <div style={{ marginTop: '24px', color: 'rgba(255,255,255,0.4)', fontSize: '0.75rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em' }}>
                  FRAME {currentFrame + 1} / {frames.length} — {frames[currentFrame].name.toUpperCase()}
                </div>
              </div>
            ) : (
              <div style={{ color: 'rgba(255,255,255,0.15)', textAlign: 'center' }}>
                <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎞️</div>
                <p style={{ fontWeight: 600, letterSpacing: '0.05em' }}>WAITING FOR FRAMES</p>
              </div>
            )}
            
            {frames.length > 0 && (
               <div style={{ position: 'absolute', bottom: '24px', left: '24px', right: '24px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
                  <div style={{ height: '100%', width: `${((currentFrame + 1) / frames.length) * 100}%`, background: 'var(--blue)', borderRadius: '2px', transition: 'width 0.1s linear' }} />
               </div>
            )}
          </div>

          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid var(--border)' }}>
               <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 800, color: 'var(--text-dim)', letterSpacing: '0.05em' }}>TIMELINE</h3>
               <span style={{ fontSize: '0.7rem', background: 'var(--blue)', color: 'white', padding: '2px 8px', borderRadius: '10px' }}>{frames.length} ITEMS</span>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', paddingRight: '8px' }}>
              {frames.map((frame, idx) => (
                <div 
                  key={frame.id} 
                  onClick={() => {setCurrentFrame(idx); setIsPlaying(false)}}
                  style={{ 
                    display: 'flex', alignItems: 'center', gap: '12px', padding: '10px', borderRadius: '14px', cursor: 'pointer', transition: 'all 0.2s',
                    background: currentFrame === idx ? 'rgba(67,97,238,0.15)' : 'rgba(255,255,255,0.02)',
                    border: '1px solid ' + (currentFrame === idx ? 'var(--blue)' : 'transparent'),
                    transform: currentFrame === idx ? 'scale(1.02)' : 'none'
                  }}
                >
                  <img src={frame.url} style={{ width: '48px', height: '48px', objectFit: 'cover', borderRadius: '8px' }} alt={`Frame ${idx}`} />
                  <div style={{ flex: 1, overflow: 'hidden' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, whiteSpace: 'nowrap', textOverflow: 'ellipsis', color: currentFrame === idx ? 'var(--text)' : 'var(--text-dim)' }}>{frame.name}</div>
                    <div style={{ fontSize: '0.7rem', color: currentFrame === idx ? 'var(--blue)' : 'var(--text-dim)', opacity: 0.8 }}>INDEX: {idx + 1}</div>
                  </div>
                  <button onClick={(e) => {e.stopPropagation(); removeFrame(frame.id)}} style={{ background: 'rgba(255,51,102,0.1)', border: 'none', color: 'var(--pink)', cursor: 'pointer', width: '24px', height: '24px', borderRadius: '6px', fontSize: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✕</button>
                </div>
              ))}
              {frames.length === 0 && (
                 <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-dim)', fontSize: '0.85rem', border: '1px dashed var(--border)', borderRadius: '16px' }}>
                    Queue is empty
                 </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
