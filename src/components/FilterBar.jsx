import { Search } from 'lucide-react';
import { CATEGORIES, STATUSES, PRIORITIES } from '../data/constants';

export function SearchBar({ value, onChange, placeholder = 'Search issues...' }) {
  return (
    <div className="search-box">
      <Search size={16} />
      <input
        className="input"
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Search"
      />
    </div>
  );
}

export default function FilterBar({ filters, setFilters, sort, setSort, showSort = true }) {
  const update = (key, value) => setFilters((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="filter-bar">
      <SearchBar value={filters.search} onChange={(v) => update('search', v)} />
      <select className="select filter-select" value={filters.category} onChange={(e) => update('category', e.target.value)} aria-label="Filter by category">
        <option value="">All Categories</option>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>
      <select className="select filter-select" value={filters.status} onChange={(e) => update('status', e.target.value)} aria-label="Filter by status">
        <option value="">All Status</option>
        {STATUSES.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <select className="select filter-select" value={filters.priority} onChange={(e) => update('priority', e.target.value)} aria-label="Filter by priority">
        <option value="">All Priorities</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
      {showSort && (
        <select className="select filter-select" value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort issues">
          <option value="latest">Sort: Latest</option>
          <option value="oldest">Sort: Oldest</option>
          <option value="priority">Sort: Highest Priority</option>
          <option value="related">Sort: Most Related</option>
        </select>
      )}
    </div>
  );
}
