import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { MOCK_ISSUES } from '../data/issues';
import { DEFAULT_USER } from '../data/users';
import { DEFAULT_NOTIFICATIONS } from '../data/notifications';
import { getItem, setItem, removeItem, KEYS } from '../utils/localStorage';

const AppContext = createContext(null);

const DEFAULT_SETTINGS = {
  theme: 'dark',
  language: 'English',
  notifyEmail: true,
  notifyPush: true,
  notifyDuplicates: true,
  profileVisible: true,
  shareLocation: true,
};

export function AppProvider({ children }) {
  const [issues, setIssues] = useState(() => getItem(KEYS.ISSUES, MOCK_ISSUES));
  const [user, setUser] = useState(() => getItem(KEYS.USER, null));
  const [notifications, setNotifications] = useState(() => getItem(KEYS.NOTIFICATIONS, DEFAULT_NOTIFICATIONS));
  const [settings, setSettings] = useState(() => getItem(KEYS.SETTINGS, DEFAULT_SETTINGS));
  const [toast, setToast] = useState(null);

  useEffect(() => setItem(KEYS.ISSUES, issues), [issues]);
  useEffect(() => setItem(KEYS.NOTIFICATIONS, notifications), [notifications]);
  useEffect(() => setItem(KEYS.SETTINGS, settings), [settings]);
  useEffect(() => {
    if (user) setItem(KEYS.USER, user);
    else removeItem(KEYS.USER);
  }, [user]);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type, id: Date.now() });
    setTimeout(() => setToast(null), 3500);
  }, []);

  const addIssue = useCallback((issue) => {
    setIssues((prev) => [issue, ...prev]);
  }, []);

  const updateIssueStatus = useCallback((id, status) => {
    setIssues((prev) => prev.map((i) => (i.id === id ? { ...i, status } : i)));
  }, []);

  const login = useCallback((email) => {
    const mockUser = { ...DEFAULT_USER, email: email || DEFAULT_USER.email };
    setUser(mockUser);
    return mockUser;
  }, []);

  const signup = useCallback((data) => {
    const mockUser = {
      ...DEFAULT_USER,
      id: `USR-${Date.now()}`,
      name: data.fullName,
      email: data.email,
      phone: data.phone,
      avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(data.fullName || 'Citizen')}`,
    };
    setUser(mockUser);
    return mockUser;
  }, []);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  const updateUser = useCallback((patch) => {
    setUser((prev) => ({ ...prev, ...patch }));
  }, []);

  const markNotificationRead = useCallback((id) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  }, []);

  const markAllNotificationsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const updateSettings = useCallback((patch) => {
    setSettings((prev) => ({ ...prev, ...patch }));
  }, []);

  const value = {
    issues,
    addIssue,
    updateIssueStatus,
    user,
    login,
    signup,
    logout,
    updateUser,
    notifications,
    markNotificationRead,
    markAllNotificationsRead,
    settings,
    updateSettings,
    toast,
    showToast,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
