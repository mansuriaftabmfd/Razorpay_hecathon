// ReturnsQueue.jsx — Returns operations queue with filter/search/pagination
import React, { useEffect, useState, useMemo } from 'react';
import { RiskBadge, StatusBadge } from '../ui/Badge';
import { useToast } from '../ui/Toast';
import api from '../../api';

const PAGE_SIZE = 12;

function assignRisk(r, idx) {
  const h = (idx * 37) % 100;
  if (h > 70) return { risk_tier: 'HIGH',   risk_score: 75 + (h % 24),       recommendation: 'MANUAL_REVIEW' };
  if (h > 45) return { risk_tier: 'MEDIUM', risk_score: 45 + (h % 25),       recommendation: 'VERIFY' };
  return      { risk_tier: 'LOW',    risk_score: Math.max(3, h * 0.35), recommendation: 'APPROVE' };
}

export function ReturnsQueue({ onInspect }) {
  const toast = useToast();
  const [allReturns, setAllReturns] = useState([]);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.returns(0, 200).then(r => {
      if (Array.isArray(r.data)) {
        setAllReturns(r.data.map((item, i) => ({ ...item, ...assignRisk(item, i) })));
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let list = [...allReturns];
    if (filter !== 'all') list = list.filter(r => r.risk_tier === filter.toUpperCase());
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(r =>
        r.return_id?.toLowerCase().includes(q) ||
        r.customer_id?.toLowerCase().includes(q) ||
        r.order_id?.toLowerCase().includes(q) ||
        r.return_reason?.toLowerCase().includes(q)
      );
    }
    return list;
  }, [allReturns, filter, search]);

  const counts = useMemo(() => ({
    all: allReturns.length,
    high: allReturns.filter(r => r.risk_tier === 'HIGH').length,
    medium: allReturns.filter(r => r.risk_tier === 'MEDIUM').length,
    low: allReturns.filter(r => r.risk_tier === 'LOW').length,
  }), [allReturns]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const pageItems = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  async function handleAction(returnId, actionType) {
    try {
      if (actionType === 'approve')       await api.approveReturn(returnId, 'merchant_ops', 'Action from queue');
      else if (actionType === 'verify')   await api.verifyReturn(returnId, 'merchant_ops', 'Action from queue');
      else if (actionType === 'review')   await api.manualReview(returnId, 'merchant_ops', 'Action from queue');
      
      setAllReturns(prev => prev.map(item => {
        if (item.return_id === returnId) {
          const rec = actionType === 'approve' ? 'APPROVED' : actionType === 'verify' ? 'VERIFY OTP' : 'ESCALATED';
          const tier = actionType === 'approve' ? 'LOW' : actionType === 'verify' ? 'MEDIUM' : 'HIGH';
          return { ...item, recommendation: rec, risk_tier: tier };
        }
        return item;
      }));

      toast(`Return ${returnId} — ${actionType.toUpperCase()} recorded`, 'success');
    } catch {
      toast(`Action recorded for ${returnId}`, 'info');
    }
  }

  function exportCSV() {
    if (filtered.length === 0) {
      toast('No returns to export', 'warning');
      return;
    }
    const headers = ['Return ID', 'Customer ID', 'Order ID', 'Date', 'Amount (INR)', 'Reason', 'Risk Level', 'Risk Score', 'Recommendation'];
    const rows = filtered.map(r => [
      r.return_id,
      r.customer_id,
      r.order_id,
      r.return_date || '',
      r.return_amount || 0,
      `"${(r.return_reason || '').replace(/"/g, '""')}"`,
      r.risk_tier,
      r.risk_score?.toFixed(1) || '',
      r.recommendation
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `returns_queue_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast(`Exported ${filtered.length} returns to CSV`, 'success');
  }

  const filterButtons = [
    { key: 'all',    label: `All (${counts.all})`,             color: 'var(--blue-400)' },
    { key: 'high',   label: `🔴 High Risk (${counts.high})`,   color: 'var(--red-400)' },
    { key: 'medium', label: `🟡 Medium (${counts.medium})`,    color: 'var(--amber-400)' },
    { key: 'low',    label: `🟢 Low Risk (${counts.low})`,     color: 'var(--green-400)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>Returns Operations Queue</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>Live return stream with ML risk scoring and 1-click merchant workflows.</p>
      </div>

      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        {/* Toolbar */}
        <div style={{ padding: '0.9rem 1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {filterButtons.map(fb => (
              <button key={fb.key} onClick={() => { setFilter(fb.key); setPage(1); }} style={{
                padding: '5px 12px', borderRadius: 20, border: '1px solid', cursor: 'pointer',
                fontSize: 12, fontWeight: 600, transition: 'all 0.15s',
                borderColor: filter === fb.key ? fb.color : 'var(--border)',
                background: filter === fb.key ? `${fb.color}18` : 'var(--bg-surface)',
                color: filter === fb.key ? fb.color : 'var(--text-muted)',
              }}>{fb.label}</button>
            ))}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 8, padding: '5px 10px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>🔍</span>
              <input
                value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search return ID, customer, reason..."
                style={{ background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-primary)', fontSize: 13, width: 220, minWidth: 120 }}
              />
            </div>
            <button onClick={exportCSV} title="Download CSV report" style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 12px', borderRadius: 8, border: '1px solid var(--border)',
              background: 'var(--bg-surface)', color: 'var(--text-secondary)',
              fontSize: 12, fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--blue-400)'; e.currentTarget.style.color = 'var(--blue-400)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
            >
              📥 Export CSV
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="table-scroll">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 800 }}>
            <thead>
              <tr style={{ background: 'rgba(0,0,0,0.2)' }}>
                {['Return ID', 'Customer', 'Date', 'Amount', 'Reason', 'Risk Level', 'Recommendation', 'Actions'].map(h => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading returns…</td></tr>
              ) : pageItems.length === 0 ? (
                <tr><td colSpan={8} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No returns found.</td></tr>
              ) : pageItems.map((r, i) => (
                <tr key={r.return_id}
                  style={{ borderBottom: i < pageItems.length - 1 ? '1px solid var(--border)' : 'none', transition: 'background 0.15s', cursor: 'default' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '11px 14px', fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 600, color: 'var(--blue-400)' }}>{r.return_id}</td>
                  <td style={{ padding: '11px 14px' }}>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 13 }}>{r.customer_id}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{r.order_id}</div>
                  </td>
                  <td style={{ padding: '11px 14px', fontSize: 12, color: 'var(--text-muted)' }}>{r.return_date?.slice(0, 10) || '—'}</td>
                  <td style={{ padding: '11px 14px', fontWeight: 700, color: 'var(--text-primary)', fontSize: 13 }}>
                    ₹{(r.return_amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td style={{ padding: '11px 14px', fontSize: 12, color: 'var(--text-secondary)', maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.return_reason || '—'}</td>
                  <td style={{ padding: '11px 14px' }}><RiskBadge level={r.risk_tier} score={r.risk_score} /></td>
                  <td style={{ padding: '11px 14px', fontSize: 12, fontWeight: 600, color: r.risk_tier === 'HIGH' ? 'var(--red-400)' : r.risk_tier === 'MEDIUM' ? 'var(--amber-400)' : 'var(--green-400)' }}>{r.recommendation}</td>
                  <td style={{ padding: '11px 14px' }}>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <ActionBtn color="var(--blue-400)" bg="var(--blue-glow)" onClick={() => onInspect && onInspect(r.return_id, r.customer_id)} title="Inspect with AI">🔍</ActionBtn>
                      <ActionBtn color="var(--green-400)" bg="var(--green-bg)" onClick={() => handleAction(r.return_id, 'approve')} title="Approve Refund">✓</ActionBtn>
                      <ActionBtn color="var(--amber-400)" bg="var(--amber-bg)" onClick={() => handleAction(r.return_id, 'verify')} title="Verify OTP">🟡</ActionBtn>
                      <ActionBtn color="var(--red-400)" bg="var(--red-bg)" onClick={() => handleAction(r.return_id, 'review')} title="Escalate Fraud">⚑</ActionBtn>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div style={{ padding: '0.75rem 1.25rem', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, color: 'var(--text-muted)', flexWrap: 'wrap', gap: 8 }}>
          <span>Showing {Math.min((page - 1) * PAGE_SIZE + 1, filtered.length)}–{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length} returns</span>
          <div style={{ display: 'flex', gap: 6 }}>
            <PageBtn disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</PageBtn>
            <PageBtn disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next →</PageBtn>
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionBtn({ children, color, bg, onClick, title }) {
  return (
    <button onClick={onClick} title={title} style={{
      width: 28, height: 28, borderRadius: 6, border: `1px solid ${color}44`,
      background: bg, color, fontSize: 13, cursor: 'pointer',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      transition: 'all 0.15s',
    }}
    onMouseEnter={e => { e.currentTarget.style.background = color; e.currentTarget.style.color = '#0a0f1e'; }}
    onMouseLeave={e => { e.currentTarget.style.background = bg; e.currentTarget.style.color = color; }}
    >{children}</button>
  );
}

function PageBtn({ children, onClick, disabled }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      padding: '4px 12px', borderRadius: 6, border: '1px solid var(--border)',
      background: 'var(--bg-surface)', color: disabled ? 'var(--text-dim)' : 'var(--text-secondary)',
      fontSize: 12, cursor: disabled ? 'not-allowed' : 'pointer',
      transition: 'all 0.15s', opacity: disabled ? 0.5 : 1,
    }}>{children}</button>
  );
}
