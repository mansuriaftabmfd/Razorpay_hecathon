// Sidebar.jsx — Sleek modern vertical sidebar navigation inspired by Behance design
import React, { useState, useEffect } from 'react';
import api from '../../api';

const navItems = [
  { key: 'about',      label: 'About Project',   icon: '🏠', badge: null },
  { key: 'overview',   label: 'Overview',        icon: '▦',  badge: 'Live' },
  { key: 'returns',    label: 'Returns Queue',   icon: '↩',  badge: '44' },
  { key: 'simulator',  label: 'AI Simulator',    icon: '⚡', badge: 'Test' },
  { key: 'models',     label: 'ML Metrics',      icon: '◈',  badge: '96.8%' },
  { key: 'audit',      label: 'Audit Vault',     icon: '🔐', badge: null },
];

export function Sidebar({ activeTab, onTabChange, isCollapsed, onToggleCollapse, mobileOpen, onMobileClose }) {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.health().then(r => setHealth(r.data)).catch(() => setHealth(null));
  }, []);

  const isHealthy = health?.status === 'healthy';

  function handleSelect(key) {
    onTabChange(key);
    if (onMobileClose) onMobileClose();
  }

  return (
    <>
      {/* Mobile overlay backdrop */}
      {mobileOpen && (
        <div 
          className="sidebar-backdrop"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      <aside className={`app-sidebar ${isCollapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        {/* Brand Header */}
        <div className="sidebar-header">
          <div className="brand-logo-container">
            <div className="brand-icon">
              <span style={{ fontSize: 20 }}>🛡️</span>
            </div>
            {!isCollapsed && (
              <div className="brand-text">
                <div className="brand-title">
                  ReturnShield <span className="brand-ai">AI</span>
                </div>
                <div className="brand-sub">Razorpay Hackathon</div>
              </div>
            )}
          </div>

          {/* Desktop collapse toggle */}
          <button 
            className="collapse-toggle-btn desktop-only" 
            onClick={onToggleCollapse}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label="Toggle sidebar collapse"
          >
            {isCollapsed ? '→' : '←'}
          </button>
        </div>

        {/* Merchant / Admin Profile Card (Behance style) */}
        {!isCollapsed ? (
          <div className="sidebar-profile-card">
            <div className="profile-avatar">
              <span>⚡</span>
              <span className="profile-status-dot" />
            </div>
            <div className="profile-info">
              <div className="profile-name">Merchant Portal</div>
              <div className="profile-role">Razorpay Risk Guard</div>
            </div>
          </div>
        ) : (
          <div className="sidebar-profile-compact" title="Merchant Portal — Active">
            <span className="profile-status-dot compact" />
            <span>⚡</span>
          </div>
        )}

        {/* Navigation list */}
        <nav className="sidebar-nav">
          <div className="nav-section-label">
            {!isCollapsed && <span>MAIN MENU</span>}
          </div>

          {navItems.map(item => {
            const isActive = activeTab === item.key;
            return (
              <button
                key={item.key}
                onClick={() => handleSelect(item.key)}
                className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                title={isCollapsed ? item.label : undefined}
              >
                {/* Active Indicator Bar */}
                {isActive && <div className="active-indicator" />}

                <span className="nav-item-icon">{item.icon}</span>

                {!isCollapsed && (
                  <>
                    <span className="nav-item-label">{item.label}</span>
                    {item.badge && (
                      <span className={`nav-item-badge ${isActive ? 'active-badge' : ''}`}>
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom Status Card / Action (Behance style) */}
        <div className="sidebar-footer">
          {!isCollapsed ? (
            <div className="sidebar-action-card">
              <div className="action-card-header">
                <div className="live-status-pill">
                  <span className={`status-beacon ${isHealthy ? 'live' : 'connecting'}`} />
                  <span>{isHealthy ? 'AI Engine Live' : 'Connecting…'}</span>
                </div>
                <span className="model-version">XGBoost v1.4</span>
              </div>
              <p className="action-card-desc">
                Sub-15ms inference on 23 behavioral return fraud features.
              </p>
              <button 
                className="action-card-btn"
                onClick={() => handleSelect('simulator')}
              >
                <span>⚡ Test Simulator</span>
              </button>
            </div>
          ) : (
            <div className="sidebar-compact-status" title={isHealthy ? 'AI Engine Live (<15ms)' : 'Connecting…'}>
              <span className={`status-beacon ${isHealthy ? 'live' : 'connecting'}`} />
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

// Mobile Top Bar
export function MobileHeader({ onToggleMobile, activeTab }) {
  const activeItem = navItems.find(t => t.key === activeTab) || navItems[1];

  return (
    <header className="mobile-header">
      <button 
        className="mobile-hamburger-btn" 
        onClick={onToggleMobile}
        aria-label="Open Navigation"
      >
        <span style={{ fontSize: 20 }}>☰</span>
      </button>

      <div className="mobile-header-brand">
        <span style={{ fontSize: 18 }}>🛡️</span>
        <span className="mobile-brand-title">
          ReturnShield <span>AI</span>
        </span>
      </div>

      <div className="mobile-current-tab">
        <span>{activeItem.icon}</span>
        <span className="mobile-tab-name">{activeItem.label}</span>
      </div>
    </header>
  );
}
