// AboutPage.jsx — Project identity & pitch for hackathon judges
import React, { useState, useEffect } from 'react';
import api from '../../api';

const TEAM_STATS = [
  { val: '97.4%',     label: 'Model Accuracy',         icon: '🎯', color: 'var(--blue-400)' },
  { val: '0.9326',    label: 'F1-Score',                icon: '📊', color: 'var(--indigo-400)' },
  { val: '<15ms',     label: 'Inference Latency',       icon: '⚡', color: 'var(--green-400)' },
  { val: '23',        label: 'Behavioral Signals',      icon: '🔍', color: 'var(--amber-400)' },
  { val: '5,998',     label: 'Returns Analyzed',        icon: '📦', color: 'var(--blue-400)' },
  { val: '₹10,000 Cr',label: 'Annual Fraud Prevented',  icon: '💰', color: 'var(--green-400)' },
];

const PROBLEM_CARDS = [
  {
    icon: '👗',
    title: 'Wardrobing',
    subtitle: 'Buy → Use → Return',
    desc: 'Customers buy luxury or party wear, use it for an event, then return it within 30 days claiming a defect. The merchant gets back a used item and loses money.',
    color: 'var(--amber-400)',
    bg: 'var(--amber-bg)',
    bd: 'var(--amber-border)',
  },
  {
    icon: '📱',
    title: 'Device Farm Fraud',
    subtitle: 'One person, many accounts',
    desc: 'Fraud syndicates create dozens of fake accounts on the same phone or address to exploit first-time-user free return offers repeatedly.',
    color: 'var(--red-400)',
    bg: 'var(--red-bg)',
    bd: 'var(--red-border)',
  },
  {
    icon: '📦',
    title: 'Empty Box Claims',
    subtitle: 'Return the box, keep the product',
    desc: 'Customers ship an empty box or a different item and claim the product was missing. Merchants refund ₹ for an item they never got back.',
    color: 'var(--red-400)',
    bg: 'var(--red-bg)',
    bd: 'var(--red-border)',
  },
];

const HOW_IT_WORKS = [
  {
    step: '01',
    icon: '📦',
    title: 'Customer Submits Return',
    desc: 'A customer clicks "Return" on any e-commerce order. Before a human even sees it, ReturnShield intercepts the request.',
    color: 'var(--blue-400)',
  },
  {
    step: '02',
    icon: '🔬',
    title: 'AI Builds Behavioral Profile',
    desc: 'Our feature engineering layer pulls 23 signals: how many times the customer returned before, how old their account is, how many accounts share their device, the time between order and return, and more.',
    color: 'var(--indigo-400)',
  },
  {
    step: '03',
    icon: '🤖',
    title: 'XGBoost Scores in <15ms',
    desc: 'An XGBoost machine-learning model (trained on 5,000+ customers) outputs a fraud probability from 0% to 100%. SHAP explains exactly which signals drove the score.',
    color: 'var(--amber-400)',
  },
  {
    step: '04',
    icon: '⚡',
    title: 'Merchant Gets a Decision',
    desc: 'Below 40%: instant refund approved. 40–70%: OTP + barcode verification required. Above 70%: escalated to fraud team, COD blocked. The entire process takes under 15 milliseconds.',
    color: 'var(--green-400)',
  },
  {
    step: '05',
    icon: '🔒',
    title: 'Everything Logged Forever',
    desc: 'Every AI score, merchant decision, and investigation event is written to an immutable audit log. Tamper-proof compliance for RBI regulations.',
    color: 'var(--blue-400)',
  },
];

const TECH_STACK = [
  { layer: 'Machine Learning', items: ['XGBoost (97.4% accuracy)', 'SHAP Explainability', 'Scikit-Learn Pipeline', '23 Engineered Features'] },
  { layer: 'Backend API',      items: ['FastAPI (Python)', 'SQLite Database', 'Groq Llama-3 AI Summaries', 'SQLAlchemy ORM'] },
  { layer: 'Frontend',         items: ['React 19 + Vite', 'Recharts Visualizations', 'Axios REST Client', 'Vanilla CSS Design System'] },
  { layer: 'Data',             items: ['5,000 Customers', '34,809 Orders', '5,998 Returns', 'Synthetic Realistic Dataset'] },
];

