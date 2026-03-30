/**
 * NicheLab — Auth & Subscription Flow
 * File: pages/auth-subscription.tsx  (or app/auth-subscription/page.tsx for App Router)
 *
 * Covers:
 *  - Step 1: Plan selection (Starter / Pro, Monthly / Annual toggle)
 *  - Step 2: Registration form with legal consent gate
 *  - Step 3: Email verification holding screen
 *  - Redirect logic: confirmed Pro → dashboard, confirmed Starter → dashboard
 *
 * Dependencies:
 *   npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
 *   (Tailwind CSS assumed — mirrors existing NicheLab gold/light theme)
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useRouter, useSearchParams } from 'next/navigation';

// ─────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────
type Plan = 'starter' | 'pro';
type Cycle = 'monthly' | 'yearly';
type Step = 'plan' | 'register' | 'verify';

interface PriceConfig {
  label: string;
  monthly: { price: string; sub: string; link: string };
  yearly:  { price: string; sub: string; link: string; saving: string };
  features: string[];
  dimFeatures?: string[];
}

// ─────────────────────────────────────────────────────────────────
// PLAN CONFIGURATION
// ─────────────────────────────────────────────────────────────────
const PLANS: Record<Plan, PriceConfig> = {
  starter: {
    label: 'Starter',
    monthly: { price: '$36',  sub: 'per month',          link: 'https://buy.stripe.com/9B63cw0A72uufWf5ywebu00' },
    yearly:  { price: '$299', sub: 'per year',            link: 'https://buy.stripe.com/aFa4gAdmT8SS5hB1igebu01', saving: 'Save $133' },
    features: [
      '10 intelligence briefs per week',
      '15-Point Comprehensive Analytical Framework',
      'Premium Document Delivery (PDF & Word)',
      'Encrypted Research Environment',
      'Rigorous APA-7 Citation Standard',
    ],
    dimFeatures: [
      'Unrestricted Global Intelligence Access',
      'Pro-Tier Executive Summaries',
      'Priority Algorithmic Processing',
      'Advance Intelligence on Emerging Verticals',
      'Direct Analyst Correspondence',
    ],
  },
  pro: {
    label: 'Pro',
    monthly: { price: '$84',  sub: 'per month',           link: 'https://buy.stripe.com/bJe00kbeLc547pJgdaebu02' },
    yearly:  { price: '$699', sub: 'per year',             link: 'https://buy.stripe.com/aFa6oI0A7glk6lFf96ebu03', saving: 'Save $309' },
    features: [
      'Unrestricted Global Intelligence Access',
      '15-Point Comprehensive Analytical Framework',
      'Pro-Tier Executive Summaries',
      'Premium Document Delivery (PDF & Word)',
      'Encrypted Research Environment',
      'Rigorous APA-7 Citation Standard',
      'Priority Algorithmic Processing',
      'Advance Intelligence on Emerging Verticals',
      'Direct Analyst Correspondence',
    ],
  },
};

// ─────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────
export default function AuthSubscriptionPage() {
  const supabase   = createClientComponentClient();
  const router     = useRouter();
  const params     = useSearchParams();

  const [step,   setStep]   = useState<Step>('plan');
  const [plan,   setPlan]   = useState<Plan>((params?.get('plan') as Plan) || 'pro');
  const [cycle,  setCycle]  = useState<Cycle>((params?.get('cycle') as Cycle) || 'monthly');
  const [email,  setEmail]  = useState('');
  const [name,   setName]   = useState('');
  const [focus,  setFocus]  = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');
  const [registeredEmail, setRegisteredEmail] = useState('');

  // ── Redirect already-confirmed members immediately ─────────────
  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const { data: profile } = await supabase
        .from('profiles')
        .select('tier, role, email_confirmed_at')
        .eq('id', session.user.id)
        .single();

      if (profile?.email_confirmed_at) {
        // Confirmed — send to dashboard
        router.replace('/dashboard');
      }
    };
    checkSession();
  }, [supabase, router]);

  // ── Registration handler ───────────────────────────────────────
  const handleRegister = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreed) { setError('You must accept the Terms of Service and Privacy Policy to continue.'); return; }
    setError('');
    setLoading(true);

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password: crypto.randomUUID(), // Temporary — user sets password via email link
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback?plan=${plan}&cycle=${cycle}`,
          data: {
            full_name:          name.trim(),
            professional_focus: focus.trim(),
            tier:               plan,
            source:             'web-signup',
          },
        },
      });

      if (signUpError) throw signUpError;

      // Record legal consent (fire and forget — non-blocking)
      if (data.user) {
        supabase.rpc('record_legal_consent', {
          p_user_id:     data.user.id,
          p_tos_version: '2025-01-01',
        }).catch(() => {}); // Silently handle — consent timestamp is best-effort here
      }

      setRegisteredEmail(email);
      setStep('verify');

    } catch (err: any) {
      if (err.message?.includes('already registered')) {
        setError('An account with this email already exists. Please sign in via the Members Console.');
      } else {
        setError(err.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [agreed, email, name, focus, plan, cycle, supabase]);

  // ─────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────
  return (
    <div style={{
      minHeight: '100vh',
      background: '#FAFAF7',
      fontFamily: "'Instrument Sans', system-ui, sans-serif",
      paddingTop: '80px',
      paddingBottom: '80px',
    }}>

      {/* ── Navigation Logo ────────────────────────────────── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, height: 66,
        background: 'rgba(250,250,247,.95)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(20,20,16,.10)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 48px', zIndex: 1000,
      }}>
        <a href="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <span style={{
            width: 34, height: 34, background: '#141410', borderRadius: 7,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#B8860B', fontWeight: 700, fontSize: 13,
          }}>N</span>
          <span style={{ fontFamily: "'Playfair Display', Georgia, serif", fontSize: 19, fontWeight: 500, color: '#141410' }}>
            NicheLab
          </span>
        </a>
        <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: '#A8A898', letterSpacing: '1.5px', textTransform: 'uppercase' }}>
          Secure Registration
        </span>
      </nav>

      {/* ── STEP: PLAN SELECTION ──────────────────────────── */}
      {step === 'plan' && (
        <PlanSelection
          plan={plan}    setPlan={setPlan}
          cycle={cycle}  setCycle={setCycle}
          onContinue={() => setStep('register')}
        />
      )}

      {/* ── STEP: REGISTRATION FORM ───────────────────────── */}
      {step === 'register' && (
        <RegistrationForm
          plan={plan} cycle={cycle}
          email={email}   setEmail={setEmail}
          name={name}     setName={setName}
          focus={focus}   setFocus={setFocus}
          agreed={agreed} setAgreed={setAgreed}
          loading={loading}
          error={error}
          onBack={() => setStep('plan')}
          onSubmit={handleRegister}
        />
      )}

      {/* ── STEP: EMAIL VERIFICATION ──────────────────────── */}
      {step === 'verify' && (
        <VerificationScreen email={registeredEmail} plan={plan} />
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Plan Selection
// ─────────────────────────────────────────────────────────────────
function PlanSelection({
  plan, setPlan, cycle, setCycle, onContinue,
}: {
  plan: Plan; setPlan: (p: Plan) => void;
  cycle: Cycle; setCycle: (c: Cycle) => void;
  onContinue: () => void;
}) {
  const S = styles;
  const current = PLANS[plan][cycle];

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '0 24px' }}>

      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <span style={S.eyebrow}>Select Your Membership</span>
        <h1 style={S.headline}>Intelligence access begins<br />with the right <em style={{ color: '#B8860B', fontStyle: 'italic' }}>commitment.</em></h1>
        <p style={S.subtext}>All memberships include the complete 15-section research methodology. Choose the tier that matches your analytical cadence.</p>
      </div>

      {/* Billing Toggle */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 40 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 14,
          background: '#fff', border: '1px solid rgba(20,20,16,.10)',
          borderRadius: 100, padding: '5px 5px 5px 18px',
        }}>
          <span
            onClick={() => setCycle('monthly')}
            style={{ fontSize: 14, color: cycle === 'monthly' ? '#141410' : '#A8A898', fontWeight: cycle === 'monthly' ? 500 : 400, cursor: 'pointer', userSelect: 'none' }}
          >Monthly</span>
          <div
            onClick={() => setCycle(cycle === 'monthly' ? 'yearly' : 'monthly')}
            style={{
              width: 44, height: 24, background: cycle === 'yearly' ? '#B8860B' : 'rgba(20,20,16,.16)',
              borderRadius: 100, position: 'relative', cursor: 'pointer', transition: 'background .25s',
            }}
          >
            <div style={{
              position: 'absolute', top: 3, left: 3, width: 18, height: 18,
              background: '#fff', borderRadius: '50%', boxShadow: '0 1px 4px rgba(0,0,0,.15)',
              transition: 'transform .25s cubic-bezier(.34,1.56,.64,1)',
              transform: cycle === 'yearly' ? 'translateX(20px)' : 'none',
            }} />
          </div>
          <span
            onClick={() => setCycle('yearly')}
            style={{ fontSize: 14, color: cycle === 'yearly' ? '#141410' : '#A8A898', fontWeight: cycle === 'yearly' ? 500 : 400, cursor: 'pointer', userSelect: 'none' }}
          >Annual</span>
          <span style={{
            background: '#B8860B', color: '#fff', padding: '5px 12px', borderRadius: 100,
            fontFamily: 'DM Mono, monospace', fontSize: 9, letterSpacing: 1, textTransform: 'uppercase',
          }}>Save 30%</span>
        </div>
      </div>

      {/* Plan Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
        {(['starter', 'pro'] as Plan[]).map(p => {
          const cfg  = PLANS[p];
          const data = cfg[cycle];
          const isActive = plan === p;

          return (
            <div
              key={p}
              onClick={() => setPlan(p)}
              style={{
                background: isActive ? '#FFFEF8' : '#fff',
                border: `2px solid ${isActive ? '#B8860B' : 'rgba(20,20,16,.10)'}`,
                borderRadius: 16, padding: '36px 32px',
                cursor: 'pointer', position: 'relative',
                transition: 'all .2s',
                boxShadow: isActive ? '0 8px 32px rgba(184,134,11,.12)' : 'none',
              }}
            >
              {p === 'pro' && (
                <span style={{
                  position: 'absolute', top: -1, right: 24,
                  background: '#B8860B', color: '#fff',
                  fontFamily: 'DM Mono, monospace', fontSize: 9, fontWeight: 500, letterSpacing: 1.5,
                  padding: '5px 12px', borderRadius: '0 0 8px 8px', textTransform: 'uppercase',
                }}>Most Selected</span>
              )}

              <div style={{ fontFamily: 'DM Mono, monospace', fontSize: 10, letterSpacing: 2, textTransform: 'uppercase', color: '#A8A898', marginBottom: 14 }}>
                {cfg.label}
              </div>
              <div style={{ fontFamily: "'Playfair Display', Georgia, serif", fontSize: 58, fontWeight: 400, lineHeight: 1, letterSpacing: -2, color: '#141410', marginBottom: 4 }}>
                {data.price}
              </div>
              <div style={{ fontSize: 13, color: '#A8A898', marginBottom: 4 }}>{data.sub}</div>
              {'saving' in data && (
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: 10, color: '#16c784', letterSpacing: .5, marginBottom: 20 }}>
                  {data.saving} vs monthly
                </div>
              )}
              <div style={{ marginBottom: 20, paddingTop: 8, borderTop: '1px solid rgba(20,20,16,.08)' }}></div>

              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 9 }}>
                {cfg.features.map(f => (
                  <li key={f} style={{ display: 'flex', gap: 10, fontSize: 13, color: '#6A6A58', lineHeight: 1.5 }}>
                    <span style={{ color: '#B8860B', flexShrink: 0, marginTop: 1 }}>✓</span>{f}
                  </li>
                ))}
                {cfg.dimFeatures?.map(f => (
                  <li key={f} style={{ display: 'flex', gap: 10, fontSize: 13, color: '#C8C8B8', lineHeight: 1.5 }}>
                    <span style={{ color: '#C8C8B8', flexShrink: 0, marginTop: 1 }}>–</span>{f}
                  </li>
                ))}
              </ul>

              {isActive && (
                <div style={{ marginTop: 20, display: 'flex', alignItems: 'center', gap: 6, color: '#B8860B', fontSize: 13, fontWeight: 500 }}>
                  <span>●</span> Selected
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Trust bar */}
      <TrustBar />

      {/* Continue CTA */}
      <div style={{ textAlign: 'center', marginTop: 32 }}>
        <button onClick={onContinue} style={S.btnGold}>
          Continue with {PLANS[plan].label} — {PLANS[plan][cycle].price} <span style={{ opacity: .8 }}>→</span>
        </button>
        <p style={{ marginTop: 12, fontSize: 12, color: '#A8A898', fontFamily: 'DM Mono, monospace', letterSpacing: .3 }}>
          Registration required before payment. Secure billing via Stripe.
        </p>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Registration Form with Legal Gate
