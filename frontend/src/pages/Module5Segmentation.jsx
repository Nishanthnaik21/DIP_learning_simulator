import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Module5Segmentation() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  // Tab 0: Edge Detection
  const [edgeDetector, setEdgeDetector] = useState('Canny')
  const [edgeKsize, setEdgeKsize] = useState(3)
  const [edgeSigma, setEdgeSigma] = useState(1.5)
  const [edgeT1, setEdgeT1] = useState(50)
  const [edgeT2, setEdgeT2] = useState(150)
  const [edgeImage, setEdgeImage] = useState(null)

  // Tab 1: Hough
  const [houghType, setHoughType] = useState('line')
  const [houghThresh, setHoughThresh] = useState(80)
  const [houghMinLen, setHoughMinLen] = useState(50)
  const [houghMaxGap, setHoughMaxGap] = useState(10)
  const [houghDp, setHoughDp] = useState(1.5)
  const [houghMinDist, setHoughMinDist] = useState(30)
  const [houghP1, setHoughP1] = useState(80)
  const [houghP2, setHoughP2] = useState(30)
  const [houghMinR, setHoughMinR] = useState(10)
  const [houghMaxR, setHoughMaxR] = useState(60)
  const [houghImage, setHoughImage] = useState(null)

  // Tab 2: Thresholding
  const [threshMethod, setThreshMethod] = useState('Otsu')
  const [threshT, setThreshT] = useState(127)
  const [threshBlock, setThreshBlock] = useState(11)
  const [threshC, setThreshC] = useState(2)
  const [threshClasses, setThreshClasses] = useState(3)
  const [threshImage, setThreshImage] = useState(null)

  // Tab 3: Corners
  const [cornerDetector, setCornerDetector] = useState('Shi-Tomasi')
  const [cornerBlock, setCornerBlock] = useState(2)
  const [cornerKsize, setCornerKsize] = useState(3)
  const [cornerK, setCornerK] = useState(0.04)
  const [cornerThresh, setCornerThresh] = useState(10)
  const [cornerMax, setCornerMax] = useState(100)
  const [cornerQuality, setCornerQuality] = useState(0.01)
  const [cornerMinDist, setCornerMinDist] = useState(10)
  const [cornerFastThresh, setCornerFastThresh] = useState(10)
  const [cornerImage, setCornerImage] = useState(null)

  // Tab 4: Descriptors
  const [descThresh, setDescThresh] = useState(127)
  const [descNumShow, setDescNumShow] = useState(5)
  const [descData, setDescData] = useState(null)
  const [descImage, setDescImage] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      setEdgeImage(null); setHoughImage(null); setThreshImage(null); setCornerImage(null); setDescImage(null); setDescData(null)
    }
  }

  const runApi = async (endpoint, formData, setImgState, isJson = false) => {
    if (!file) return
    setLoading(true)
    try {
      formData.append('file', file)
      if (isJson) {
        const res = await axios.post(`/api/module5/${endpoint}`, formData)
        setImgState(res.data.image)
        setDescData(res.data.data)
      } else {
        const res = await axios.post(`/api/module5/${endpoint}`, formData, { responseType: 'blob' })
        setImgState(URL.createObjectURL(res.data))
      }
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const runEdge = () => {
    const fd = new FormData(); fd.append('detector', edgeDetector); fd.append('ksize', edgeKsize)
    fd.append('sigma', edgeSigma); fd.append('t1', edgeT1); fd.append('t2', edgeT2)
    runApi('edge_detection', fd, setEdgeImage)
  }

  const runHough = () => {
    const fd = new FormData(); fd.append('htype', houghType); fd.append('threshold', houghThresh)
    fd.append('min_len', houghMinLen); fd.append('max_gap', houghMaxGap); fd.append('dp', houghDp)
    fd.append('min_dist', houghMinDist); fd.append('p1', houghP1); fd.append('p2', houghP2)
    fd.append('min_r', houghMinR); fd.append('max_r', houghMaxR)
    runApi('hough', fd, setHoughImage)
  }

  const runThresh = () => {
    const fd = new FormData(); fd.append('method', threshMethod); fd.append('T', threshT)
    fd.append('block', threshBlock); fd.append('C', threshC); fd.append('classes', threshClasses)
    runApi('thresholding', fd, setThreshImage)
  }

  const runCorner = () => {
    const fd = new FormData(); fd.append('detector', cornerDetector); fd.append('block', cornerBlock)
    fd.append('ksize', cornerKsize); fd.append('k', cornerK); fd.append('thresh', cornerThresh)
    fd.append('max_corners', cornerMax); fd.append('quality', cornerQuality); fd.append('min_dist', cornerMinDist)
    fd.append('fast_thresh', cornerFastThresh)
    runApi('corners', fd, setCornerImage)
  }

  const runDesc = () => {
    const fd = new FormData(); fd.append('thresh', descThresh); fd.append('num_show', descNumShow)
    runApi('descriptors', fd, setDescImage, true)
  }

  const tabs = ['🔪 Edge Detection', '📐 Hough Transforms', '🔲 Thresholding', '◆ Corner Detection', '📏 Descriptors']

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <button onClick={() => navigate('/modules')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>✂️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Module 5: Segmentation</h1>
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

            {/* TAB 0: Edge Detection */}
            {activeTab === 0 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Edge Detection Filters</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Segmentation often starts with finding boundaries.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Detector</label>
                      <select value={edgeDetector} onChange={e => setEdgeDetector(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="Sobel (combined)">Sobel Operator</option>
                        <option value="Canny">Canny Edge Detector</option>
                        <option value="Laplacian">Laplacian (2nd Deriv)</option>
                        <option value="Prewitt">Prewitt</option>
                      </select>
                    </div>
                    {edgeDetector === 'Canny' ? (
                      <>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Low Threshold (T1)</label>
                             <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{edgeT1}</span>
                          </div>
                          <input type="range" min="1" max="255" value={edgeT1} onChange={e => setEdgeT1(parseInt(e.target.value))} />
                        </div>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>High Threshold (T2)</label>
                             <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{edgeT2}</span>
                          </div>
                          <input type="range" min="1" max="255" value={edgeT2} onChange={e => setEdgeT2(parseInt(e.target.value))} />
                        </div>
                      </>
                    ) : (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                           <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Kernel Size</label>
                           <span style={{ color: 'var(--blue)', fontWeight: 700 }}>{edgeKsize}x{edgeKsize}</span>
                        </div>
                        <input type="range" min="1" max="7" step="2" value={edgeKsize} onChange={e => setEdgeKsize(parseInt(e.target.value))} />
                      </div>
                    )}
                  </div>
                  <button onClick={runEdge} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Processing...' : '🔪 Run Edge Detector'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{edgeImage && <img src={edgeImage} alt="Edges" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
              </div>
            )}

            {/* TAB 1: Hough */}
            {activeTab === 1 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Hough Shape Transforms</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Detect parametric shapes like lines and circles.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Shape Type</label>
                      <select value={houghType} onChange={e => setHoughType(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="line">Straight Lines (Standard)</option>
                        <option value="prob_line">Lines (Probabilistic)</option>
                        <option value="circles">Circles (Hough Circle)</option>
                      </select>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Voting Threshold</label>
                         <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{houghThresh}</span>
                      </div>
                      <input type="range" min="10" max="300" value={houghThresh} onChange={e => setHoughThresh(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runHough} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Detecting Shapes...' : '📐 Run Hough Transform'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{houghImage && <img src={houghImage} alt="Hough" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
              </div>
            )}

            {/* TAB 2: Thresholding */}
            {activeTab === 2 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Image Thresholding</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Simplest form of segmentation.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Method</label>
                      <select value={threshMethod} onChange={e => setThreshMethod(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="Manual">Manual Threshold</option>
                        <option value="Otsu">Otsu (Global Auto)</option>
                        <option value="Adaptive Gaussian">Adaptive (Local)</option>
                        <option value="Multi">Multi-level</option>
                      </select>
                    </div>
                    <div>
                      {threshMethod === 'Manual' ? (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Threshold Value (T)</label>
                             <span style={{ color: 'var(--green)', fontWeight: 700 }}>{threshT}</span>
                          </div>
                          <input type="range" min="0" max="255" value={threshT} onChange={e => setThreshT(parseInt(e.target.value))} />
                        </>
                      ) : (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                             <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Block Size (Local)</label>
                             <span style={{ color: 'var(--green)', fontWeight: 700 }}>{threshBlock}x{threshBlock}</span>
                          </div>
                          <input type="range" min="3" max="99" step="2" value={threshBlock} onChange={e => setThreshBlock(parseInt(e.target.value))} />
                        </>
                      )}
                    </div>
                  </div>
                  <button onClick={runThresh} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Thresholding...' : '🔲 Run Thresholding'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{threshImage && <img src={threshImage} alt="Thresholded" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
              </div>
            )}

            {/* TAB 3: Corners */}
            {activeTab === 3 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Corner & Interest Points</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Identify critical features for tracking and matching.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Detector</label>
                      <select value={cornerDetector} onChange={e => setCornerDetector(e.target.value)} style={{ width: '100%', background: 'var(--bg-elevated)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px' }}>
                        <option value="Shi-Tomasi">Shi-Tomasi (Good Features)</option>
                        <option value="Harris">Harris Corner</option>
                        <option value="FAST">FAST Detector</option>
                      </select>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Max Corners</label>
                         <span style={{ color: 'var(--orange)', fontWeight: 700 }}>{cornerMax}</span>
                      </div>
                      <input type="range" min="10" max="500" step="10" value={cornerMax} onChange={e => setCornerMax(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runCorner} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Detecting Corners...' : '◆ Run Corner Detector'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{cornerImage && <img src={cornerImage} alt="Corners" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
              </div>
            )}

            {/* TAB 4: Descriptors */}
            {activeTab === 4 && file && (
              <div>
                <h3 style={{ marginTop: 0, fontFamily: 'var(--font-heading)' }}>Boundary & Region Descriptors</h3>
                <p style={{ color: 'var(--text-dim)', marginBottom: '20px', fontSize: '0.95rem', maxWidth: '800px' }}>
                  Quantify object properties once segmented.
                </p>
                <div style={{ background: 'var(--bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '20px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Segmentation Threshold</label>
                         <span style={{ color: 'var(--red)', fontWeight: 700 }}>{descThresh}</span>
                      </div>
                      <input type="range" min="1" max="255" value={descThresh} onChange={e => setDescThresh(parseInt(e.target.value))} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                         <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Show Top N Regions</label>
                         <span style={{ color: 'var(--red)', fontWeight: 700 }}>{descNumShow}</span>
                      </div>
                      <input type="range" min="1" max="20" value={descNumShow} onChange={e => setDescNumShow(parseInt(e.target.value))} />
                    </div>
                  </div>
                  <button onClick={runDesc} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, width: '100%' }}>
                    {loading ? '⏳ Computing Descriptors...' : '📏 Analyze Regions'}
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
                  <div style={{ flex: 1 }}><img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} /></div>
                  <div style={{ flex: 1 }}>{descImage && <img src={descImage} alt="Contours" style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border)' }} />}</div>
                </div>
                {descData && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    {descData.map((d, i) => (
                      <div key={i} style={{ padding: '16px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                        <h4 style={{ margin: '0 0 8px 0', fontSize: '0.9rem', color: 'var(--blue)' }}>REGION #{i+1}</h4>
                        <p style={{ margin: '4px 0', fontSize: '0.85rem' }}>Area: <b>{d.area.toFixed(0)}</b> | Perim: <b>{d.perimeter.toFixed(1)}</b></p>
                        <p style={{ margin: '4px 0', fontSize: '0.85rem' }}>Circularity: <b>{d.circularity.toFixed(3)}</b></p>
                        <p style={{ margin: '4px 0', fontSize: '0.65rem', color: 'var(--text-dim)', wordBreak: 'break-all' }}>Hu: {d.hu.map(h => h.toExponential(1)).join(', ')}</p>
                      </div>
                    ))}
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
