import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { dataAPI, openTool } from '../utils/api'
import ToolCard from '../components/ToolCard'


export default function Tools() {
  const [tools,   setTools]   = useState([])
  const [filter,  setFilter]  = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    dataAPI.tools()
      .then(r => setTools(r.data.tools))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() =>
    tools.filter(t => {
      const matchText  = !filter || t.name.toLowerCase().includes(filter.toLowerCase()) || t.desc.toLowerCase().includes(filter.toLowerCase())
      return matchText
    }), [tools, filter]
  )

  return (
    <div className="with-navbar" style={{ minHeight:'100vh', padding:'40px 32px 80px' }}>
      <div style={{ maxWidth:'1300px', margin:'0 auto' }}>

        {/* Header */}
        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}>
          <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'8px' }}>
            <span style={{ fontSize:'2rem' }}>🛠️</span>
            <h1 style={{
              fontFamily:'var(--font-heading)', fontWeight:900,
              fontSize:'clamp(1.8rem, 4vw, 3rem)', letterSpacing:'-0.02em',
              background:'linear-gradient(135deg,#b44fff,#4cc9f0)',
              WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text',
            }}>Tools & Features</h1>
          </div>
          <p style={{ color:'var(--text-dim)', fontSize:'0.9rem', maxWidth:'600px', marginBottom:'28px' }}>
            18 specialized DIP tools — from quiz and lab reports to optical flow and forgery detection.
            Each opens inline in the Simulator.
          </p>

          {/* Search + color filter */}
          <div style={{ display:'flex', gap:'12px', marginBottom:'32px', flexWrap:'wrap', alignItems:'center' }}>
            <input
              placeholder="🔍  Search tools…"
              value={filter}
              onChange={e => setFilter(e.target.value)}
              style={{
                background:'var(--bg-glass)', border:'1px solid var(--border)',
                borderRadius:'12px', padding:'10px 16px',
                color:'var(--text)', fontSize:'0.88rem', outline:'none',
                fontFamily:'var(--font-body)', minWidth:'220px', flex:'1', maxWidth:'400px',
              }}
            />
          </div>
        </motion.div>

        {/* Tool count */}
        <div style={{ fontSize:'0.76rem', color:'var(--text-dim)', marginBottom:'16px', fontFamily:'var(--font-mono)' }}>
          Showing {filtered.length} of {tools.length} tools
        </div>

        {/* Grid by Categories */}
        {loading ? (
          <div style={{ textAlign:'center', padding:'60px', color:'var(--text-dim)' }}>Loading tools…</div>
        ) : (
          [
            { 
              group: "Image Processing & Enhancement", 
              items: ["Super Res", "Webcam Filter", "JPEG DCT", "Batch Processor"] 
            },
            { 
              group: "Analysis & Feature Extraction", 
              items: ["Shape Analysis", "Optical Flow", "Template Mat", "PSNR Metrics"] 
            },
            { 
              group: "Visualization & Comparison", 
              items: ["Compare Slider", "GIF Animator", "Stitching"] 
            },
            { 
              group: "Utilities & Output", 
              items: ["Lab Report", "Code Exporter", "Session Log"] 
            },
            { 
              group: "Learning & Experimentation", 
              items: ["DIP Quiz", "Params Lab", "Code Explainer"] 
            },
            { 
              group: "Forensics & Document Processing", 
              items: ["Doc Scanner", "ELA Forensics"] 
            }
          ].map((cat, catIdx) => {
            const catTools = filtered.filter(t => cat.items.includes(t.name));
            if (catTools.length === 0 && (filter || color !== 'All')) return null;
            if (catTools.length === 0 && !filter && color === 'All') {
                // If we are showing all and this category is empty (maybe names changed?), we should still handle it or skip
                return null;
            }

            return (
              <div key={cat.group} style={{ marginBottom: '48px' }}>
                <h3 style={{ 
                  fontSize: '0.95rem', 
                  fontWeight: 700, 
                  color: 'var(--text)', 
                  marginBottom: '20px', 
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  fontFamily: 'var(--font-heading)'
                }}>
                  <div style={{ width: '4px', height: '18px', borderRadius: '2px', background: 'linear-gradient(180deg, #b44fff, #4cc9f0)' }} />
                  {cat.group}
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 400, marginLeft: 'auto' }}>
                    {catTools.length} tool{catTools.length !== 1 ? 's' : ''}
                  </span>
                </h3>
                <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(175px, 1fr))', gap:'16px' }}>
                  {cat.items.map((itemName, i) => {
                    const tool = filtered.find(t => t.name === itemName);
                    if (!tool) return null;
                    return (
                      <motion.div key={tool.id}
                        initial={{ opacity:0, scale:0.94 }} animate={{ opacity:1, scale:1 }}
                        transition={{ delay:i * 0.03, duration:0.3 }}
                      >
                        <ToolCard tool={tool} onOpen={() => openTool(navigate, tool.page)} />
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            );
          })
        )}

        {!loading && filtered.length === 0 && (
          <div style={{ textAlign:'center', padding:'60px', color:'var(--text-dim)' }}>No tools match your search.</div>
        )}
      </div>
    </div>
  )
}
