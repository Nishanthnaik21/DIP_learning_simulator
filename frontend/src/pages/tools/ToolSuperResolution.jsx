import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolSuperResolution() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [resultUrl, setResultUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [scale, setScale] = useState(2)
  const [info, setInfo] = useState(null)
  const fileInputRef = useRef(null)
  const canvasRef = useRef(null)

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      const f = e.target.files[0]
      setFile(f); setPreviewUrl(URL.createObjectURL(f)); setResultUrl(null); setInfo(null)
    }
  }

  const run = () => {
    if (!previewUrl) return
    setLoading(true)
    const img = new Image()
    img.onload = () => {
      const w = img.width, h = img.height
      const canvas = canvasRef.current
      canvas.width = w * scale; canvas.height = h * scale
      const ctx = canvas.getContext('2d')
      ctx.imageSmoothingEnabled = true
      ctx.imageSmoothingQuality = 'high'
      ctx.drawImage(img, 0, 0, w * scale, h * scale)
      // Apply light unsharp-mask-like enhancement via pixel manipulation
      const id = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const d = id.data
      // Simple sharpen kernel applied in JS
      const sw = canvas.width, sh = canvas.height
      const tmp = new Uint8ClampedArray(d)
      const k = [-0,-1,0,-1,5,-1,0,-1,0]
      for (let y = 1; y < sh - 1; y++) {
        for (let x = 1; x < sw - 1; x++) {
          for (let c = 0; c < 3; c++) {
            let val = 0
            for (let ky = -1; ky <= 1; ky++)
              for (let kx = -1; kx <= 1; kx++)
                val += tmp[((y + ky) * sw + (x + kx)) * 4 + c] * k[(ky + 1) * 3 + (kx + 1)]
            d[(y * sw + x) * 4 + c] = Math.max(0, Math.min(255, val))
          }
        }
      }
      ctx.putImageData(id, 0, 0)
      setResultUrl(canvas.toDataURL('image/jpeg', 0.95))
      setInfo({ orig: `${w}×${h}`, upsc: `${w * scale}×${h * scale}` })
      setLoading(false)
    }
    img.src = previewUrl
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🔭</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Super Resolution</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontFamily: 'var(--font-heading)' }}>Configure Upscaling</h3>
          <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '20px', alignItems: 'end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '8px' }}>SOURCE IMAGE</label>
              <button onClick={() => fileInputRef.current.click()} style={{ width: '100%', background: 'var(--blue)', color: 'white', padding: '10px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
                {file ? 'Change Image' : 'Select Image'}
              </button>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '8px' }}>UPSCALE FACTOR</label>
              <div style={{ display: 'flex', gap: '8px', background: 'rgba(0,0,0,0.2)', padding: '4px', borderRadius: '10px' }}>
                {[2, 3, 4].map(s => (
                  <button key={s} onClick={() => setScale(s)} style={{ flex: 1, padding: '8px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, background: scale === s ? 'var(--purple)' : 'transparent', color: scale === s ? 'white' : 'var(--text-dim)', transition: 'all 0.2s' }}>{s}×</button>
                ))}
              </div>
            </div>
            <button onClick={run} disabled={!file || loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', fontWeight: 700, cursor: 'pointer', height: '42px' }}>
              {loading ? '⏳ PROCESSING' : '🔭 UPSCALE'}
            </button>
          </div>
        </div>

        {info && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
            {[
              { label: 'Original Res', val: info.orig, color: 'var(--blue)' },
              { label: 'Target Res', val: info.upsc, color: 'var(--green)' },
              { label: 'Magnification', val: `${scale}×`, color: 'var(--pink)' }
            ].map((stat) => (
              <div key={stat.label} style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '16px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>{stat.label}</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: stat.color }}>{stat.val}</div>
              </div>
            ))}
          </div>
        )}

        {previewUrl && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            <div>
              <h4 style={{ marginBottom: '12px', fontSize: '0.9rem', color: 'var(--text-dim)' }}>INPUT IMAGE</h4>
              <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '12px', borderRadius: '16px' }}>
                <img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '10px' }} />
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-dim)' }}>ENHANCED RESULT ({scale}×)</h4>
                {resultUrl && (
                  <a href={resultUrl} download="upscaled.jpg" style={{ color: 'var(--green)', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', borderBottom: '1px solid var(--green)' }}>
                    DOWNLOAD RESULT
                  </a>
                )}
              </div>
              <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '12px', borderRadius: '16px' }}>
                {resultUrl
                  ? <img src={resultUrl} alt="Upscaled" style={{ width: '100%', borderRadius: '10px' }} />
                  : <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', border: '2px dashed var(--border)', borderRadius: '10px' }}>
                      Click Upscale to process
                    </div>}
              </div>
            </div>
          </div>
        )}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  )
}
