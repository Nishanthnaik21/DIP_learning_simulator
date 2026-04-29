import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ToolImageStitching() {
  const navigate = useNavigate()
  const [file1, setFile1] = useState(null)
  const [file2, setFile2] = useState(null)
  const [preview1, setPreview1] = useState(null)
  const [preview2, setPreview2] = useState(null)
  const [resultImg, setResultImg] = useState(null)
  const [loading, setLoading] = useState(false)
  const [overlap, setOverlap] = useState(0)
  const file1Ref = useRef(null)
  const file2Ref = useRef(null)
  const canvasRef = useRef(null)

  const handleFile1 = (e) => {
    if (e.target.files?.[0]) {
      setFile1(e.target.files[0])
      setPreview1(URL.createObjectURL(e.target.files[0]))
      setResultImg(null)
    }
  }

  const handleFile2 = (e) => {
    if (e.target.files?.[0]) {
      setFile2(e.target.files[0])
      setPreview2(URL.createObjectURL(e.target.files[0]))
      setResultImg(null)
    }
  }

  const runStitch = () => {
    if (!preview1 || !preview2) return
    setLoading(true)
    
    const img1 = new Image()
    const img2 = new Image()
    let loaded = 0
    
    const onLoaded = () => {
      loaded++
      if (loaded === 2) {
        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')
        
        // Target height will be the max of the two
        const h = Math.max(img1.height, img2.height)
        // Calculate overlap offset (0 to 100 pixels)
        const offset = Math.round(overlap)
        const w = img1.width + img2.width - offset
        
        canvas.width = w
        canvas.height = h
        
        // Draw first image
        ctx.drawImage(img1, 0, 0)
        
        // Draw second image with overlap
        // Simple alpha blending at the edge could be added for better "stitching"
        ctx.globalAlpha = 0.8 // slight transparency for overlap visualization
        ctx.drawImage(img2, img1.width - offset, 0)
        ctx.globalAlpha = 1.0
        
        setResultImg(canvas.toDataURL('image/jpeg', 0.95))
        setLoading(false)
      }
    }
    
    img1.onload = onLoaded
    img2.onload = onLoaded
    img1.src = preview1
    img2.src = preview2
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🧵</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Image Stitching / Panorama</h1>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', textAlign: 'center' }}>
            <h4 style={{ marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em', fontWeight: 800 }}>LEFT PERSPECTIVE</h4>
            <input type="file" ref={file1Ref} onChange={handleFile1} accept="image/*" style={{ display: 'none' }} />
            <button onClick={() => file1Ref.current.click()} style={{ width: '100%', background: 'rgba(255,255,255,0.03)', color: 'var(--text)', padding: '20px', border: '2px dashed var(--border)', borderRadius: '16px', cursor: 'pointer', marginBottom: '20px', fontWeight: 700 }}>
              {file1 ? '🔄 CHANGE LEFT' : '📁 UPLOAD LEFT'}
            </button>
            {preview1 && <img src={preview1} alt="Left" style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} />}
          </div>

          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', textAlign: 'center' }}>
            <h4 style={{ marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em', fontWeight: 800 }}>RIGHT PERSPECTIVE</h4>
            <input type="file" ref={file2Ref} onChange={handleFile2} accept="image/*" style={{ display: 'none' }} />
            <button onClick={() => file2Ref.current.click()} style={{ width: '100%', background: 'rgba(255,255,255,0.03)', color: 'var(--text)', padding: '20px', border: '2px dashed var(--border)', borderRadius: '16px', cursor: 'pointer', marginBottom: '20px', fontWeight: 700 }}>
              {file2 ? '🔄 CHANGE RIGHT' : '📁 UPLOAD RIGHT'}
            </button>
            {preview2 && <img src={preview2} alt="Right" style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} />}
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', marginBottom: '40px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '40px', alignItems: 'end' }}>
            <div style={{ width: '100%' }}>
               <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <label style={{ fontSize: '0.9rem', color: 'var(--text-dim)', fontWeight: 700 }}>OVERLAP BLENDING (PIXELS)</label>
                  <span style={{ color: 'var(--blue)', fontWeight: 800, fontSize: '1.1rem' }}>{overlap} PX</span>
               </div>
               <input 
                 type="range" min="0" max="400" value={overlap} 
                 onChange={(e) => setOverlap(parseInt(e.target.value))}
               />
            </div>

            <button 
              onClick={runStitch} 
              disabled={!file1 || !file2 || loading}
              style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '14px 48px', borderRadius: '12px', fontWeight: 800, cursor: 'pointer', opacity: (!file1 || !file2 || loading) ? 0.5 : 1, fontSize: '1.1rem', boxShadow: '0 10px 20px rgba(114, 9, 183, 0.3)' }}
            >
              {loading ? '⏳ STITCHING...' : '🧵 GENERATE PANORAMA'}
            </button>
          </div>

          {resultImg && (
            <div style={{ marginTop: '48px', textAlign: 'center' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', marginBottom: '24px' }}>Stitched Result</h3>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '20px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                 <img src={resultImg} alt="Stitched Panorama" style={{ width: '100%', borderRadius: '12px' }} />
              </div>
              <a href={resultImg} download="panorama.jpg" style={{ background: 'rgba(6,214,160,0.1)', color: 'var(--green)', padding: '12px 32px', borderRadius: '24px', textDecoration: 'none', fontWeight: 800, border: '1px solid rgba(6,214,160,0.2)', fontSize: '0.9rem' }}>
                ⬇️ EXPORT HIGH-RES PANORAMA
              </a>
            </div>
          )}
        </div>
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  )
}
