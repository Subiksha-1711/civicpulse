import { Sparkles, CheckCircle2, Info, CheckCheck, BellOff } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { EmptyState } from '../components/ui';
import { useApp } from '../context/AppContext';

export default function Notifications() {
  const { notifications, markNotificationRead, markAllNotificationsRead } = useApp();
  const iconFor = (type) => (type === 'ai' ? Sparkles : type === 'success' ? CheckCircle2 : Info);

  return (
    <AppLayout title="Notifications">
      <div className="page-head flex-between" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1>Notifications</h1>
          <p>Stay updated on your issues and community activity</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={markAllNotificationsRead}>
          <CheckCheck size={15} /> Mark all as read
        </button>
      </div>

      {notifications.length === 0 ? (
        <EmptyState icon={BellOff} title="No notifications" message="You're all caught up!" />
      ) : (
        <div className="card">
          {notifications.map((n) => {
            const Icon = iconFor(n.type);
            return (
              <div
                key={n.id}
                className={`notif-item ${!n.read ? 'unread' : ''}`}
                style={{ cursor: 'pointer' }}
                onClick={() => markNotificationRead(n.id)}
              >
                <Icon size={17} style={{ marginTop: 2, flexShrink: 0, color: '#34d67a' }} />
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
    </AppLayout>
  );
}
