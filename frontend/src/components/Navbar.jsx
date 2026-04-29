import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { openStreamlit } from '../utils/api'

const NAV_LINKS = [
  { to: '/',        label: 'Home',    icon: '🏠' },
  { to: '/modules', label: 'Modules', icon: '📚' },
  { to: '/tools',   label: 'Tools',   icon: '🛠️' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const location          = useLocation()
  const navigate          = useNavigate()
  const [backendOnline, setBackendOnline] = useState(null)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    window.addEventListener('scroll', onScroll, { passive: true })
    
    // Check backend health
    const checkHealth = () => {
      fetch('/api/health')
        .then(r => r.ok ? setBackendOnline(true) : setBackendOnline(false))
        .catch(() => setBackendOnline(false))
    }
    checkHealth()
    const timer = setInterval(checkHealth, 10000)
    
    return () => {
      window.removeEventListener('scroll', onScroll)
      clearInterval(timer)
    }
  }, [])

  return (
    <nav style={{
      position:      'fixed',
      top:           0, left: 0, right: 0,
      zIndex:        1000,
      height:        '62px',
      display:       'flex',
      alignItems:    'center',
      justifyContent:'space-between',
      padding:       '0 28px',
      background:    scrolled ? 'var(--nav-bg)' : 'transparent',
      backdropFilter:scrolled ? 'blur(22px)'    : 'none',
      borderBottom:  scrolled ? '1px solid var(--nav-border)' : 'none',
      transition:    'all 0.3s ease',
    }}>

      {/* ─── Logo ─────────────────────────── */}
      <div style={{ display:'flex', alignItems:'center', gap:'16px' }}>
        <Link to="/" style={{ display:'flex', alignItems:'center', gap:'12px', textDecoration:'none' }}>
          <span style={{ fontSize:'1.7rem', filter:'drop-shadow(0 0 10px #4361ee88)' }}>🔬</span>
          <div style={{ fontFamily:'var(--font-heading)', fontWeight:900, fontSize:'1.4rem', color:'var(--text)', letterSpacing:'-0.02em' }}>
            Dashboard
          </div>
        </Link>
      </div>

      {/* ─── Page links ────────────────────────────── */}
      <div style={{ display:'flex', gap:'2px', alignItems:'center' }}>
        {NAV_LINKS.map(({ to, label, icon }) => {
          const active = location.pathname === to
          return (
            <Link key={to} to={to} style={{
              display:       'flex', alignItems:'center', gap:'8px',
              padding:       '10px 18px',
              borderRadius:  '12px',
              textDecoration:'none',
              fontSize:      '0.94rem',
              fontWeight:    700,
              fontFamily:    'var(--font-heading)',
              color:         active ? '#4361ee' : 'rgba(230,237,243,0.55)',
              background:    active ? 'rgba(67,97,238,0.12)' : 'transparent',
              border:        active ? '1px solid rgba(67,97,238,0.22)' : '1px solid transparent',
              transition:    'all 0.2s',
            }}>
              <span style={{ fontSize:'1rem' }}>{icon}</span> {label}
            </Link>
          )
        })}

        {/* ─── Theme Toggle ───────────────────── */}
        <button
          id="theme-toggle-btn"
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          title={isDark ? 'Light mode' : 'Dark mode'}
          style={{ marginLeft: '10px' }}
        >
          <div className="theme-toggle__track" />
          <div className="theme-toggle__thumb">{isDark ? '🌙' : '☀️'}</div>
        </button>
      </div>

      {/* ─── User info + logout ─────────────────────── */}
      <div style={{ display:'flex', alignItems:'center', gap:'10px' }}>
        <div style={{
          background:  'rgba(255,255,255,0.04)',
          border:      '1px solid rgba(255,255,255,0.08)',
          borderRadius:'10px',
          padding:     '6px 14px',
          fontSize:    '0.8rem',
          color:       'rgba(230,237,243,0.55)',
        }}>
          👤 <strong style={{ color:'white', fontWeight:700 }}>{user?.username}</strong>
          <span style={{ marginLeft:'8px', fontSize:'0.68rem', color:'rgba(230,237,243,0.28)', textTransform:'uppercase', letterSpacing:'0.06em' }}>{user?.role}</span>
        </div>

        <button onClick={logout} style={{
          padding:     '7px 14px',
          borderRadius:'10px',
          border:      '1px solid rgba(255,51,102,0.22)',
          background:  'rgba(255,51,102,0.07)',
          color:       'var(--red)',
          fontSize:    '0.8rem',
          fontWeight:  600,
          cursor:      'pointer',
          fontFamily:  'var(--font-heading)',
          transition:  'all 0.2s',
        }}>
          🚪 Logout
        </button>
      </div>
    </nav>
  )
}
