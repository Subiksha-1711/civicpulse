import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronRight, Sparkles, MapPin, Tag, AlertTriangle } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import { EmptyState } from '../components/ui';
import MapView from '../components/MapView';
import { useApp } from '../context/AppContext';

const TABS = ['Overview', 'Complaints', 'Activity', 'Location'];

export default function IssueDetails() {
  const { id } = useParams();
  const { issues, updateIssueStatus, showToast } = useApp();
  const [tab, setTab] = useState('Overview');
  const navigate = useNavigate();

  const issue = issues.find((i) => i.id === id);

  if (!issue) {
    return (
      <AppLayout title="Issue Details">
        <EmptyState icon={AlertTriangle} title="Issue not found" message="This issue may have been removed or the link is incorrect." />
      </AppLayout>
    );
  }

  const relatedIssues = issues.filter((i) => i.clusterId && i.clusterId === issue.clusterId && i.id !== issue.id).slice(0, 5);

  const handleStatusChange = (status) => {
    updateIssueStatus(issue.id, status);
    showToast(`Status updated to ${status}`);
  };

  return (
    <AppLayout title="Issue Details">
      <div className="breadcrumb">
        <Link to="/issues" className="muted">All Issues</Link>
        <ChevronRight size={13} />
        <span>Issue Details</span>
      </div>

      <div className="detail-header">
        <div>
          <h1>{issue.title}</h1>
          <div className="detail-sub" style={{ marginBottom: 8 }}>
            <span className="category-chip">{issue.category}</span>
            <span className="category-chip">{issue.subcategory}</span>
            <span className="muted text-sm">{issue.id}</span>
          </div>
          <div className="detail-sub">
            <span><MapPin size={14} /> {issue.location}</span>
            <span><Tag size={14} /> {issue.relatedComplaints} complaints</span>
            <span>First reported {new Date(issue.reportedAt).toLocaleDateString()}</span>
          </div>
        </div>
        <StatusBadge status={issue.status} />
      </div>

      <div className="details-grid">
        <div>
          <div className="card card-pad">
            <div className="tabs">
              {TABS.map((t) => (
                <button key={t} className={`tab-btn ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>{t}</button>
              ))}
            </div>

            {tab === 'Overview' && (
              <>
                <h3 style={{ marginTop: 0 }}>Description</h3>
                <p className="muted" style={{ lineHeight: 1.6 }}>{issue.description}</p>
                {issue.additionalInfo && (
                  <>
                    <h4>Additional Information</h4>
                    <p className="muted">{issue.additionalInfo}</p>
                  </>
                )}
                <h4>Photos</h4>
                {(() => {
                  const photos = issue.images || [issue.image];
                  const [hero, ...rest] = photos;
                  const visibleThumbs = rest.slice(0, 3);
                  const extra = rest.length - visibleThumbs.length;
                  return (
                    <>
                      <img className="photo-hero" src={hero} alt="Issue evidence 1" />
                      {rest.length > 0 && (
                        <div className="photo-thumb-row">
                          {visibleThumbs.map((img, idx) => (
                            <div key={idx} className="thumb-wrap">
                              <img src={img} alt={`Issue evidence ${idx + 2}`} />
                              {extra > 0 && idx === visibleThumbs.length - 1 && (
                                <div className="more-overlay">+{extra}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  );
                })()}

                <div className="ai-summary-box">
                  <h3><Sparkles size={16} /> AI Cluster Summary</h3>
                  <p>
                    This issue is linked from {issue.relatedComplaints} similar complaints. AI has detected these
                    complaints are about the same real-world issue.
                  </p>
                  <div className="ai-metric-row">
                    <div><div className="m-val">{issue.relatedComplaints}</div><div className="m-lbl">Total Complaints</div></div>
                    <div><div className="m-val">{issue.clusterId || '—'}</div><div className="m-lbl">Cluster ID</div></div>
                    <div><div className="m-val">{issue.aiConfidence || 98}%</div><div className="m-lbl">AI Confidence</div></div>
                  </div>
                </div>
              </>
            )}

            {tab === 'Complaints' && (
              <>
                <h3 style={{ marginTop: 0 }}>Related Complaints ({relatedIssues.length})</h3>
                {relatedIssues.length === 0 ? (
                  <p className="muted">No other complaints have been linked to this cluster yet.</p>
                ) : (
                  relatedIssues.map((r) => (
                    <div key={r.id} className="complaint-item" style={{ cursor: 'pointer' }} onClick={() => navigate(`/issues/${r.id}`)}>
                      <h4>{r.id} · {r.reportedBy}</h4>
                      <p>{r.description.slice(0, 120)}...</p>
                    </div>
                  ))
                )}
              </>
            )}

            {tab === 'Activity' && (
              <div className="timeline">
                <div className="timeline-item">
                  <h4>Issue reported by {issue.reportedBy}</h4>
                  <span>{new Date(issue.reportedAt).toLocaleString()}</span>
                </div>
                {issue.status !== 'Open' && (
                  <div className="timeline-item">
                    <h4>Status changed to In Progress</h4>
                    <span>Assigned to Maintenance Team</span>
                  </div>
                )}
                <div className="timeline-item">
                  <h4>AI clustered {issue.relatedComplaints} complaints into this issue</h4>
                  <span>Confidence: {issue.aiConfidence || 98}%</span>
                </div>
                {issue.status === 'Resolved' && (
                  <div className="timeline-item">
                    <h4>Issue marked as Resolved</h4>
                    <span>Closed by City Authority</span>
                  </div>
                )}
              </div>
            )}

            {tab === 'Location' && (
              <>
                <h3 style={{ marginTop: 0 }}>Location</h3>
                <MapView issues={[issue]} height={320} />
              </>
            )}
          </div>
        </div>

        <div>
          <div className="card card-pad">
            <h3 style={{ marginTop: 0 }}>Issue Information</h3>
            <div className="info-row"><span>Status</span><StatusBadge status={issue.status} /></div>
            <div className="info-row"><span>Priority</span><PriorityBadge priority={issue.priority} /></div>
            <div className="info-row"><span>Category</span><span>{issue.category}</span></div>
            <div className="info-row"><span>Subcategory</span><span>{issue.subcategory}</span></div>
            <div className="info-row"><span>Location</span><span>{issue.location}</span></div>
            <div className="info-row"><span>Reported By</span><span>{issue.reportedBy}</span></div>
            <div className="info-row"><span>Reported On</span><span>{new Date(issue.reportedAt).toLocaleDateString()}</span></div>

            <h4 style={{ marginTop: 20, marginBottom: 10 }}>Update Status</h4>
            <div className="flex gap-8" style={{ flexWrap: 'wrap' }}>
              {['Open', 'In Progress', 'Resolved'].map((s) => (
                <button
                  key={s}
                  className={`btn btn-sm ${issue.status === s ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => handleStatusChange(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="card card-pad" style={{ marginTop: 18 }}>
            <h3 style={{ marginTop: 0 }}>Map</h3>
            <MapView issues={[issue]} small height={180} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
