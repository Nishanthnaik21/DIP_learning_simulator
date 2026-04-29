import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const SNIPPETS = (val, lang) => {
  const v = val || 0;
  if (lang === 'python') {
    return {
      grayscale: `# Convert image to grayscale and adjust brightness\nimport cv2\nimport numpy as np\n\n# Load image\nimg = cv2.imread('input.jpg')\n\n# Convert to grayscale\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n\n# Adjust brightness by ${v}\nresult = np.clip(gray.astype(int) + ${v}, 0, 255).astype(np.uint8)\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
      
      histogram_eq: `# Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)\nimport cv2\n\n# Load image in grayscale\nimg = cv2.imread('input.jpg', 0)\n\n# Create CLAHE object with clip limit ${v}\nclahe = cv2.createCLAHE(clipLimit=${v}.0, tileGridSize=(8,8))\n\n# Apply CLAHE\nresult = clahe.apply(img)\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
      
      gaussian_blur: `# Apply Gaussian Blur with variable kernel size\nimport cv2\n\n# Load image\nimg = cv2.imread('input.jpg')\n\n# Apply Gaussian blur with kernel size ${v}x${v}\nresult = cv2.GaussianBlur(img, (${v}, ${v}), 0)\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
      
      canny_edge: `# Canny Edge Detection with variable threshold\nimport cv2\n\n# Load image\nimg = cv2.imread('input.jpg', 0)\n\n# Apply Canny detector with upper threshold ${v}\n# Lower threshold is set to half of upper threshold\nedges = cv2.Canny(img, ${v}/2, ${v})\n\n# Save result\ncv2.imwrite('result.jpg', edges)`,
      
      dft: `# Discrete Fourier Transform and spectrum visualization\nimport cv2\nimport numpy as np\n\n# Load image in grayscale\nimg = cv2.imread('input.jpg', 0)\n\n# Compute 2D DFT\nf = np.fft.fft2(img)\nfshift = np.fft.fftshift(f)\n\n# Compute magnitude spectrum with log transform (gain ${v})\nmag = ${v} * np.log(np.abs(fshift) + 1)\n\n# Normalize to 0-255 range\nresult = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
      
      morphology: `# Morphological Dilation\nimport cv2\nimport numpy as np\n\n# Load image and threshold\nimg = cv2.imread('input.jpg', 0)\n_, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)\n\n# Create 5x5 rectangular kernel\nkernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))\n\n# Apply Dilation with ${v} iterations\nresult = cv2.dilate(binary, kernel, iterations=${v})\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
      
      sobel: `# Sobel Edge Detection\nimport cv2\nimport numpy as np\n\n# Load image in grayscale\nimg = cv2.imread('input.jpg', 0)\n\n# Compute Sobel gradients in X and Y with kernel size ${v}\nsx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=${v})\nsy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=${v})\n\n# Combine gradients to get magnitude\nresult = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
      
      wavelet: `# Wavelet Image Compression\nimport cv2\nimport pywt\nimport numpy as np\n\n# Load image as float\nimg = cv2.imread('input.jpg', 0).astype(float)\n\n# Perform 2-level Haar Wavelet decomposition\ncoeffs = pywt.wavedec2(img, 'haar', level=2)\n\n# Flatten and threshold coefficients (keep ${v}%)\nall_coeffs = np.concatenate([c.flatten() for arr in coeffs[1:] for c in arr])\nthresh = np.percentile(np.abs(all_coeffs), 100 - ${v})\n\n# Reconstruct image from thresholded coefficients\nrec = pywt.waverec2(coeffs, 'haar')\nresult = cv2.normalize(rec, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\n\n# Save result\ncv2.imwrite('result.jpg', result)`,
    }
  } else {
    return {
      grayscale: `% Grayscale and Brightness adjustment\nimg = imread('input.jpg');\ngray = rgb2gray(img);\n\n% Adjust brightness by ${v}\nresult = gray + ${v};\nimwrite(result, 'result.jpg');`,
      
      histogram_eq: `% Histogram Equalization\nimg = imread('input.jpg');\ngray = rgb2gray(img);\n\n% Apply global equalization\nresult = histeq(gray);\nimwrite(result, 'result.jpg');`,
      
      gaussian_blur: `% Gaussian Smoothing\nimg = imread('input.jpg');\n\n% Create Gaussian filter of size ${v} with sigma 2.0\nh = fspecial('gaussian', [${v} ${v}], 2.0);\n\n% Apply filter\nresult = imfilter(img, h);\nimwrite(result, 'result.jpg');`,
      
      canny_edge: `% Canny Edge Detection\nimg = imread('input.jpg');\ngray = rgb2gray(img);\n\n% Apply Canny with sensitivity threshold ${v/255}\nresult = edge(gray, 'Canny', ${v/255});\nimwrite(result, 'result.jpg');`,
      
      dft: `% Frequency Domain DFT Spectrum\nimg = imread('input.jpg');\ngray = double(rgb2gray(img));\n\n% Compute centered FFT\nF = fftshift(fft2(gray));\n\n% Compute log-magnitude spectrum (gain ${v})\nspec = ${v} * log(abs(F) + 1);\n\n% Normalize and save\nresult = mat2gray(spec);\nimwrite(result, 'result.jpg');`,
      
      sobel: `% Sobel Edge Detection\nimg = imread('input.jpg');\ngray = rgb2gray(img);\n\n% Compute Sobel edges\nresult = edge(gray, 'Sobel');\nimwrite(result, 'result.jpg');`,
    }
  }
}

