import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { dataAPI, openModule } from '../utils/api'
import ModuleCard from '../components/ModuleCard'

export default function Modules() {
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    dataAPI.modules()
      .then(r => setModules(r.data.modules))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="with-navbar" style={{ minHeight:'100vh', padding:'40px 32px 80px' }}>
      <div style={{ maxWidth:'1300px', margin:'0 auto' }}>

        {/* Header */}
        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.5 }}>
          <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'8px' }}>
            <span style={{ fontSize:'2rem' }}>📚</span>
            <h1 style={{
              fontFamily:'var(--font-heading)', fontWeight:900,
              fontSize:'clamp(1.8rem, 4vw, 3rem)', letterSpacing:'-0.02em',
              background:'linear-gradient(135deg,#4361ee,#b44fff)',
              WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text',
            }}>Course Modules</h1>
          </div>
        </motion.div>

        {/* Module cards */}
        {loading ? (
          <div style={{ textAlign:'center', padding:'60px', color:'var(--text-dim)' }}>Loading modules…</div>
        ) : (
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(min(100%, 340px), 1fr))', gap:'24px' }}>
            {modules.map((mod, i) => (
              <motion.div key={mod.id}
                initial={{ opacity:0, y:30 }} animate={{ opacity:1, y:0 }}
                transition={{ delay:i * 0.1, duration:0.5 }}
                style={{ height:'100%' }}
              >
                <ModuleCard
                  module={mod}
                  onOpen={() => openModule(navigate, mod.streamlit_page)}
                />
              </motion.div>
            ))}
          </div>
        )}

        {/* Info banner */}
        <motion.div
          initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:0.8 }}
          style={{ marginTop:'48px', background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'14px', padding:'20px 24px', display:'flex', gap:'14px', alignItems:'flex-start' }}
        >
          <span style={{ fontSize:'1.4rem', lineHeight:1 }}>💡</span>
          <div>
            <div style={{ fontWeight:700, color:'#4361ee', marginBottom:'4px', fontFamily:'var(--font-heading)', fontSize:'0.9rem' }}>How to use modules</div>
            <p style={{ color:'var(--text-dim)', fontSize:'0.82rem', lineHeight:1.6 }}>
              Each module opens the Streamlit DIP Simulator right here — no new tab needed.
              Log in with the same credentials (admin / student / guest). The simulator provides
              interactive sliders, real-time image processing, quizzes and PDF lab report generation.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
