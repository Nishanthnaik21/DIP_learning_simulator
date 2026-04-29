import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const EXPLAIN_MAP = {
  // Python / OpenCV
  'cv2.imread': 'Loads an image from the specified file path.',
  'cv2.cvtColor': 'Converts an image from one color space to another (e.g., BGR to Grayscale).',
  'cv2.GaussianBlur': 'Smoothes an image using a Gaussian filter to reduce noise and detail.',
  'cv2.Canny': 'Finds edges in an image using the multi-stage Canny edge detection algorithm.',
  'cv2.threshold': 'Applies a fixed-level threshold to each array element.',
  'cv2.adaptiveThreshold': 'Applies a threshold that varies across the image based on local neighborhood.',
  'cv2.Sobel': 'Calculates image derivatives using an extended Sobel operator.',
  'cv2.Laplacian': 'Calculates the Laplacian of an image (second-order derivative).',
  'cv2.dilate': 'Expands the bright regions in an image (morphological dilation).',
  'cv2.erode': 'Shrinks the bright regions in an image (morphological erosion).',
  'cv2.morphologyEx': 'Performs advanced morphological transformations like Opening or Closing.',
  'cv2.findContours': 'Retrieves contours from a binary image.',
  'cv2.drawContours': 'Draws contour outlines or filled contours.',
  'cv2.equalizeHist': 'Equalizes the histogram of a grayscale image to improve contrast.',
  'cv2.createCLAHE': 'Creates a CLAHE (Contrast Limited Adaptive Histogram Equalization) object.',
  'np.fft.fft2': 'Computes the 2-Dimensional Discrete Fourier Transform.',
  'np.fft.fftshift': 'Shifts the zero-frequency component to the center of the spectrum.',
  'cv2.normalize': 'Normalizes the range of values in an array (e.g., to 0-255).',
  'cv2.imwrite': 'Saves the image to a file.',
  'import cv2': 'Imports the OpenCV library for computer vision tasks.',
  'import numpy as np': 'Imports NumPy for numerical operations and array handling.',
  'plt.imshow': 'Displays an image using Matplotlib.',
  
  // Matlab
  'imread': 'Reads an image from a file into a matrix.',
  'rgb2gray': 'Converts an RGB image or colormap to grayscale.',
  'fspecial': 'Creates a predefined 2-D filter (e.g., gaussian, laplacian).',
  'imfilter': 'Filters a multidimensional array with a given kernel.',
  'edge': 'Finds edges in an intensity image (e.g., Canny, Sobel).',
  'fft2': 'Computes the 2-D Discrete Fourier Transform.',
  'fftshift': 'Shifts the zero-frequency component to the center of the spectrum.',
  'imshow': 'Displays an image in a figure window.',
  'imwrite': 'Writes an image to a file.',
  'histeq': 'Enhances contrast using Histogram Equalization.',
  'imdilate': 'Performs morphological dilation on an image.',
  'imerode': 'Performs morphological erosion on an image.',
}

