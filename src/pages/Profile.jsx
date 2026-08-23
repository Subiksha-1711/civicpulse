import { useState } from 'react';
import { Pencil, Save, ListChecks, CheckCircle2, Clock } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { Field, Button } from '../components/ui';
import { useApp } from '../context/AppContext';

export default function Profile() {
  const { user, updateUser, showToast, issues } = useApp();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ name: user?.name || '', email: user?.email || '', phone: user?.phone || '' });

  const myReportsCount = issues.filter((i) => i.reportedBy === user?.name).length || user?.totalReports || 0;

  const handleSave = () => {
    updateUser(form);
    setEditing(false);
    showToast('Profile updated successfully');
  };

  return (
    <AppLayout title="Profile">
      <div className="page-head">
        <h1>My Profile</h1>
        <p>Manage your account information</p>
      </div>

      <div className="card">
        <div className="profile-head">
          <div className="profile-avatar"><img src={user?.avatar} alt="" /></div>
          <div style={{ flex: 1 }}>
            <h2 style={{ margin: '0 0 4px' }}>{user?.name}</h2>
            <p className="muted" style={{ margin: 0 }}>{user?.email}</p>
          </div>
          {!editing ? (
            <Button variant="secondary" size="sm" onClick={() => setEditing(true)}><Pencil size={14} /> Edit Profile</Button>
          ) : (
            <Button size="sm" onClick={handleSave}><Save size={14} /> Save Changes</Button>
          )}
        </div>

        <div className="card-pad" style={{ paddingTop: 0 }}>
          {editing ? (
            <>
              <div className="field-row">
                <Field label="Full Name"><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></Field>
                <Field label="Email"><input className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Field>
              </div>
              <Field label="Phone"><input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></Field>
            </>
          ) : (
            <>
              <div className="info-row"><span>Full Name</span><span>{user?.name}</span></div>
              <div className="info-row"><span>Email</span><span>{user?.email}</span></div>
              <div className="info-row"><span>Phone</span><span>{user?.phone}</span></div>
              <div className="info-row"><span>Member Since</span><span>{user?.joinedAt ? new Date(user.joinedAt).toLocaleDateString() : '—'}</span></div>
            </>
          )}

          <div className="profile-stats">
            <div className="card stat-card">
              <div className="icon blue"><ListChecks size={20} /></div>
              <div><div className="value">{myReportsCount || user?.totalReports}</div><div className="label">Total Reports</div></div>
            </div>
            <div className="card stat-card">
              <div className="icon green"><CheckCircle2 size={20} /></div>
              <div><div className="value">{user?.resolvedReports}</div><div className="label">Resolved</div></div>
            </div>
            <div className="card stat-card">
              <div className="icon amber"><Clock size={20} /></div>
              <div><div className="value">{user?.activeReports}</div><div className="label">Active</div></div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
