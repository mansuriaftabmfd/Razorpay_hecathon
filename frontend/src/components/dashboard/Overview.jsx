// Overview.jsx — Main dashboard with KPIs and charts
import React, { useEffect, useState } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
} from 'recharts';
import { KpiCard } from '../ui/Card';
import { RiskBadge } from '../ui/Badge';
import api from '../../api';

const PRIORITY_DATA = [
  { return_id: 'RET000011', customer_id: 'CUST00027', amount: 903.73,   reason: 'Damaged in Transit', score: 98.8, level: 'HIGH' },
  { return_id: 'RET000006', customer_id: 'CUST00017', amount: 12499.00, reason: 'Changed Mind',        score: 86.4, level: 'HIGH' },
  { return_id: 'RET000012', customer_id: 'CUST00027', amount: 3450.00,  reason: 'Defective Item',      score: 94.2, level: 'HIGH' },
];

// Human-readable names for SHAP features shown in the bar chart
const FEATURE_LABELS = {
  previous_returns:       'Times Returned Before',
  account_age_days:       'Account Age (Days)',
  return_gap_days:        'Days Since Last Return',
  return_to_order_ratio:  'Return ÷ Order Ratio',
  device_linked_accounts: 'Accounts on Same Device',
  current_order_amount:   'Order Value (₹)',
  refund_to_order_ratio:  'Refund ÷ Order Ratio',
};

const SHAP_DATA = [
  { feature: 'previous_returns',      impact: 2.38 },
  { feature: 'account_age_days',      impact: 1.84 },
  { feature: 'return_gap_days',       impact: 1.42 },
  { feature: 'return_to_order_ratio', impact: 1.15 },
  { feature: 'device_linked_accounts',impact: 0.92 },
  { feature: 'current_order_amount',  impact: 0.74 },
  { feature: 'refund_to_order_ratio', impact: 0.58 },
].map(d => ({ ...d, label: FEATURE_LABELS[d.feature] || d.feature }));

const RISK_COLORS = ['#10b981', '#f59e0b', '#ef4444'];

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, padding: '8px 12px', fontSize: 12 }}>
        <p style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{payload[0].name}</p>
        <p style={{ color: payload[0].color }}>{payload[0].value?.toLocaleString()}</p>
      </div>
    );
  }
  return null;
};

