export default function StatCard({ icon: Icon, value, label, color = 'blue', trend }) {
  return (
    <div className="card stat-card">
      <div className={`icon ${color}`}>
        <Icon size={22} />
      </div>
      <div>
        <div className="value">{value}</div>
        <div className="label">{label}</div>
        {trend && <div className="trend">{trend}</div>}
      </div>
    </div>
  );
}
