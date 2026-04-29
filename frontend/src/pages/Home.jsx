import { useEffect, useState, lazy, Suspense } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { dataAPI, openModule, openTool, openStreamlit } from '../utils/api'
import ModuleCard from '../components/ModuleCard'
import ToolCard   from '../components/ToolCard'

const DIPScene = lazy(() => import('../scenes/DIPScene'))

/* ─── Section header ────────────────────────────────── */
function SectionHeader({ title, subtitle, color, id }) {
  return (
    <div id={id} style={{ display:'flex', alignItems:'center', gap:'16px', marginBottom:'12px' }}>
      <div style={{ width:'4px', minWidth:'4px', height:'32px', background:`linear-gradient(180deg,${color},${color}44)`, borderRadius:'2px', boxShadow:`0 0 10px ${color}44` }} />
      <div>
        <h2 style={{ fontSize:'1.4rem', fontWeight:800, color:'var(--text)', fontFamily:'var(--font-heading)', letterSpacing:'-0.01em', lineHeight:1.2 }}>{title}</h2>
        <p style={{ fontSize:'0.78rem', color:'var(--text-dim)', marginTop:'2px' }}>{subtitle}</p>
      </div>
      <div style={{ flex:1, height:'1px', background:`linear-gradient(90deg,${color}33,transparent)` }} />
    </div>
  )
}

/* ─── Stat card ─────────────────────────────────────── */
function StatCard({ icon, label, value, color }) {
  return (
    <div style={{ textAlign:'center', padding:'4px' }}>
      <div style={{ fontSize:'0.68rem', color:'var(--text-dim)', letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:'4px' }}>
        {icon} {label}
      </div>
      <div style={{ fontFamily:'var(--font-heading)', fontSize:'1.4rem', fontWeight:800, color }}>
        {value}
      </div>
    </div>
  )
}