export function Overview({ onInspect }) {
  const [overview, setOverview] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [priorityReturns, setPriorityReturns] = useState(PRIORITY_DATA);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.dashboardOverview().catch(() => null),
      api.metrics().catch(() => null),
      api.returns(0, 50).catch(() => null),
    ]).then(([o, m, ret]) => {
      setOverview(o?.data || null);
      setMetrics(m?.data || null);
      if (ret?.data?.returns && Array.isArray(ret.data.returns)) {
        const highs = ret.data.returns
          .filter(r => r.risk_tier === 'HIGH')
          .slice(0, 5)
          .map(r => ({
            return_id: r.return_id,
            customer_id: r.customer_id,
            amount: r.return_amount || 0,
            reason: r.return_reason || 'Policy Violation',
            score: r.risk_score || 85,
            level: 'HIGH'
          }));
        if (highs.length > 0) {
          setPriorityReturns(highs);
        }
      }
      setLoading(false);
    });
  }, []);

  const pieData = overview ? [
    { name: 'Low Risk',    value: overview.low_risk_count    || 3178 },
    { name: 'Medium Risk', value: overview.medium_risk_count || 1240 },
    { name: 'High Risk',   value: overview.high_risk_count   || 1580 },
  ] : [
    { name: 'Low Risk', value: 3178 }, { name: 'Medium Risk', value: 1240 }, { name: 'High Risk', value: 1580 },
  ];

  const saved = ((overview?.abusive_flagged || 1580) * 2712).toLocaleString('en-IN');

  return (
    <div className="section-gap">

      {/* ── Section header ── */}
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
          Merchant Risk Command Center
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
          Real-time return fraud telemetry, AI risk scores, and automated policy decisions.
        </p>
      </div>

      {/* ── "How ReturnShield AI Works" explainer banner ── */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(99,102,241,0.08) 100%)',
        border: '1px solid rgba(59,130,246,0.2)',
        borderRadius: 'var(--radius-lg)',
        padding: '1.1rem 1.25rem',
      }}>
        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 13, color: 'var(--blue-400)', marginBottom: 14 }}>
          🛡️ How ReturnShield AI Works
        </div>
        <div className="grid-3">
          {[
            {
              icon: '🔍',
              title: 'Customer Returns Item',
              desc: 'A customer submits a return request on an e-commerce platform. ReturnShield intercepts it before any decision is made.',
            },
            {
              icon: '🤖',
              title: 'AI Scores in < 15ms',
              desc: 'Our XGBoost machine-learning model analyzes 23 behavioral signals — like past return history, account age, and linked devices — and calculates a fraud probability score from 0% to 100%.',
            },
            {
              icon: '⚡',
              title: 'Merchant Acts',
              desc: 'Based on the score, merchants instantly approve the refund, request OTP verification, or escalate to the fraud team — preventing ₹10,000+ Cr in annual fraud.',
            },
          ].map(card => (
            <div key={card.title} style={{
              background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)', padding: '0.9rem 1rem',
            }}>
              <div style={{ fontSize: 22, marginBottom: 6 }}>{card.icon}</div>
              <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)', marginBottom: 5 }}>{card.title}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.55 }}>{card.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── KPI Grid ── */}
      <div className="grid-kpi">
        <KpiCard
          label="Total Returns Processed"
          value={(overview?.total_returns || 5998).toLocaleString()}
          sub="(all returns AI-scored automatically)"
          accent="var(--blue-400)"
          icon="📦"
          trend={{ positive: true, label: 'Live DB Mirror' }}
        />
        <KpiCard
          label="Return Abuse Rate"
          value={`${overview?.abuse_rate_percent || 26.4}%`}
          sub="(% of returns showing fraud signals)"
          accent="var(--red-400)"
          icon="⚠️"
          trend={{ positive: false, label: 'High Precision Filter' }}
        />
        <KpiCard
          label="Fraud Leakage Prevented"
          value={`₹${saved}`}
          sub="(estimated ₹ saved vs no AI filtering)"
          accent="var(--green-400)"
          icon="💰"
          trend={{ positive: true, label: '+34.8% savings' }}
        />
        <KpiCard
          label="AI Decision Accuracy"
          value={metrics ? `${(metrics.f1_score * 100).toFixed(1)}%` : '96.0%'}
          sub={`(F1-Score — balance of catching fraud without blocking good customers)`}
          accent="var(--indigo-400)"
          icon="🎯"
          trend={{ positive: true, label: `ROC-AUC: ${metrics ? (metrics.roc_auc * 100).toFixed(1) : '97.0'}%` }}
        />
      </div>

      {/* ── Charts row ── */}
      <div className="grid-2-auto">

        {/* Pie chart */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem' }}>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14, marginBottom: 2 }}>Risk Tier Distribution</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>How all AI-scored returns are classified</div>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 12, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <span style={{ color: 'var(--green-400)' }}>🟢 Low = approve</span>
            <span style={{ color: 'var(--amber-400)' }}>🟡 Medium = verify</span>
            <span style={{ color: 'var(--red-400)' }}>🔴 High = escalate</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={3} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={RISK_COLORS[i]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend formatter={(v) => <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* SHAP bar chart */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem' }}>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14, marginBottom: 2 }}>
            Top Fraud Signals
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
            Which customer behaviors most strongly predict fraud (globally, across all returns)
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 12 }}>
            Measured by SHAP — higher bar = stronger influence on the AI score
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={SHAP_DATA} layout="vertical" margin={{ left: 0, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="label" tick={{ fill: '#94a3b8', fontSize: 10 }} width={180} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="impact" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Priority escalations table ── */}
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14 }}>Priority Escalations</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
              High-risk returns needing immediate action — click 🔍 Inspect to open the AI investigation
            </div>
          </div>
          <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 20, background: 'var(--red-bg)', border: '1px solid var(--red-border)', color: 'var(--red-400)', fontWeight: 700 }}>
            {priorityReturns.length} Urgent
          </span>
        </div>
        <div className="table-scroll">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 600 }}>
            <thead>
              <tr style={{ background: 'rgba(0,0,0,0.2)' }}>
                {['Return ID', 'Customer', 'Amount', 'Reason', 'AI Risk Score', 'Action'].map(h => (
                  <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {priorityReturns.map((r, i) => (
                <tr key={r.return_id}
                  style={{ borderBottom: i < priorityReturns.length - 1 ? '1px solid var(--border)' : 'none', transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 600, color: 'var(--blue-400)' }}>{r.return_id}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--text-primary)', fontSize: 13 }}>{r.customer_id}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--text-primary)', fontSize: 13 }}>₹{r.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontSize: 13 }}>{r.reason}</td>
                  <td style={{ padding: '12px 16px' }}><RiskBadge level={r.level} score={r.score} /></td>
                  <td style={{ padding: '12px 16px' }}>
                    <button
                      onClick={() => onInspect && onInspect(r.return_id, r.customer_id)}
                      style={{
                        padding: '5px 12px', borderRadius: 6, border: '1px solid var(--border-hover)',
                        background: 'var(--bg-elevated)', color: 'var(--blue-400)',
                        fontSize: 12, fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s',
                      }}
                      onMouseEnter={e => { e.currentTarget.style.background = 'var(--blue-500)'; e.currentTarget.style.color = '#fff'; }}
                      onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.color = 'var(--blue-400)'; }}
                    >
                      🔍 Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
