import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Minus, MapPin } from 'lucide-react';
import { PRIORITY_COLORS } from '../data/constants';

export default function MapView({ issues, small, height, heatmap = true }) {
  const [selected, setSelected] = useState(null);
  const [zoom, setZoom] = useState(1);
  const navigate = useNavigate();

  const bounds = useMemo(() => {
    if (!issues.length) return { minLat: 0, maxLat: 1, minLng: 0, maxLng: 1 };
    const lats = issues.map((i) => i.latitude);
    const lngs = issues.map((i) => i.longitude);
    return {
      minLat: Math.min(...lats),
      maxLat: Math.max(...lats),
      minLng: Math.min(...lngs),
      maxLng: Math.max(...lngs),
    };
  }, [issues]);

  const project = (lat, lng) => {
    const padX = 8, padY = 8;
    const w = 100 - padX * 2;
    const h = 100 - padY * 2;
    const latRange = bounds.maxLat - bounds.minLat || 1;
    const lngRange = bounds.maxLng - bounds.minLng || 1;
    const x = padX + ((lng - bounds.minLng) / lngRange) * w;
    const y = padY + (1 - (lat - bounds.minLat) / latRange) * h;
    return { x, y };
  };

  return (
    <>
      <div className={`map-shell ${small ? 'small' : ''}`} style={height ? { height } : undefined}>
        <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0, opacity: 0.35 }} className="map-grid-svg">
          <defs>
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="currentColor" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0 }}>
          <path d="M -5 15 Q 25 25, 40 45 T 60 70 T 105 90" fill="none" stroke="var(--blue-400)" strokeWidth="0.6" opacity="0.35" />
          <g fill="var(--green-500)" opacity="0.18">
            <circle cx="14" cy="30" r="7" />
            <circle cx="20" cy="34" r="5" />
            <circle cx="80" cy="20" r="6" />
            <circle cx="86" cy="24" r="4" />
            <circle cx="30" cy="80" r="6" />
          </g>
        </svg>
        <div style={{ position: 'absolute', inset: 0, transform: `scale(${zoom})`, transformOrigin: 'center' }} className={heatmap ? 'heatmap-on' : ''}>
          {issues.map((issue) => {
            const { x, y } = project(issue.latitude, issue.longitude);
            const color = PRIORITY_COLORS[issue.priority];
            return (
              <div
                key={issue.id}
                className="map-marker"
                style={{ left: `${x}%`, top: `${y}%` }}
                onClick={() => setSelected(selected === issue.id ? null : issue.id)}
              >
                <div className="pin" style={{ background: color, color }}>
                  <span>{issue.relatedComplaints}</span>
                </div>
                {selected === issue.id && (
                  <div className="map-popup" onClick={(e) => e.stopPropagation()}>
                    <strong style={{ fontSize: 13.5 }}>{issue.title}</strong>
                    <div className="muted text-sm" style={{ margin: '6px 0' }}>{issue.category} · {issue.location}</div>
                    <div className="flex gap-8" style={{ marginBottom: 10 }}>
                      <span className="badge badge-open" style={{ fontSize: 10.5 }}>{issue.status}</span>
                      <span className="badge badge-medium" style={{ fontSize: 10.5 }}>{issue.priority}</span>
                    </div>
                    <button className="btn btn-primary btn-sm btn-block" onClick={() => navigate(`/issues/${issue.id}`)}>
                      View Details
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {!small && (
          <div className="map-controls">
            <button className="map-zoom-btn" onClick={() => setZoom((z) => Math.min(z + 0.2, 2))} aria-label="Zoom in"><Plus size={16} /></button>
            <button className="map-zoom-btn" onClick={() => setZoom((z) => Math.max(z - 0.2, 0.6))} aria-label="Zoom out"><Minus size={16} /></button>
          </div>
        )}
      </div>
      {!small && (
        <div className="map-legend-row">
          <span><MapPin size={13} color="#ef4444" /> High (20+)</span>
          <span><MapPin size={13} color="#f59e0b" /> Medium (10-20)</span>
          <span><MapPin size={13} color="#22c55e" /> Low (1-10)</span>
        </div>
      )}
    </>
  );
}