/* ─── Main page ─────────────────────────────────────── */
export default function Home() {
  const { user }    = useAuth()
  const { isDark }  = useTheme()
  const navigate    = useNavigate()
  const [modules,  setModules]  = useState([])
  const [tools,    setTools]    = useState([])
  const [stats,    setStats]    = useState(null)

  useEffect(() => {
    dataAPI.modules().then(r => setModules(r.data.modules)).catch(() => {})
    dataAPI.tools().then(r   => setTools(r.data.tools)).catch(() => {})
    dataAPI.stats().then(r   => setStats(r.data)).catch(() => {})
  }, [])

  return (
    <div style={{ background:'var(--bg)', minHeight:'100vh' }}>

      {/* ════════════════════════════════════════════
          HERO — full-screen Three.js canvas
      ════════════════════════════════════════════ */}
      <section style={{ position:'relative', height:'100vh', overflow:'hidden' }}>
        <div style={{ position:'absolute', inset:0 }}>
          <Suspense fallback={<div style={{ background: isDark ? '#050a14' : '#f0f4f8', position:'absolute', inset:0 }} />}>
            <DIPScene isDark={isDark} />
          </Suspense>
        </div>

        {/* Floating Widgets — Visible only when logged in */}
        {user && stats && (
          <div style={{ position:'absolute', inset:0, zIndex:20, pointerEvents:'none' }}>
            
            {/* Top-Left: Last Tool */}
            <motion.div
              initial={{ opacity:0, x:-20 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.6 }}
              style={{ position:'absolute', top:'100px', left:'40px', pointerEvents:'auto' }}
            >
              <div style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'18px', padding:'12px 18px', backdropFilter:'blur(12px)', display:'flex', alignItems:'center', gap:'12px', boxShadow:'0 8px 32px rgba(0,0,0,0.2)' }}>
                <div style={{ width:'32px', height:'32px', borderRadius:'10px', background:'rgba(67,97,238,0.1)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1rem', color:'var(--blue)' }}>🛠️</div>
                <div>
                  <div style={{ fontSize:'0.6rem', color:'var(--text-dim)', textTransform:'uppercase', fontWeight:800, letterSpacing:'0.05em' }}>Last Tool</div>
                  <div style={{ fontSize:'0.82rem', fontWeight:700, color:'var(--text)' }}>{stats.last_tool || 'None'}</div>
                </div>
              </div>
            </motion.div>

            {/* Top-Right: Images Processed */}
            <motion.div
              initial={{ opacity:0, x:20 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.7 }}
              style={{ position:'absolute', top:'100px', right:'40px', pointerEvents:'auto' }}
            >
              <div style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'18px', padding:'12px 18px', backdropFilter:'blur(12px)', display:'flex', alignItems:'center', gap:'12px', boxShadow:'0 8px 32px rgba(0,0,0,0.2)' }}>
                <div style={{ width:'32px', height:'32px', borderRadius:'10px', background:'rgba(180,79,255,0.1)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1rem', color:'#b44fff' }}>🖼️</div>
                <div>
                  <div style={{ fontSize:'0.6rem', color:'var(--text-dim)', textTransform:'uppercase', fontWeight:800, letterSpacing:'0.05em' }}>Processed</div>
                  <div style={{ fontSize:'0.82rem', fontWeight:700, color:'var(--text)' }}>{stats.total_processed || 0} Images</div>
                </div>
              </div>
            </motion.div>

            {/* Bottom-Left: Recently Used */}
            <motion.div
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.9 }}
              style={{ position:'absolute', bottom:'100px', left:'40px', pointerEvents:'auto' }}
            >
              <div style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'18px', padding:'14px', backdropFilter:'blur(12px)', width:'200px', boxShadow:'0 8px 32px rgba(0,0,0,0.2)' }}>
                <div style={{ fontSize:'0.6rem', color:'var(--text-dim)', textTransform:'uppercase', fontWeight:800, letterSpacing:'0.05em', marginBottom:'8px', display:'flex', alignItems:'center', gap:'6px' }}>
                  <span style={{ width:'4px', height:'4px', borderRadius:'50%', background:'#06d6a0' }}></span> Recently Used
                </div>
                <div style={{ display:'flex', flexDirection:'column', gap:'6px' }}>
                  {(stats.recent_activity || []).slice(0, 2).map((act, i) => (
                    <div key={i} style={{ fontSize:'0.7rem', color:'var(--text)', opacity: 0.9 - (i*0.3), overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>• {act}</div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Bottom-Right: Recommended Tools */}
            <motion.div
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.8 }}
              style={{ position:'absolute', bottom:'100px', right:'40px', pointerEvents:'auto' }}
            >
              <div style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'18px', padding:'16px', backdropFilter:'blur(12px)', width:'220px', boxShadow:'0 8px 32px rgba(0,0,0,0.2)' }}>
                <div style={{ fontSize:'0.65rem', color:'var(--blue)', textTransform:'uppercase', fontWeight:800, letterSpacing:'0.06em', marginBottom:'12px', display:'flex', alignItems:'center', gap:'6px' }}>
                  <span style={{ width:'4px', height:'4px', borderRadius:'50%', background:'var(--blue)' }}></span> Recommended Tools
                </div>
                <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
                  {[
                    { n: 'Super Res',      p: '/tool/superresolution', i: '🚀' },
                    { n: 'Webcam Filter',  p: '/tool/webcam',          i: '📷' },
                    { n: 'Compare Slider', p: '/tool/comparison',      i: '↔️' },
                    { n: 'Code Explainer', p: '/tool/codeexplainer',   i: '📖' }
                  ].map((t, i) => (
                    <div 
                      key={t.n}
                      onClick={() => navigate(t.p)}
                      style={{ fontSize:'0.78rem', color:'var(--text)', display:'flex', alignItems:'center', gap:'10px', cursor:'pointer', padding:'4px 8px', borderRadius:'8px', background:'rgba(255,255,255,0.03)', transition:'all 0.2s' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(67,97,238,0.1)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                    >
                      <span style={{ fontSize:'0.9rem' }}>{t.i}</span> {t.n}
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>

          </div>
        )}

        {/* Content overlay */}
        <div style={{ position:'absolute', inset:0, zIndex:10, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', pointerEvents:'none' }}>
          <motion.div
            initial={{ opacity:0, y:40 }}
            animate={{ opacity:1, y:0 }}
            transition={{ duration:0.85, ease:[0.34,1.56,0.64,1] }}
            style={{ textAlign:'center' }}
          >
            {/* Title */}
            <h1 style={{
              fontFamily:'var(--font-heading)',
              fontSize:'clamp(2.6rem, 7vw, 5rem)', fontWeight:900, lineHeight:1.0,
              background:'linear-gradient(135deg,#4361ee,#b44fff,#4cc9f0,#06d6a0)',
              backgroundSize:'300% 300%',
              WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text',
              animation:'gradient-shift 5s ease infinite',
              marginBottom:'16px', letterSpacing:'-0.02em',
            }}>
              DIP Learning<br />Simulator
            </h1>

            {/* CTA */}
            {!user && (
              <motion.button
                whileHover={{ scale:1.05 }}
                whileTap={{ scale:0.95 }}
                onClick={() => navigate('/login')}
                style={{
                  pointerEvents:'auto',
                  marginTop:'10px',
                  padding:'12px 32px',
                  background:'linear-gradient(135deg, #4361ee, #7209b7)',
                  color:'white',
                  border:'none',
                  borderRadius:'12px',
                  fontFamily:'var(--font-heading)',
                  fontSize:'1rem',
                  fontWeight:700,
                  cursor:'pointer',
                  boxShadow:'0 8px 24px rgba(67,97,238,0.4)',
                }}
              >
                🚀 Sign In to Explore
              </motion.button>
            )}
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity:0 }} animate={{ opacity:1 }}
            transition={{ delay:1.5 }}
            style={{ position:'absolute', bottom:'28px', display:'flex', flexDirection:'column', alignItems:'center', gap:'6px', color:'rgba(230,237,243,0.3)', animation:'scroll-bounce 2s ease-in-out infinite', pointerEvents:'none' }}
          >
            <span style={{ fontSize:'0.66rem', letterSpacing:'0.15em', textTransform:'uppercase' }}>Scroll</span>
            <svg width="18" height="22" viewBox="0 0 18 22" fill="none">
              <path d="M9 4L9 16M9 16L3 10M9 16L15 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </motion.div>
        </div>
      </section>

      {/* ════════════════════════════════════════════
          DASHBOARD — Quick Stats & Activity
      ════════════════════════════════════════════ */}
      {user && stats && (
        <section style={{ padding:'40px 32px 0', maxWidth:'1400px', margin:'0 auto' }}>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))', gap:'20px' }}>
            
            {/* Widget: Last Tool */}
            <motion.div 
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
              style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'24px', padding:'24px', display:'flex', alignItems:'center', gap:'20px', boxShadow:'0 10px 30px rgba(0,0,0,0.1)' }}
            >
              <div style={{ width:'56px', height:'56px', borderRadius:'16px', background:'rgba(67,97,238,0.1)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.5rem', color:'var(--blue)', border:'1px solid rgba(67,97,238,0.2)' }}>
                🛠️
              </div>
              <div>
                <div style={{ fontSize:'0.7rem', color:'var(--text-dim)', letterSpacing:'0.1em', textTransform:'uppercase', fontWeight:700, marginBottom:'4px' }}>Last Used Tool</div>
                <div style={{ fontSize:'1.1rem', fontWeight:800, color:'var(--text)' }}>{stats.last_tool || 'None'}</div>
              </div>
            </motion.div>

            {/* Widget: Images Processed */}
            <motion.div 
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.1 }}
              style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'24px', padding:'24px', display:'flex', alignItems:'center', gap:'20px', boxShadow:'0 10px 30px rgba(0,0,0,0.1)' }}
            >
              <div style={{ width:'56px', height:'56px', borderRadius:'16px', background:'rgba(180,79,255,0.1)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.5rem', color:'#b44fff', border:'1px solid rgba(180,79,255,0.2)' }}>
                🖼️
              </div>
              <div>
                <div style={{ fontSize:'0.7rem', color:'var(--text-dim)', letterSpacing:'0.1em', textTransform:'uppercase', fontWeight:700, marginBottom:'4px' }}>Images Processed</div>
                <div style={{ fontSize:'1.5rem', fontWeight:900, color:'var(--text)' }}>{stats.total_processed || 0}</div>
              </div>
            </motion.div>

            {/* Widget: Avg PSNR */}
            <motion.div 
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.2 }}
              style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'24px', padding:'24px', display:'flex', alignItems:'center', gap:'20px', boxShadow:'0 10px 30px rgba(0,0,0,0.1)' }}
            >
              <div style={{ width:'56px', height:'56px', borderRadius:'16px', background:'rgba(76,201,240,0.1)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.5rem', color:'#4cc9f0', border:'1px solid rgba(76,201,240,0.2)' }}>
                📉
              </div>
              <div>
                <div style={{ fontSize:'0.7rem', color:'var(--text-dim)', letterSpacing:'0.1em', textTransform:'uppercase', fontWeight:700, marginBottom:'4px' }}>Avg PSNR Quality</div>
                <div style={{ fontSize:'1.5rem', fontWeight:900, color:'var(--text)' }}>{stats.avg_psnr || 0} <small style={{ fontSize:'0.8rem', fontWeight:500, opacity:0.5 }}>dB</small></div>
              </div>
            </motion.div>

            {/* Widget: Recent Activity */}
            <motion.div 
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.3 }}
              style={{ background:'var(--bg-glass)', border:'1px solid var(--border)', borderRadius:'24px', padding:'20px 24px', gridColumn:'span 1', display:'flex', flexDirection:'column', boxShadow:'0 10px 30px rgba(0,0,0,0.1)' }}
            >
              <div style={{ fontSize:'0.7rem', color:'var(--text-dim)', letterSpacing:'0.1em', textTransform:'uppercase', fontWeight:700, marginBottom:'12px', display:'flex', alignItems:'center', gap:'8px' }}>
                <span style={{ width:'6px', height:'6px', borderRadius:'50%', background:'#06d6a0' }}></span>
                Recent Activity
              </div>
              <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
                {stats.recent_activity && stats.recent_activity.length > 0 ? (
                  stats.recent_activity.map((act, i) => (
                    <div key={i} style={{ fontSize:'0.78rem', color:'var(--text)', display:'flex', alignItems:'center', gap:'8px', opacity: 1 - (i * 0.15) }}>
                      <span style={{ color:'var(--blue)', fontSize:'0.8rem' }}>•</span> {act}
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize:'0.78rem', color:'var(--text-dim)', fontStyle:'italic' }}>No recent activity</div>
                )}
              </div>
            </motion.div>

          </div>
        </section>
      )}

      {/* ════════════════════════════════════════════
          BASIC STATS BAR (Public)
      ════════════════════════════════════════════ */}
      {!user && stats && (
        <section style={{ background:'var(--bg-glass)', borderTop:'1px solid var(--border)', backdropFilter:'blur(12px)', marginTop: '40px' }}>
          <div style={{ maxWidth:'1200px', margin:'0 auto', padding:'22px 32px', display:'flex', justifyContent:'space-around', flexWrap:'wrap', gap:'16px' }}>
            <StatCard icon="📚" label="Modules"     value={stats.modules}        color="#4361ee" />
            <StatCard icon="🛠️" label="Tools"       value={stats.tools}          color="#b44fff" />
            <StatCard icon="📄" label="Pages"       value={stats.pages}          color="#4cc9f0" />
            <StatCard icon="👥" label="Users"       value={stats.users}          color="#06d6a0" />
          </div>
        </section>
      )}

      {!user && (
        <section style={{ padding:'60px 20px', textAlign:'center', background:'var(--bg-glass)', borderTop:'1px solid var(--border)', borderBottom:'1px solid var(--border)' }}>
           <h3 style={{ fontFamily:'var(--font-heading)', fontSize:'1.5rem', marginBottom:'12px' }}>Ready to start learning?</h3>
           <p style={{ color:'var(--text-dim)', marginBottom:'24px' }}>Sign in to access all 5 modules and 18 specialized tools.</p>
           <button onClick={() => navigate('/login')} style={{ padding:'12px 28px', background:'var(--blue)', color:'white', border:'none', borderRadius:'10px', fontWeight:700, cursor:'pointer' }}>
              Sign In Now
           </button>
        </section>
      )}

      {/* ════════════════════════════════════════════
          MODULES SECTION
      ════════════════════════════════════════════ */}
      <section id="modules" style={{ padding:'80px 32px 0', maxWidth:'1400px', margin:'0 auto' }}>
        <SectionHeader title="Course Modules" subtitle="5 comprehensive DIP modules" color="#4361ee" id="modules-header" />
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))', gap:'20px', marginTop:'28px' }}>
          {modules.map((mod, i) => (
            <motion.div key={mod.id}
              initial={{ opacity:0, y:30 }} whileInView={{ opacity:1, y:0 }}
              viewport={{ once:true }} transition={{ delay:i * 0.09, duration:0.5 }}
              style={{ height:'100%' }}
            >
              <ModuleCard module={mod} onOpen={() => openModule(navigate, mod.streamlit_page)} />
            </motion.div>
          ))}
        </div>
        {!user && modules.length === 0 && (
          <div style={{ textAlign:'center', padding:'40px', color:'var(--text-dim)', background:'rgba(255,255,255,0.02)', borderRadius:'12px', marginTop:'20px', border:'1px dashed var(--border)' }}>
             Please <span style={{ color:'var(--blue)', cursor:'pointer', fontWeight:600 }} onClick={() => navigate('/login')}>Sign In</span> to view module content.
          </div>
        )}
      </section>

      {/* ════════════════════════════════════════════
          TOOLS SECTION
      ════════════════════════════════════════════ */}
      <section id="tools" style={{ padding:'64px 32px 0', maxWidth:'1400px', margin:'0 auto' }}>
        <SectionHeader title="Tools & Features" subtitle="18 specialized DIP tools" color="#b44fff" id="tools-header" />
        
        {[
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
        ].map((cat, catIdx) => (
          <div key={cat.group} style={{ marginTop: '42px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '18px' }}>
              <div style={{ width: '4px', height: '18px', background: 'linear-gradient(180deg, #b44fff, transparent)', borderRadius: '2px' }} />
              <h3 style={{ 
                fontSize: '0.85rem', 
                fontWeight: 800, 
                color: 'var(--text)', 
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                opacity: 0.9,
                fontFamily: 'var(--font-heading)'
              }}>
                {cat.group}
              </h3>
              <div style={{ flex: 1, height: '1px', background: 'linear-gradient(90deg, var(--border), transparent)', opacity: 0.4 }} />
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(170px, 1fr))', gap:'14px' }}>
              {cat.items.map((itemName, i) => {
                const tool = tools.find(t => t.name === itemName);
                if (!tool) return null;
                return (
                  <motion.div key={tool.id}
                    initial={{ opacity:0, y: 10 }} whileInView={{ opacity:1, y: 0 }}
                    viewport={{ once:true }} transition={{ delay:i * 0.04, duration:0.4 }}
                  >
                    <ToolCard tool={tool} onOpen={() => openTool(navigate, tool.page)} />
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
        {!user && tools.length === 0 && (
          <div style={{ textAlign:'center', padding:'40px', color:'var(--text-dim)', background:'rgba(255,255,255,0.02)', borderRadius:'12px', marginTop:'20px', border:'1px dashed var(--border)' }}>
             Please <span style={{ color:'var(--blue)', cursor:'pointer', fontWeight:600 }} onClick={() => navigate('/login')}>Sign In</span> to view tools.
          </div>
        )}
      </section>

      {/* ════════════════════════════════════════════
          QUICK START
      ════════════════════════════════════════════ */}
      <section style={{ padding:'64px 32px 80px', maxWidth:'1200px', margin:'0 auto' }}>
        <SectionHeader title="Quick Start" subtitle="Get up and running in 6 steps" color="#4cc9f0" />
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(160px, 1fr))', gap:'15px', marginTop:'28px' }}>
          {[
            { n:'01', t:'Choose Image',   d:'Pick from 10 samples or upload your own',   c:'#4361ee' },
            { n:'02', t:'Select Module',  d:'Navigate to any of 5 course modules',        c:'#b44fff' },
            { n:'03', t:'Experiment',     d:'Adjust sliders — see results instantly',     c:'#4cc9f0' },
            { n:'04', t:'Compare',        d:'Drag-compare before/after with slider',      c:'#f8961e' },
            { n:'05', t:'Export',         d:'Download PDF, code, GIF, or session',        c:'#ff3366' },
            { n:'06', t:'Quiz',           d:'Test knowledge with 25 MCQs',               c:'#06d6a0' },
          ].map(({ n, t, d, c }, i) => (
            <motion.div key={n}
              initial={{ opacity:0, y:18 }} whileInView={{ opacity:1, y:0 }}
              viewport={{ once:true }} transition={{ delay:i * 0.06 }}
              style={{ background:'rgba(255,255,255,0.02)', border:`1px solid ${c}18`, borderRadius:'14px', padding:'20px 16px', textAlign:'center' }}
            >
              <div style={{ width:'40px', height:'40px', borderRadius:'11px', background:`${c}12`, border:`1.5px solid ${c}30`, display:'flex', alignItems:'center', justifyContent:'center', margin:'0 auto 12px', fontFamily:'var(--font-mono)', fontWeight:700, color:c, fontSize:'0.88rem' }}>{n}</div>
              <div style={{ fontWeight:700, fontSize:'0.84rem', marginBottom:'6px', color:'var(--text)' }}>{t}</div>
              <div style={{ fontSize:'0.7rem', color:'var(--text-dim)', lineHeight:1.5 }}>{d}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ════════════════════════════════════════════
          FOOTER
      ════════════════════════════════════════════ */}
      <footer style={{ borderTop:'1px solid var(--border)', padding:'22px 32px', display:'flex', justifyContent:'space-between', flexWrap:'wrap', gap:'10px', color:'var(--text-dim)', fontSize:'0.72rem', fontFamily:'var(--font-mono)', background:'var(--bg-elevated)' }}>
        <span>DIP Learning Simulator</span>
        <span>Simulator Backend + 3D Interface</span>
        <span>24 pages · 18 tools · Dual-Theme</span>
      </footer>
    </div>
  )
}
