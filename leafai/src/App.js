import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './components/LanguageSelector';
import VoiceAssistant from './components/VoiceAssistant/VoiceAssistant';

const API_BASE = "http://localhost:5000/api";

/* ─── Simple Router ─────────────────────────────────────── */
function useRouter() {
  const [path, setPath] = useState(window.location.hash || '#/');
  useEffect(() => {
    const onHash = () => setPath(window.location.hash || '#/');
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);
  const navigate = useCallback((to) => { window.location.hash = to; }, []);
  return { path, navigate };
}

/* ─── Navbar ─────────────────────────────────────────────── */
function Navbar({ navigate, path, user }) {
  const { t } = useTranslation();
  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate('#/')} id="nav-logo">
        Leaf<span>AI</span>
      </div>
      <div className="navbar-links">
        <a id="nav-how" onClick={() => navigate('#/how-it-works')} style={{color: path==='#/how-it-works'?'#fefae0':undefined}}>{t('nav.how')}</a>
        <a id="nav-scan" onClick={() => navigate('#/scanner')} style={{color: path==='#/scanner'?'#fefae0':undefined}}>{t('nav.scan')}</a>
        <a id="nav-ty" onClick={() => navigate('#/thankyou')} style={{color: path==='#/thankyou'?'#fefae0':undefined}}>{t('nav.summary')}</a>
        <LanguageSelector />
        {user && <span className="user-badge" style={{color: 'white', background: 'rgba(255,255,255,0.1)', padding: '0.3rem 0.8rem', borderRadius: '20px', fontSize: '0.85rem'}}>👤 {user.name}</span>}
      </div>
    </nav>
  );
}

/* ─── Fade-In Hook ───────────────────────────────────────── */
function useFadeIn() {
  useEffect(() => {
    const sections = document.querySelectorAll('.fade-in-section');
    const observer = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.15 }
    );
    sections.forEach(s => observer.observe(s));
    return () => observer.disconnect();
  }, []);
}