// ─────────────────────────────────────────────────────────────────
function RegistrationForm({
  plan, cycle, email, setEmail, name, setName, focus, setFocus,
  agreed, setAgreed, loading, error, onBack, onSubmit,
}: {
  plan: Plan; cycle: Cycle;
  email: string; setEmail: (v: string) => void;
  name: string;  setName:  (v: string) => void;
  focus: string; setFocus: (v: string) => void;
  agreed: boolean; setAgreed: (v: boolean) => void;
  loading: boolean; error: string;
  onBack: () => void;
  onSubmit: (e: React.FormEvent) => void;
}) {
  const S = styles;
  const cfg  = PLANS[plan];
  const data = cfg[cycle];
  const canSubmit = Boolean(email && name && focus && agreed && !loading);

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '0 24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '5fr 7fr', gap: 64, alignItems: 'start' }}>

        {/* Left: Plan summary */}
        <div>
          <button onClick={onBack} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, color: '#A8A898', marginBottom: 32, display: 'flex', alignItems: 'center', gap: 6 }}>
            ← Back to plans
          </button>

          <span style={S.eyebrow}>Selected Plan</span>
          <h2 style={{ fontFamily: "'Playfair Display', Georgia, serif", fontSize: 36, fontWeight: 400, letterSpacing: -1, lineHeight: 1.1, marginBottom: 8, color: '#141410' }}>
            NicheLab <em style={{ fontStyle: 'italic', color: '#B8860B' }}>{cfg.label}</em>
          </h2>
          <div style={{ fontFamily: "'Playfair Display', Georgia, serif", fontSize: 48, fontWeight: 400, letterSpacing: -2, color: '#141410', lineHeight: 1, marginBottom: 6 }}>
            {data.price}
          </div>
          <div style={{ fontSize: 13, color: '#A8A898', marginBottom: 28 }}>{data.sub}</div>

          <div style={{ borderTop: '1px solid rgba(20,20,16,.10)', paddingTop: 20 }}>
            {cfg.features.slice(0, 5).map(f => (
              <div key={f} style={{ display: 'flex', gap: 10, fontSize: 13, color: '#6A6A58', marginBottom: 10, lineHeight: 1.5 }}>
                <span style={{ color: '#B8860B' }}>✓</span>{f}
              </div>
            ))}
            {cfg.features.length > 5 && (
              <div style={{ fontSize: 12, color: '#A8A898', fontFamily: 'DM Mono, monospace', letterSpacing: .3, marginTop: 6 }}>
                +{cfg.features.length - 5} more benefits included
              </div>
            )}
          </div>

          <div style={{ marginTop: 28 }}>
            <TrustBar compact />
          </div>
        </div>

        {/* Right: Form */}
        <div style={{ background: '#fff', border: '1px solid rgba(20,20,16,.10)', borderRadius: 16, padding: 44, boxShadow: '0 16px 48px rgba(20,20,16,.09)' }}>
          <div style={{ fontFamily: "'Playfair Display', Georgia, serif", fontSize: 22, fontWeight: 500, marginBottom: 28, color: '#141410' }}>
            Create Your Account
          </div>

          <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>

            <FormField label="Full Name *" htmlFor="reg-name">
              <input
                id="reg-name"
                type="text"
                required
                autoComplete="name"
                placeholder="Dr. Jane Smith"
                value={name}
                onChange={e => setName(e.target.value)}
                style={styles.input}
              />
            </FormField>

            <FormField label="Email Address *" htmlFor="reg-email">
              <input
                id="reg-email"
                type="email"
                required
                autoComplete="email"
                placeholder="jane@institution.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                style={styles.input}
              />
            </FormField>

            <FormField label="Professional / Company Focus *" htmlFor="reg-focus">
              <input
                id="reg-focus"
                type="text"
                required
                placeholder="e.g. Venture Capital · Series A · B2B SaaS"
                value={focus}
                onChange={e => setFocus(e.target.value)}
                style={styles.input}
              />
            </FormField>

            {/* ── Legal Consent Gate ─────────────────────── */}
            <div style={{
              background: agreed ? 'rgba(184,134,11,.05)' : 'rgba(20,20,16,.03)',
              border: `1px solid ${agreed ? 'rgba(184,134,11,.25)' : 'rgba(20,20,16,.10)'}`,
              borderRadius: 10, padding: '16px 18px', marginBottom: 22,
              transition: 'all .2s',
            }}>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: 14, cursor: 'pointer' }}>
                <div style={{ position: 'relative', flexShrink: 0, marginTop: 2 }}>
                  <input
                    type="checkbox"
                    checked={agreed}
                    onChange={e => setAgreed(e.target.checked)}
                    style={{ position: 'absolute', opacity: 0, width: '100%', height: '100%', cursor: 'pointer' }}
                  />
                  <div style={{
                    width: 20, height: 20,
                    background: agreed ? '#B8860B' : '#fff',
                    border: `2px solid ${agreed ? '#B8860B' : 'rgba(20,20,16,.25)'}`,
                    borderRadius: 5,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    transition: 'all .15s',
                  }}>
                    {agreed && <span style={{ color: '#fff', fontSize: 12, lineHeight: 1 }}>✓</span>}
                  </div>
                </div>
                <span style={{ fontSize: 13, color: '#6A6A58', lineHeight: 1.65 }}>
                  I have read, understood, and agree to the NicheLab{' '}
                  <a href="/legal/terms-of-service" target="_blank" rel="noopener noreferrer" style={{ color: '#B8860B', textDecoration: 'underline' }}>
                    Terms of Service
                  </a>{' '}
                  and{' '}
                  <a href="/legal/privacy-policy" target="_blank" rel="noopener noreferrer" style={{ color: '#B8860B', textDecoration: 'underline' }}>
                    Privacy Policy
                  </a>
                  . I acknowledge that NicheLab research materials are provided for informational purposes and do not constitute financial advice.
                </span>
              </label>
            </div>

            {/* Error display */}
            {error && (
              <div style={{
                background: '#fff5f5', border: '1px solid rgba(239,68,68,.25)',
                borderRadius: 8, padding: '12px 16px', marginBottom: 16,
                fontSize: 13, color: '#b91c1c', lineHeight: 1.5,
              }}>
                {error}
              </div>
            )}

            {/* Submit — disabled until legal gate is cleared */}
            <button
              type="submit"
              disabled={!canSubmit}
              style={{
                ...styles.btnGold,
                opacity: canSubmit ? 1 : 0.45,
                cursor: canSubmit ? 'pointer' : 'not-allowed',
                width: '100%',
                justifyContent: 'center',
                fontSize: 15,
              }}
            >
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <LoadingSpinner /> Processing…
                </span>
              ) : (
                `Verify Email & Continue →`
              )}
            </button>

            <p style={{ marginTop: 12, fontSize: 11, color: '#A8A898', textAlign: 'center', fontFamily: 'DM Mono, monospace', letterSpacing: .3, lineHeight: 1.6 }}>
              A verification link will be sent to your email.<br />
              Payment is collected only after confirmation.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Email Verification Holding Screen
