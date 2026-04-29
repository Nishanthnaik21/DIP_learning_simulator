import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolTemplateMatching() {
  const navigate = useNavigate()
  const [sceneFile, setSceneFile] = useState(null)
  const [sceneUrl, setSceneUrl] = useState(null)
  const [tmplFile, setTmplFile] = useState(null)
  const [tmplUrl, setTmplUrl] = useState(null)
  const [detector, setDetector] = useState('Harris')
  const [resultUrl, setResultUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const sceneRef = useRef(null)
  const tmplRef = useRef(null)

  const handleScene = (e) => { if (e.target.files?.[0]) { setSceneFile(e.target.files[0]); setSceneUrl(URL.createObjectURL(e.target.files[0])); setResultUrl(null) } }
  const handleTmpl = (e) => { if (e.target.files?.[0]) { setTmplFile(e.target.files[0]); setTmplUrl(URL.createObjectURL(e.target.files[0])); setResultUrl(null) } }

  const run = async () => {
    if (!sceneFile) return
    setLoading(true)
    try {
      // Use corner detection on scene as proxy for template matching visualization
      const fd = new FormData()
      fd.append('file', sceneFile)
      fd.append('detector', detector)
      fd.append('block', 2); fd.append('ksize', 3); fd.append('k', 0.04)
      fd.append('thresh', 10); fd.append('max_corners', 100)
      fd.append('quality', 0.01); fd.append('min_dist', 10)
      fd.append('fast_thresh', 10); fd.append('use_nms', true)
      const res = await axios.post('/api/module5/corners', fd, { responseType: 'blob' })
      setResultUrl(URL.createObjectURL(res.data))
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🎯</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Template Matching & Corner Detection</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', marginBottom: '24px', display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'rgba(67,97,238,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem' }}>🎯</div>
          <div style={{ flex: 1 }}>
             <h3 style={{ margin: '0 0 4px', fontFamily: 'var(--font-heading)' }}>Feature Extraction Hub</h3>
             <p style={{ margin: 0, color: 'var(--text-dim)', fontSize: '0.88rem', lineHeight: 1.5 }}>
                Identify unique structural landmarks within a scene. Use Harris, Shi-Tomasi, or FAST detectors to extract feature points essential for template matching and object tracking.
             </p>
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', marginBottom: '24px' }}>
          <input type="file" ref={sceneRef} onChange={handleScene} accept="image/*" style={{ display: 'none' }} />
          <input type="file" ref={tmplRef} onChange={handleTmpl} accept="image/*" style={{ display: 'none' }} />
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr auto', gap: '24px', alignItems: 'end' }}>
            <div>
               <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '10px', fontWeight: 800 }}>SOURCE SCENE</label>
               <button onClick={() => sceneRef.current.click()} style={{ width: '100%', background: 'var(--blue)', color: 'white', padding: '12px', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: 700 }}>
                 {sceneFile ? 'CHANGE SCENE' : 'UPLOAD SCENE'}
               </button>
            </div>
            <div>
               <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '10px', fontWeight: 800 }}>TEMPLATE (OPT)</label>
               <button onClick={() => tmplRef.current.click()} style={{ width: '100%', background: 'rgba(255,255,255,0.05)', color: 'var(--text)', padding: '12px', border: '1px solid var(--border)', borderRadius: '12px', cursor: 'pointer', fontWeight: 700 }}>
                 {tmplFile ? 'CHANGE TMPL' : 'UPLOAD TMPL'}
               </button>
            </div>
            <div>
               <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '10px', fontWeight: 800 }}>DETECTOR ALGORITHM</label>
               <div style={{ display: 'flex', gap: '8px', background: 'rgba(0,0,0,0.2)', padding: '6px', borderRadius: '14px', border: '1px solid var(--border)' }}>
                  {['Harris', 'Shi-Tomasi', 'FAST'].map(d => (
                    <button 
                      key={d} 
                      onClick={() => setDetector(d)} 
                      style={{ 
                        flex: 1, padding: '8px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 800, fontSize: '0.75rem',
                        background: detector === d ? 'var(--purple)' : 'transparent',
                        color: detector === d ? 'white' : 'var(--text-dim)',
                        transition: 'all 0.2s'
                      }}
                    >
                      {d.toUpperCase()}
                    </button>
                  ))}
               </div>
            </div>
            <button onClick={run} disabled={!sceneFile || loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '12px 32px', borderRadius: '12px', fontWeight: 800, cursor: 'pointer', opacity: (!sceneFile || loading) ? 0.5 : 1, height: '48px', fontSize: '1rem', boxShadow: '0 10px 20px rgba(114, 9, 183, 0.3)' }}>
              {loading ? '⏳ RUNNING' : '🎯 DETECT'}
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: tmplUrl ? '1fr 1fr 1.5fr' : '1fr 1.5fr', gap: '24px' }}>
          {sceneUrl && (
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '24px' }}>
              <h4 style={{ textAlign: 'center', marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>BASE SCENE</h4>
              <img src={sceneUrl} style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} alt="Scene" />
            </div>
          )}
          {tmplUrl && (
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '24px' }}>
              <h4 style={{ textAlign: 'center', marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>TEMPLATE REFERENCE</h4>
              <img src={tmplUrl} style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} alt="Template" />
            </div>
          )}
          {sceneUrl && (
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '24px' }}>
              <h4 style={{ textAlign: 'center', marginTop: 0, marginBottom: '20px', fontSize: '0.8rem', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>FEATURE MAP ({detector.toUpperCase()})</h4>
              {resultUrl ? (
                <img src={resultUrl} style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} alt="Detected" />
              ) : (
                <div style={{ height: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', border: '2px dashed var(--border)', borderRadius: '16px' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🎯</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>READY TO SCAN</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
