import { useState, useMemo } from 'react';
import AppLayout from '../components/AppLayout';
import MapView from '../components/MapView';
import { Switch } from '../components/ui';
import { CATEGORIES, STATUSES } from '../data/constants';
import { useApp } from '../context/AppContext';

export default function MapPage() {
  const { issues } = useApp();
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [heatmap, setHeatmap] = useState(true);

  const filtered = useMemo(
    () => issues.filter((i) => (!category || i.category === category) && (!status || i.status === status)),
    [issues, category, status]
  );

  return (
    <AppLayout title="Map View">
      <div className="page-head">
        <h1>Map View</h1>
        <p>Explore issues across the city</p>
      </div>

      <div className="card card-pad">
        <div className="map-toolbar">
          <div className="filter-bar" style={{ margin: 0 }}>
            <select className="select filter-select" value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Filter by category">
              <option value="">All Categories</option>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <select className="select filter-select" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter by status">
              <option value="">All Status</option>
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <span className="muted text-sm">{filtered.length} issues shown</span>
          </div>
          <div className="flex gap-8" style={{ alignItems: 'center' }}>
            <Switch on={heatmap} onToggle={() => setHeatmap((h) => !h)} label="Heatmap glow" />
            <span className="text-sm">Heatmap</span>
          </div>
        </div>

        <MapView issues={filtered} height={520} heatmap={heatmap} />
      </div>
    </AppLayout>
  );
}