// ─────────────────────────────────────────────────────────────────
function VerificationScreen({ email, plan }: { email: string; plan: Plan }) {
  const [resending, setResending] = useState(false);
  const [resent,    setResent]    = useState(false);
  const supabase = createClientComponentClient();

  const handleResend = async () => {
    setResending(true);
    try {
      await supabase.auth.resend({ type: 'signup', email });
      setResent(true);
    } catch (_) {}
    finally { setResending(false); }
  };

  return (
    <div style={{ maxWidth: 540, margin: '0 auto', padding: '20px 24px 0', textAlign: 'center' }}>

      {/* Animated envelope */}
      <div style={{
        width: 80, height: 80,
        background: 'rgba(184,134,11,.08)',
        border: '1px solid rgba(184,134,11,.2)',
        borderRadius: 20,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 36, margin: '0 auto 28px',
        animation: 'pulse 2s ease infinite',
      }}>
        ✉
      </div>

      <span style={styles.eyebrow}>Verification Required</span>

      <h1 style={{
        fontFamily: "'Playfair Display', Georgia, serif",
        fontSize: 40, fontWeight: 400, letterSpacing: -1.5, lineHeight: 1.08,
        color: '#141410', margin: '12px 0 18px',
      }}>
        Check your<br /><em style={{ fontStyle: 'italic', color: '#B8860B' }}>inbox.</em>
      </h1>

      <p style={{ fontSize: 16, color: '#6A6A58', lineHeight: 1.80, fontWeight: 300, marginBottom: 32 }}>
        A verification link has been dispatched to{' '}
        <strong style={{ color: '#141410', fontWeight: 500 }}>{email}</strong>.<br />
        Access to NicheLab's research infrastructure requires email confirmation
        to protect the integrity of proprietary intelligence data.
      </p>

      {/* Status card */}
      <div style={{
        background: '#fff', border: '1px solid rgba(20,20,16,.10)',
        borderRadius: 14, padding: '28px 32px', marginBottom: 32,
        boxShadow: '0 4px 20px rgba(20,20,16,.07)',
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { ico: '📧', title: 'Verify your email', desc: 'Click the secure link in your email to confirm your address.' },
            { ico: '💳', title: 'Complete payment', desc: `You'll be redirected to activate your ${PLANS[plan].label} membership.` },
            { ico: '📊', title: 'Access intelligence', desc: 'Full research dashboard access is granted immediately upon payment.' },
          ].map(item => (
            <div key={item.title} style={{ display: 'flex', gap: 16, textAlign: 'left' }}>
              <div style={{
                width: 38, height: 38, background: 'rgba(184,134,11,.07)',
                border: '1px solid rgba(184,134,11,.18)', borderRadius: 9,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 16, flexShrink: 0,
              }}>{item.ico}</div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#141410', marginBottom: 3 }}>{item.title}</div>
                <div style={{ fontSize: 13, color: '#6A6A58', lineHeight: 1.55 }}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resend control */}
      {!resent ? (
        <button
          onClick={handleResend}
          disabled={resending}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 14, color: '#B8860B', textDecoration: 'underline' }}
        >
          {resending ? 'Sending…' : "Didn't receive it? Resend verification email"}
        </button>
      ) : (
        <p style={{ fontSize: 14, color: '#16c784', fontFamily: 'DM Mono, monospace', letterSpacing: .3 }}>
          ✓ Verification email resent successfully
        </p>
      )}

      <p style={{ marginTop: 24, fontSize: 12, color: '#A8A898', fontFamily: 'DM Mono, monospace', letterSpacing: .3, lineHeight: 1.7 }}>
        Check spam/junk if not received within 2 minutes.<br />
        From: <strong>noreply@nichelab.io</strong>
      </p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Trust Bar
// ─────────────────────────────────────────────────────────────────
function TrustBar({ compact = false }: { compact?: boolean }) {
  const items = [
    { ico: '🔒', text: 'Secure 256-bit Encrypted Payment' },
    { ico: '🏛', text: 'Institutional Grade Data Protection' },
    { ico: '💳', text: 'Stripe PCI-DSS Level 1 Certified' },
  ];
  return (
    <div style={{
      display: 'flex',
      flexDirection: compact ? 'column' : 'row',
      flexWrap: 'wrap',
      gap: compact ? 10 : 20,
      justifyContent: compact ? 'flex-start' : 'center',
      background: compact ? 'transparent' : 'rgba(184,134,11,.05)',
      border: compact ? 'none' : '1px solid rgba(184,134,11,.12)',
      borderRadius: compact ? 0 : 10,
      padding: compact ? 0 : '14px 24px',
    }}>
      {items.map(item => (
        <div key={item.text} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: compact ? 14 : 16 }}>{item.ico}</span>
          <span style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: compact ? 10 : 11,
            letterSpacing: compact ? .3 : 1,
            color: '#B8860B',
            textTransform: compact ? 'none' : 'uppercase',
          }}>
            {item.text}
          </span>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────
function FormField({ label, htmlFor, children }: { label: string; htmlFor: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <label htmlFor={htmlFor} style={{
        display: 'block', fontFamily: 'DM Mono, monospace',
        fontSize: 9.5, letterSpacing: 1.5, textTransform: 'uppercase',
        color: '#A8A898', marginBottom: 8,
      }}>{label}</label>
      {children}
    </div>
  );
}

function LoadingSpinner() {
  return (
    <span style={{
      display: 'inline-block', width: 14, height: 14,
      border: '2px solid rgba(255,255,255,.3)',
      borderTopColor: '#fff', borderRadius: '50%',
      animation: 'spin .6s linear infinite',
    }} />
  );
}

// ─────────────────────────────────────────────────────────────────
// SHARED STYLES
// ─────────────────────────────────────────────────────────────────
const styles = {
  eyebrow: {
    display: 'inline-flex', alignItems: 'center', gap: 8,
    fontFamily: 'DM Mono, monospace', fontSize: 10.5, letterSpacing: 2.5,
    textTransform: 'uppercase' as const, color: '#B8860B', marginBottom: 16,
  },
  headline: {
    fontFamily: "'Playfair Display', Georgia, serif",
    fontSize: 'clamp(38px, 4.5vw, 58px)', fontWeight: 400,
    lineHeight: 1.07, letterSpacing: -1.5,
    color: '#141410', marginBottom: 18,
  },
  subtext: {
    fontSize: 17, color: '#6A6A58', lineHeight: 1.80,
    fontWeight: 300, maxWidth: 520, margin: '0 auto 0',
  },
  btnGold: {
    display: 'inline-flex', alignItems: 'center', gap: 8,
    padding: '15px 34px',
    background: '#B8860B', color: '#fff', border: 'none',
    borderRadius: 8, fontSize: 15, fontWeight: 500,
    cursor: 'pointer', fontFamily: "'Instrument Sans', system-ui, sans-serif",
    transition: 'all .22s',
    letterSpacing: .2,
  },
  input: {
    width: '100%', padding: '12px 16px',
    background: '#FAFAF7', border: '1px solid rgba(20,20,16,.15)',
    borderRadius: 7, color: '#141410', fontSize: 14,
    fontFamily: "'Instrument Sans', system-ui, sans-serif",
    outline: 'none', transition: 'all .2s',
    boxSizing: 'border-box' as const,
  },
};
