import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolComparison() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState(false)
  const [sliderX, setSliderX] = useState(50)
  const [leftOp, setLeftOp] = useState('original')
  const [rightOp, setRightOp] = useState('edges')
  const fileInputRef = useRef(null)

  const OPS = [
    { key: 'original', label: 'Original', endpoint: null },
    { key: 'grayscale', label: 'Grayscale', endpoint: 'module1/linear_operations', params: { op: 'negative', value: 0 } },
    { key: 'edges', label: 'Edge Detection', endpoint: 'module5/edge_detection', params: { detector: 'Canny', t1: 50, t2: 150, ksize: 3, sigma: 1.5, aperture: 3 } },
    { key: 'blur', label: 'Gaussian Blur', endpoint: 'module2/smoothing', params: { ftype: 'gaussian', ksize: 11, sigma: 3, d: 9, noise: false } },
    { key: 'sharp', label: 'Sharpened', endpoint: 'module2/sharpening', params: { stype: 'unsharp', weight: 1, amount: 2, sigma: 2, ksize: 3, boost: 2 } },
    { key: 'eq', label: 'Hist. Equalized', endpoint: 'module2/histogram', params: { method: 'global', clip: 2, tile: 8 } },
  ]

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
      setPreviewUrl(URL.createObjectURL(e.target.files[0]))
      setResults({})
    }
  }

  const fetchOp = async (opKey) => {
    if (!file) return null
    if (opKey === 'original') return previewUrl
    if (results[opKey]) return results[opKey]
    const op = OPS.find(o => o.key === opKey)
    if (!op?.endpoint) return previewUrl
    const fd = new FormData()
    fd.append('file', file)
    Object.entries(op.params || {}).forEach(([k, v]) => fd.append(k, v))
    const res = await axios.post(`/api/${op.endpoint}`, fd, { responseType: 'blob' })
    return URL.createObjectURL(res.data)
  }

  const runComparison = async () => {
    if (!file) return
    setLoading(true)
    try {
      const [lUrl, rUrl] = await Promise.all([fetchOp(leftOp), fetchOp(rightOp)])
      setResults(prev => ({ ...prev, [leftOp]: lUrl, [rightOp]: rUrl }))
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }
  const sel = { background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '8px 12px', borderRadius: '8px', fontFamily: 'var(--font-body)' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>⚖️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Image Comparison</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontFamily: 'var(--font-heading)' }}>Configure Comparison</h3>
          <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '16px', alignItems: 'end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '6px' }}>SOURCE IMAGE</label>
              <button onClick={() => fileInputRef.current.click()} style={{ width: '100%', background: 'var(--blue)', color: 'white', padding: '10px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>
                {file ? 'Change Image' : 'Select Image'}
              </button>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '6px' }}>LEFT SIDE</label>
              <select value={leftOp} onChange={e => setLeftOp(e.target.value)} style={{ ...sel, width: '100%' }}>{OPS.map(o => <option key={o.key} value={o.key}>{o.label}</option>)}</select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '6px' }}>RIGHT SIDE</label>
              <select value={rightOp} onChange={e => setRightOp(e.target.value)} style={{ ...sel, width: '100%' }}>{OPS.map(o => <option key={o.key} value={o.key}>{o.label}</option>)}</select>
            </div>
            <button onClick={runComparison} disabled={!file || loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', height: '42px' }}>
              {loading ? '⏳ PROCESSING' : '⚖️ COMPARE'}
            </button>
          </div>
        </div>

        {results[leftOp] && results[rightOp] && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '20px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', alignItems: 'center' }}>
               <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)' }}>Interactive Split-View</h3>
               <span style={{ background: 'var(--blue)', color: 'white', padding: '4px 12px', borderRadius: '20px', fontWeight: 800, fontSize: '0.9rem' }}>OFFSET: {sliderX}%</span>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
               <input type="range" min="5" max="95" value={sliderX} onChange={e => setSliderX(+e.target.value)} />
            </div>

            <div style={{ position: 'relative', borderRadius: '16px', overflow: 'hidden', userSelect: 'none', border: '1px solid var(--border)', boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }}>
              <img src={results[rightOp]} alt="Right" style={{ width: '100%', display: 'block' }} />
              <div style={{ position: 'absolute', top: 0, left: 0, width: `${sliderX}%`, overflow: 'hidden', height: '100%' }}>
                <img src={results[leftOp]} alt="Left" style={{ width: `${10000 / sliderX}%`, display: 'block', maxWidth: 'none' }} />
              </div>
              <div style={{ position: 'absolute', top: 0, left: `${sliderX}%`, width: '4px', height: '100%', background: 'white', transform: 'translateX(-50%)', boxShadow: '0 0 15px rgba(0,0,0,0.5)', zIndex: 10 }}>
                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: '36px', height: '36px', borderRadius: '50%', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--blue)', fontSize: '1rem', fontWeight: 900, boxShadow: '0 4px 10px rgba(0,0,0,0.3)' }}>↔</div>
              </div>
              <div style={{ position: 'absolute', top: '16px', left: '16px', background: 'rgba(13,17,23,0.75)', backdropFilter: 'blur(8px)', color: 'white', padding: '6px 14px', borderRadius: '10px', fontSize: '0.8rem', fontWeight: 700, border: '1px solid rgba(255,255,255,0.1)' }}>{OPS.find(o => o.key === leftOp)?.label}</div>
              <div style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(13,17,23,0.75)', backdropFilter: 'blur(8px)', color: 'white', padding: '6px 14px', borderRadius: '10px', fontSize: '0.8rem', fontWeight: 700, border: '1px solid rgba(255,255,255,0.1)' }}>{OPS.find(o => o.key === rightOp)?.label}</div>
            </div>
          </div>
        )}

        {!previewUrl && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '80px 20px', borderRadius: '20px', textAlign: 'center', color: 'var(--text-dim)' }}>
            <div style={{ fontSize: '4rem', marginBottom: '20px' }}>⚖️</div>
            <h2 style={{ fontFamily: 'var(--font-heading)', color: 'var(--text)' }}>Ready to Compare?</h2>
            <p style={{ maxWidth: '500px', margin: '0 auto' }}>Upload an image and select two processing techniques to analyze their differences in real-time with an interactive split-screen slider.</p>
          </div>
        )}
      </div>
    </div>
  )
}
