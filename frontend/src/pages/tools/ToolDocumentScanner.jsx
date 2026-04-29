import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolDocumentScanner() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [resultUrl, setResultUrl] = useState(null)
  const [step, setStep] = useState('edges')
  const [loading, setLoading] = useState(false)
  const fileRef = useRef(null)
  const canvasRef = useRef(null)

  const handleFile = (e) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setPreviewUrl(URL.createObjectURL(e.target.files[0])); setResultUrl(null) } }

  const process = async (s) => {
    if (!file) return
    setStep(s); setLoading(true)
    try {
      const fd = new FormData(); fd.append('file', file)
      let res
      if (s === 'edges') {
        fd.append('detector', 'Canny'); fd.append('t1', 50); fd.append('t2', 150); fd.append('ksize', 3); fd.append('sigma', 1.5); fd.append('aperture', 3)
        res = await axios.post('/api/module5/edge_detection', fd, { responseType: 'blob' })
      } else if (s === 'threshold') {
        fd.append('method', 'Adaptive Gaussian'); fd.append('T', 127); fd.append('block', 11); fd.append('C', 2); fd.append('classes', 3)
        res = await axios.post('/api/module5/thresholding', fd, { responseType: 'blob' })
      } else if (s === 'sharpen') {
        fd.append('stype', 'unsharp'); fd.append('weight', 1); fd.append('amount', 2); fd.append('sigma', 1); fd.append('ksize', 3); fd.append('boost', 2)
        res = await axios.post('/api/module2/sharpening', fd, { responseType: 'blob' })
      } else if (s === 'grayscale') {
        fd.append('method', 'Otsu'); fd.append('T', 0); fd.append('block', 11); fd.append('C', 2); fd.append('classes', 2)
        res = await axios.post('/api/module5/thresholding', fd, { responseType: 'blob' })
      }
      setResultUrl(URL.createObjectURL(res.data))
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  const STEPS = [
    { key: 'grayscale', label: '⬛ B&W (Otsu)', desc: 'Binarize using Otsu thresholding' },
    { key: 'edges', label: '✏️ Edge Detect', desc: 'Find document boundary edges' },
    { key: 'threshold', label: '🎯 Adaptive Thresh', desc: 'Remove shadows with adaptive threshold' },
    { key: 'sharpen', label: '🔪 Sharpen Text', desc: 'Enhance text sharpness' },
  ]

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>📄</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Document Scanner</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)' }}>Image Acquisition</h3>
          <input type="file" ref={fileRef} onChange={handleFile} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <button onClick={() => fileRef.current.click()} style={{ background: 'var(--blue)', color: 'white', padding: '12px 24px', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: 700 }}>
              📸 UPLOAD SOURCE PHOTO
            </button>
            {file && <span style={{ color: 'var(--cyan)', fontWeight: 700, fontSize: '0.85rem' }}>{file.name.toUpperCase()}</span>}
          </div>
        </div>

        {previewUrl && (
          <>
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                 <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)' }}>Processing Pipeline</h3>
                 {loading && <span style={{ color: 'var(--cyan)', fontSize: '0.8rem', fontWeight: 800 }}>⚡ SIGNAL PROCESSING...</span>}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                {STEPS.map(s => (
                  <button 
                    key={s.key} 
                    onClick={() => process(s.key)} 
                    disabled={loading} 
                    style={{ 
                      padding: '16px', border: '1px solid ' + (step === s.key && resultUrl ? 'var(--blue)' : 'var(--border)'), 
                      borderRadius: '16px', cursor: 'pointer', transition: 'all 0.2s', 
                      background: step === s.key && resultUrl ? 'rgba(67,97,238,0.1)' : 'rgba(255,255,255,0.02)', 
                      textAlign: 'left', position: 'relative'
                    }}
                  >
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: step === s.key && resultUrl ? 'var(--blue)' : 'var(--text)', marginBottom: '4px' }}>{s.label.toUpperCase()}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.4 }}>{s.desc}</div>
                    {step === s.key && resultUrl && <div style={{ position: 'absolute', top: '12px', right: '12px', fontSize: '0.8rem' }}>💎</div>}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '24px' }}>
                <h4 style={{ textAlign: 'center', marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>SOURCE CAPTURE</h4>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '16px' }}>
                   <img src={previewUrl} style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} alt="Original" />
                </div>
              </div>
              <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '24px' }}>
                <h4 style={{ textAlign: 'center', marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>PROCESSED SCAN</h4>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '16px', minHeight: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  {resultUrl ? (
                    <>
                      <img src={resultUrl} style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} alt="Processed" />
                      <div style={{ textAlign: 'center', marginTop: '16px' }}>
                        <a href={resultUrl} download="scanned.jpg" style={{ background: 'rgba(6,214,160,0.1)', color: 'var(--green)', padding: '8px 20px', borderRadius: '20px', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 800, border: '1px solid rgba(6,214,160,0.2)' }}>
                          ⬇️ EXPORT SCANNED DOCUMENT
                        </a>
                      </div>
                    </>
                  ) : (
                    <div style={{ textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
                       <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>⚙️</div>
                       Select a processing algorithm<br/>to generate scan
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