export default function ToolCodeExplainer() {
  const navigate = useNavigate()
  const [code, setCode] = useState(`import cv2\nimport numpy as np\n\n# Load image\nimg = cv2.imread('input.jpg')\n\n# Preprocess\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\nblurred = cv2.GaussianBlur(gray, (5, 5), 0)\n\n# Detect edges\nedges = cv2.Canny(blurred, 50, 150)\n\n# Save result\ncv2.imwrite('result.jpg', edges)`)
  const [lang, setLang] = useState('python')
  const [results, setResults] = useState(null)
  const [activeLine, setActiveLine] = useState(null)

  const explainCode = () => {
    const lines = code.split('\n')
    const explanation = lines.map((line, idx) => {
      let detail = 'Generic code line.'
      const trimmed = line.trim()
      
      if (trimmed.startsWith('#') || trimmed.startsWith('%') || trimmed.startsWith('//')) {
        detail = 'Comment line providing context or documentation.'
      } else {
        // Simple heuristic matcher
        for (const [func, desc] of Object.entries(EXPLAIN_MAP)) {
          if (trimmed.includes(func)) {
            detail = desc
            break
          }
        }
      }

      return {
        id: idx,
        text: line,
        explanation: detail
      }
    })

    setResults({
      lines: explanation,
      summary: `This ${lang} script performs image processing. It likely involves loading an image, applying some transformations (like filtering or edge detection), and saving the result.`
    })
  }

  return (
    <div className="with-navbar" style={{ minHeight:'100vh', padding:'40px 32px 80px', background:'var(--bg)', color:'var(--text)' }}>
      <div style={{ maxWidth:'1200px', margin:'0 auto' }}>
        
        {/* Header */}
        <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background:'transparent', border:'1px solid var(--border)', color:'var(--text)', padding:'6px 12px', borderRadius:'8px', cursor:'pointer' }}>← Back</button>
          <span style={{ fontSize:'2rem' }}>📖</span>
          <h1 style={{ fontFamily:'var(--font-heading)', fontWeight:800, margin:0 }}>Code Explainer</h1>
        </div>

        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'30px' }}>
          
          {/* Left: Input */}
          <div style={{ display:'flex', flexDirection:'column', gap:'20px' }}>
            <div style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', padding:'24px', borderRadius:'24px', height:'100%', display:'flex', flexDirection:'column' }}>
                <h3 style={{ marginTop:0, marginBottom:'20px', fontFamily:'var(--font-heading)', fontSize:'1rem' }}>Source Code</h3>
                
                <div style={{ display:'flex', gap:'8px', marginBottom:'16px' }}>
                    {['python', 'matlab'].map(l => (
                        <button key={l} onClick={() => setLang(l)} style={{ padding:'6px 16px', borderRadius:'8px', border:'none', cursor:'pointer', fontWeight:700, fontSize:'0.75rem', background: lang === l ? 'var(--blue)' : 'rgba(255,255,255,0.05)', color: lang === l ? 'white' : 'var(--text-dim)' }}>
                            {l.toUpperCase()}
                        </button>
                    ))}
                </div>

                <textarea 
                    value={code}
                    onChange={e => setCode(e.target.value)}
                    style={{
                        flex:1, minHeight:'400px', background:'#0d1117', border:'1px solid var(--border)', borderRadius:'12px', padding:'20px', color:'#a5d6ff', fontFamily:'var(--font-mono)', fontSize:'0.9rem', lineHeight:1.6, outline:'none', resize:'none'
                    }}
                    placeholder="Paste your code here..."
                />

                <button 
                    onClick={explainCode}
                    style={{ marginTop:'20px', padding:'14px', background:'var(--blue)', color:'white', border:'none', borderRadius:'12px', fontWeight:700, cursor:'pointer', boxShadow:'0 8px 24px rgba(67,97,238,0.3)' }}
                >
                    Explain Code ✨
                </button>
            </div>
          </div>

          {/* Right: Explanation */}
          <div style={{ display:'flex', flexDirection:'column', gap:'20px' }}>
            <div style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', padding:'24px', borderRadius:'24px', height:'100%', overflow:'hidden', display:'flex', flexDirection:'column' }}>
                <h3 style={{ marginTop:0, marginBottom:'20px', fontFamily:'var(--font-heading)', fontSize:'1rem' }}>Line-by-Line Explanation</h3>
                
                {!results ? (
                    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', color:'var(--text-dim)', textAlign:'center', opacity:0.6 }}>
                        <div style={{ fontSize:'2.5rem', marginBottom:'12px' }}>💡</div>
                        <p style={{ fontSize:'0.85rem' }}>Paste your code on the left and click "Explain Code" to see how it works line-by-line.</p>
                    </div>
                ) : (
                    <div style={{ flex:1, overflowY:'auto', paddingRight:'10px' }} className="custom-scrollbar">
                        <div style={{ background:'rgba(6,214,160,0.05)', border:'1px solid rgba(6,214,160,0.15)', borderRadius:'12px', padding:'16px', marginBottom:'24px' }}>
                            <div style={{ fontSize:'0.65rem', fontWeight:800, color:'#06d6a0', letterSpacing:'0.1em', marginBottom:'6px' }}>SUMMARY</div>
                            <div style={{ fontSize:'0.85rem', color:'var(--text)', lineHeight:1.5 }}>{results.summary}</div>
                        </div>

                        <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
                            {results.lines.map((item, i) => (
                                <motion.div 
                                    key={i}
                                    initial={{ opacity:0, x:10 }} animate={{ opacity:1, x:0 }} transition={{ delay: i * 0.03 }}
                                    onMouseEnter={() => setActiveLine(i)}
                                    onMouseLeave={() => setActiveLine(null)}
                                    style={{
                                        padding:'12px 16px', borderRadius:'12px', background: activeLine === i ? 'rgba(67,97,238,0.08)' : 'rgba(255,255,255,0.02)', border:'1px solid ' + (activeLine === i ? 'rgba(67,97,238,0.2)' : 'transparent'), transition:'all 0.2s', cursor:'default'
                                    }}
                                >
                                    <div style={{ fontFamily:'var(--font-mono)', fontSize:'0.75rem', color: activeLine === i ? 'var(--blue)' : 'var(--text-dim)', marginBottom:'6px', whiteSpace:'pre', overflow:'hidden', textOverflow:'ellipsis' }}>
                                        {item.text || ' '}
                                    </div>
                                    <div style={{ fontSize:'0.82rem', color:'var(--text)', lineHeight:1.4 }}>
                                        {item.explanation}
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
          </div>

        </div>
      </div>
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); borderRadius: 10px; }
      `}</style>
    </div>
  )
}
