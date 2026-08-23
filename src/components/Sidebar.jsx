import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, FilePlus2, ClipboardList, ListChecks, Map, BarChart3,
  Bell, MessageSquareWarning, User, Settings, LogOut, Radar, X, ShieldCheck,
} from 'lucide-react';
import { useApp } from '../context/AppContext';

const LINKS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/report', label: 'Report Issue', icon: FilePlus2 },
  { to: '/my-reports', label: 'My Reports', icon: ClipboardList },
  { to: '/issues', label: 'All Issues', icon: ListChecks },
  { to: '/map', label: 'Map View', icon: Map },
  { to: '/deduplication', label: 'AI Deduplication', icon: Radar },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/feedback', label: 'Feedback', icon: MessageSquareWarning },
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ open, onClose }) {
  const { logout, showToast } = useApp();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    showToast('Logged out successfully');
    navigate('/login');
  };

  return (
    <>
      <div className={`sidebar-overlay ${open ? 'open' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <button className="sidebar-close-btn" onClick={onClose} aria-label="Close menu">
          <X size={22} />
        </button>
        <div className="sidebar-brand">
          <div className="brand">
            <span className="brand-icon"><ShieldCheck size={19} /></span>
            CivicPulse
          </div>
        </div>
        <nav className="sidebar-nav">
          {LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span className="link-icon"><Icon size={16} /></span>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button className="sidebar-logout" onClick={handleLogout}>
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>
    </>
  );
}
