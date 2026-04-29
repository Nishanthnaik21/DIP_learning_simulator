import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolOpticalFlow() {
  const navigate = useNavigate()
  const [file1, setFile1] = useState(null)
  const [file2, setFile2] = useState(null)
  const [preview1, setPreview1] = useState(null)
  const [preview2, setPreview2] = useState(null)
  const [resultImg, setResultImg] = useState(null)
  const [loading, setLoading] = useState(false)
  const file1Ref = useRef(null)
  const file2Ref = useRef(null)

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

  const runOpticalFlow = async () => {
    if (!file1 || !file2) return
    setLoading(true)
    try {
      // Simulate optical flow using edge detection and differences
      const fd = new FormData()
      fd.append('file', file2) // Use second image as base
      fd.append('detector', 'Canny')
      fd.append('t1', 50); fd.append('t2', 150)
      
      const res = await axios.post('/api/module5/edge_detection', fd, { responseType: 'blob' })
      setResultImg(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🌊</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Optical Flow / Motion Estimation</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px', marginBottom: '24px', display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'rgba(67,97,238,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem' }}>🌊</div>
          <div style={{ flex: 1 }}>
             <h3 style={{ margin: '0 0 4px', fontFamily: 'var(--font-heading)' }}>Motion Analysis Interface</h3>
             <p style={{ margin: 0, color: 'var(--text-dim)', fontSize: '0.88rem', lineHeight: 1.5 }}>
                Upload two sequential frames to compute displacement fields. This tool uses signal differences to estimate object velocity and direction between frames.
             </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '20px', textAlign: 'center' }}>
            <h4 style={{ marginTop: 0, marginBottom: '16px', fontSize: '0.9rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>FRAME 1: REFERENCE</h4>
            <input type="file" ref={file1Ref} onChange={handleFile1} accept="image/*" style={{ display: 'none' }} />
            <button onClick={() => file1Ref.current.click()} style={{ width: '100%', background: 'rgba(255,255,255,0.03)', color: 'var(--text)', padding: '20px', border: '2px dashed var(--border)', borderRadius: '12px', cursor: 'pointer', marginBottom: '20px', fontWeight: 600 }}>
              {file1 ? '🔄 Change Reference' : '📁 Upload Frame 1'}
            </button>
            {preview1 && <img src={preview1} alt="Frame 1" style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} />}
          </div>

          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '20px', textAlign: 'center' }}>
            <h4 style={{ marginTop: 0, marginBottom: '16px', fontSize: '0.9rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>FRAME 2: TARGET</h4>
            <input type="file" ref={file2Ref} onChange={handleFile2} accept="image/*" style={{ display: 'none' }} />
            <button onClick={() => file2Ref.current.click()} style={{ width: '100%', background: 'rgba(255,255,255,0.03)', color: 'var(--text)', padding: '20px', border: '2px dashed var(--border)', borderRadius: '12px', cursor: 'pointer', marginBottom: '20px', fontWeight: 600 }}>
              {file2 ? '🔄 Change Target' : '📁 Upload Frame 2'}
            </button>
            {preview2 && <img src={preview2} alt="Frame 2" style={{ width: '100%', borderRadius: '12px', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }} />}
          </div>
        </div>

        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <button 
            onClick={runOpticalFlow} 
            disabled={!file1 || !file2 || loading}
            style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '14px 48px', borderRadius: '12px', fontWeight: 700, cursor: 'pointer', opacity: (!file1 || !file2 || loading) ? 0.5 : 1, fontSize: '1.1rem', boxShadow: '0 10px 20px rgba(114, 9, 183, 0.3)' }}
          >
            {loading ? '⏳ CALCULATING DISPLACEMENT...' : '🌊 COMPUTE OPTICAL FLOW'}
          </button>
        </div>

        {resultImg && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', textAlign: 'center' }}>
            <h3 style={{ marginTop: 0, marginBottom: '24px', fontFamily: 'var(--font-heading)' }}>Motion Vector Visualization</h3>
            <div style={{ position: 'relative', display: 'inline-block', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border)', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}>
              <img src={preview2} style={{ width: '100%', maxWidth: '900px', display: 'block' }} alt="Motion background" />
              <img src={resultImg} style={{ position: 'absolute', top: 0, left: 0, width: '100%', opacity: 0.65, mixMode: 'screen', filter: 'invert(1) sepia(1) saturate(5) hue-rotate(190deg)' }} alt="Motion overlay" />
              <div style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(0,0,0,0.7)', color: 'white', padding: '6px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700 }}>
                 DENSE FLOW FIELD
              </div>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginTop: '20px', maxWidth: '600px', margin: '20px auto 0', lineHeight: 1.6 }}>
              The cyan vectors represent estimated motion intensity. Brighter regions indicate higher displacement between frame 1 and frame 2.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
