import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Module4ColorMorphology() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  // Tab 0: Color Models
  const [colorModel, setColorModel] = useState('RGB')
  const [colorImage, setColorImage] = useState(null)

  // Tab 1: Pseudo-Color
  const [pseudoMode, setPseudoMode] = useState('colormap')
  const [pseudoCmap, setPseudoCmap] = useState('Jet')
  const [pseudoLo, setPseudoLo] = useState(80)
  const [pseudoHi, setPseudoHi] = useState(180)
  const [pseudoImage, setPseudoImage] = useState(null)

  // Tab 2: Wavelets
  const [wavType, setWavType] = useState('haar')
  const [wavLevel, setWavLevel] = useState(2)
  const [wavKeep, setWavKeep] = useState(10)
  const [wavImage, setWavImage] = useState(null)

  // Tab 3: Morphology
  const [morphOp, setMorphOp] = useState('Erosion')
  const [morphThresh, setMorphThresh] = useState(127)
  const [morphShape, setMorphShape] = useState('Rectangle')
  const [morphSize, setMorphSize] = useState(5)
  const [morphIters, setMorphIters] = useState(1)
  const [morphImage, setMorphImage] = useState(null)

  // Tab 4: Hit-or-Miss
  const [hitPattern, setHitPattern] = useState('isolated')
  const [hitThresh, setHitThresh] = useState(127)
  const [hitImage, setHitImage] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      setColorImage(null); setPseudoImage(null); setWavImage(null); setMorphImage(null); setHitImage(null)
    }
  }

  const runApi = async (endpoint, formData, setImgState) => {
    if (!file) return
    setLoading(true)
    try {
      formData.append('file', file)
      const res = await axios.post(`/api/module4/${endpoint}`, formData, { responseType: 'blob' })
      setImgState(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runColor = () => {
    const fd = new FormData(); fd.append('model', colorModel)
    runApi('color_models', fd, setColorImage)
  }

  const runPseudo = () => {
    const fd = new FormData(); fd.append('mode', pseudoMode); fd.append('cmap', pseudoCmap)
    fd.append('lo', pseudoLo); fd.append('hi', pseudoHi)
    runApi('pseudo_color', fd, setPseudoImage)
  }

  const runWavelets = () => {
    const fd = new FormData(); fd.append('wavelet', wavType); fd.append('level', wavLevel); fd.append('keep_pct', wavKeep)
    runApi('wavelets', fd, setWavImage)
  }

  const runMorph = () => {
    const fd = new FormData(); fd.append('op', morphOp); fd.append('thresh_val', morphThresh)
    fd.append('se_shape', morphShape); fd.append('se_size', morphSize); fd.append('iters', morphIters)
    runApi('morphology', fd, setMorphImage)
  }

  const runHit = () => {
    const fd = new FormData(); fd.append('pattern', hitPattern); fd.append('thresh', hitThresh)
    runApi('hitormiss', fd, setHitImage)
  }

  const tabs = ['🎨 Color Models', '🌈 Pseudo-Color', '〰️ Wavelets', '◾ Morphology', '🎯 Hit-or-Miss']

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <button onClick={() => navigate('/modules')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>
            ← Back
          </button>
          <span style={{ fontSize: '2rem' }}>🎨</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Module 4: Color & Morphology</h1>
        </div>

        {/* Tabs */}
        <div>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', borderBottom: '1px solid var(--border)', paddingBottom: '12px', flexWrap: 'wrap' }}>
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

            {/* TAB 0: Color Models */}
            {activeTab === 0 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Color Model Separation</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Decompose images into different color models.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Model</label>
                      <select value={colorModel} onChange={e => setColorModel(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="RGB">RGB (Additive)</option>
                        <option value="HSV">HSV (Perceptual)</option>
                        <option value="LAB">CIELAB (L*a*b*)</option>
                        <option value="YCbCr">YCbCr (Video)</option>
                        <option value="CMY">CMY (Subtractive)</option>
                      </select>
                    </div>
                    <button onClick={runColor} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, flex: 1 }}>
                      {loading ? '⏳ Separating...' : '🎨 Separate Channels'}
                    </button>
                  </div>
                </div>
                {colorImage && <img src={colorImage} alt="Color Channels" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}
              </div>
            )}

            {/* TAB 1: Pseudo-Color */}
            {activeTab === 1 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Pseudo-Color & Slicing</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                   Highlight specific ranges or apply continuous color maps.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Mode</label>
                      <select value={pseudoMode} onChange={e => setPseudoMode(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="colormap">Continuous Colormap</option>
                        <option value="slice">Intensity Slicing</option>
                      </select>
                    </div>
                    <div>
                      {pseudoMode === 'colormap' ? (
                        <>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Map Type</label>
                          <select value={pseudoCmap} onChange={e => setPseudoCmap(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                            <option value="Jet">Jet</option>
                            <option value="Hot">Hot</option>
                            <option value="Rainbow">Rainbow</option>
                            <option value="Ocean">Ocean</option>
                            <option value="Inferno">Inferno</option>
                          </select>
                        </>
                      ) : (
                        <div style={{ display: 'flex', gap: '20px' }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                               <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Lower Bound</label>
                               <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{pseudoLo}</span>
                            </div>
                            <input type="range" min="0" max="255" value={pseudoLo} onChange={e => setPseudoLo(parseInt(e.target.value))} />
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                               <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Upper Bound</label>
                               <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{pseudoHi}</span>
                            </div>
                            <input type="range" min="0" max="255" value={pseudoHi} onChange={e => setPseudoHi(parseInt(e.target.value))} />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <button onClick={runPseudo} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '🌈 Apply Pseudo-Color'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{pseudoImage && <img src={pseudoImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
              </div>
            )}

            {/* TAB 2: Wavelets */}
            {activeTab === 2 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Wavelet Compression</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Multi-resolution analysis for compression.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Wavelet</label>
                      <select value={wavType} onChange={e => setWavType(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="haar">Haar (Simple)</option>
                        <option value="db2">Daubechies 2</option>
                        <option value="sym4">Symlet 4</option>
                      </select>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Decomposition Level</label>
                         <span style={{ color: 'var(--blue)', fontWeight: 700 }}>L{wavLevel}</span>
                      </div>
                      <input type="range" min="1" max="4" value={wavLevel} onChange={e => setWavLevel(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Coefficients to Keep</label>
                         <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{wavKeep}%</span>
                      </div>
                      <input type="range" min="1" max="100" value={wavKeep} onChange={e => setWavKeep(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runWavelets} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Reconstructing...' : '〰️ Run DWT Compression'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{wavImage && <><img src={wavImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Wavelet Reconstruction</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 3: Morphology */}
            {activeTab === 3 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Morphological Operations</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Process binary shapes using structuring elements.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Operation</label>
                      <select value={morphOp} onChange={e => setMorphOp(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="Erosion">Erosion</option>
                        <option value="Dilation">Dilation</option>
                        <option value="Opening">Opening</option>
                        <option value="Closing">Closing</option>
                        <option value="Gradient">Morphological Gradient</option>
                        <option value="Skeletonisation">Skeletonisation</option>
                      </select>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Binary Threshold</label>
                         <span style={{ color: 'var(--green)', fontWeight: 700 }}>{morphThresh}</span>
                      </div>
                      <input type="range" min="0" max="255" value={morphThresh} onChange={e => setMorphThresh(parseInt(e.target.value))} />
                    </div>
                    {morphOp !== 'Skeletonisation' && (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Element Size</label>
                           <span style={{ color: 'var(--green)', fontWeight: 700 }}>{morphSize}x{morphSize}</span>
                        </div>
                        <input type="range" min="3" max="25" step="2" value={morphSize} onChange={e => setMorphSize(parseInt(e.target.value))} />
                      </div>
                    )}
                  </div>
                  <button onClick={runMorph} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '◾ Apply Morphology'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{morphImage && <img src={morphImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
              </div>
            )}

            {/* TAB 4: Hit-or-Miss */}
            {activeTab === 4 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Hit-or-Miss Transform</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Detect specific pixel configurations.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Pattern</label>
                      <select value={hitPattern} onChange={e => setHitPattern(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="isolated">Isolated Foreground Pixel</option>
                        <option value="corner">Top-Right Corner</option>
                        <option value="line">Horizontal Line End</option>
                      </select>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Binarize Threshold</label>
                         <span style={{ color: 'var(--orange)', fontWeight: 700 }}>{hitThresh}</span>
                      </div>
                      <input type="range" min="0" max="255" value={hitThresh} onChange={e => setHitThresh(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runHit} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Detecting...' : '🎯 Detect Pattern'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{hitImage && <img src={hitImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
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
