import { useState } from 'react'

export default function ModuleCard({ module: mod, onOpen }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onOpen}
      style={{
        position:     'relative',
        overflow:     'hidden',
        borderRadius: '18px',
        padding:      '22px 18px 18px',
        cursor:       'pointer',
        background:   hovered ? `${mod.color}0e` : 'var(--bg-glass)',
        border:       `1.5px solid ${hovered ? mod.color + '55' : mod.color + '1a'}`,
        boxShadow:    hovered
          ? `0 22px 55px ${mod.color}20, 0 0 30px ${mod.color}0c, inset 0 1px 0 rgba(255,255,255,0.06)`
          : '0 2px 12px rgba(0,0,0,0.1)',
        transform:    hovered ? 'translateY(-8px) scale(1.02)' : 'none',
        transition:   'all 0.35s cubic-bezier(0.34,1.56,0.64,1)',
        height:       '100%',
        display:      'flex',
        flexDirection:'column',
      }}
    >
      {/* Coloured top accent bar */}
      <div style={{
        position:   'absolute', top: 0, left: 0, right: 0, height: '3px',
        background: `linear-gradient(90deg, ${mod.color}, ${mod.color}44)`,
        borderRadius:'18px 18px 0 0',
      }} />

      {/* Glow orb (visible on hover) */}
      <div style={{
        position:'absolute', top:'-40px', right:'-30px',
        width:'120px', height:'120px', borderRadius:'50%',
        background: `${mod.color}1a`,
        filter:'blur(40px)',
        opacity: hovered ? 1 : 0,
        transition:'opacity 0.4s',
        pointerEvents:'none',
      }} />

      {/* Module number badge */}
      <div style={{
        fontSize:'0.6rem', fontWeight:700, letterSpacing:'0.14em',
        color:`${mod.color}99`, textTransform:'uppercase',
        fontFamily:'var(--font-mono)', marginBottom:'10px',
      }}>
        MODULE {mod.number}
      </div>

      {/* Icon */}
      <div style={{
        fontSize:'2.3rem', marginBottom:'8px',
        filter: hovered ? `drop-shadow(0 0 14px ${mod.color}55)` : 'none',
        transition:'filter 0.3s',
        lineHeight: 1,
      }}>
        {mod.icon}
      </div>

      {/* Title */}
      <h3 style={{
        fontSize:'1.05rem', fontWeight:800,
        color: hovered ? mod.color : 'var(--text)',
        fontFamily:'var(--font-heading)', lineHeight:1.25,
        marginBottom:'4px', transition:'color 0.3s',
      }}>
        {mod.title}
      </h3>

      <p style={{ fontSize:'0.72rem', color:'var(--text-dim)', marginBottom:'14px', lineHeight:1.5 }}>
        {mod.subtitle}
      </p>

      {/* Topics pills */}
      <div style={{ display:'flex', flexWrap:'wrap', gap:'4px', marginBottom:'18px', flex: 1 }}>
        {mod.topics.map(t => (
          <span key={t} style={{
            background:`${mod.color}10`, border:`1px solid ${mod.color}20`,
            color:`${mod.color}cc`, borderRadius:'20px',
            padding:'2px 8px', fontSize:'0.64rem', fontWeight:500,
          }}>{t}</span>
        ))}
      </div>

      {/* CTA row */}
      <div style={{
        display:'flex', alignItems:'center', justifyContent:'center', gap:'7px',
        background:  hovered ? `${mod.color}18` : 'transparent',
        border:      `1px solid ${hovered ? mod.color + '44' : mod.color + '22'}`,
        borderRadius:'10px', padding:'9px 12px',
        fontSize:'0.74rem', fontWeight:700,
        color: mod.color, transition:'all 0.3s',
        fontFamily:'var(--font-heading)',
      }}>
        <span>▶</span>
        <span>Open in Simulator</span>
        <span style={{ marginLeft:'auto', opacity:0.5, fontSize:'0.68rem' }}>→</span>
      </div>
    </div>
  )
}
