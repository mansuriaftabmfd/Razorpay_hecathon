// Navbar.jsx — Top navigation bar with responsive mobile menu
import React, { useState, useEffect } from 'react';
import api from '../../api';

const tabs = [
  { key: 'about',      label: 'About',        icon: '🏠' },
  { key: 'overview',   label: 'Overview',     icon: '▦' },
  { key: 'returns',    label: 'Returns Queue', icon: '↩' },
  { key: 'simulator',  label: 'AI Simulator',  icon: '⚡' },
  { key: 'models',     label: 'ML Metrics',    icon: '◈' },
  { key: 'audit',      label: 'Audit Vault',   icon: '🔐' },
];

export function Navbar({ activeTab, onTabChange }) {
  const [health, setHealth] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    api.health().then(r => setHealth(r.data)).catch(() => setHealth(null));
  }, []);

  const isHealthy = health?.status === 'healthy';

  function handleTabClick(key) {
    onTabChange(key);
    setMobileOpen(false);
  }

  return (
    <header className="navbar">
      {/* Brand */}
      <div className="navbar-brand">
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 18, boxShadow: '0 0 16px rgba(59,130,246,0.4)',
        }}>🛡️</div>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>
            ReturnShield <span style={{ background: 'linear-gradient(90deg,#3b82f6,#818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI</span>
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>Razorpay Hackathon</div>
        </div>
      </div>

      {/* Hamburger for mobile */}
      <button className="hamburger-btn" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu">
        {mobileOpen ? '✕' : '☰'}
      </button>

      {/* Tabs */}
      <nav className={`navbar-tabs${mobileOpen ? ' mobile-open' : ''}`}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => handleTabClick(t.key)} className="nav-tab" style={{
            background: activeTab === t.key ? 'var(--bg-elevated)' : 'transparent',
            color: activeTab === t.key ? 'var(--blue-400)' : 'var(--text-muted)',
            fontWeight: activeTab === t.key ? 600 : 500,
            boxShadow: activeTab === t.key ? 'var(--shadow-sm)' : 'none',
          }}>
            <span style={{ fontSize: 14 }}>{t.icon}</span>
            <span className="tab-label">{t.label}</span>
          </button>
        ))}
      </nav>

      {/* Status */}
      <div className="navbar-status">
        <div style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '5px 12px', borderRadius: 20,
          background: isHealthy ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
          border: `1px solid ${isHealthy ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
          fontSize: 12, fontWeight: 600,
          color: isHealthy ? 'var(--green-400)' : 'var(--red-400)',
        }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%',
            background: isHealthy ? 'var(--green-400)' : 'var(--red-400)',
            boxShadow: isHealthy ? '0 0 8px var(--green-400)' : '0 0 8px var(--red-400)',
            animation: 'pulse 2s infinite',
          }} />
          {isHealthy ? 'Model Live' : health ? 'Degraded' : 'Connecting…'}
        </div>
      </div>
    </header>
  );
}
