import { lazy, Suspense, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const LoginScene = lazy(() => import('../scenes/LoginScene'))

/* ── Shared input style ─────────────────────────────────────────────────────── */
function InputField({ label, value, onChange, placeholder, type = 'text' }) {
  const [focused, setFocused] = useState(false)
  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display:'block', fontSize:'0.76rem', color:'rgba(230,237,243,0.55)', marginBottom:'6px', fontWeight:500, letterSpacing:'0.05em' }}>
        {label}
      </label>
      <input
        type={type} value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          width:'100%', padding:'11px 14px',
          background: focused ? 'rgba(67,97,238,0.08)' : 'rgba(255,255,255,0.04)',
          border: focused ? '1px solid rgba(67,97,238,0.55)' : '1px solid rgba(255,255,255,0.1)',
          boxShadow: focused ? '0 0 0 3px rgba(67,97,238,0.12)' : 'none',
          borderRadius:'10px', color:'#e6edf3',
          fontFamily:'var(--font-body)', fontSize:'0.92rem',
          outline:'none', transition:'all 0.2s',
        }}
      />
    </div>
  )
}

const BTN_STYLE = {
  width:'100%', padding:'13px 24px',
  background:'linear-gradient(135deg, #4361ee, #7209b7)',
  color:'white', border:'none', borderRadius:'12px',
  fontFamily:'var(--font-heading)', fontSize:'0.95rem', fontWeight:700,
  letterSpacing:'0.04em', cursor:'pointer', marginTop:'6px',
  transition:'all 0.3s cubic-bezier(0.34,1.56,0.64,1)',
  boxShadow:'0 8px 26px rgba(67,97,238,0.4)',
}

