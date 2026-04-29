import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const CHALLENGES = [
  { id: 1, title: '🧩 Noise Removal', desc: 'Remove salt-and-pepper noise from this image. Target PSNR > 30 dB.', target: 'Apply the best filter to remove noise effectively.', hint: 'Median filter works best for salt-and-pepper noise.', ep: 'module2/smoothing', defaultParams: { ftype: 'gaussian', ksize: 5, sigma: 1.5, d: 9, noise: true, noise_prob: 0.05 } },
  { id: 2, title: '🔍 Edge Detection', desc: 'Detect only the strongest edges. Use Canny with optimal thresholds.', target: 'Find the right threshold values for clean edge maps.', hint: 'Try t1=50, t2=150 for a good starting point.', ep: 'module5/edge_detection', defaultParams: { detector: 'Canny', t1: 50, t2: 150, ksize: 3, sigma: 1.5, aperture: 3 } },
  { id: 3, title: '📊 Contrast Enhancement', desc: 'Enhance the contrast of a dark image using histogram techniques.', target: 'Apply equalization to reveal hidden details.', hint: 'CLAHE works better than global equalization for many images.', ep: 'module2/histogram', defaultParams: { method: 'clahe', clip: 2, tile: 8 } },
]

export default function ToolParameterChallenge() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [challenge, setChallenge] = useState(CHALLENGES[0])
  const [params, setParams] = useState({ ...CHALLENGES[0].defaultParams })
  const [resultUrl, setResultUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const [score, setScore] = useState(null)
  const fileInputRef = useRef(null)

  const selectChallenge = (c) => { setChallenge(c); setParams({ ...c.defaultParams }); setResultUrl(null); setScore(null); setShowHint(false) }

  const handleFile = (e) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setPreviewUrl(URL.createObjectURL(e.target.files[0])); setResultUrl(null); setScore(null) } }

  const run = async () => {
    if (!file) return
    setLoading(true)
    try {
      const fd = new FormData(); fd.append('file', file)
      Object.entries(params).forEach(([k, v]) => fd.append(k, v))
      const res = await axios.post(`/api/${challenge.ep}`, fd, { responseType: 'blob' })
      setResultUrl(URL.createObjectURL(res.data))
      // Compute a "score" based on param similarity to ideal
      const ideal = challenge.defaultParams
      let s = 100
      if (challenge.id === 2) { s = Math.max(0, 100 - Math.abs(params.t1 - 50) / 2 - Math.abs(params.t2 - 150) / 3) }
      else if (challenge.id === 1) { s = params.ftype === 'median' ? 95 : params.ftype === 'gaussian' ? 75 : 60 }
      else { s = params.method === 'clahe' ? 90 : 70 }
      setScore(Math.round(s))
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  const inp = { background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: '6px', fontFamily: 'var(--font-body)', width: '80px' }
  const sel = { background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: '6px', fontFamily: 'var(--font-body)' }
  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🎯</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Parameter Challenge</h1>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
          {CHALLENGES.map(c => (
            <button 
              key={c.id} 
              onClick={() => selectChallenge(c)} 
              style={{ 
                padding: '12px 24px', border: 'none', borderRadius: '14px', cursor: 'pointer', fontWeight: 800, transition: 'all 0.3s', 
                background: challenge.id === c.id ? 'var(--blue)' : 'rgba(255,255,255,0.03)', 
                color: challenge.id === c.id ? 'white' : 'var(--text-dim)',
                boxShadow: challenge.id === c.id ? '0 10px 20px rgba(67, 97, 238, 0.3)' : 'none',
                transform: challenge.id === c.id ? 'scale(1.05)' : 'none'
              }}
            >
              {c.title.toUpperCase()}
            </button>
          ))}
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', marginBottom: '24px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: '-20px', right: '-20px', fontSize: '8rem', opacity: 0.05 }}>🎯</div>
          <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)', fontSize: '1.5rem', marginBottom: '12px' }}>{challenge.title}</h3>
          <p style={{ color: 'var(--text-dim)', fontSize: '1rem', lineHeight: 1.6, maxWidth: '80%', marginBottom: '20px' }}>{challenge.desc}</p>
          <div style={{ display: 'inline-block', padding: '8px 16px', background: 'rgba(76, 201, 240, 0.1)', color: 'var(--cyan)', borderRadius: '10px', fontSize: '0.85rem', fontWeight: 800, letterSpacing: '0.05em' }}>
             OBJECTIVE: {challenge.target.toUpperCase()}
          </div>
          
          <div style={{ marginTop: '24px' }}>
            <button onClick={() => setShowHint(!showHint)} style={{ background: 'transparent', border: '1px solid rgba(255,204,0,0.3)', color: '#ffcc00', padding: '6px 16px', borderRadius: '10px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              {showHint ? '🙈 CONCEAL CLUE' : '💡 REVEAL INTEL'}
            </button>
            {showHint && (
               <div style={{ marginTop: '12px', color: '#ffcc00', fontSize: '0.9rem', background: 'rgba(255,204,0,0.05)', padding: '16px', borderRadius: '16px', border: '1px dashed rgba(255,204,0,0.3)', maxWidth: '500px', lineHeight: 1.5 }}>
                 <strong>ANALYSIS HINT:</strong> {challenge.hint}
               </div>
            )}
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', marginBottom: '24px' }}>
          <input type="file" ref={fileInputRef} onChange={handleFile} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '32px' }}>
            <button onClick={() => fileInputRef.current.click()} style={{ background: 'var(--blue)', color: 'white', padding: '12px 24px', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: 800 }}>
              📸 UPLOAD TEST SUBJECT
            </button>
            {file && <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{file.name.toUpperCase()}</span>}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
             <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 800, color: 'var(--text-dim)', letterSpacing: '0.05em' }}>PARAMETER CONFIGURATION</h4>
             {score !== null && (
               <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-dim)' }}>PRECISION SCORE:</span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 900, color: score >= 85 ? 'var(--green)' : score >= 65 ? '#ffcc00' : 'var(--pink)' }}>{score}%</span>
               </div>
             )}
          </div>

          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '32px', alignItems: 'end', background: 'rgba(0,0,0,0.2)', padding: '20px', borderRadius: '16px', border: '1px solid var(--border)' }}>
            {challenge.id === 1 && (
              <>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px' }}>FILTER ALGORITHM</label>
                  <select value={params.ftype || 'gaussian'} onChange={e => setParams(p => ({ ...p, ftype: e.target.value }))} style={{ width: '100%', background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontWeight: 600 }}>
                    <option value="average">Box Filter</option>
                    <option value="gaussian">Gaussian</option>
                    <option value="median">Median (De-noise)</option>
                    <option value="bilateral">Bilateral</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px' }}>KERNEL SIZE</label>
                  <input type="number" step="2" min="3" max="21" value={params.ksize || 5} onChange={e => setParams(p => ({ ...p, ksize: +e.target.value }))} style={{ width: '100%', background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontWeight: 600 }} />
                </div>
              </>
            )}
            {challenge.id === 2 && (
              <>
                <div style={{ flex: 1 }}>
                   <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px' }}>LOW THRESHOLD (T1)</label>
                   <input type="number" min="0" max="200" value={params.t1 || 50} onChange={e => setParams(p => ({ ...p, t1: +e.target.value }))} style={{ width: '100%', background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontWeight: 600 }} />
                </div>
                <div style={{ flex: 1 }}>
                   <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px' }}>HIGH THRESHOLD (T2)</label>
                   <input type="number" min="0" max="400" value={params.t2 || 150} onChange={e => setParams(p => ({ ...p, t2: +e.target.value }))} style={{ width: '100%', background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontWeight: 600 }} />
                </div>
              </>
            )}
            {challenge.id === 3 && (
              <>
                <div style={{ flex: 1 }}>
                   <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px' }}>ENHANCEMENT TYPE</label>
                   <select value={params.method || 'global'} onChange={e => setParams(p => ({ ...p, method: e.target.value }))} style={{ width: '100%', background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontWeight: 600 }}>
                      <option value="global">Global Equalization</option>
                      <option value="clahe">CLAHE (Adaptive)</option>
                   </select>
                </div>
                <div style={{ flex: 1 }}>
                   <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px' }}>CONTRAST CLIP LIMIT</label>
                   <input type="number" step="0.5" value={params.clip || 2} onChange={e => setParams(p => ({ ...p, clip: +e.target.value }))} style={{ width: '100%', background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontWeight: 600 }} />
                </div>
              </>
            )}
            <button onClick={run} disabled={!file || loading} style={{ background: 'var(--green)', color: 'white', border: 'none', padding: '10px 40px', borderRadius: '10px', fontWeight: 800, cursor: 'pointer', height: '41px' }}>
              {loading ? '⏳' : 'EXECUTE'}
            </button>
          </div>

          {previewUrl && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '20px', border: '1px solid var(--border)' }}>
                 <h4 style={{ textAlign: 'center', marginTop: 0, fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '16px' }}>INPUT SIGNAL</h4>
                 <img src={previewUrl} style={{ width: '100%', borderRadius: '12px' }} alt="Input" />
              </div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '20px', border: '1px solid var(--border)', minHeight: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                 <h4 style={{ textAlign: 'center', marginTop: 0, fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '16px' }}>OUTPUT RESULT</h4>
                 {resultUrl ? (
                    <img src={resultUrl} style={{ width: '100%', borderRadius: '12px' }} alt="Output" />
                 ) : (
                    <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '40px' }}>
                       <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⚙️</div>
                       Awaiting parameter execution
                    </div>
                 )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
