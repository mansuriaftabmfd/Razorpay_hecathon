// Toast.jsx — Notification system
import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const show = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500);
  }, []);

  const iconMap = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  const colorMap = {
    success: 'var(--green-400)',
    error: 'var(--red-400)',
    warning: 'var(--amber-400)',
    info: 'var(--blue-400)',
  };

  return (
    <ToastContext.Provider value={show}>
      {children}
      <div style={{
        position: 'fixed', bottom: 24, right: 24, zIndex: 9999,
        display: 'flex', flexDirection: 'column', gap: 10,
      }}>
        {toasts.map(t => (
          <div key={t.id} style={{
            display: 'flex', alignItems: 'center', gap: 10,
            background: 'var(--bg-elevated)',
            border: `1px solid ${colorMap[t.type]}44`,
            borderLeft: `3px solid ${colorMap[t.type]}`,
            borderRadius: 'var(--radius-md)',
            padding: '0.7rem 1rem',
            boxShadow: 'var(--shadow-lg)',
            color: 'var(--text-primary)',
            fontSize: 13,
            fontWeight: 500,
            minWidth: 260,
            animation: 'slideInRight 0.3s ease',
          }}>
            <span style={{ color: colorMap[t.type], fontWeight: 700, fontSize: 15 }}>{iconMap[t.type]}</span>
            {t.message}
          </div>
        ))}
      </div>
      <style>{`@keyframes slideInRight { from { opacity:0; transform:translateX(40px); } to { opacity:1; transform:translateX(0); } }`}</style>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