const OP_CONFIGS = {
    grayscale:     { min: -100, max: 100, step: 1,  default: 0,   label: 'Brightness Offset' },
    histogram_eq:  { min: 1,    max: 10,  step: 1,  default: 2,   label: 'Contrast Limit' },
    gaussian_blur: { min: 3,    max: 31,  step: 2,  default: 11,  label: 'Kernel Size (px)' },
    canny_edge:    { min: 10,   max: 250, step: 5,  default: 150, label: 'Upper Threshold' },
    dft:           { min: 1,    max: 50,  step: 1,  default: 20,  label: 'Spectrum Gain' },
    morphology:    { min: 1,    max: 10,  step: 1,  default: 1,   label: 'Dilation Iterations' },
    sobel:         { min: 1,    max: 7,   step: 2,  default: 3,   label: 'Sobel Kernel Size' },
    wavelet:       { min: 1,    max: 100, step: 1,  default: 20,  label: 'Coeffs to Keep (%)' },
}

export default function ToolCodeExporter() {
  const navigate = useNavigate()
  const [lang, setLang] = useState('python')
  const [op, setOp] = useState('grayscale')
  const [val, setVal] = useState(0)
  const [copied, setCopied] = useState(false)
  
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [resultUrl, setResultUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  const ops = Object.keys(SNIPPETS(0, lang))
  const code = SNIPPETS(val, lang)?.[op] || '# No snippet available'
  const config = OP_CONFIGS[op] || { min:0, max:100, step:1, default:0, label:'Value' }

  useEffect(() => {
    setVal(OP_CONFIGS[op]?.default || 0)
  }, [op])

  useEffect(() => {
    const timer = setTimeout(() => {
        if (file && op) runOperation()
    }, 300)
    return () => clearTimeout(timer)
  }, [file, op, val])

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      const f = e.target.files[0]
      setFile(f)
      setPreviewUrl(URL.createObjectURL(f))
      setResultUrl(null)
    }
  }

  const runOperation = async () => {
    if (!file) return
    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    let endpoint = ''
    if (op === 'grayscale' || op === 'negative') {
        endpoint = '/api/module1/linear_operations'
        formData.append('op', 'brightness')
        formData.append('value', val.toString())
    } else if (op === 'histogram_eq') {
        endpoint = '/api/module2/histogram'
        formData.append('method', 'clahe')
        formData.append('clip', val.toString())
    } else if (op === 'gaussian_blur') {
        endpoint = '/api/module2/smoothing'
        formData.append('ftype', 'gaussian')
        formData.append('ksize', val.toString())
        formData.append('sigma', '2.0')
    } else if (op === 'canny_edge') {
        endpoint = '/api/module5/edge_detection'
        formData.append('detector', 'Canny')
        formData.append('t1', (val/2).toString())
        formData.append('t2', val.toString())
    } else if (op === 'dft') {
        endpoint = '/api/module2/dft'
        formData.append('view', 'magnitude')
    } else if (op === 'morphology') {
        endpoint = '/api/module4/morphology'
        formData.append('op', 'Dilation')
        formData.append('iters', val.toString())
    } else if (op === 'sobel') {
        endpoint = '/api/module5/edge_detection'
        formData.append('detector', 'Sobel (combined)')
        formData.append('ksize', val.toString())
    } else if (op === 'wavelet') {
        endpoint = '/api/module4/wavelets'
        formData.append('wavelet', 'haar')
        formData.append('level', '2')
        formData.append('keep_pct', val.toString())
    }

    try {
      const res = await axios.post(endpoint, formData, { responseType: 'blob' })
      setResultUrl(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const copyCode = () => {
    navigator.clipboard.writeText(code).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000) })
  }

  const download = () => {
    const blob = new Blob([code], { type: 'text/plain' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${op}.${lang === 'python' ? 'py' : 'm'}`; a.click()
  }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1150px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>💻</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Code Exporter</h1>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '30px' }}>
          
          {/* Controls Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* 1. Input */}
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
                <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', color: 'white' }}>1</span>
                    Input Image
                </h3>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
                <div 
                    onClick={() => fileInputRef.current.click()}
                    style={{ 
                        height: '160px', borderRadius: '16px', border: '2px dashed var(--border)', 
                        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                        cursor: 'pointer', overflow: 'hidden', background: 'rgba(255,255,255,0.02)',
                        transition: 'all 0.3s'
                    }}
                >
                    {previewUrl ? (
                        <img src={previewUrl} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                        <>
                            <span style={{ fontSize: '1.8rem', marginBottom: '8px' }}>🖼️</span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 600 }}>Click to upload image</span>
                        </>
                    )}
                </div>
            </div>

            {/* 2. Algorithm */}
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
                <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', color: 'white' }}>2</span>
                    Operation
                </h3>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', background: 'rgba(0,0,0,0.2)', padding: '4px', borderRadius: '12px' }}>
                    {['python', 'matlab'].map(l => (
                    <button key={l} onClick={() => { setLang(l); setOp(Object.keys(SNIPPETS(0, l))[0]) }} style={{ flex: 1, padding: '10px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 800, fontSize: '0.7rem', transition: 'all 0.3s', background: lang === l ? 'var(--blue)' : 'transparent', color: lang === l ? 'white' : 'var(--text-dim)', letterSpacing: '0.05em' }}>
                        {l.toUpperCase()}
                    </button>
                    ))}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    {ops.map(o => (
                    <button key={o} onClick={() => setOp(o)} style={{ padding: '10px 8px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 700, fontSize: '0.7rem', transition: 'all 0.2s', background: op === o ? 'rgba(67,97,238,0.15)' : 'rgba(255,255,255,0.02)', color: op === o ? 'var(--blue)' : 'var(--text-dim)', border: '1px solid ' + (op === o ? 'var(--blue)' : 'transparent'), textAlign: 'center' }}>
                        {o.replace(/_/g, ' ').toUpperCase()}
                    </button>
                    ))}
                </div>
            </div>

            {/* 3. Parameters */}
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
                <h3 style={{ marginTop: 0, marginBottom: '20px', fontFamily: 'var(--font-heading)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', color: 'white' }}>3</span>
                    Parameters
                </h3>
                <div style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                    <label style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-dim)' }}>{config.label}</label>
                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--blue)' }}>{val}</span>
                </div>
                <input 
                    type="range" min={config.min} max={config.max} step={config.step} value={val} 
                    onChange={e => setVal(Number(e.target.value))}
                    style={{ width: '100%', accentColor: 'var(--blue)', cursor: 'pointer' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '0.65rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    <span>{config.min}</span>
                    <span>{config.max}</span>
                </div>
            </div>
          </div>

          {/* Result & Code Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Image Preview */}
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 800 }}>Result Preview</h3>
                    {loading && <div style={{ fontSize: '0.75rem', color: 'var(--blue)', fontWeight: 800, background: 'rgba(67,97,238,0.1)', padding: '4px 12px', borderRadius: '20px', animation: 'pulse 1.5s infinite' }}>PROCESSING</div>}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 700, letterSpacing: '0.05em' }}>ORIGINAL</div>
                        <div style={{ background: '#000', borderRadius: '14px', overflow: 'hidden', aspectRatio: '1/1', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
                            {previewUrl ? <img src={previewUrl} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} /> : <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>No image uploaded</span>}
                        </div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 700, letterSpacing: '0.05em' }}>PROCESSED</div>
                        <div style={{ background: '#000', borderRadius: '14px', overflow: 'hidden', aspectRatio: '1/1', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
                            {resultUrl ? <img src={resultUrl} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} /> : <div style={{ textAlign: 'center', padding: '20px' }}><div style={{ fontSize: '1.2rem', marginBottom: '8px' }}>✨</div><div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Select operation to see result</div></div>}
                        </div>
                    </div>
                </div>
            </div>

            {/* Code Panel */}
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', borderRadius: '24px', overflow: 'hidden', boxShadow: '0 20px 50px rgba(0,0,0,0.3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', background: 'rgba(0,0,0,0.4)', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ display: 'flex', gap: '5px' }}>
                            {[1,2,3].map(i => <div key={i} style={{ width: '9px', height: '9px', borderRadius: '50%', background: i===1 ? '#ff5f56' : i===2 ? '#ffbd2e' : '#27c93f' }} />)}
                        </div>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-dim)', marginLeft: '10px', background: 'rgba(255,255,255,0.05)', padding: '2px 10px', borderRadius: '4px' }}>{op}.{lang === 'python' ? 'py' : 'm'}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button onClick={copyCode} style={{ background: copied ? 'rgba(6,214,160,0.2)' : 'rgba(255,255,255,0.06)', color: copied ? '#06d6a0' : 'var(--text)', border: 'none', padding: '8px 18px', borderRadius: '10px', cursor: 'pointer', fontWeight: 800, fontSize: '0.75rem', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            {copied ? '✅ COPIED' : '📋 COPY CODE'}
                        </button>
                        <button onClick={download} style={{ background: 'var(--blue)', color: 'white', border: 'none', padding: '8px 18px', borderRadius: '10px', cursor: 'pointer', fontWeight: 800, fontSize: '0.75rem', boxShadow: '0 4px 12px rgba(67, 97, 238, 0.3)' }}>DOWNLOAD</button>
                    </div>
                </div>
                <div style={{ position: 'relative' }}>
                    <pre style={{ margin: 0, padding: '28px', fontFamily: 'var(--font-mono)', fontSize: '0.88rem', lineHeight: 1.8, color: '#a5d6ff', background: '#0d1117', overflowX: 'auto', whiteSpace: 'pre' }}>
                        <code>{code}</code>
                    </pre>
                    <div style={{ position: 'absolute', bottom: '15px', right: '20px', fontSize: '0.65rem', color: 'rgba(255,255,255,0.15)', pointerEvents: 'none' }}>Dynamic Snippet Generator</div>
                </div>
            </div>

          </div>
        </div>
      </div>
      <style>{`
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
      `}</style>
    </div>
  )
}
