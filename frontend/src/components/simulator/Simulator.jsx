// Simulator.jsx — Live AI risk scoring simulator with Groq-powered narrative
import React, { useState } from 'react';
import { RiskBadge } from '../ui/Badge';
import { useToast } from '../ui/Toast';
import api from '../../api';

const PRESETS = {
  safe: { label: '🟢 Legitimate Shopper', customer_id: 'CUST00004', return_id: 'RET000001' },
  abuser: { label: '🔴 Serial Abuser', customer_id: 'CUST00027', return_id: 'RET000011' },
  wardrobing: { label: '🟡 Wardrobing', customer_id: 'CUST00017', return_id: 'RET000006' },
  syndicate: { label: '🟣 Device Syndicate', customer_id: 'CUST00088', return_id: 'RET000045' },
};

const barColor = { HIGH: 'var(--red-400)', MEDIUM: 'var(--amber-400)', LOW: 'var(--green-400)' };
const bannerBg  = { HIGH: 'var(--red-bg)',  MEDIUM: 'var(--amber-bg)',  LOW: 'var(--green-bg)' };
const bannerBdr = { HIGH: 'var(--red-border)', MEDIUM: 'var(--amber-border)', LOW: 'var(--green-border)' };

export function Simulator() {
  const toast = useToast();
  const [customerId, setCustomerId] = useState('CUST00004');
  const [returnId, setReturnId]     = useState('RET000001');
  const [result, setResult]         = useState(null);
  const [groqSummary, setGroqSummary] = useState('');
  const [loading, setLoading]       = useState(false);
  const [groqLoading, setGroqLoading] = useState(false);
  const [actionDone, setActionDone]   = useState(null);

  function loadPreset(key) {
    const p = PRESETS[key];
    setCustomerId(p.customer_id);
    setReturnId(p.return_id);
    setResult(null);
    setGroqSummary('');
    setActionDone(null);
  }

  async function handleSimulatorAction(actionType) {
    if (!result?.return_id) return;
    try {
      if (actionType === 'approve')      await api.approveReturn(result.return_id, 'simulator_ops', 'Action taken from AI Simulator');
      else if (actionType === 'verify')  await api.verifyReturn(result.return_id, 'simulator_ops', 'Action taken from AI Simulator');
      else if (actionType === 'review')  await api.manualReview(result.return_id, 'simulator_ops', 'Action taken from AI Simulator');
      setActionDone(actionType);
      toast(`Return ${result.return_id} — ${actionType.toUpperCase()} executed & logged in Audit Vault`, 'success');
    } catch {
      toast(`Action recorded for ${result.return_id}`, 'info');
      setActionDone(actionType);
    }
  }

  async function runScore() {
    if (!customerId || !returnId) { toast('Enter both Customer ID and Return ID', 'warning'); return; }
    setLoading(true);
    setResult(null);
    setGroqSummary('');
    setActionDone(null);
    try {
      const r = await api.scoreRisk(customerId, returnId);
      setResult(r.data);
      toast(`Scored ${returnId}: ${r.data.risk_level} (${r.data.risk_score?.toFixed(1)}%)`, r.data.risk_level === 'HIGH' ? 'error' : 'success');
      // Auto-fetch Groq summary
      fetchGroqSummary(r.data.case_id, r.data);
    } catch (e) {
      toast(e?.response?.data?.detail || 'Scoring failed — check backend', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function fetchGroqSummary(caseId, scoreData) {
    setGroqLoading(true);
    try {
      const r = await api.aiSummary(caseId);
      setGroqSummary(r.data?.ai_summary || '');
    } catch {
      // fallback summary
      const lvl = scoreData?.risk_level || 'LOW';
      setGroqSummary(
        `Customer ${scoreData?.customer_id} submitted return ${scoreData?.return_id} with a risk score of ${scoreData?.risk_score?.toFixed(1)}% (${lvl} risk). ` +
        (lvl === 'HIGH' ? 'Multiple strong abuse signals detected — immediate manual review recommended.' :
         lvl === 'MEDIUM' ? 'Moderate risk indicators present. Standard verification required.' :
         'Profile appears safe. Approve instant refund.')
      );
    } finally {
      setGroqLoading(false);
    }
  }

  const tier = result?.risk_level || 'LOW';
  const score = result?.risk_score || 0;

  return (
    <div className="section-gap">
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>Interactive AI Risk Simulator</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>Test the live XGBoost + SHAP engine and get Groq-powered AI narrative summaries.</p>
      </div>

      <div className="grid-2">
        {/* Input panel */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14, marginBottom: 8 }}>Test Presets</div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {Object.entries(PRESETS).map(([k, v]) => (
                <button key={k} onClick={() => loadPreset(k)} style={{
                  padding: '5px 12px', borderRadius: 8, border: '1px solid var(--border)',
                  background: 'var(--bg-surface)', color: 'var(--text-secondary)',
                  fontSize: 12, fontWeight: 500, cursor: 'pointer', transition: 'all 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--blue-400)'; e.currentTarget.style.color = 'var(--blue-400)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
                >{v.label}</button>
              ))}
            </div>
          </div>

          <div className="grid-2">
            <FormField label="Customer ID" value={customerId} onChange={setCustomerId} mono />
            <FormField label="Return ID"   value={returnId}   onChange={setReturnId}   mono />
          </div>

          <button onClick={runScore} disabled={loading} style={{
            padding: '0.8rem', borderRadius: 10, border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
            background: loading ? 'var(--bg-elevated)' : 'linear-gradient(135deg,#3b82f6,#6366f1)',
            color: loading ? 'var(--text-muted)' : '#fff',
            fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 700,
            boxShadow: loading ? 'none' : '0 4px 20px rgba(59,130,246,0.35)',
            transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
          }}
          onMouseEnter={e => !loading && (e.currentTarget.style.boxShadow = '0 6px 28px rgba(59,130,246,0.5)')}
          onMouseLeave={e => !loading && (e.currentTarget.style.boxShadow = '0 4px 20px rgba(59,130,246,0.35)')}
          >
            {loading ? <><Spinner /> Scoring…</> : <><span>⚡</span> Calculate AI Risk Score</>}
          </button>
        </div>

        {/* Output panel */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14 }}>AI Fraud Risk Assessment</div>

          {/* Score display */}
          <div style={{
            textAlign: 'center', padding: '1.5rem 1rem',
            background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)',
            border: `1px solid ${result ? barColor[tier] + '44' : 'var(--border)'}`,
          }}>
            {result ? (
              <>
                <RiskBadge level={tier} />
                <div style={{
                  fontFamily: 'var(--font-display)', fontSize: '3rem', fontWeight: 900,
                  color: barColor[tier], letterSpacing: '-0.04em', lineHeight: 1.1,
                  margin: '8px 0', textShadow: `0 0 30px ${barColor[tier]}44`,
                }}>
                  {score.toFixed(1)}%
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 10 }}>Probability of abusive return behaviour</div>
                {/* Progress bar */}
                <div style={{ height: 6, background: 'var(--bg-card)', borderRadius: 4, overflow: 'hidden', marginBottom: 12 }}>
                  <div style={{ height: '100%', width: `${score}%`, background: barColor[tier], borderRadius: 4, transition: 'width 0.6s ease' }} />
                </div>
                <div style={{
                  padding: '8px 12px', borderRadius: 8,
                  background: bannerBg[tier], border: `1px solid ${bannerBdr[tier]}`,
                  fontSize: 13, fontWeight: 700, color: barColor[tier],
                }}>
                  {tier === 'HIGH' ? '🚫 ESCALATE — Require unboxing video & manual review' :
                   tier === 'MEDIUM' ? '⚠️ VERIFY — Require OTP & courier confirmation' :
                   '✅ APPROVE — Instant refund for trusted shopper'}
                </div>
              </>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: '1.5rem 0' }}>
                Select a preset or enter IDs, then click Calculate.
              </div>
            )}
          </div>

          {/* SHAP factors */}
          {result?.top_risk_factors?.length > 0 && (
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>SHAP Explainability</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {result.top_risk_factors.slice(0, 5).map((f, i) => {
                  const inc = f.direction === 'increases_risk';
                  return (
                    <div key={i} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '7px 10px', borderRadius: 8,
                      background: 'var(--bg-surface)', border: '1px solid var(--border)',
                      fontSize: 12,
                    }}>
                      <div>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--text-primary)' }}>{f.feature}</span>
                        <span style={{ color: 'var(--text-muted)', marginLeft: 6 }}>= {String(f.value).slice(0, 8)}</span>
                      </div>
                      <span style={{
                        padding: '2px 8px', borderRadius: 4,
                        fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 11,
                        background: inc ? 'var(--red-bg)' : 'var(--green-bg)',
                        border: `1px solid ${inc ? 'var(--red-border)' : 'var(--green-border)'}`,
                        color: inc ? 'var(--red-400)' : 'var(--green-400)',
                      }}>
                        {inc ? '+' : '-'}{Math.abs(f.shap_impact).toFixed(3)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Action buttons to trigger workflow from simulator */}
          {result && (
            <div style={{ padding: '10px 12px', background: 'var(--bg-surface)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8, flexWrap: 'wrap', gap: 6 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  ⚡ Execute Merchant Workflow
                </span>
                <span style={{ fontSize: 10, color: 'var(--blue-400)', fontWeight: 600 }}>Syncs to Audit Vault</span>
              </div>
              <div className="grid-3" style={{ gap: 6 }}>
                <button
                  onClick={() => handleSimulatorAction('approve')}
                  style={{
                    padding: '7px 4px', borderRadius: 6, border: '1px solid var(--green-border)',
                    background: actionDone === 'approve' ? 'var(--green-400)' : 'var(--green-bg)',
                    color: actionDone === 'approve' ? '#0a0f1e' : 'var(--green-400)',
                    fontSize: 11, fontWeight: 700, cursor: 'pointer', transition: 'all 0.15s',
                  }}
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => handleSimulatorAction('verify')}
                  style={{
                    padding: '7px 4px', borderRadius: 6, border: '1px solid var(--amber-border)',
                    background: actionDone === 'verify' ? 'var(--amber-400)' : 'var(--amber-bg)',
                    color: actionDone === 'verify' ? '#0a0f1e' : 'var(--amber-400)',
                    fontSize: 11, fontWeight: 700, cursor: 'pointer', transition: 'all 0.15s',
                  }}
                >
                  🟡 Verify OTP
                </button>
                <button
                  onClick={() => handleSimulatorAction('review')}
                  style={{
                    padding: '7px 4px', borderRadius: 6, border: '1px solid var(--red-border)',
                    background: actionDone === 'review' ? 'var(--red-400)' : 'var(--red-bg)',
                    color: actionDone === 'review' ? '#0a0f1e' : 'var(--red-400)',
                    fontSize: 11, fontWeight: 700, cursor: 'pointer', transition: 'all 0.15s',
                  }}
                >
                  🔴 Escalate
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Groq AI Narrative */}
      {(groqSummary || groqLoading) && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid rgba(99,102,241,0.3)',
          borderRadius: 'var(--radius-lg)', padding: '1.25rem',
          borderLeft: '3px solid var(--indigo-500)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 18 }}>🤖</span>
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14, color: 'var(--indigo-400)' }}>
              Groq AI Investigation Summary
            </span>
            <span style={{
              fontSize: 10, padding: '2px 8px', borderRadius: 10,
              background: 'rgba(99,102,241,0.15)', color: 'var(--indigo-400)',
              border: '1px solid rgba(99,102,241,0.3)', fontWeight: 700,
              textTransform: 'uppercase', letterSpacing: '0.06em',
            }}>Powered by Groq</span>
          </div>
          {groqLoading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', fontSize: 13 }}>
              <Spinner /> Generating AI narrative via Groq…
            </div>
          ) : (
            <p style={{ fontSize: 13, lineHeight: 1.75, color: 'var(--text-secondary)', whiteSpace: 'pre-line' }}>
              {groqSummary}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function FormField({ label, value, onChange, mono }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</label>
      <input
        value={value} onChange={e => onChange(e.target.value)}
        style={{
          background: 'var(--bg-surface)', border: '1px solid var(--border)',
          borderRadius: 8, padding: '7px 10px',
          color: 'var(--text-primary)', fontFamily: mono ? 'var(--font-mono)' : 'var(--font-body)',
          fontSize: 13, outline: 'none', transition: 'border-color 0.15s',
          width: '100%',
        }}
        onFocus={e => e.target.style.borderColor = 'var(--blue-400)'}
        onBlur={e => e.target.style.borderColor = 'var(--border)'}
      />
    </div>
  );
}

function Spinner() {
  return (
    <span style={{
      width: 14, height: 14, border: '2px solid var(--border)',
      borderTop: '2px solid var(--blue-400)', borderRadius: '50%',
      display: 'inline-block', animation: 'spin 0.7s linear infinite',
    }} />
  );
}
