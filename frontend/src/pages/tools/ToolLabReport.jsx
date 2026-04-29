import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export default function ToolLabReport() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [experiments, setExperiments] = useState([])
  const [title, setTitle] = useState('')
  const [aim, setAim] = useState('')
  const [theory, setTheory] = useState('')
  const [result, setResult] = useState('')
  const [module, setModule] = useState('Module 1')
  const [editIdx, setEditIdx] = useState(null)

  const MODULES = ['Module 1: Image Fundamentals', 'Module 2: Spatial & Frequency Filters', 'Module 3: Image Restoration', 'Module 4: Color & Morphology', 'Module 5: Segmentation & Features']

  const save = () => {
    if (!title.trim()) return
    const entry = { title, module, aim, theory, result, date: new Date().toLocaleDateString(), user: user?.username || 'Student' }
    if (editIdx !== null) {
      setExperiments(prev => prev.map((e, i) => i === editIdx ? entry : e))
      setEditIdx(null)
    } else {
      setExperiments(prev => [...prev, entry])
    }
    setTitle(''); setAim(''); setTheory(''); setResult('')
  }

  const edit = (i) => {
    const e = experiments[i]
    setTitle(e.title); setModule(e.module); setAim(e.aim); setTheory(e.theory); setResult(e.result)
    setEditIdx(i)
  }

  const del = (i) => setExperiments(prev => prev.filter((_, j) => j !== i))

  const printReport = () => window.print()

  const inp = { background: 'var(--bg)', color: 'var(--text)', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', width: '100%', fontFamily: 'var(--font-body)', fontSize: '0.93rem', resize: 'vertical' }
  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>📋</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Lab Report Builder</h1>
          {experiments.length > 0 && <button onClick={printReport} style={{ marginLeft: 'auto', background: 'rgba(67,97,238,0.15)', color: '#4361ee', border: '1px solid rgba(67,97,238,0.3)', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>🖨️ Print</button>}
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '24px', fontFamily: 'var(--font-heading)', fontSize: '1.4rem' }}>{editIdx !== null ? '✏️ EDIT EXPERIMENT ENTRY' : '➕ COMPOSE NEW ENTRY'}</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', display: 'block', marginBottom: '8px', letterSpacing: '0.05em' }}>EXPERIMENT NOMENCLATURE</label>
              <input value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Canny Edge Optimization" style={{ ...inp, background: 'rgba(0,0,0,0.2)', padding: '12px 16px' }} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', display: 'block', marginBottom: '8px', letterSpacing: '0.05em' }}>SIMULATOR MODULE</label>
              <select value={module} onChange={e => setModule(e.target.value)} style={{ ...inp, background: 'rgba(0,0,0,0.2)', padding: '12px 16px' }}>{MODULES.map(m => <option key={m}>{m}</option>)}</select>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '32px' }}>
            {[
               { l: 'PRIMARY OBJECTIVE (AIM)', v: aim, s: setAim, r: 2 },
               { l: 'THEORETICAL FRAMEWORK', v: theory, s: setTheory, r: 4 },
               { l: 'EMPIRICAL OBSERVATIONS', v: result, s: setResult, r: 4 }
            ].map((field) => (
              <div key={field.l}>
                <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-dim)', display: 'block', marginBottom: '8px', letterSpacing: '0.05em' }}>{field.l}</label>
                <textarea value={field.v} onChange={e => field.s(e.target.value)} rows={field.r} placeholder={`Document ${field.l.toLowerCase()}...`} style={{ ...inp, background: 'rgba(0,0,0,0.2)', padding: '16px' }} />
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={save} disabled={!title.trim()} style={{ background: 'var(--blue)', color: 'white', border: 'none', padding: '12px 32px', borderRadius: '12px', fontWeight: 800, cursor: 'pointer', opacity: title.trim() ? 1 : 0.5, transition: 'all 0.2s' }}>
              {editIdx !== null ? 'UPDATE RECORD' : 'APPEND TO REPORT'}
            </button>
            {editIdx !== null && (
               <button onClick={() => { setEditIdx(null); setTitle(''); setAim(''); setTheory(''); setResult('') }} style={{ background: 'transparent', color: 'var(--text-dim)', border: '1px solid var(--border)', padding: '12px 24px', borderRadius: '12px', cursor: 'pointer', fontWeight: 700 }}>
                  CANCEL
               </button>
            )}
          </div>
        </div>

        {experiments.length === 0 ? (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '100px 20px', borderRadius: '24px', textAlign: 'center', color: 'var(--text-dim)' }}>
             <div style={{ fontSize: '3.5rem', marginBottom: '24px' }}>📋</div>
             <h2 style={{ fontFamily: 'var(--font-heading)', color: 'var(--text)' }}>Report Workspace Empty</h2>
             <p>Start documenting your digital image processing findings to generate a professional PDF lab report.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {experiments.map((exp, i) => (
              <div key={i} style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px', position: 'relative' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid var(--border)' }}>
                  <div>
                    <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)', fontSize: '1.3rem' }}>EXP {i + 1}: {exp.title.toUpperCase()}</h3>
                    <div style={{ fontSize: '0.75rem', color: 'var(--cyan)', marginTop: '6px', fontWeight: 800, letterSpacing: '0.05em' }}>
                       {exp.module.toUpperCase()} &nbsp;·&nbsp; {exp.date} &nbsp;·&nbsp; {exp.user.toUpperCase()}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => edit(i)} style={{ background: 'rgba(67,97,238,0.1)', color: 'var(--blue)', border: 'none', padding: '10px', borderRadius: '10px', cursor: 'pointer', fontWeight: 800, fontSize: '0.8rem' }}>EDIT</button>
                    <button onClick={() => del(i)} style={{ background: 'rgba(255,51,102,0.1)', color: 'var(--pink)', border: 'none', padding: '10px', borderRadius: '10px', cursor: 'pointer', fontWeight: 800, fontSize: '0.8rem' }}>DELETE</button>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '32px' }}>
                  {exp.aim && (
                    <div>
                       <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px', letterSpacing: '0.1em' }}>OBJECTIVE</div>
                       <div style={{ fontSize: '0.92rem', lineHeight: 1.6 }}>{exp.aim}</div>
                    </div>
                  )}
                  {exp.theory && (
                    <div>
                       <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px', letterSpacing: '0.1em' }}>FRAMEWORK</div>
                       <div style={{ fontSize: '0.92rem', lineHeight: 1.6 }}>{exp.theory}</div>
                    </div>
                  )}
                  {exp.result && (
                    <div style={{ gridColumn: '1 / -1' }}>
                       <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-dim)', marginBottom: '8px', letterSpacing: '0.1em' }}>OBSERVATIONS & ANALYSIS</div>
                       <div style={{ fontSize: '0.92rem', lineHeight: 1.6, background: 'rgba(0,0,0,0.2)', padding: '20px', borderRadius: '16px', border: '1px solid var(--border)' }}>{exp.result}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
