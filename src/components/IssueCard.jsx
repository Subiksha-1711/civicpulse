import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Users, Tag } from 'lucide-react';
import { StatusBadge, PriorityBadge } from './Badges';

function timeAgoStr(dateStr) {
  const diffMs = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  if (hours < 1) return 'Just now';
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} day${days > 1 ? 's' : ''} ago`;
  return new Date(dateStr).toLocaleDateString();
}

export default function IssueCard({ issue }) {
  const navigate = useNavigate();
  return (
    <div
      className="card issue-card"
      role="button"
      tabIndex={0}
      onClick={() => navigate(`/issues/${issue.id}`)}
      onKeyDown={(e) => e.key === 'Enter' && navigate(`/issues/${issue.id}`)}
      style={{ cursor: 'pointer' }}
    >
      <img src={issue.image} alt={issue.title} />
      <div className="content">
        <h3>{issue.title}</h3>
        <div className="meta">
          <span><Tag size={13} /> {issue.category} · {issue.subcategory}</span>
          <span><MapPin size={13} /> {issue.location}</span>
          <span><Clock size={13} /> {timeAgoStr(issue.reportedAt)} · <Users size={13} /> {issue.relatedComplaints} complaints</span>
        </div>
        <div className="badges">
          <PriorityBadge priority={issue.priority} />
        </div>
      </div>
      <div className="side">
        <StatusBadge status={issue.status} />
      </div>
    </div>
  );
}
