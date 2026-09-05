// Card.jsx — Base card container
import React from 'react';

export function Card({ children, style, className, hover = true }) {
  return (
    <div
      className={className}
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '1.25rem',
        transition: 'border-color 0.2s, transform 0.2s, box-shadow 0.2s',
        ...style,
      }}
      onMouseEnter={hover ? (e) => {
        e.currentTarget.style.borderColor = 'var(--border-hover)';
        e.currentTarget.style.boxShadow = 'var(--shadow-md)';
      } : undefined}
      onMouseLeave={hover ? (e) => {
        e.currentTarget.style.borderColor = 'var(--border)';
        e.currentTarget.style.boxShadow = 'none';
      } : undefined}
    >
      {children}
    </div>
  );
}

export function KpiCard({ label, value, sub, accent = 'var(--blue-400)', icon, trend }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      padding: '1.35rem',
      position: 'relative',
      overflow: 'hidden',
      transition: 'border-color 0.2s, box-shadow 0.2s',
      cursor: 'default',
    }}
    onMouseEnter={e => { e.currentTarget.style.borderColor = accent; e.currentTarget.style.boxShadow = `0 0 20px ${accent}22`; }}
    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.boxShadow = 'none'; }}
    >
      {/* Top accent strip */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '2px', background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</span>
        {icon && (
          <span style={{ width: 32, height: 32, borderRadius: 8, background: `${accent}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: accent, fontSize: 16 }}>
            {icon}
          </span>
        )}
      </div>

      <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 800, color: accent, letterSpacing: '-0.03em', lineHeight: 1.1, marginBottom: '0.4rem' }}>
        {value}
      </div>

      {sub && <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{sub}</div>}
      {trend && (
        <div style={{ marginTop: '0.5rem', fontSize: '11px', fontWeight: 600, color: trend.positive ? 'var(--green-400)' : 'var(--red-400)' }}>
          {trend.positive ? '↑' : '↓'} {trend.label}
        </div>
      )}
    </div>
  );
}
