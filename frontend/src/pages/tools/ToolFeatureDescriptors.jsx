import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ToolFeatureDescriptors() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [resultImg, setResultImg] = useState(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [thresh, setThresh] = useState(127)
  const [numShow, setNumShow] = useState(5)
  const fileInputRef = useRef(null)

  const handleFile = (e) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setPreviewUrl(URL.createObjectURL(e.target.files[0])); setResultImg(null); setData(null) } }

  const run = async () => {
    if (!file) return
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('thresh', thresh); fd.append('num_show', numShow)
      const res = await axios.post('/api/module5/descriptors', fd)
      setResultImg(res.data.image)
      setData(res.data.data)
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }
  const inp = { background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: '6px', width: '80px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🔷</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Feature Descriptors</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)' }}>Feature Configuration</h3>
          <input type="file" ref={fileInputRef} onChange={handleFile} accept="image/*" style={{ display: 'none' }} />
          
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr auto', gap: '24px', alignItems: 'end' }}>
            <div>
               <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 600 }}>SOURCE IMAGE</label>
               <button onClick={() => fileInputRef.current.click()} style={{ width: '100%', background: 'var(--blue)', color: 'white', padding: '10px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
                 {file ? 'Change Image' : 'Select Image'}
               </button>
            </div>
            
            <div>
               <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>THRESHOLD</label>
                  <span style={{ color: 'var(--cyan)', fontWeight: 800 }}>{thresh}</span>
               </div>
               <input type="range" min="0" max="255" value={thresh} onChange={e => setThresh(+e.target.value)} />
            </div>

            <div>
               <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>SHOW TOP</label>
                  <span style={{ color: 'var(--purple)', fontWeight: 800 }}>{numShow}</span>
               </div>
               <input type="range" min="1" max="20" value={numShow} onChange={e => setNumShow(+e.target.value)} />
            </div>

            <button onClick={run} disabled={!file || loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', fontWeight: 700, cursor: 'pointer', height: '42px' }}>
              {loading ? '⏳ ANALYZING' : '🔷 EXTRACT'}
            </button>
          </div>
        </div>

        {previewUrl && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
            <div>
              <h4 style={{ marginBottom: '12px', fontSize: '0.9rem', color: 'var(--text-dim)', fontWeight: 700 }}>INPUT IMAGE</h4>
              <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '12px', borderRadius: '16px' }}>
                <img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '10px' }} />
              </div>
            </div>
            <div>
              <h4 style={{ marginBottom: '12px', fontSize: '0.9rem', color: 'var(--text-dim)', fontWeight: 700 }}>FEATURE VISUALIZATION</h4>
              <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '12px', borderRadius: '16px' }}>
                {resultImg 
                  ? <img src={resultImg} alt="Features" style={{ width: '100%', borderRadius: '10px' }} /> 
                  : <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', border: '2px dashed var(--border)', borderRadius: '10px' }}>
                      Click Extract to visualize
                    </div>
                }
              </div>
            </div>
          </div>
        )}

        {data && data.length > 0 && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '20px', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', alignItems: 'center' }}>
               <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)' }}>Extracted Shape Descriptors</h3>
               <span style={{ background: 'var(--blue)', color: 'white', padding: '4px 12px', borderRadius: '20px', fontWeight: 800, fontSize: '0.85rem' }}>{data.length} REGIONS FOUND</span>
            </div>
            
            <div style={{ overflowX: 'auto', margin: '0 -24px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                    {['INDEX', 'AREA (PX²)', 'PERIMETER', 'CIRCULARITY', 'CENTROID', 'ASPECT RATIO'].map(h => (
                      <th key={h} style={{ padding: '16px 24px', textAlign: 'left', color: 'var(--text-dim)', fontWeight: 800, borderBottom: '1px solid var(--border)', fontSize: '0.7rem', letterSpacing: '0.05em' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.map((d, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border)', transition: 'background 0.2s' }}>
                      <td style={{ padding: '16px 24px', fontWeight: 700, color: 'var(--blue)' }}>#{i + 1}</td>
                      <td style={{ padding: '16px 24px' }}>{Math.round(d.area)}</td>
                      <td style={{ padding: '16px 24px' }}>{d.perimeter?.toFixed(1)}</td>
                      <td style={{ padding: '16px 24px' }}>
                         <span style={{ color: d.circularity > 0.8 ? 'var(--green)' : 'var(--cyan)', fontWeight: 700 }}>{d.circularity?.toFixed(3)}</span>
                      </td>
                      <td style={{ padding: '16px 24px', color: 'var(--text-dim)' }}>({d.cx?.toFixed(0)}, {d.cy?.toFixed(0)})</td>
                      <td style={{ padding: '16px 24px', fontWeight: 700 }}>{d.aspect?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