/* ════════════════════════════════════════════════════════════
   PAGE 1 — AUTH
════════════════════════════════════════════════════════════ */
function AuthPage({ navigate, setUser }) {
  const { t, i18n } = useTranslation();
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ name:'', email:'', pass:'', confirm:'' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const set = (k, v) => setForm(f => ({...f, [k]: v}));

  const validateLogin = () => {
    const e = {};
    if (!form.email.includes('@')) e.email = t('errors.email');
    if (form.pass.length < 6) e.pass = t('errors.pass');
    return e;
  };
  const validateSignup = () => {
    const e = validateLogin();
    if (!form.name.trim()) e.name = t('errors.name');
    if (form.pass !== form.confirm) e.confirm = t('errors.confirm');
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = tab === 'login' ? validateLogin() : validateSignup();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    
    setLoading(true);
    try {
      const endpoint = tab === 'login' ? '/auth/login' : '/auth/signup';
      const body = tab === 'login' 
        ? { email: form.email, password: form.pass }
        : { name: form.name, email: form.email, password: form.pass, language: i18n.language };

      const res = await fetch(API_BASE + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();

      if (res.ok) {
        localStorage.setItem('leafai_user', JSON.stringify(data.user));
        setUser(data.user);
        navigate('#/how-it-works');
      } else {
        setErrors({ server: data.error || t('errors.auth') });
      }
    } catch (err) {
      setErrors({ server: t('errors.server') });
    } finally {
      setLoading(false);
    }
  };

  const Field = ({ id, label, type='text', k, placeholder='' }) => (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      <input id={id} type={type} placeholder={placeholder}
        value={form[k]} onChange={ev => { set(k, ev.target.value); setErrors(er => ({...er, [k]: undefined})); }}
        className={errors[k] ? 'error' : ''} />
      {errors[k] && <div className="error-msg">{errors[k]}</div>}
    </div>
  );

  return (
    <div className="auth-layout page-enter">
      <div className="auth-left">
        <div className="float-leaf" /><div className="float-leaf" /><div className="float-leaf" /><div className="float-leaf" />
        <div className="auth-left-content">
          <div className="auth-brand">Leaf<span>AI</span></div>
          <div className="auth-tagline">{t('auth.welcome')}</div>
          <div className="auth-plant-art">
            <div className="leaf-art">
              <div className="leaf leaf-1" />
              <div className="leaf leaf-2" />
              <div className="leaf leaf-3" />
              <div className="leaf leaf-4" />
              <div className="stem" />
            </div>
          </div>
          <p style={{color:'rgba(149,213,178,0.7)',fontSize:'0.9rem',lineHeight:1.6,maxWidth:280}}>
            {t('auth.tagline')}
          </p>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <div className="auth-tabs">
            <button id="tab-login" className={`auth-tab ${tab==='login'?'active':''}`} onClick={() => { setTab('login'); setErrors({}); }}>{t('auth.login')}</button>
            <button id="tab-signup" className={`auth-tab ${tab==='signup'?'active':''}`} onClick={() => { setTab('signup'); setErrors({}); }}>{t('auth.signup')}</button>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {errors.server && <div className="error-msg" style={{marginBottom:'1rem',textAlign:'center'}}>{errors.server}</div>}
            {tab === 'signup' && <Field id="f-name" label={t('auth.name')} k="name" placeholder="Priya Patil" />}
            <Field id="f-email" label={t('auth.email')} type="email" k="email" placeholder="you@example.com" />
            <Field id="f-pass" label={t('auth.pass')} type="password" k="pass" placeholder="••••••••" />
            {tab === 'signup' && <Field id="f-confirm" label={t('auth.confirm')} type="password" k="confirm" placeholder="••••••••" />}
            
            <button id="btn-submit-auth" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? t('auth.processing') : (tab === 'login' ? t('auth.btn_login') : t('auth.btn_signup'))}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   PAGE 2 — HOW IT WORKS
════════════════════════════════════════════════════════════ */
function HowItWorksPage({ navigate, path, user }) {
  const { t } = useTranslation();
  useFadeIn();

  const steps = [
    { icon:'📷', title: t('how.step1_title'), desc: t('how.step1_desc') },
    { icon:'🧠', title: t('how.step2_title'), desc: t('how.step2_desc') },
    { icon:'🌿', title: t('how.step3_title'), desc: t('how.step3_desc') },
  ];

  return (
    <div className="page-enter">
      <Navbar navigate={navigate} path={path} user={user} />

      <section className="how-hero">
        <h1>{t('how.title')}</h1>
        <p>{t('how.desc')}</p>
      </section>

      <section className="steps-section">
        <div className="steps-container fade-in-section">
          {steps.map((s, i) => (
            <React.Fragment key={i}>
              <div className="step-card">
                <div className="step-num">{i+1}</div>
                <div className="step-icon">{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
              {i < steps.length-1 && <div className="steps-connector">→</div>}
            </React.Fragment>
          ))}
        </div>
      </section>

      <div className="how-cta fade-in-section">
        <button id="btn-start-scanning" className="btn btn-earth" onClick={() => navigate('#/scanner')}>
          {t('how.start')}
        </button>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   PAGE 3 — SCANNER
════════════════════════════════════════════════════════════ */
function ScannerPage({ navigate, path, user, setLastScan, lastResults, setLastResults }) {
  const { t, i18n } = useTranslation();
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState(lastResults);
  const [barWidth, setBarWidth] = useState(lastResults ? lastResults.confidence * 100 : 0);
  const [error, setError] = useState(null);
  const fileRef = useRef();

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = e => setImage(e.target.result);
    reader.readAsDataURL(file);
    setResults(null); setBarWidth(0); setError(null);
  };

  const handleDrop = (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); };

  const handleScan = async () => {
    if (!imageFile) return;
    setScanning(true); setResults(null); setBarWidth(0); setError(null);

    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('language', i18n.language);
    if (user?._id) formData.append('user_id', user._id);

    try {
      const res = await fetch(API_BASE + '/predict', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (res.ok) {
        setResults(data);
        setLastScan(data);
        setLastResults(data);
        setTimeout(() => setBarWidth(data.confidence * 100), 100);
      } else {
        setError(data.error || t('errors.scan'));
      }
    } catch (err) {
      setError(t('errors.server'));
    } finally {
      setScanning(false);
    }
  };

  const confLevel = barWidth >= 75 ? 'high' : barWidth >= 50 ? 'medium' : 'low';
  const fillClass = confLevel === 'high' ? '' : confLevel === 'medium' ? 'medium' : 'low';

  return (
    <div className="scanner-page page-enter">
      <Navbar navigate={navigate} path={path} user={user} />

      <div className="scanner-container">
        <div className="scanner-panel">
          <h2>{t('scanner.title')}</h2>

          <div
            id="upload-zone"
            className={`upload-zone ${scanning ? 'scan-anim-wrapper' : ''}`}
            onClick={() => !image && fileRef.current.click()}
            onDrop={handleDrop}
            onDragOver={e => e.preventDefault()}
          >
            {scanning && <div className="scan-line" />}
            {image ? (
              <img src={image} alt="Uploaded leaf" onClick={() => fileRef.current.click()} />
            ) : (
              <>
                <div className="upload-icon">🍃</div>
                <p>{t('scanner.prompt')}</p>
              </>
            )}
            <input ref={fileRef} type="file" accept="image/*"
              onChange={e => handleFile(e.target.files[0])} />
          </div>

          {image && !scanning && (
            <button style={{marginTop:'0.5rem',fontSize:'0.8rem',background:'none',border:'none',color:'#e63946',cursor:'pointer'}}
              onClick={() => { setImage(null); setImageFile(null); setResults(null); setBarWidth(0); }}>
              {t('scanner.remove')}
            </button>
          )}

          {scanning && (
            <div className="spinner-wrap">
              <div className="spinner" />
              <p style={{marginTop:'1rem',color:'var(--green-mid)',fontWeight:600}}>{t('auth.processing')}</p>
            </div>
          )}

          {error && <div className="error-msg" style={{marginTop:'1rem'}}>{error}</div>}

          {!scanning && (
            <button id="btn-scan-now" className="btn btn-primary" style={{marginTop:'1.5rem',width:'100%',justifyContent:'center'}}
              onClick={handleScan} disabled={!image}>
              {image ? t('scanner.btn_scan') : t('scanner.btn_upload_first')}
            </button>
          )}
        </div>

        {results && (
          <div className="scanner-panel animate-pop">
            <h2>{t('scanner.results_title')}</h2>
            <div className="confidence-bar-wrap">
              <label>{t('scanner.confidence')}</label>
              <div className="confidence-track">
                <div className={`confidence-fill ${fillClass}`} style={{width: barWidth+'%'}} />
              </div>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span className="confidence-pct">
                  {Math.round(barWidth)}%
                </span>
              </div>
              <div className="disease-name">{t('scanner.detected')}: {results.disease}</div>
            </div>

            <div className="treatment-card" id="treatment-report">
              <h3>{t('scanner.treatment')}</h3>
              <p style={{fontSize:'0.9rem',marginBottom:'1rem',fontStyle:'italic'}}>{results.cure.description}</p>
              <ol>
                {results.cure.treatment_steps.map((s, i) => (
                  <li key={i}><strong>{s.title}</strong>: {s.detail}</li>
                ))}
              </ol>
              <div className="preventive-section">
                <h4>{t('scanner.prevention')}</h4>
                <ul>
                  {results.cure.prevention.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            </div>

            <div style={{marginTop:'1.5rem',textAlign:'center'}}>
              <button id="btn-go-summary" className="btn btn-earth" onClick={() => navigate('#/thankyou')}>
                {t('scanner.view_summary')}
              </button>
            </div>
          </div>
        )}
      </div>
      <VoiceAssistant context={{ results }} navigate={navigate} />
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   PAGE 4 — THANK YOU
════════════════════════════════════════════════════════════ */
const CONFETTI = ['🍃','🌿','🍀','🌱','🪴'];

function ThankYouPage({ navigate, path, user, lastScan }) {
  const { t } = useTranslation();
  const leaves = Array.from({length: 15}, (_, i) => ({
    id: i, emoji: CONFETTI[i % CONFETTI.length], left: Math.random() * 100,
    delay: Math.random() * 5, dur: 4 + Math.random() * 4, size: 0.8 + Math.random() * 0.8,
  }));

  return (
    <div className="page-enter" style={{position:'relative',overflow:'hidden'}}>
      <Navbar navigate={navigate} path={path} user={user} />
      {leaves.map(l => (
        <div key={l.id} className="confetti-leaf" style={{
          left: l.left+'%', fontSize: l.size+'rem', animationDuration: l.dur+'s', animationDelay: l.delay+'s',
        }}>{l.emoji}</div>
      ))}

      <div className="ty-page">
        <svg className="checkmark-svg" viewBox="0 0 100 100">
          <circle className="checkmark-circle" cx="50" cy="50" r="45" />
          <polyline className="checkmark-check" points="28,52 44,68 72,36" />
        </svg>

        <h1>{t('summary.title')}</h1>
        <p className="subtitle">{t('summary.subtitle')}</p>

        {lastScan ? (
          <div className="summary-card">
            <h3>{t('summary.card_title')}</h3>
            {[
              [t('scanner.detected'), lastScan.disease],
              [t('scanner.confidence'), (lastScan.confidence * 100).toFixed(1) + '%'],
              [t('summary.status'), t('summary.saved')],
            ].map(([l, v]) => (
              <div className="summary-row" key={l}>
                <span className="summary-label">{l}</span>
                <span className="summary-value">{v}</span>
              </div>
            ))}
          </div>
        ) : null}

        <div className="ty-buttons">
          <button className="btn btn-primary" onClick={() => navigate('#/scanner')}>{t('summary.btn_another')}</button>
          <button className="btn btn-outline" onClick={() => navigate('#/how-it-works')}>{t('summary.btn_home')}</button>
        </div>
      </div>
      <VoiceAssistant context={{ results: lastScan }} navigate={navigate} />
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   ROOT APP
════════════════════════════════════════════════════════════ */
function App() {
  const { path, navigate } = useRouter();
  const [user, setUser] = useState(null);
  const [lastScan, setLastScan] = useState(null);
  const [lastResults, setLastResults] = useState(null);

  useEffect(() => {
    const saved = localStorage.getItem('leafai_user');
    if (saved) {
      setUser(JSON.parse(saved));
    }
  }, []);

  const commonProps = { navigate, path, user };

  const pages = {
    '#/'           : <AuthPage {...commonProps} setUser={setUser} />,
    '#/how-it-works': <HowItWorksPage {...commonProps} />,
    '#/scanner'    : <ScannerPage {...commonProps} setLastScan={setLastScan} lastResults={lastResults} setLastResults={setLastResults} />,
    '#/thankyou'   : <ThankYouPage {...commonProps} lastScan={lastScan} />,
  };

  return pages[path] || pages['#/'];
}

export default App;
