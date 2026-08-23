import AppLayout from '../components/AppLayout';
import { Switch } from '../components/ui';
import { useApp } from '../context/AppContext';

export default function Settings() {
  const { settings, updateSettings, showToast } = useApp();

  const toggle = (key) => {
    updateSettings({ [key]: !settings[key] });
    showToast('Settings updated');
  };

  return (
    <AppLayout title="Settings">
      <div className="page-head">
        <h1>Settings</h1>
        <p>Manage your account and application preferences</p>
      </div>

      <div className="card card-pad" style={{ maxWidth: 680 }}>
        <div className="settings-section">
          <h3>Notification Settings</h3>
          <div className="settings-row">
            <div><div className="lbl">Email Notifications</div><div className="desc">Receive updates about your issues via email</div></div>
            <Switch on={settings.notifyEmail} onToggle={() => toggle('notifyEmail')} label="Email notifications" />
          </div>
          <div className="settings-row">
            <div><div className="lbl">Push Notifications</div><div className="desc">Get instant alerts on your device</div></div>
            <Switch on={settings.notifyPush} onToggle={() => toggle('notifyPush')} label="Push notifications" />
          </div>
          <div className="settings-row">
            <div><div className="lbl">Duplicate Alerts</div><div className="desc">Notify me when AI detects a similar complaint nearby</div></div>
            <Switch on={settings.notifyDuplicates} onToggle={() => toggle('notifyDuplicates')} label="Duplicate alerts" />
          </div>
        </div>

        <div className="settings-section">
          <h3>Theme Preference</h3>
          <div className="settings-row">
            <div><div className="lbl">Dark Mode</div><div className="desc">CivicPulse currently uses a dark navy theme</div></div>
            <Switch on={settings.theme === 'dark'} onToggle={() => { updateSettings({ theme: settings.theme === 'dark' ? 'light' : 'dark' }); showToast('Theme preference saved'); }} label="Dark mode" />
          </div>
        </div>

        <div className="settings-section">
          <h3>Privacy Settings</h3>
          <div className="settings-row">
            <div><div className="lbl">Public Profile</div><div className="desc">Allow others to see your reporting activity</div></div>
            <Switch on={settings.profileVisible} onToggle={() => toggle('profileVisible')} label="Public profile" />
          </div>
          <div className="settings-row">
            <div><div className="lbl">Share Location</div><div className="desc">Allow CivicPulse to use your location for reports</div></div>
            <Switch on={settings.shareLocation} onToggle={() => toggle('shareLocation')} label="Share location" />
          </div>
        </div>

        <div className="settings-section">
          <h3>Language</h3>
          <select
            className="select"
            value={settings.language}
            onChange={(e) => { updateSettings({ language: e.target.value }); showToast('Language preference saved'); }}
          >
            <option>English</option>
            <option>Hindi</option>
            <option>Tamil</option>
            <option>Telugu</option>
            <option>Kannada</option>
          </select>
        </div>
      </div>
    </AppLayout>
  );
}
