// Badge.jsx — Risk level and status badges
import React from 'react';

const styles = {
  base: {
    display: 'inline-flex', alignItems: 'center', gap: '4px',
    padding: '3px 10px', borderRadius: '20px',
    fontSize: '11px', fontWeight: 700, letterSpacing: '0.04em',
    textTransform: 'uppercase', whiteSpace: 'nowrap',
  },
  LOW:    { background: 'var(--green-bg)',  border: '1px solid var(--green-border)',  color: 'var(--green-400)' },
  MEDIUM: { background: 'var(--amber-bg)',  border: '1px solid var(--amber-border)',  color: 'var(--amber-400)' },
  HIGH:   { background: 'var(--red-bg)',    border: '1px solid var(--red-border)',    color: 'var(--red-400)' },
  PENDING:{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)', color: 'var(--indigo-400)' },
  APPROVE:{ background: 'var(--green-bg)',  border: '1px solid var(--green-border)',  color: 'var(--green-400)' },
  VERIFY: { background: 'var(--amber-bg)',  border: '1px solid var(--amber-border)',  color: 'var(--amber-400)' },
  MANUAL_REVIEW: { background: 'var(--red-bg)', border: '1px solid var(--red-border)', color: 'var(--red-400)' },
};

export function RiskBadge({ level, score }) {
  const s = styles[level] || styles.LOW;
  return (
    <span style={{ ...styles.base, ...s }}>
      {level} {score !== undefined && `${Number(score).toFixed(1)}%`}
    </span>
  );
}

export function StatusBadge({ status }) {
  const s = styles[status] || styles.PENDING;
  return <span style={{ ...styles.base, ...s }}>{status}</span>;
}