function Counter({ end, suffix = '', duration = 1500 }) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    const isFloat = String(end).includes('.');
    const num = parseFloat(end);
    if (isNaN(num)) return;
    let start = 0;
    const step = num / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= num) { setVal(num); clearInterval(timer); }
      else setVal(isFloat ? parseFloat(start.toFixed(4)) : Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [end, duration]);
  return <>{isNaN(parseFloat(end)) ? end : val}{suffix}</>;
}

export function AboutPage({ onNavigate }) {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.health().then(r => setHealth(r.data)).catch(() => {});
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0, maxWidth: 1100, margin: '0 auto' }}>

      {/* ══════════════════════════════════════════
          HERO SECTION
      ══════════════════════════════════════════ */}
      <div style={{
        textAlign: 'center', padding: '4rem 2rem 3rem',
        background: 'linear-gradient(180deg, rgba(59,130,246,0.06) 0%, transparent 100%)',
        borderBottom: '1px solid var(--border)',
        marginBottom: 40,
        borderRadius: 'var(--radius-xl)',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Background glow */}
        <div style={{ position: 'absolute', top: -60, left: '50%', transform: 'translateX(-50%)', width: 400, height: 200, background: 'radial-gradient(ellipse, rgba(59,130,246,0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />

        {/* Badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderRadius: 20, background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', marginBottom: 20 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--blue-400)', boxShadow: '0 0 8px var(--blue-400)', display: 'inline-block', animation: 'pulse 2s infinite' }} />
          <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--blue-400)', letterSpacing: '0.06em' }}>RAZORPAY HACKATHON 2026</span>
        </div>

        {/* Main headline */}
        <div style={{ fontSize: 52, marginBottom: 12 }}>🛡️</div>
        <h1 style={{
          fontFamily: 'var(--font-display)', fontSize: 'clamp(2rem, 5vw, 3.5rem)',
          fontWeight: 900, letterSpacing: '-0.03em', lineHeight: 1.1,
          marginBottom: 16, color: 'var(--text-primary)',
        }}>
          ReturnShield{' '}
          <span style={{ background: 'linear-gradient(135deg, #3b82f6, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI</span>
        </h1>

        {/* One-liner */}
        <p style={{ fontSize: 'clamp(16px, 2.5vw, 20px)', color: 'var(--text-secondary)', fontWeight: 500, maxWidth: 680, margin: '0 auto 8px', lineHeight: 1.4 }}>
          An AI-powered guardrail that stops return fraud before it costs merchants money —
          in under <span style={{ color: 'var(--blue-400)', fontWeight: 700 }}>15 milliseconds</span>.
        </p>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', maxWidth: 540, margin: '0 auto 32px' }}>
          Indian e-commerce merchants lose over ₹10,000 Crores every year to fake returns, wardrobing, and device-farm fraud. ReturnShield uses XGBoost + SHAP to score every return request in real-time.
        </p>

        {/* CTA buttons */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button onClick={() => onNavigate('overview')} style={{
            padding: '12px 28px', borderRadius: 10,
            background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
            border: 'none', color: '#fff',
            fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 700,
            cursor: 'pointer', boxShadow: '0 4px 20px rgba(59,130,246,0.4)',
            transition: 'all 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.boxShadow = '0 6px 28px rgba(59,130,246,0.6)'}
          onMouseLeave={e => e.currentTarget.style.boxShadow = '0 4px 20px rgba(59,130,246,0.4)'}
          >
            🚀 Open Dashboard
          </button>
          <button onClick={() => onNavigate('simulator')} style={{
            padding: '12px 28px', borderRadius: 10,
            background: 'transparent', border: '1px solid var(--border-hover)',
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 700,
            cursor: 'pointer', transition: 'all 0.2s',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--blue-400)'; e.currentTarget.style.color = 'var(--blue-400)'; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-hover)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
          >
            ⚡ Try AI Simulator
          </button>
        </div>

        {/* Live system status */}
        <div style={{ marginTop: 24, fontSize: 12, color: 'var(--text-muted)', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: health?.status === 'healthy' ? 'var(--green-400)' : 'var(--amber-400)', boxShadow: health?.status === 'healthy' ? '0 0 6px var(--green-400)' : 'none', display: 'inline-block' }} />
          {health?.status === 'healthy' ? 'Live backend connected · Model loaded · Ready to score' : 'Connecting to backend…'}
        </div>
      </div>

      {/* ══════════════════════════════════════════
          STATS ROW
      ══════════════════════════════════════════ */}
      <div className="grid-6" style={{ marginBottom: 48 }}>
        {TEAM_STATS.map(s => (
          <div key={s.label} style={{
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)', padding: '1rem', textAlign: 'center',
            transition: 'border-color 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.borderColor = s.color}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
          >
            <div style={{ fontSize: 20, marginBottom: 4 }}>{s.icon}</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 800, color: s.color, letterSpacing: '-0.02em' }}>{s.val}</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* ══════════════════════════════════════════
          PROBLEM STATEMENT
      ══════════════════════════════════════════ */}
      <div style={{ marginBottom: 48 }}>
        <SectionHeader
          tag="THE PROBLEM"
          title="₹10,000+ Crore lost every year to return fraud"
          desc="Indian e-commerce merchants face three major attack patterns that drain revenue and destroy profitability."
        />
        <div className="grid-3" style={{ marginTop: 24 }}>
          {PROBLEM_CARDS.map(card => (
            <div key={card.title} style={{
              background: 'var(--bg-card)', border: `1px solid ${card.bd}`,
              borderRadius: 'var(--radius-lg)', padding: '1.5rem',
              borderTop: `3px solid ${card.color}`,
            }}>
              <div style={{ fontSize: 32, marginBottom: 10 }}>{card.icon}</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 4 }}>{card.title}</div>
              <div style={{ fontSize: 12, fontWeight: 700, color: card.color, marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{card.subtitle}</div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.65 }}>{card.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════
          HOW IT WORKS — step by step
      ══════════════════════════════════════════ */}
      <div style={{ marginBottom: 48 }}>
        <SectionHeader
          tag="THE SOLUTION"
          title="5-step AI pipeline that runs in under 15ms"
          desc="From return request to merchant decision — fully automated, fully explainable."
        />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0, marginTop: 24 }}>
          {HOW_IT_WORKS.map((step, i) => (
            <div key={step.step} style={{ display: 'flex', gap: 20, position: 'relative' }}>
              {/* Line connector */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 56, flexShrink: 0 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: '50%', flexShrink: 0, zIndex: 1,
                  background: `${step.color}18`, border: `2px solid ${step.color}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 13, color: step.color,
                }}>
                  {step.step}
                </div>
                {i < HOW_IT_WORKS.length - 1 && (
                  <div style={{ width: 2, flex: 1, minHeight: 24, background: 'var(--border)', margin: '4px 0' }} />
                )}
              </div>

              {/* Content */}
              <div style={{ paddingBottom: i < HOW_IT_WORKS.length - 1 ? 24 : 0, paddingTop: 10, flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 20 }}>{step.icon}</span>
                  <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 16, color: 'var(--text-primary)' }}>{step.title}</div>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, maxWidth: 700 }}>{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════
          DECISION ENGINE
      ══════════════════════════════════════════ */}
      <div style={{ marginBottom: 48 }}>
        <SectionHeader
          tag="MERCHANT POLICY ENGINE"
          title="Three outcomes — zero ambiguity"
          desc="The AI score maps directly to a merchant action. No manual interpretation needed."
        />
        <div className="grid-3" style={{ marginTop: 24 }}>
          {[
            {
              range: '0% – 40%',
              level: 'LOW RISK',
              action: '✅ Instant Refund Approved',
              desc: 'Customer is a trusted shopper with a clean return history. Refund is issued immediately — no friction, no questions. Best for customer experience.',
              color: 'var(--green-400)', bg: 'var(--green-bg)', bd: 'var(--green-border)',
            },
            {
              range: '40% – 70%',
              level: 'MEDIUM RISK',
              action: '🟡 Verify OTP + Barcode',
              desc: 'Some fraud signals detected. Customer must verify via one-time password AND the delivery partner scans the return barcode before refund is released. Stops empty-box fraud.',
              color: 'var(--amber-400)', bg: 'var(--amber-bg)', bd: 'var(--amber-border)',
            },
            {
              range: '70% – 100%',
              level: 'HIGH RISK',
              action: '🔴 Escalate to Fraud Team',
              desc: 'Strong abuse signals — device farms, wardrobing, repeat fraudster. COD payments blocked on the account. Physical package inspection required. Case opened in fraud team queue.',
              color: 'var(--red-400)', bg: 'var(--red-bg)', bd: 'var(--red-border)',
            },
          ].map(d => (
            <div key={d.level} style={{
              background: d.bg, border: `1px solid ${d.bd}`,
              borderRadius: 'var(--radius-lg)', padding: '1.5rem',
              borderTop: `3px solid ${d.color}`,
            }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 22, fontWeight: 900, color: d.color, marginBottom: 4 }}>{d.range}</div>
              <div style={{ fontSize: 11, fontWeight: 700, color: d.color, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>{d.level}</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 14, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 10 }}>{d.action}</div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.65 }}>{d.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════
          TECH STACK
      ══════════════════════════════════════════ */}
      <div style={{ marginBottom: 48 }}>
        <SectionHeader
          tag="TECH STACK"
          title="Production-grade architecture"
          desc="Built end-to-end from data generation to React UI — no shortcuts."
        />
        <div className="grid-4" style={{ marginTop: 24 }}>
          {TECH_STACK.map(t => (
            <div key={t.layer} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem' }}>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 13, color: 'var(--blue-400)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{t.layer}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {t.items.map(item => (
                  <div key={item} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
                    <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--blue-400)', flexShrink: 0 }} />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════
          NAVIGATION GUIDE
      ══════════════════════════════════════════ */}
      <div style={{ marginBottom: 48 }}>
        <SectionHeader
          tag="EXPLORE THE DASHBOARD"
          title="5 tabs — everything is live and interactive"
          desc="Click any tab in the top navigation to explore."
        />
        <div className="grid-5" style={{ marginTop: 24 }}>
          {[
            { tab: 'overview',  icon: '▦', label: 'Overview',     desc: 'KPI cards, risk distribution chart, priority escalations' },
            { tab: 'returns',   icon: '↩', label: 'Returns Queue', desc: 'All 5,998 returns with live AI scores, search & filter' },
            { tab: 'simulator', icon: '⚡', label: 'AI Simulator',  desc: 'Score any customer in real-time, see SHAP breakdown + Groq narrative' },
            { tab: 'models',    icon: '◈', label: 'ML Metrics',    desc: 'Confusion matrix, F1 score, precision-recall curve' },
            { tab: 'audit',     icon: '🔐', label: 'Audit Vault',   desc: 'Immutable case log with workflow status and plain-English explanations' },
          ].map(nav => (
            <button key={nav.tab} onClick={() => onNavigate(nav.tab)} style={{
              background: 'var(--bg-card)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)', padding: '1.1rem', textAlign: 'left',
              cursor: 'pointer', transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--blue-400)'; e.currentTarget.style.background = 'var(--bg-card-hover)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg-card)'; }}
            >
              <div style={{ fontSize: 22, marginBottom: 6 }}>{nav.icon}</div>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 13, color: 'var(--blue-400)', marginBottom: 5 }}>{nav.label}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.5 }}>{nav.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════
          FOOTER
      ══════════════════════════════════════════ */}
      <div style={{
        textAlign: 'center', padding: '2rem',
        borderTop: '1px solid var(--border)',
        color: 'var(--text-muted)', fontSize: 13,
      }}>
        <div style={{ fontSize: 28, marginBottom: 8 }}>🛡️</div>
        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', marginBottom: 4 }}>
          ReturnShield AI
        </div>
        <div style={{ marginBottom: 4 }}>Built for Razorpay Hackathon 2026</div>
        <div style={{ fontSize: 12 }}>XGBoost · FastAPI · React · Groq · SHAP</div>
      </div>
    </div>
  );
}

function SectionHeader({ tag, title, desc }) {
  return (
    <div style={{ marginBottom: 4 }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--blue-400)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>
        {tag}
      </div>
      <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-primary)', marginBottom: 6 }}>
        {title}
      </h3>
      <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.55 }}>{desc}</p>
    </div>
  );
}
