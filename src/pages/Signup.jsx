import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { Field, Button } from '../components/ui';
import { useApp } from '../context/AppContext';
import { GoogleGlyph, AppleGlyph } from '../components/OAuthGlyphs';

export default function Signup() {
  const [form, setForm] = useState({ fullName: '', email: '', phone: '', password: '', confirmPassword: '' });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const { signup, showToast } = useApp();
  const navigate = useNavigate();

  const validate = () => {
    const errs = {};
    if (!form.fullName.trim()) errs.fullName = 'Full name is required';
    if (!form.email.trim()) errs.email = 'Email is required';
    else if (!/^\S+@\S+\.\S+$/.test(form.email)) errs.email = 'Enter a valid email address';
    if (!form.phone.trim()) errs.phone = 'Phone number is required';
    else if (!/^[+]?[\d\s-]{8,15}$/.test(form.phone)) errs.phone = 'Enter a valid phone number';
    if (!form.password) errs.password = 'Password is required';
    else if (form.password.length < 6) errs.password = 'Password must be at least 6 characters';
    if (form.confirmPassword !== form.password) errs.confirmPassword = 'Passwords do not match';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    signup(form);
    showToast('Account created successfully! Welcome to CivicPulse.');
    navigate('/dashboard');
  };

  return (
    <div className="auth-shell">
      <div className="card auth-card">
        <div className="auth-brand">
          <span className="brand-icon"><ShieldCheck size={19} /></span>
          CivicPulse
        </div>
        <h1>Create Account</h1>
        <p className="sub">Join CivicPulse today</p>
        <form onSubmit={handleSubmit} noValidate>
          <Field label="Full Name" required error={errors.fullName}>
            <input
              className={`input ${errors.fullName ? 'input-error' : ''}`}
              placeholder="Enter your full name"
              value={form.fullName}
              onChange={(e) => setForm({ ...form, fullName: e.target.value })}
            />
          </Field>
          <Field label="Email" required error={errors.email}>
            <input
              className={`input ${errors.email ? 'input-error' : ''}`}
              type="email"
              placeholder="Enter your email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </Field>
          <Field label="Phone Number" required error={errors.phone}>
            <input
              className={`input ${errors.phone ? 'input-error' : ''}`}
              placeholder="Enter your phone number"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </Field>
          <Field label="Password" required error={errors.password}>
            <div className="password-toggle">
              <input
                className={`input ${errors.password ? 'input-error' : ''}`}
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
              <button type="button" onClick={() => setShowPassword((v) => !v)} aria-label="Toggle password visibility">
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </Field>
          <Field label="Confirm Password" required error={errors.confirmPassword}>
            <input
              className={`input ${errors.confirmPassword ? 'input-error' : ''}`}
              type={showPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
            />
          </Field>
          <Button type="submit" className="btn-block">Sign Up</Button>
        </form>
        <div className="auth-divider">Or continue with</div>
        <div className="oauth-row">
          <button className="oauth-btn" aria-label="Continue with Google" onClick={() => { signup({ fullName: 'Google User', email: 'demo@google.com', phone: '+91 90000 00000' }); showToast('Account created with Google'); navigate('/dashboard'); }}>
            <GoogleGlyph />
          </button>
          <button className="oauth-btn" aria-label="Continue with Apple" onClick={() => { signup({ fullName: 'Apple User', email: 'demo@apple.com', phone: '+91 90000 00001' }); showToast('Account created with Apple'); navigate('/dashboard'); }}>
            <AppleGlyph />
          </button>
        </div>
        <div className="auth-footer-link">
          Already have an account? <Link to="/login">Login</Link>
        </div>
      </div>
    </div>
  );
}
