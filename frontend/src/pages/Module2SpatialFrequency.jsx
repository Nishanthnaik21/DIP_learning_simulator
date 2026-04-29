import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Module2SpatialFrequency() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  // Tab 0: Histogram Processing
  const [histMethod, setHistMethod] = useState('global')
  const [clipLimit, setClipLimit] = useState(2.0)
  const [tileSize, setTileSize] = useState(8)
  const [histImage, setHistImage] = useState(null)

  // Tab 1: Smoothing
  const [smoothType, setSmoothType] = useState('average')
  const [smoothKsize, setSmoothKsize] = useState(5)
  const [smoothSigma, setSmoothSigma] = useState(1.5)
  const [smoothD, setSmoothD] = useState(9)
  const [smoothNoise, setSmoothNoise] = useState(false)
  const [smoothImage, setSmoothImage] = useState(null)

  // Tab 2: Sharpening
  const [sharpType, setSharpType] = useState('laplacian')
  const [sharpWeight, setSharpWeight] = useState(1.0)
  const [sharpAmount, setSharpAmount] = useState(1.5)
  const [sharpBoost, setSharpBoost] = useState(2.0)
  const [sharpImage, setSharpImage] = useState(null)

  // Tab 3: DFT Spectrum
  const [dftView, setDftView] = useState('magnitude')
  const [dftImage, setDftImage] = useState(null)

  // Tab 4: Frequency Filters
  const [freqType, setFreqType] = useState('ideal_lpf')
  const [freqD0, setFreqD0] = useState(30)
  const [freqN, setFreqN] = useState(2)
  const [freqImage, setFreqImage] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      setHistImage(null); setSmoothImage(null); setSharpImage(null); setDftImage(null); setFreqImage(null)
    }
  }

  const runApi = async (endpoint, formData, setImgState) => {
    if (!file) return
    setLoading(true)
    try {
      formData.append('file', file)
      const res = await axios.post(`/api/module2/${endpoint}`, formData, { responseType: 'blob' })
      setImgState(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runHistogram = () => {
    const fd = new FormData(); fd.append('method', histMethod); fd.append('clip', clipLimit); fd.append('tile', tileSize)
    runApi('histogram', fd, setHistImage)
  }

  const runSmoothing = () => {
    const fd = new FormData(); fd.append('ftype', smoothType); fd.append('ksize', smoothKsize)
    fd.append('sigma', smoothSigma); fd.append('d', smoothD); fd.append('noise', smoothNoise)
    runApi('smoothing', fd, setSmoothImage)
  }

  const runSharpening = () => {
    const fd = new FormData(); fd.append('stype', sharpType); fd.append('weight', sharpWeight)
    fd.append('amount', sharpAmount); fd.append('boost', sharpBoost)
    runApi('sharpening', fd, setSharpImage)
  }

  const runDft = () => {
    const fd = new FormData(); fd.append('view', dftView)
    runApi('dft', fd, setDftImage)
  }

  const runFreq = () => {
    const fd = new FormData(); fd.append('ftype', freqType); fd.append('d0', freqD0); fd.append('n', freqN)
    runApi('frequency_filter', fd, setFreqImage)
  }

  const tabs = ['📊 Histogram', '🌊 Smoothing', '🔪 Sharpening', '📡 DFT Spectrum', '🎛️ Freq Filters']

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <button onClick={() => navigate('/modules')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>
            ← Back
          </button>
          <span style={{ fontSize: '2rem' }}>📡</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Module 2: Spatial & Frequency</h1>
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

            {/* TAB 0: Histogram */}
            {activeTab === 0 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Histogram Processing</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  The <b>Histogram</b> represents the distribution of intensity levels in an image. <b>Histogram Equalization</b> stretches the intensity range to enhance contrast.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Method</label>
                      <select value={histMethod} onChange={e => setHistMethod(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="global">Global Equalisation</option>
                        <option value="clahe">CLAHE (Adaptive)</option>
                      </select>
                    </div>
                    {histMethod === 'clahe' && (
                      <div style={{ display: 'flex', gap: '20px' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Clip Limit</label>
                             <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{clipLimit}</span>
                          </div>
                          <input type="range" min="0.1" max="10" step="0.1" value={clipLimit} onChange={e => setClipLimit(parseFloat(e.target.value))} />
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Tile Size</label>
                             <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{tileSize}x{tileSize}</span>
                          </div>
                          <input type="range" min="2" max="32" step="2" value={tileSize} onChange={e => setTileSize(parseInt(e.target.value))} />
                        </div>
                      </div>
                    )}
                  </div>
                  <button onClick={runHistogram} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '✨ Apply Equalization'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{histImage && <><img src={histImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Enhanced Result</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 1: Smoothing */}
            {activeTab === 1 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Smoothing Spatial Filters</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Smoothing filters are used for <b>noise reduction</b> and <b>blurring</b>. <b>Median</b> filtering is excellent for removing salt-and-pepper noise.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Filter Type</label>
                      <select value={smoothType} onChange={e => setSmoothType(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="average">Average (Box)</option>
                        <option value="gaussian">Gaussian</option>
                        <option value="median">Median</option>
                        <option value="bilateral">Bilateral</option>
                      </select>
                    </div>
                    {['average', 'gaussian', 'median'].includes(smoothType) && (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Kernel Size</label>
                           <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{smoothKsize}x{smoothKsize}</span>
                        </div>
                        <input type="range" min="3" max="25" step="2" value={smoothKsize} onChange={e => setSmoothKsize(parseInt(e.target.value))} />
                      </div>
                    )}
                    {smoothType === 'gaussian' && (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Sigma</label>
                           <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{smoothSigma}</span>
                        </div>
                        <input type="range" min="0.5" max="10" step="0.5" value={smoothSigma} onChange={e => setSmoothSigma(parseFloat(e.target.value))} />
                      </div>
                    )}
                    <div style={{ display: 'flex', alignItems: 'center', paddingTop: '24px' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}>
                        <input type="checkbox" checked={smoothNoise} onChange={e => setSmoothNoise(e.target.checked)} style={{ width: '18px', height: '18px' }} /> Add Impulse Noise
                      </label>
                    </div>
                  </div>
                  <button onClick={runSmoothing} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '🌊 Apply Smoothing'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{smoothImage && <><img src={smoothImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Smoothed Result</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 2: Sharpening */}
            {activeTab === 2 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Sharpening Spatial Filters</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                   Sharpening highlights intensity transitions. The <b>Laplacian</b> detects fine detail, while <b>Sobel</b> is used for edge magnitude.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Sharpening Type</label>
                      <select value={sharpType} onChange={e => setSharpType(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="laplacian">Laplacian (2nd Derivative)</option>
                        <option value="unsharp">Unsharp Masking</option>
                        <option value="sobel">Sobel Operator</option>
                        <option value="boost">High-boost Filtering</option>
                      </select>
                    </div>
                    {['laplacian', 'sobel', 'boost'].includes(sharpType) && (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Effect Strength</label>
                           <span style={{ color: 'var(--red)', fontWeight: 700 }}>{sharpWeight}x</span>
                        </div>
                        <input type="range" min="0.1" max="5" step="0.1" value={sharpWeight} onChange={e => setSharpWeight(parseFloat(e.target.value))} />
                      </div>
                    )}
                  </div>
                  <button onClick={runSharpening} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '🔪 Apply Sharpening'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{sharpImage && <><img src={sharpImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Sharpened Result</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 3: DFT Spectrum */}
            {activeTab === 3 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Frequency Domain: DFT Spectrum</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  The <b>Discrete Fourier Transform</b> converts images to the <b>Frequency Domain</b>. Low frequencies (center) correspond to smooth regions.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Spectrum View</label>
                      <select value={dftView} onChange={e => setDftView(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="magnitude">Magnitude Spectrum (Log scaled)</option>
                        <option value="phase">Phase Spectrum</option>
                      </select>
                    </div>
                    <button onClick={runDft} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, flex: 1 }}>
                      {loading ? '⏳ Computing DFT...' : '📡 Generate Spectrum'}
                    </button>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{dftImage && <><img src={dftImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Frequency Spectrum</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 4: Frequency Filters */}
            {activeTab === 4 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Frequency Domain Filters</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Filters in the frequency domain can be <b>Lowpass</b> or <b>Highpass</b>. <b>Butterworth</b> and <b>Gaussian</b> provide smoother transitions than Ideal filters.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Filter Type</label>
                      <select value={freqType} onChange={e => setFreqType(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="ideal_lpf">Ideal Lowpass</option>
                        <option value="ideal_hpf">Ideal Highpass</option>
                        <option value="gaussian_lpf">Gaussian Lowpass</option>
                        <option value="gaussian_hpf">Gaussian Highpass</option>
                        <option value="butterworth_lpf">Butterworth Lowpass</option>
                        <option value="butterworth_hpf">Butterworth Highpass</option>
                      </select>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Cut-off Radius (D0)</label>
                         <span style={{ color: 'var(--purple-light)', fontWeight: 700 }}>{freqD0} px</span>
                      </div>
                      <input type="range" min="5" max="200" step="1" value={freqD0} onChange={e => setFreqD0(parseInt(e.target.value))} />
                    </div>
                    {freqType.includes('butterworth') && (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Order (n)</label>
                           <span style={{ color: 'var(--purple-light)', fontWeight: 700 }}>{freqN}</span>
                        </div>
                        <input type="range" min="1" max="10" step="1" value={freqN} onChange={e => setFreqN(parseInt(e.target.value))} />
                      </div>
                    )}
                  </div>
                  <button onClick={runFreq} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '🎛️ Apply Frequency Filter'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{freqImage && <><img src={freqImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Filtered Image</p></>}</div>
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
