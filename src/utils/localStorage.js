const KEYS = {
  USER: 'civicpulse_user',
  ISSUES: 'civicpulse_issues',
  NOTIFICATIONS: 'civicpulse_notifications',
  SETTINGS: 'civicpulse_settings',
};

export function getItem(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function setItem(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // storage full or unavailable - ignore
  }
}

export function removeItem(key) {
  try {
    localStorage.removeItem(key);
  } catch {
    // ignore
  }
}

export { KEYS };
