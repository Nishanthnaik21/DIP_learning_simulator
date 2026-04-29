import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Module1Fundamentals() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  // Tab 1: Pixel Inspector
  const [pxX, setPxX] = useState(100)
  const [pxY, setPxY] = useState(100)
  const [pixelData, setPixelData] = useState(null)

  // Tab 2: Sampling & Quantization
  const [sampleFactor, setSampleFactor] = useState(1)
  const [quantBits, setQuantBits] = useState(8)
  const [quantImage, setQuantImage] = useState(null)

  // Tab 4: Linear Operations
  const [operation, setOperation] = useState('brightness')
  const [opValue, setOpValue] = useState(30)
  const [opImage, setOpImage] = useState(null)

  // Tab 5: Statistics
  const [stats, setStats] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      // Reset states
      setPixelData(null)
      setQuantImage(null)
      setOpImage(null)
      setStats(null)
    }
  }

  const runPixelInspector = async () => {
    if (!file) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('x', pxX)
      formData.append('y', pxY)
      const res = await axios.post('/api/module1/pixel_inspector', formData)
      setPixelData(res.data)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runSampling = async () => {
    if (!file) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('factor', sampleFactor)
      formData.append('bits', quantBits)
      const res = await axios.post('/api/module1/sampling_quantization', formData, { responseType: 'blob' })
      setQuantImage(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runOperation = async () => {
    if (!file) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('op', operation)
      formData.append('value', opValue)
      const res = await axios.post('/api/module1/linear_operations', formData, { responseType: 'blob' })
      setOpImage(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runStats = async () => {
    if (!file) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await axios.post('/api/module1/statistics', formData)
      setStats(res.data)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const tabs = ['🔍 Pixel Inspector', '📉 Sampling', '➕ Operations', '📊 Statistics']

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <button onClick={() => navigate('/modules')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>
            ← Back
          </button>
          <span style={{ fontSize: '2rem' }}>🖼️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Module 1: Image Fundamentals</h1>
        </div>

        {/* Tabs */}
        <div>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
            {tabs.map((tab, idx) => (
              <button
                key={tab}
                onClick={() => setActiveTab(idx)}
                style={{
                  background: activeTab === idx ? 'var(--blue)' : 'transparent',
                  color: activeTab === idx ? 'white' : 'var(--text-dim)',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  transition: 'all 0.2s'
                }}
              >
                {tab}
              </button>
            ))}
          </div>

          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', minHeight: '400px', marginBottom: '24px' }}>
            
            {!file && (
              <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-dim)' }}>
                <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📁</div>
                <h3 style={{ fontFamily: 'var(--font-heading)', margin: 0 }}>Please upload an image below to use this module.</h3>
              </div>
            )}

            {/* TAB 0: Pixel Inspector */}
            {activeTab === 0 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Pixel Neighbourhood Inspector</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Explore the fundamental building blocks of digital images. By inspecting individual pixels, you can see their raw intensity values and how they form local neighbourhoods (3x3 patches) used in many image processing algorithms.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '20px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>X Coordinate</label>
                         <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{pxX}</span>
                      </div>
                      <input type="range" min="1" max="1024" value={pxX} onChange={e => setPxX(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Y Coordinate</label>
                         <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{pxY}</span>
                      </div>
                      <input type="range" min="1" max="1024" value={pxY} onChange={e => setPxY(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runPixelInspector} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '🔍 Inspecting...' : '🔍 Inspect Pixel'}
                  </button>
                </div>
                
                {pixelData && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div style={{ background: 'var(--bg)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: 'var(--text-dim)' }}>INTENSITY</h4>
                      <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--blue)' }}>{pixelData.intensity}</div>
                      {pixelData.rgb && (
                        <div style={{ marginTop: '10px', display: 'flex', gap: '12px' }}>
                          <span style={{ background: 'rgba(255,51,102,0.1)', padding: '4px 10px', borderRadius: '6px', color: '#ff3366', fontSize: '0.85rem' }}><b>R</b> {pixelData.rgb.R}</span>
                          <span style={{ background: 'rgba(6,214,160,0.1)', padding: '4px 10px', borderRadius: '6px', color: '#06d6a0', fontSize: '0.85rem' }}><b>G</b> {pixelData.rgb.G}</span>
                          <span style={{ background: 'rgba(67,97,238,0.1)', padding: '4px 10px', borderRadius: '6px', color: '#4361ee', fontSize: '0.85rem' }}><b>B</b> {pixelData.rgb.B}</span>
                        </div>
                      )}
                    </div>
                    <div style={{ background: 'var(--bg)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: 'var(--text-dim)' }}>3x3 NEIGHBOURHOOD</h4>
                      <table style={{ width: '100%', textAlign: 'center', borderCollapse: 'separate', borderSpacing: '4px' }}>
                        <tbody>
                          {pixelData.patch.map((row, i) => (
                            <tr key={i}>
                              {row.map((val, j) => (
                                <td key={j} style={{ padding: '8px', borderRadius: '6px', border: '1px solid var(--border)', background: i===1 && j===1 ? 'var(--blue)' : 'rgba(255,255,255,0.02)', color: i===1 && j===1 ? 'white' : 'var(--text)', fontSize: '0.9rem', fontWeight: 600 }}>
                                  {val}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 1: Sampling */}
            {activeTab === 1 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Sampling & Quantization</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Understand how continuous images are converted into digital form. <b>Sampling</b> reduces spatial resolution, while <b>Quantization</b> reduces intensity levels.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Sampling Factor</label>
                         <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{sampleFactor}x</span>
                      </div>
                      <input type="range" min="1" max="16" value={sampleFactor} onChange={e => setSampleFactor(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Quantization Bits</label>
                         <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{quantBits} bits</span>
                      </div>
                      <input type="range" min="1" max="8" value={quantBits} onChange={e => setQuantBits(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runSampling} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '✨ Apply Transformation'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{quantImage && <><img src={quantImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Processed (Factor: {sampleFactor}, Bits: {quantBits})</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 2: Operations */}
            {activeTab === 2 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Linear & Point Operations</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Point operations modify pixel values based on their current intensity. Adjust sliders to see how these transforms affect the dynamic range and contrast.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', gap: '16px', marginBottom: '20px' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Operation Type</label>
                      <select value={operation} onChange={e => setOperation(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="brightness">Brightness</option>
                        <option value="contrast">Contrast</option>
                        <option value="gamma">Gamma Correction</option>
                        <option value="log">Log Transform</option>
                        <option value="negative">Negative</option>
                        <option value="threshold">Threshold</option>
                      </select>
                    </div>
                    {['brightness', 'contrast', 'gamma', 'log', 'threshold'].includes(operation) && (
                      <div style={{ flex: 2 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Parameter Value</label>
                           <span style={{ color: 'var(--orange)', fontWeight: 700 }}>{opValue}</span>
                        </div>
                        <input 
                          type="range" 
                          min={operation === 'brightness' ? -100 : operation === 'contrast' || operation === 'gamma' ? 0.1 : 0} 
                          max={operation === 'brightness' ? 100 : operation === 'contrast' || operation === 'gamma' ? 4 : 255} 
                          step={operation === 'contrast' || operation === 'gamma' ? 0.1 : 1}
                          value={opValue} 
                          onChange={e => setOpValue(parseFloat(e.target.value))} 
                        />
                      </div>
                    )}
                  </div>
                  <button onClick={runOperation} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '🚀 Execute Operation'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{opImage && <><img src={opImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Processed Result</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 3: Statistics */}
            {activeTab === 3 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Image Statistics</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Quantitative analysis of an image. Statistical measures like <b>Mean</b>, <b>Standard Deviation</b>, and <b>Entropy</b> provide insights into overall brightness, contrast, and information content.
                </p>
                <button onClick={runStats} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '6px 16px', borderRadius: '8px', cursor: 'pointer', marginBottom: '20px' }}>
                  {loading ? 'Calculating...' : 'Calculate Stats'}
                </button>
                
                {stats && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                    {Object.entries(stats).map(([k, v]) => {
                      if (k === 'histogram') return null
                      return (
                        <div key={k} style={{ background: 'var(--bg)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)', textAlign: 'center' }}>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>{k}</div>
                          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--cyan)' }}>
                            {typeof v === 'number' && v % 1 !== 0 ? v.toFixed(2) : v}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )}

          </div>
        </div>

        {/* Upload Section */}
        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontFamily: 'var(--font-heading)' }}>Upload Image</h3>
          <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <button onClick={() => fileInputRef.current.click()} style={{ background: 'var(--blue)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
              Choose File
            </button>
            {previewUrl && <img src={previewUrl} alt="Preview" style={{ height: '80px', borderRadius: '8px', border: '1px solid var(--border)' }} />}
          </div>
        </div>
      </div>
    </div>
  )
}
