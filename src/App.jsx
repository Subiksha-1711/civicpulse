import { Routes, Route, Navigate } from 'react-router-dom';

import Landing from './pages/Landing';
import About from './pages/About';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ReportIssue from './pages/ReportIssue';
import Issues from './pages/Issues';
import IssueDetails from './pages/IssueDetails';
import Deduplication from './pages/Deduplication';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import MapPage from './pages/MapPage';
import MyReports from './pages/MyReports';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';
import SettingsPage from './pages/Settings';
import Feedback from './pages/Feedback';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/about" element={<About />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route path="/issues" element={<Issues />} />
      <Route path="/issues/:id" element={<IssueDetails />} />
      <Route path="/report" element={<ReportIssue />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/map" element={<MapPage />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/deduplication" element={<Deduplication />} />
      <Route path="/my-reports" element={<MyReports />} />
      <Route path="/notifications" element={<Notifications />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/feedback" element={<Feedback />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
