import { useState, useMemo, useEffect } from 'react';
import { ClipboardX, ChevronLeft, ChevronRight } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import FilterBar from '../components/FilterBar';
import IssueCard from '../components/IssueCard';
import { EmptyState } from '../components/ui';
import { useApp } from '../context/AppContext';

const PAGE_SIZE = 6;
const PRIORITY_ORDER = { High: 3, Medium: 2, Low: 1 };

export default function Issues() {
  const { issues } = useApp();
  const [filters, setFilters] = useState({ search: '', category: '', status: '', priority: '' });
  const [sort, setSort] = useState('latest');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const filterKey = `${filters.search}|${filters.category}|${filters.status}|${filters.priority}|${sort}`;

  // Simulate a brief network-style loading state whenever filters change, and
  // reset back to page 1 so results always start from the top of the list.
  useEffect(() => {
    setLoading(true);
    setPage(1);
    const t = setTimeout(() => setLoading(false), 400);
    return () => clearTimeout(t);
  }, [filterKey]);

  const filtered = useMemo(() => {
    let result = issues.filter((issue) => {
      if (filters.search && !`${issue.title} ${issue.location} ${issue.category}`.toLowerCase().includes(filters.search.toLowerCase())) return false;
      if (filters.category && issue.category !== filters.category) return false;
      if (filters.status && issue.status !== filters.status) return false;
      if (filters.priority && issue.priority !== filters.priority) return false;
      return true;
    });

    result = [...result].sort((a, b) => {
      if (sort === 'latest') return new Date(b.reportedAt) - new Date(a.reportedAt);
      if (sort === 'oldest') return new Date(a.reportedAt) - new Date(b.reportedAt);
      if (sort === 'priority') return PRIORITY_ORDER[b.priority] - PRIORITY_ORDER[a.priority];
      if (sort === 'related') return b.relatedComplaints - a.relatedComplaints;
      return 0;
    });

    return result;
  }, [issues, filters, sort]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageItems = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <AppLayout title="All Issues">
      <div className="page-head">
        <h1>All Issues</h1>
        <p>Browse all reported issues in your area ({filtered.length} results)</p>
      </div>

      <FilterBar filters={filters} setFilters={setFilters} sort={sort} setSort={setSort} />

      {loading ? (
        <div className="issues-grid">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 100 }} />
          ))}
        </div>
      ) : pageItems.length === 0 ? (
        <EmptyState icon={ClipboardX} title="No issues found" message="Try adjusting your filters or search terms." />
      ) : (
        <div className="issues-grid">
          {pageItems.map((issue) => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>
      )}

      {!loading && totalPages > 1 && (
        <div className="pagination">
          <button className="page-btn" disabled={page === 1} onClick={() => setPage((p) => p - 1)} aria-label="Previous page">
            <ChevronLeft size={16} />
          </button>
          {Array.from({ length: totalPages }).map((_, i) => (
            <button key={i} className={`page-btn ${page === i + 1 ? 'active' : ''}`} onClick={() => setPage(i + 1)}>
              {i + 1}
            </button>
          ))}
          <button className="page-btn" disabled={page === totalPages} onClick={() => setPage((p) => p + 1)} aria-label="Next page">
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </AppLayout>
  );
}
