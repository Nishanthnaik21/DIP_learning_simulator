import { useState } from 'react'

export default function ToolCard({ tool, onOpen }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onOpen}
      style={{
        position:     'relative',
        overflow:     'hidden',
        borderRadius: '14px',
        padding:      '18px 14px',
        cursor:       'pointer',
        textAlign:    'center',
        background:   hovered ? `${tool.color}0c` : 'var(--bg-glass)',
        border:       `1.5px solid ${hovered ? tool.color + '50' : 'var(--border)'}`,
        boxShadow:    hovered ? `0 14px 35px ${tool.color}18` : '0 1px 5px rgba(0,0,0,0.2)',
        transform:    hovered ? 'translateY(-5px) scale(1.03)' : 'none',
        transition:   'all 0.3s cubic-bezier(0.34,1.56,0.64,1)',
      }}
    >
      {/* Top glow bar on hover */}
      <div style={{
        position:'absolute', top:0, left:0, right:0, height:'2px',
        background: `linear-gradient(90deg, transparent, ${tool.color}, transparent)`,
        opacity: hovered ? 1 : 0,
        transition:'opacity 0.3s',
      }} />

      {/* Icon box */}
      <div style={{
        width:'44px', height:'44px', borderRadius:'12px',
        background: `linear-gradient(135deg, ${tool.color}18, ${tool.color}28)`,
        border: `1px solid ${tool.color}25`,
        display:'flex', alignItems:'center', justifyContent:'center',
        margin:'0 auto 10px',
        fontSize:'1.3rem',
        filter: hovered ? `drop-shadow(0 0 10px ${tool.color}55)` : 'none',
        transition:'all 0.3s',
      }}>
        {tool.icon}
      </div>

      {/* Name */}
      <div style={{
        fontSize:'0.84rem', fontWeight:750,
        color: hovered ? tool.color : 'var(--text)',
        fontFamily:'var(--font-heading)',
        marginBottom:'4px', lineHeight:1.3,
        transition:'color 0.3s',
        letterSpacing:'0.01em',
      }}>
        {tool.name}
      </div>

      {/* Description */}
      <div style={{ fontSize:'0.64rem', color:'var(--text-dim)', lineHeight:1.4 }}>
        {tool.desc}
      </div>
    </div>
  )
}
