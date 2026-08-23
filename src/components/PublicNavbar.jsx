import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, ShieldCheck } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function PublicNavbar() {
  const [open, setOpen] = useState(false);
  const { user } = useApp();
  const navigate = useNavigate();

  return (
    <nav className="landing-nav">
      <Link to="/" className="brand">
        <span className="brand-icon"><ShieldCheck size={19} /></span>
        CivicPulse
      </Link>
      <div className="landing-nav-links">
        <Link to="/">Home</Link>
        <Link to="/#features">Features</Link>
        <Link to="/issues">Issues</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/about">About Us</Link>
      </div>
      <div className="landing-nav-actions">
        {user ? (
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/dashboard')}>Dashboard</button>
        ) : (
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/login')}>Login</button>
        )}
        <button className="mobile-menu-btn" onClick={() => setOpen((v) => !v)} aria-label="Toggle menu">
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>
      {open && (
        <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: '#0b1526', borderBottom: '1px solid #14243d', padding: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Link to="/" onClick={() => setOpen(false)}>Home</Link>
          <Link to="/issues" onClick={() => setOpen(false)}>Issues</Link>
          <Link to="/dashboard" onClick={() => setOpen(false)}>Dashboard</Link>
          <Link to="/about" onClick={() => setOpen(false)}>About Us</Link>
        </div>
      )}
    </nav>
  );
}
