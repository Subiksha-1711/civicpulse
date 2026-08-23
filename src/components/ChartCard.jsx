export default function ChartCard({ title, action, children }) {
  return (
    <div className="card chart-card">
      <div className="chart-card-head">
        <h3>{title}</h3>
        {action}
      </div>
      {children}
    </div>
  );
}
