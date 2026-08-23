import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClipboardX, ChevronLeft, ChevronRight } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { StatusBadge } from '../components/Badges';
import { EmptyState } from '../components/ui';
import { useApp } from '../context/AppContext';

const TABS = ['All', 'Open', 'In Progress', 'Resolved'];
const PAGE_SIZE = 8;

export default function MyReports() {
  const { issues, user } = useApp();
  const [tab, setTab] = useState('All');
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  // Simulate "my" reports: reported by current user, plus a slice of mock issues for demo purposes
  const myIssues = useMemo(() => {
    const own = issues.filter((i) => i.reportedBy === (user?.name || 'You'));
    const sample = issues.slice(0, 12);
    const combined = [...own, ...sample.filter((i) => !own.find((o) => o.id === i.id))];
    return combined;
  }, [issues, user]);

  const filtered = tab === 'All' ? myIssues : myIssues.filter((i) => i.status === tab);
  const countFor = (t) => (t === 'All' ? myIssues.length : myIssues.filter((i) => i.status === t).length);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageSafe = Math.min(page, totalPages);
  const pageItems = filtered.slice((pageSafe - 1) * PAGE_SIZE, pageSafe * PAGE_SIZE);

  const changeTab = (t) => { setTab(t); setPage(1); };

  return (
    <AppLayout title="My Reports">
      <div className="page-head">
        <h1>My Reports</h1>
        <p>Track the status of issues you have reported</p>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={ClipboardX} title="No reports here" message="You haven't reported any issues in this category yet." />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="tabs" style={{ margin: 0, padding: '4px 20px 0' }}>
            {TABS.map((t) => (
              <button key={t} className={`tab-btn ${tab === t ? 'active' : ''}`} onClick={() => changeTab(t)}>
                {t} ({countFor(t)})
              </button>
            ))}
          </div>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Issue</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Reported On</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((i) => (
                  <tr key={i.id} onClick={() => navigate(`/issues/${i.id}`)}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{i.title}</div>
                      <div className="muted text-sm">{i.location}</div>
                    </td>
                    <td>{i.category}</td>
                    <td><StatusBadge status={i.status} /></td>
                    <td>{new Date(i.reportedAt).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex-between" style={{ padding: '14px 20px' }}>
            <span className="muted text-sm">
              Showing {(pageSafe - 1) * PAGE_SIZE + 1} to {Math.min(pageSafe * PAGE_SIZE, filtered.length)} of {filtered.length} reports
            </span>
            <div className="flex gap-8">
              <button className="page-btn" disabled={pageSafe === 1} onClick={() => setPage((p) => Math.max(1, p - 1))} aria-label="Previous page"><ChevronLeft size={15} /></button>
              {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((n) => (
                <button key={n} className={`page-btn ${n === pageSafe ? 'active' : ''}`} onClick={() => setPage(n)}>{n}</button>
              ))}
              <button className="page-btn" disabled={pageSafe === totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))} aria-label="Next page"><ChevronRight size={15} /></button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
