import { useSearchParams, useNavigate, useLocation } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { STREAMLIT_BASE } from '../utils/api'

export default function StreamlitViewer() {
  const [searchParams]      = useSearchParams()
  const navigate            = useNavigate()
  const location            = useLocation()
  const iframeRef           = useRef(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(false)

  // page = e.g. "Module1_Fundamentals" or "" (home)
  const page    = searchParams.get('page') || ''
  // label for the top bar
  const label   = searchParams.get('label') || 'Streamlit Simulator'
  // from = the page that opened this viewer (for the back link)
  const from    = searchParams.get('from') || '/'

  const src = page
    ? `${STREAMLIT_BASE}/${page}`
    : STREAMLIT_BASE

  // Reset loading state whenever the URL changes
  useEffect(() => {
    setLoading(true)
    setError(false)
  }, [src])

  const handleLoad = () => setLoading(false)
  const handleError = () => { setLoading(false); setError(true) }

  const goBack = () => navigate(from)

  const refresh = () => {
    if (iframeRef.current) {
      setLoading(true)
      setError(false)
      // Force reload by resetting src
      const currentSrc = iframeRef.current.src
      iframeRef.current.src = ''
      setTimeout(() => { iframeRef.current.src = currentSrc }, 50)
    }
  }

  // Open current page in actual new tab as fallback
  const openExternal = () => window.open(src, '_blank', 'noopener,noreferrer')

  return (
    <div className="viewer-shell">
      {/* ── Top control bar ──────────────────────────────────────────── */}
      <div className="viewer-bar">
        {/* Back button */}
        <button className="viewer-btn viewer-btn--back" onClick={goBack} title="Go back">
          <span className="viewer-btn__icon">←</span>
          <span className="viewer-btn__label">Back</span>
        </button>

        {/* Breadcrumb / label */}
        <div className="viewer-breadcrumb">
          <span className="viewer-breadcrumb__logo">🔬</span>
          <span className="viewer-breadcrumb__sep">/</span>
          <span className="viewer-breadcrumb__page">{label}</span>
        </div>

        {/* Right actions */}
        <div className="viewer-actions">
          {loading && (
            <span className="viewer-loading-dot" title="Loading…">
              <span /><span /><span />
            </span>
          )}

          <button className="viewer-btn viewer-btn--icon" onClick={refresh} title="Reload">
            ↺
          </button>

          <button className="viewer-btn viewer-btn--icon" onClick={openExternal} title="Open in new tab">
            ↗
          </button>
        </div>
      </div>

      {/* ── iframe area ──────────────────────────────────────────────── */}
      <div className="viewer-frame-wrap">
        {/* Shimmer loader */}
        {loading && !error && (
          <div className="viewer-shimmer">
            <div className="viewer-shimmer__logo">🔬</div>
            <div className="viewer-shimmer__text">Loading {label}…</div>
            <div className="viewer-shimmer__bar">
              <div className="viewer-shimmer__fill" />
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="viewer-error">
            <div style={{ fontSize: '3rem', marginBottom: '12px' }}>⚠️</div>
            <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.1rem', marginBottom: '8px', color: '#e6edf3' }}>
              Could not connect to Streamlit
            </div>
            <div style={{ color: 'var(--text-dim)', fontSize: '0.82rem', marginBottom: '24px', maxWidth: '340px', textAlign: 'center', lineHeight: 1.6 }}>
              Make sure the Streamlit server is running on <code style={{ color: '#4cc9f0' }}>{STREAMLIT_BASE}</code>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="viewer-btn viewer-btn--primary" onClick={refresh}>↺ Retry</button>
              <button className="viewer-btn viewer-btn--ghost" onClick={openExternal}>Open in new tab ↗</button>
            </div>
          </div>
        )}

        <iframe
          ref={iframeRef}
          src={src}
          title={label}
          className={`viewer-iframe ${loading || error ? 'viewer-iframe--hidden' : ''}`}
          onLoad={handleLoad}
          onError={handleError}
          allow="camera; microphone; clipboard-read; clipboard-write"
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-downloads"
        />
      </div>
    </div>
  )
}
