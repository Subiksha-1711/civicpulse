import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { Field, Button } from '../components/ui';
import { useApp } from '../context/AppContext';
import { GoogleGlyph, AppleGlyph } from '../components/OAuthGlyphs';

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const { login, showToast } = useApp();
  const navigate = useNavigate();

  const validate = () => {
    const errs = {};
    if (!form.email.trim()) errs.email = 'Email or phone is required';
    if (!form.password.trim()) errs.password = 'Password is required';
    else if (form.password.length < 4) errs.password = 'Password must be at least 4 characters';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    login(form.email);
    showToast('Welcome back! Logged in successfully.');
    navigate('/dashboard');
  };

  return (
    <div className="auth-shell">
      <div className="card auth-card">
        <div className="auth-brand">
          <span className="brand-icon"><ShieldCheck size={19} /></span>
          CivicPulse
        </div>
        <h1>Welcome Back!</h1>
        <p className="sub">Login to your CivicPulse account</p>
        <form onSubmit={handleSubmit} noValidate>
          <Field label="Email or Phone" required error={errors.email}>
            <input
              className={`input ${errors.email ? 'input-error' : ''}`}
              type="text"
              placeholder="Enter your email or phone"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </Field>
          <Field label="Password" required error={errors.password}>
            <div className="password-toggle">
              <input
                className={`input ${errors.password ? 'input-error' : ''}`}
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
              <button type="button" onClick={() => setShowPassword((v) => !v)} aria-label="Toggle password visibility">
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </Field>
          <div className="auth-forgot">
            <Link to="#" onClick={(e) => e.preventDefault()}>Forgot Password?</Link>
          </div>
          <Button type="submit" className="btn-block">Login</Button>
        </form>
        <div className="auth-divider">Or continue with</div>
        <div className="oauth-row">
          <button className="oauth-btn" aria-label="Continue with Google" onClick={() => { login('demo@google.com'); showToast('Logged in with Google'); navigate('/dashboard'); }}>
            <GoogleGlyph />
          </button>
          <button className="oauth-btn" aria-label="Continue with Apple" onClick={() => { login('demo@apple.com'); showToast('Logged in with Apple'); navigate('/dashboard'); }}>
            <AppleGlyph />
          </button>
        </div>
        <div className="auth-footer-link">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </div>
      </div>
    </div>
  );
}
