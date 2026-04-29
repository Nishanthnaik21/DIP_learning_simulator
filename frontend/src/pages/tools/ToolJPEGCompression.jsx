import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ToolJPEGCompression() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [quality, setQuality] = useState(80)
  const [compressedUrl, setCompressedUrl] = useState(null)
  const [originalSize, setOriginalSize] = useState(0)
  const [compressedSize, setCompressedSize] = useState(0)
  const fileInputRef = useRef(null)
  const canvasRef = useRef(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0]
      setFile(f); setOriginalSize(f.size)
      setPreviewUrl(URL.createObjectURL(f)); setCompressedUrl(null)
    }
  }

  const compress = () => {
    if (!previewUrl) return
    const img = new Image()
    img.onload = () => {
      const canvas = canvasRef.current
      canvas.width = img.width; canvas.height = img.height
      canvas.getContext('2d').drawImage(img, 0, 0)
      const dataUrl = canvas.toDataURL('image/jpeg', quality / 100)
      setCompressedUrl(dataUrl)
      setCompressedSize(Math.round((dataUrl.split(',')[1].length * 3) / 4))
    }
    img.src = previewUrl
  }

  const ratio = originalSize > 0 ? Math.round((1 - compressedSize / originalSize) * 100) : 0
  const fmtKB = (b) => b > 102400 ? `${(b/1048576).toFixed(2)} MB` : `${(b/1024).toFixed(1)} KB`
  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>🗜️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>JPEG Compression</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontFamily: 'var(--font-heading)' }}>1. Upload Source</h3>
          <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <button onClick={() => fileInputRef.current.click()} style={{ background: 'var(--blue)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
              Choose File
            </button>
            {file && <span style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>{file.name} · {fmtKB(originalSize)}</span>}
          </div>
        </div>

        {previewUrl && (
          <>
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)' }}>2. Compression Quality</h3>
                <span style={{ background: 'var(--blue)', color: 'white', padding: '4px 12px', borderRadius: '20px', fontWeight: 800, fontSize: '0.9rem' }}>{quality}%</span>
              </div>
              <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '20px' }}>Adjust the quality slider to find the perfect balance between file size and visual fidelity.</p>
              
              <div style={{ padding: '0 10px' }}>
                <input type="range" min="1" max="100" value={quality} onChange={e => setQuality(+e.target.value)} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '8px', fontWeight: 600 }}>
                   <span>HIGH COMPRESSION (LOW QUALITY)</span>
                   <span>LOSSLESS (HIGH QUALITY)</span>
                </div>
              </div>

              <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
                <button onClick={compress} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '12px 28px', borderRadius: '10px', fontWeight: 700, cursor: 'pointer', flex: 1 }}>
                  🗜️ Compress Image
                </button>
                {compressedUrl && (
                  <a href={compressedUrl} download="compressed.jpg" style={{ background: 'rgba(6,214,160,0.15)', color: '#06d6a0', border: '1px solid rgba(6,214,160,0.3)', padding: '12px 28px', borderRadius: '10px', fontWeight: 700, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
                    ⬇️ Download
                  </a>
                )}
              </div>
            </div>

            {compressedUrl && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
                {[
                  { label: 'Original Size', val: fmtKB(originalSize), color: 'var(--blue)' },
                  { label: 'Compressed Size', val: fmtKB(compressedSize), color: 'var(--green)' },
                  { label: 'Space Saved', val: `${ratio}%`, color: 'var(--pink)' }
                ].map((stat) => (
                  <div key={stat.label} style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '20px', borderRadius: '16px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>{stat.label}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 800, color: stat.color }}>{stat.val}</div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div>
                <h4 style={{ marginBottom: '12px', fontSize: '0.9rem', color: 'var(--text-dim)' }}>SOURCE IMAGE</h4>
                <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '12px', borderRadius: '16px' }}>
                  <img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '10px' }} />
                </div>
              </div>
              <div>
                <h4 style={{ marginBottom: '12px', fontSize: '0.9rem', color: 'var(--text-dim)' }}>COMPRESSED (Q={quality}%)</h4>
                <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '12px', borderRadius: '16px' }}>
                  {compressedUrl
                    ? <img src={compressedUrl} alt="Compressed" style={{ width: '100%', borderRadius: '10px' }} />
                    : <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', border: '2px dashed var(--border)', borderRadius: '10px' }}>
                        Click Compress to see result
                      </div>
                  }
                </div>
              </div>
            </div>
          </>
        )}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  )
}
