import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Menu, User, Settings, LogOut, CheckCheck, Sparkles, CheckCircle2, Info } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function Topbar({ title, onMenuClick }) {
  const { user, logout, notifications, markNotificationRead, markAllNotificationsRead, showToast } = useApp();
  const [menuOpen, setMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const menuRef = useRef(null);
  const notifRef = useRef(null);
  const navigate = useNavigate();

  const unreadCount = notifications.filter((n) => !n.read).length;

  useEffect(() => {
    function onClick(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const handleLogout = () => {
    logout();
    showToast('Logged out successfully');
    navigate('/login');
  };

  const iconFor = (type) => (type === 'ai' ? Sparkles : type === 'success' ? CheckCircle2 : Info);

  return (
    <header className="topbar">
      <div className="flex gap-12" style={{ alignItems: 'center' }}>
        <button className="mobile-hamburger icon-btn" onClick={onMenuClick} aria-label="Open menu">
          <Menu size={19} />
        </button>
        <div className="topbar-title">{title}</div>
      </div>
      <div className="topbar-actions">
        <div ref={notifRef} style={{ position: 'relative' }}>
          <button className="icon-btn" onClick={() => setNotifOpen((v) => !v)} aria-label="Notifications">
            <Bell size={18} />
            {unreadCount > 0 && <span className="notif-dot">{unreadCount}</span>}
          </button>
          {notifOpen && (
            <div className="notif-panel">
              <div className="notif-panel-head">
                <strong style={{ fontSize: 14 }}>Notifications</strong>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={markAllNotificationsRead}
                  style={{ padding: '4px 10px', fontSize: 11.5 }}
                >
                  <CheckCheck size={13} /> Mark all read
                </button>
              </div>
              {notifications.map((n) => {
                const Icon = iconFor(n.type);
                return (
                  <div
                    key={n.id}
                    className={`notif-item ${!n.read ? 'unread' : ''}`}
                    onClick={() => markNotificationRead(n.id)}
                    role="button"
                    tabIndex={0}
                  >
                    <Icon size={15} style={{ marginTop: 2, flexShrink: 0, color: '#34d67a' }} />
                    <div className="body">
                      <h4>{n.title}</h4>
                      <p>{n.message}</p>
                      <span>{n.time}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        <div ref={menuRef} className="user-menu">
          <button className="user-menu-trigger" onClick={() => setMenuOpen((v) => !v)}>
            <span className="user-avatar">
              <img src={user?.avatar} alt="" />
            </span>
            {user?.name?.split(' ')[0] || 'Citizen'}
          </button>
          {menuOpen && (
            <div className="dropdown">
              <div className="dropdown-item" role="button" onClick={() => { navigate('/profile'); setMenuOpen(false); }}>
                <User size={15} /> Profile
              </div>
              <div className="dropdown-item" role="button" onClick={() => { navigate('/settings'); setMenuOpen(false); }}>
                <Settings size={15} /> Settings
              </div>
              <div className="dropdown-item danger" role="button" onClick={handleLogout}>
                <LogOut size={15} /> Logout
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
