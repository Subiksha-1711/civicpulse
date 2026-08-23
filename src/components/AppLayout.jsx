import { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import Toast from './Toast';

export default function AppLayout({ title, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="app-main">
        <Topbar title={title} onMenuClick={() => setSidebarOpen(true)} />
        <div className="app-content page-fade">{children}</div>
      </div>
      <Toast />
    </div>
  );
}
