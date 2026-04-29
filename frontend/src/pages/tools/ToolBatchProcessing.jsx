import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolBatchProcessing() {
  const navigate = useNavigate()
  const [files, setFiles] = useState([])
  const [results, setResults] = useState([])
  const [operation, setOperation] = useState('grayscale')
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const fileInputRef = useRef(null)

  const OPS = [
    { key: 'grayscale', label: '⬛ Negative/Grayscale', ep: 'module1/linear_operations', params: { op: 'negative', value: 0 } },
    { key: 'brightness', label: '☀️ Brighten (+50)', ep: 'module1/linear_operations', params: { op: 'brightness', value: 50 } },
    { key: 'edges', label: '✏️ Edge Detection', ep: 'module5/edge_detection', params: { detector: 'Canny', t1: 50, t2: 150, ksize: 3, sigma: 1.5, aperture: 3 } },
    { key: 'blur', label: '🌫️ Gaussian Blur', ep: 'module2/smoothing', params: { ftype: 'gaussian', ksize: 9, sigma: 2, d: 9, noise: false } },
    { key: 'sharpen', label: '🔪 Sharpen', ep: 'module2/sharpening', params: { stype: 'unsharp', weight: 1, amount: 1.5, sigma: 2, ksize: 3, boost: 2 } },
    { key: 'equalize', label: '📊 Hist. Equalize', ep: 'module2/histogram', params: { method: 'global', clip: 2, tile: 8 } },
  ]

  const handleFiles = (e) => {
    setFiles(Array.from(e.target.files || []))
    setResults([])
  }

  const runBatch = async () => {
    if (!files.length) return
    setProcessing(true); setProgress(0); setResults([])
    const op = OPS.find(o => o.key === operation)
    const out = []
    for (let i = 0; i < files.length; i++) {
      try {
        const fd = new FormData()
        fd.append('file', files[i])
        Object.entries(op.params).forEach(([k, v]) => fd.append(k, v))
        const res = await axios.post(`/api/${op.ep}`, fd, { responseType: 'blob' })
        out.push({ name: files[i].name, original: URL.createObjectURL(files[i]), result: URL.createObjectURL(res.data), ok: true })
      } catch { out.push({ name: files[i].name, original: URL.createObjectURL(files[i]), result: null, ok: false }) }
      setProgress(Math.round(((i + 1) / files.length) * 100))
    }
    setResults(out); setProcessing(false)
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }
  const sel = { background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '9px 12px', borderRadius: '8px', fontFamily: 'var(--font-body)' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>⚙️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Batch Processing</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '20px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)' }}>Batch Configuration</h3>
          <input type="file" ref={fileInputRef} onChange={handleFiles} accept="image/*" multiple style={{ display: 'none' }} />
          
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr auto', gap: '24px', alignItems: 'end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 600 }}>SOURCE FILES</label>
              <button onClick={() => fileInputRef.current.click()} style={{ width: '100%', background: 'var(--blue)', color: 'white', padding: '10px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
                {files.length > 0 ? `Selected ${files.length} Images` : 'Choose Multiple Images'}
              </button>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 600 }}>TRANSFORMATION</label>
              <select value={operation} onChange={e => setOperation(e.target.value)} style={{ ...sel, width: '100%' }}>{OPS.map(o => <option key={o.key} value={o.key}>{o.label}</option>)}</select>
            </div>
            <button onClick={runBatch} disabled={!files.length || processing} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 32px', borderRadius: '10px', fontWeight: 700, cursor: 'pointer', height: '42px', minWidth: '160px' }}>
              {processing ? `⚙️ ${progress}%` : '▶️ START BATCH'}
            </button>
          </div>

          {processing && (
            <div style={{ marginTop: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 700 }}>
                <span>PROCESSING QUEUE</span>
                <span>{progress}%</span>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '6px', height: '10px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${progress}%`, background: 'var(--blue)', borderRadius: '6px', transition: 'width 0.3s ease', boxShadow: '0 0 15px var(--blue)' }} />
              </div>
            </div>
          )}
        </div>

        {results.length > 0 && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
               <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)' }}>Processed Output</h3>
               <span style={{ background: 'var(--green)', color: 'white', padding: '4px 12px', borderRadius: '20px', fontWeight: 800, fontSize: '0.85rem' }}>
                  {results.filter(r => r.ok).length} / {results.length} COMPLETED
               </span>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
              {results.map((r, i) => (
                <div key={i} style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', borderRadius: '16px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', height: '120px' }}>
                    <div style={{ position: 'relative' }}>
                       <img src={r.original} alt="orig" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                       <div style={{ position: 'absolute', bottom: 0, left: 0, background: 'rgba(0,0,0,0.6)', color: 'white', fontSize: '10px', padding: '2px 6px' }}>BEFORE</div>
                    </div>
                    <div style={{ position: 'relative', background: 'rgba(255,255,255,0.02)' }}>
                       {r.result ? (
                         <>
                           <img src={r.result} alt="proc" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                           <div style={{ position: 'absolute', bottom: 0, right: 0, background: 'var(--blue)', color: 'white', fontSize: '10px', padding: '2px 6px' }}>AFTER</div>
                         </>
                       ) : (
                         <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--pink)', fontSize: '0.7rem' }}>FAILED</div>
                       )}
                    </div>
                  </div>
                  <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.name}</div>
                    {r.result && (
                      <a href={r.result} download={`processed_${r.name}`} style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(6,214,160,0.1)', color: 'var(--green)', display: 'flex', alignItems: 'center', justifyContent: 'center', textDecoration: 'none', border: '1px solid rgba(6,214,160,0.2)' }}>
                        ⬇️
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
