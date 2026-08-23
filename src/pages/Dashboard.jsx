import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { ListChecks, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import MapView from '../components/MapView';
import { useApp } from '../context/AppContext';
import { STATUS_COLORS } from '../data/constants';
import { ACTIVITY_LOG } from '../data/issues';

export default function Dashboard() {
  const { issues, user } = useApp();
  const navigate = useNavigate();

  const counts = useMemo(() => {
    const open = issues.filter((i) => i.status === 'Open').length;
    const inProgress = issues.filter((i) => i.status === 'In Progress').length;
    const resolved = issues.filter((i) => i.status === 'Resolved').length;
    return { total: issues.length, open, inProgress, resolved };
  }, [issues]);

  const donutData = [
    { name: 'Open', value: counts.open, color: STATUS_COLORS.Open },
    { name: 'In Progress', value: counts.inProgress, color: STATUS_COLORS['In Progress'] },
    { name: 'Resolved', value: counts.resolved, color: STATUS_COLORS.Resolved },
  ];

  const topCategories = useMemo(() => {
    const map = {};
    issues.forEach((i) => { map[i.category] = (map[i.category] || 0) + 1; });
    const max = Math.max(...Object.values(map), 1);
    return Object.entries(map).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([name, count]) => ({ name, count, pct: (count / max) * 100 }));
  }, [issues]);

  return (
    <AppLayout title="Dashboard">
      <div className="page-head">
        <h1>Welcome back, {user?.name?.split(' ')[0] || 'Citizen'}!</h1>
        <p>Here's what's happening in your community today.</p>
      </div>

      <div className="stat-grid">
        <StatCard icon={ListChecks} value={counts.total} label="Total Issues" color="blue" trend="+12% this week" />
        <StatCard icon={Clock} value={counts.inProgress} label="In Progress" color="amber" trend="+5 this week" />
        <StatCard icon={CheckCircle2} value={counts.resolved} label="Resolved" color="green" trend="+8 this week" />
        <StatCard icon={AlertCircle} value={counts.open} label="Open" color="red" trend="-3 this week" />
      </div>

      <div className="two-col" style={{ marginBottom: 18 }}>
        <ChartCard title="Issues Overview">
          <div className="donut-wrap">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={donutData} dataKey="value" innerRadius={65} outerRadius={95} paddingAngle={3}>
                  {donutData.map((d) => <Cell key={d.name} fill={d.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="donut-center">
              <div className="n">{counts.total}</div>
              <div className="l">Total</div>
            </div>
          </div>
          {donutData.map((d) => (
            <div key={d.name} className="legend-row">
              <span><span className="legend-dot" style={{ background: d.color }} />{d.name}</span>
              <span>{d.value} ({counts.total ? Math.round((d.value / counts.total) * 100) : 0}%)</span>
            </div>
          ))}
        </ChartCard>

        <ChartCard title="Recent Activity">
          {ACTIVITY_LOG.map((a) => (
            <div key={a.id} className="activity-item">
              <div className="activity-dot" />
              <div>
                <p>{a.text}</p>
                <span>{a.hoursAgo < 24 ? `${a.hoursAgo} hours ago` : `${Math.floor(a.hoursAgo / 24)} days ago`}</span>
              </div>
            </div>
          ))}
        </ChartCard>
      </div>

      <div className="two-col">
        <ChartCard title="Top Issue Categories" action={<a href="#" onClick={(e) => { e.preventDefault(); navigate('/issues'); }}>View all</a>}>
          {topCategories.map((c) => (
            <div key={c.name} className="category-bar-row">
              <div className="top"><span>{c.name}</span><span className="muted">{c.count}</span></div>
              <div className="category-bar-track"><div className="category-bar-fill" style={{ width: `${c.pct}%` }} /></div>
            </div>
          ))}
        </ChartCard>

        <ChartCard title="Issue Map Overview" action={<a href="#" onClick={(e) => { e.preventDefault(); navigate('/map'); }}>View full map</a>}>
          <MapView issues={issues.slice(0, 20)} small height={220} />
        </ChartCard>
      </div>
    </AppLayout>
  );
}
