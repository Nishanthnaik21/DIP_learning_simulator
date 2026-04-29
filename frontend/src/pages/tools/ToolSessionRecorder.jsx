import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export default function ToolSessionRecorder() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [logs, setLogs] = useState([])
  const [isRecording, setIsRecording] = useState(true)

  // Simulation: Add some initial "past" actions if empty
  useEffect(() => {
    const savedLogs = localStorage.getItem('dip_session_logs')
    if (savedLogs) {
      setLogs(JSON.parse(savedLogs))
    } else {
      const initial = [
        { id: 1, action: 'Logged in', time: new Date(Date.now() - 1000 * 60 * 5).toLocaleTimeString(), module: 'Auth' },
        { id: 2, action: 'Opened Module 1', time: new Date(Date.now() - 1000 * 60 * 4).toLocaleTimeString(), module: 'Fundamentals' },
        { id: 3, action: 'Applied Canny Edge Detection', time: new Date(Date.now() - 1000 * 60 * 2).toLocaleTimeString(), module: 'Module 5' }
      ]
      setLogs(initial)
      localStorage.setItem('dip_session_logs', JSON.stringify(initial))
    }
  }, [])

  const addManualLog = (action) => {
    if (!isRecording) return
    const newLog = {
      id: Date.now(),
      action,
      time: new Date().toLocaleTimeString(),
      module: 'Manual Note'
    }
    const updated = [newLog, ...logs]
    setLogs(updated)
    localStorage.setItem('dip_session_logs', JSON.stringify(updated))
  }

  const clearLogs = () => {
    setLogs([])
    localStorage.removeItem('dip_session_logs')
  }

  const card = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '20px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>⏺️</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Session Recorder</h1>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
          <div>
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                   <h3 style={{ margin: 0, fontFamily: 'var(--font-heading)', fontSize: '1.4rem' }}>Activity Timeline</h3>
                   <p style={{ margin: '4px 0 0', color: 'var(--text-dim)', fontSize: '0.85rem' }}>Tracing digital processing steps and user interactions.</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button 
                    onClick={() => setIsRecording(!isRecording)} 
                    style={{ background: isRecording ? 'var(--pink)' : 'var(--green)', color: 'white', border: 'none', padding: '8px 20px', borderRadius: '10px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 800, transition: 'all 0.2s' }}
                  >
                    {isRecording ? '⏸ STOP' : '⏺ START'}
                  </button>
                  <button onClick={clearLogs} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', color: 'var(--text-dim)', padding: '8px 16px', borderRadius: '10px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 700 }}>CLEAR</button>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative' }}>
                <div style={{ position: 'absolute', left: '107px', top: '20px', bottom: '20px', width: '2px', background: 'var(--border)', zIndex: 0 }} />
                
                {logs.map(log => (
                  <div key={log.id} style={{ display: 'flex', gap: '24px', position: 'relative', zIndex: 1 }}>
                    <div style={{ color: 'var(--blue)', fontWeight: 800, fontSize: '0.75rem', width: '85px', textAlign: 'right', paddingTop: '12px', fontFamily: 'var(--font-mono)' }}>{log.time}</div>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--blue)', marginTop: '14px', border: '4px solid var(--bg)', boxShadow: '0 0 0 1px var(--border)' }} />
                    <div style={{ flex: 1, padding: '16px 20px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)', borderRadius: '16px', transition: 'transform 0.2s' }}>
                      <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '4px' }}>{log.action}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                         <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--purple)' }} />
                         CATEGORY: {log.module.toUpperCase()}
                      </div>
                    </div>
                  </div>
                ))}
                {logs.length === 0 && <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-dim)', border: '1px dashed var(--border)', borderRadius: '16px' }}>NO ACTIVITY DATA AVAILABLE</div>}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
              <h4 style={{ marginTop: 0, fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '16px' }}>OPERATOR STATUS</h4>
              <div style={{ padding: '20px', background: 'rgba(67,97,238,0.1)', borderRadius: '16px', border: '1px solid rgba(67,97,238,0.2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                   <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.2rem', color: 'white' }}>
                      {user?.username?.[0] || 'G'}
                   </div>
                   <div>
                      <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>{user?.username || 'Guest Access'}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 600 }}>ROLE: {user?.role?.toUpperCase() || 'EXTERNAL'}</div>
                   </div>
                </div>
              </div>
            </div>
            
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '24px' }}>
              <h4 style={{ marginTop: 0, fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '16px' }}>MANUAL ANNOTATION</h4>
              <textarea 
                placeholder="Type a research note..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    addManualLog(e.target.value)
                    e.target.value = ''
                  }
                }}
                style={{ width: '100%', background: 'rgba(0,0,0,0.2)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: '12px', padding: '16px', fontSize: '0.9rem', resize: 'none', height: '120px', fontFamily: 'inherit' }}
              />
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px', fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 600 }}>
                 <span style={{ padding: '2px 6px', background: 'var(--border)', borderRadius: '4px' }}>ENTER</span> TO APPEND TO TIMELINE
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