export default function Login() {
  const [tab,         setTab]        = useState('login')
  const [username,    setUsername]   = useState('')
  const [password,    setPassword]   = useState('')
  const [email,       setEmail]      = useState('')
  const [confirmPass, setConfirmPass]= useState('')
  const [role,        setRole]       = useState('student')
  const [localError,  setLocalError] = useState('')
  const [success,     setSuccess]    = useState('')

  const { login, register, loading, setError } = useAuth()
  const navigate = useNavigate()

  const switchTab = (t) => { setTab(t); setLocalError(''); setSuccess(''); setError(null) }

  /* ── Login handler ──────────────────────────────────── */
  const handleLogin = async (e) => {
    e.preventDefault(); setLocalError('')
    if (!email || !password) { 
      setLocalError('Email and password are required.')
      return 
    }
    try { await login(email, password); navigate('/') }
    catch (err) { setLocalError(err.message) }
  }

  /* ── Register handler ───────────────────────────────── */
  const handleRegister = async (e) => {
    e.preventDefault(); setLocalError(''); setSuccess('')
    if (!email || !password) { setLocalError('Email and password are required.'); return }
    if (password !== confirmPass) { setLocalError('Passwords do not match.'); return }
    try {
      const res = await register(email, password, username, role)
      setSuccess(res.message || 'Account created! You can now sign in.')
      switchTab('login')
    } catch (err) { setLocalError(err.message) }
  }

  return (
    <div style={{ position:'relative', minHeight:'100vh', overflow:'hidden' }}>

      {/* ── Three.js background ─────────────────────── */}
      <div style={{ position:'fixed', inset:0, zIndex:0 }}>
        <Suspense fallback={<div style={{ background:'#0d1117', position:'absolute', inset:0 }} />}>
          <LoginScene />
        </Suspense>
      </div>

      {/* ── Overlay grid ────────────────────────────── */}
      <div style={{
        position:'fixed', inset:0, zIndex:1, pointerEvents:'none',
        backgroundImage:'linear-gradient(rgba(67,97,238,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(67,97,238,0.04) 1px, transparent 1px)',
        backgroundSize:'50px 50px',
      }} />

      {/* ── Content ─────────────────────────────────── */}
      <div style={{
        position:'relative', zIndex:10, minHeight:'100vh',
        display:'flex', flexDirection:'column',
        alignItems:'center', justifyContent:'center', padding:'24px 20px',
      }}>

        {/* Hero */}
        <div style={{ textAlign:'center', marginBottom:'32px', animation:'fade-up 0.7s both' }}>
          <div style={{ fontSize:'3.2rem', marginBottom:'14px', filter:'drop-shadow(0 0 22px #4361ee88)', animation:'glow-pulse 2.5s ease-in-out infinite' }}>🔬</div>
          <h1 style={{
            fontFamily:'var(--font-heading)', fontSize:'clamp(1.8rem, 5vw, 2.6rem)',
            fontWeight:900, lineHeight:1.05,
            background:'linear-gradient(135deg, #4361ee, #b44fff, #4cc9f0)',
            backgroundSize:'300% 300%', WebkitBackgroundClip:'text',
            WebkitTextFillColor:'transparent', backgroundClip:'text',
            animation:'gradient-shift 4s ease infinite', marginBottom:'10px',
          }}>
            DIP Learning<br />Simulator
          </h1>
          <p style={{ color:'rgba(230,237,243,0.35)', fontSize:'0.75rem', letterSpacing:'0.18em', textTransform:'uppercase' }}>
            Interactive DIP Environment
          </p>
        </div>

        {/* Auth card */}
        <div className="glass" style={{
          borderRadius:'var(--radius-xl)', padding:'36px 40px 32px',
          width:'100%', maxWidth:'420px',
          boxShadow:'0 32px 68px rgba(0,0,0,0.55), 0 0 0 1px rgba(67,97,238,0.14), inset 0 1px 0 rgba(255,255,255,0.07)',
          animation:'card-in 0.7s cubic-bezier(0.34,1.56,0.64,1) both',
        }}>

          {/* Tab switcher */}
          <div style={{ display:'flex', background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.07)', borderRadius:'12px', padding:'4px', marginBottom:'26px' }}>
            {[['login','🔑 Sign In'],['register','✨ Register']].map(([key, lbl]) => (
              <button key={key} onClick={() => switchTab(key)} style={{
                flex:1, padding:'10px 8px', border:'none',
                borderRadius:'9px', cursor:'pointer',
                fontFamily:'var(--font-heading)', fontWeight:700, fontSize:'0.84rem',
                transition:'all 0.2s',
                background: tab === key ? 'linear-gradient(135deg,#4361ee,#7209b7)' : 'transparent',
                color:      tab === key ? 'white' : 'rgba(230,237,243,0.45)',
                boxShadow:  tab === key ? '0 2px 14px rgba(67,97,238,0.4)' : 'none',
              }}>{lbl}</button>
            ))}
          </div>

          {/* Alerts */}
          {localError && (
            <div style={{ background:'rgba(255,51,102,0.1)', border:'1px solid rgba(255,51,102,0.28)', borderRadius:'10px', padding:'10px 14px', marginBottom:'16px', fontSize:'0.83rem', color:'#ff6b8a' }}>
              ❌ {localError}
            </div>
          )}
          {success && (
            <div style={{ background:'rgba(6,214,160,0.1)', border:'1px solid rgba(6,214,160,0.28)', borderRadius:'10px', padding:'10px 14px', marginBottom:'16px', fontSize:'0.83rem', color:'#06d6a0' }}>
              ✅ {success}
            </div>
          )}

          {/* ── Sign In form ─────────────────────────── */}
          {tab === 'login' && (
            <form onSubmit={handleLogin}>
              <InputField label="📧 Email" value={email} onChange={setEmail} placeholder="your@email.com" type="email" />
              <InputField label="🔒 Password" value={password} onChange={setPassword} placeholder="Enter your password" type="password" />
              <button type="submit" disabled={loading} style={{ ...BTN_STYLE, opacity: loading ? 0.7 : 1 }}>
                {loading ? '⏳ Signing in…' : '🚀 Sign In'}
              </button>
            </form>
          )}

          {/* ── Register form ────────────────────────── */}
          {tab === 'register' && (
            <form onSubmit={handleRegister}>
              <InputField label="📧 Email" value={email} onChange={setEmail} placeholder="your@email.com" type="email" />
              <InputField label="👤 Username (optional)" value={username} onChange={setUsername} placeholder="Choose username (min 3 chars)" />
              <InputField label="🔒 Password" value={password} onChange={setPassword} placeholder="Choose password (min 4 chars)" type="password" />
              <InputField label="🔁 Confirm Password" value={confirmPass} onChange={setConfirmPass} placeholder="Repeat your password" type="password" />
              <div style={{ marginBottom:'16px' }}>
                <label style={{ display:'block', fontSize:'0.76rem', color:'rgba(230,237,243,0.55)', marginBottom:'6px', fontWeight:500, letterSpacing:'0.05em' }}>👥 Role</label>
                <select value={role} onChange={e => setRole(e.target.value)} style={{
                  width:'100%', padding:'11px 14px',
                  background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.1)',
                  borderRadius:'10px', color:'#e6edf3',
                  fontFamily:'var(--font-body)', fontSize:'0.92rem', outline:'none',
                }}>
                  <option value="student">Student</option>
                  <option value="guest">Guest</option>
                </select>
              </div>
              <button type="submit" disabled={loading} style={{ ...BTN_STYLE, opacity: loading ? 0.7 : 1 }}>
                {loading ? '⏳ Creating…' : '🌟 Create Account'}
              </button>
            </form>
          )}
        </div>

        {/* Demo credentials */}
        <div style={{ marginTop:'22px', textAlign:'center' }}>
          <p style={{ color:'rgba(230,237,243,0.28)', fontSize:'0.7rem', letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:'10px' }}>
            🔑 Demo Credentials
          </p>
          <div style={{ display:'flex', gap:'8px', justifyContent:'center' }}>
            {[
              ['admin@dip.edu','dip2024','admin'],
              ['student@dip.edu','learn123','student'],
              ['guest@dip.edu','guest','guest']
            ].map(([em, p, u]) => (
              <button key={u} onClick={() => { setEmail(em); setPassword(p); setUsername(u); switchTab('login') }} style={{
                background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.08)',
                borderRadius:'10px', padding:'8px 13px', cursor:'pointer',
                fontFamily:'var(--font-body)', transition:'all 0.2s',
              }}>
                <div style={{ fontWeight:700, color:'white', fontSize:'0.82rem' }}>{u}</div>
                <div style={{ fontFamily:'var(--font-mono)', fontSize:'0.68rem', color:'rgba(230,237,243,0.35)', marginTop:'2px' }}>{p}</div>
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginTop:'28px', textAlign:'center', fontSize:'0.68rem', color:'rgba(230,237,243,0.18)', fontFamily:'var(--font-mono)' }}>
          Simulator Backend · 3D Interface
        </div>
      </div>
    </div>
  )
}
