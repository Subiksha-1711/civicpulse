export function StatusBadge({ status }) {
  const cls = status === 'Open' ? 'badge-open' : status === 'In Progress' ? 'badge-in-progress' : 'badge-resolved';
  return (
    <span className={`badge ${cls}`}>
      <span className="badge-dot" />
      {status}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const cls = priority === 'Low' ? 'badge-low' : priority === 'Medium' ? 'badge-medium' : 'badge-high';
  return <span className={`badge ${cls}`}>{priority} Priority</span>;
}
