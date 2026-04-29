import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Module3Restoration() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  // Tab 0: Noise Models
  const [noiseType, setNoiseType] = useState('Gaussian')
  const [noiseSigma, setNoiseSigma] = useState(20)
  const [noiseProb, setNoiseProb] = useState(0.05)
  const [noiseA, setNoiseA] = useState(30)
  const [noiseK, setNoiseK] = useState(2)
  const [noiseScale, setNoiseScale] = useState(10)
  const [noiseImage, setNoiseImage] = useState(null)

  // Tab 1: Inverse Filtering
  const [invBlurSize, setInvBlurSize] = useState(10)
  const [invAngle, setInvAngle] = useState(0)
  const [invNoise, setInvNoise] = useState(5)
  const [invThreshold, setInvThreshold] = useState(0.05)
  const [invImage, setInvImage] = useState(null)

  // Tab 2: Wiener Filtering
  const [wienerBlurSize, setWienerBlurSize] = useState(10)
  const [wienerAngle, setWienerAngle] = useState(0)
  const [wienerNoise, setWienerNoise] = useState(10)
  const [wienerK, setWienerK] = useState(0.01)
  const [wienerImage, setWienerImage] = useState(null)

  // Tab 3: CLS Filtering
  const [clsBlurSize, setClsBlurSize] = useState(8)
  const [clsNoise, setClsNoise] = useState(15)
  const [clsGamma, setClsGamma] = useState(0.01)
  const [clsImage, setClsImage] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      setNoiseImage(null); setInvImage(null); setWienerImage(null); setClsImage(null)
    }
  }

  const runApi = async (endpoint, formData, setImgState) => {
    if (!file) return
    setLoading(true)
    try {
      formData.append('file', file)
      const res = await axios.post(`/api/module3/${endpoint}`, formData, { responseType: 'blob' })
      setImgState(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runNoise = () => {
    const fd = new FormData(); fd.append('ntype', noiseType); fd.append('sigma', noiseSigma)
    fd.append('prob', noiseProb); fd.append('a', noiseA); fd.append('k', noiseK); fd.append('scale', noiseScale)
    runApi('noise', fd, setNoiseImage)
  }

  const runInverse = () => {
    const fd = new FormData(); fd.append('blur_size', invBlurSize); fd.append('angle', invAngle)
    fd.append('noise_lvl', invNoise); fd.append('threshold', invThreshold)
    runApi('inverse_filter', fd, setInvImage)
  }

  const runWiener = () => {
    const fd = new FormData(); fd.append('blur_size', wienerBlurSize); fd.append('angle', wienerAngle)
    fd.append('noise_lvl', wienerNoise); fd.append('K', wienerK)
    runApi('wiener_filter', fd, setWienerImage)
  }

  const runCls = () => {
    const fd = new FormData(); fd.append('blur_size', clsBlurSize); fd.append('noise_lvl', clsNoise)
    fd.append('gamma', clsGamma)
    runApi('cls_filter', fd, setClsImage)
  }

  const tabs = ['💥 Noise Models', '🔄 Inverse Filtering', '🧠 Wiener Filtering', '📏 Constrained LS']

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <button onClick={() => navigate('/modules')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>
            ← Back
          </button>
          <span style={{ fontSize: '2rem' }}>🔧</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Module 3: Image Restoration</h1>
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

            {/* TAB 0: Noise Models */}
            {activeTab === 0 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Add Noise Models</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Image degradation often occurs during acquisition or transmission. Test different noise models.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Noise Type</label>
                      <select value={noiseType} onChange={e => setNoiseType(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="Gaussian">Gaussian (Normal)</option>
                        <option value="Salt & Pepper">Salt & Pepper (Impulse)</option>
                        <option value="Rayleigh">Rayleigh</option>
                        <option value="Uniform">Uniform</option>
                        <option value="Erlang">Erlang (Gamma)</option>
                      </select>
                    </div>
                    <div>
                      {['Gaussian', 'Rayleigh'].includes(noiseType) && (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Standard Deviation (σ)</label>
                             <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{noiseSigma}</span>
                          </div>
                          <input type="range" min="1" max="100" value={noiseSigma} onChange={e => setNoiseSigma(parseInt(e.target.value))} />
                        </>
                      )}
                      {noiseType === 'Salt & Pepper' && (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Noise Density (P)</label>
                             <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{noiseProb}</span>
                          </div>
                          <input type="range" min="0.01" max="0.5" step="0.01" value={noiseProb} onChange={e => setNoiseProb(parseFloat(e.target.value))} />
                        </>
                      )}
                    </div>
                  </div>
                  <button onClick={runNoise} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Adding Noise...' : '💥 Apply Noise Model'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Original</p></div>
                  <div style={{ flex: 1 }}>{noiseImage && <><img src={noiseImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /><p style={{ textAlign: 'center', marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Noisy Image</p></>}</div>
                </div>
              </div>
            )}

            {/* TAB 1: Inverse Filtering */}
            {activeTab === 1 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Inverse Filtering Restoration</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Restoration attempts to reconstruct an image from its degraded version.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Blur Size</label>
                         <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{invBlurSize} px</span>
                      </div>
                      <input type="range" min="2" max="30" step="1" value={invBlurSize} onChange={e => setInvBlurSize(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Angle</label>
                         <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{invAngle}°</span>
                      </div>
                      <input type="range" min="0" max="180" step="5" value={invAngle} onChange={e => setInvAngle(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Noise Level</label>
                         <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{invNoise}</span>
                      </div>
                      <input type="range" min="0" max="50" step="1" value={invNoise} onChange={e => setInvNoise(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runInverse} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Restoring...' : '🔄 Run Inverse Filter'}
                  </button>
                </div>
                {invImage && (
                  <div style={{ textAlign: 'center' }}>
                    <img src={invImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />
                    <p style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Left: Degraded | Right: Restored (Inverse Filter)</p>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: Wiener Filtering */}
            {activeTab === 2 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Wiener Filtering (MMSE)</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                   Accounts for both the degradation function and the noise power spectrum.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Blur Size</label>
                         <span style={{ color: 'var(--green)', fontWeight: 700 }}>{wienerBlurSize} px</span>
                      </div>
                      <input type="range" min="2" max="30" step="1" value={wienerBlurSize} onChange={e => setWienerBlurSize(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Noise Level</label>
                         <span style={{ color: 'var(--green)', fontWeight: 700 }}>{wienerNoise}</span>
                      </div>
                      <input type="range" min="0" max="50" step="1" value={wienerNoise} onChange={e => setWienerNoise(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Wiener Constant (K)</label>
                         <span style={{ color: 'var(--green)', fontWeight: 700 }}>{wienerK}</span>
                      </div>
                      <input type="range" min="0.001" max="0.1" step="0.001" value={wienerK} onChange={e => setWienerK(parseFloat(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runWiener} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Restoring...' : '🧠 Run Wiener Filter'}
                  </button>
                </div>
                {wienerImage && (
                  <div style={{ textAlign: 'center' }}>
                    <img src={wienerImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />
                    <p style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Left: Degraded | Right: Restored (Wiener Filter)</p>
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: CLS Filtering */}
            {activeTab === 3 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Constrained Least Squares</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Minimizes a criterion of smoothness subject to data consistency constraints.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Blur Size</label>
                         <span style={{ color: 'var(--orange)', fontWeight: 700 }}>{clsBlurSize} px</span>
                      </div>
                      <input type="range" min="2" max="30" step="1" value={clsBlurSize} onChange={e => setClsBlurSize(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Noise Level</label>
                         <span style={{ color: 'var(--orange)', fontWeight: 700 }}>{clsNoise}</span>
                      </div>
                      <input type="range" min="0" max="50" step="1" value={clsNoise} onChange={e => setClsNoise(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Gamma (γ)</label>
                         <span style={{ color: 'var(--orange)', fontWeight: 700 }}>{clsGamma}</span>
                      </div>
                      <input type="range" min="0.001" max="0.5" step="0.001" value={clsGamma} onChange={e => setClsGamma(parseFloat(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runCls} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Restoring...' : '📏 Run CLS Filter'}
                  </button>
                </div>
                {clsImage && (
                  <div style={{ textAlign: 'center' }}>
                    <img src={clsImage} alt="Processed" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />
                    <p style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>Left: Degraded | Right: Restored (CLS Filter)</p>
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
