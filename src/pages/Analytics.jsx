import { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import { ListChecks, Copy, Layers, Sparkles, Download } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import { useApp } from '../context/AppContext';

const DONUT_COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#a855f7', '#14b8a6'];

export default function Analytics() {
  const { issues } = useApp();

  const totalIssues = issues.length;
  const duplicatesDetected = Math.round(totalIssues * 0.58);
  const clustersCreated = new Set(issues.filter((i) => i.clusterId).map((i) => i.clusterId)).size || 24;

  const issuesOverTime = useMemo(() => {
    const days = ['May 18', 'May 19', 'May 20', 'May 21', 'May 22', 'May 23', 'May 24'];
    return days.map((d, idx) => ({
      day: d,
      reported: 10 + idx * 3 + Math.round(Math.sin(idx) * 4),
      resolved: 4 + idx * 2 + Math.round(Math.cos(idx) * 3),
    }));
  }, []);

  const categoryData = useMemo(() => {
    const map = {};
    issues.forEach((i) => { map[i.category] = (map[i.category] || 0) + 1; });
    return Object.entries(map).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 6);
  }, [issues]);

  const accuracyData = [
    { week: 'W1', accuracy: 92 }, { week: 'W2', accuracy: 93 }, { week: 'W3', accuracy: 95 },
    { week: 'W4', accuracy: 96 }, { week: 'W5', accuracy: 97 }, { week: 'W6', accuracy: 98 },
  ];

  const clusterSizeData = [
    { bucket: '2', count: 8 }, { bucket: '3-4', count: 12 }, { bucket: '5-6', count: 9 },
    { bucket: '7-10', count: 6 }, { bucket: '10+', count: 3 },
  ];

  return (
    <AppLayout title="Analytics">
      <div className="page-head flex-between" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1>Analytics</h1>
          <p>Insights from your city data</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
          <Download size={15} /> Export Report
        </button>
      </div>

      <div className="stat-grid">
        <StatCard icon={ListChecks} value={totalIssues} label="Total Issues" color="blue" trend="+12% vs last week" />
        <StatCard icon={Copy} value={duplicatesDetected} label="Duplicates Detected" color="amber" trend="+9% vs last week" />
        <StatCard icon={Layers} value={clustersCreated} label="Clusters Created" color="green" trend="+21% vs last week" />
        <StatCard icon={Sparkles} value="98%" label="AI Accuracy" color="green" trend="+2% vs last week" />
      </div>

      <div className="grid-2" style={{ marginBottom: 18 }}>
        <ChartCard title="Issues Over Time">
          <ResponsiveContainer width="100%" height={230}>
            <LineChart data={issuesOverTime}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e6e9ef" />
              <XAxis dataKey="day" stroke="#6b7688" fontSize={11} />
              <YAxis stroke="#6b7688" fontSize={11} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e9ef', borderRadius: 10, color: '#070d1a' }} />
              <Line type="monotone" dataKey="reported" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="resolved" stroke="#22c55e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top Categories">
          <div className="donut-wrap">
            <ResponsiveContainer width="100%" height={230}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={2}>
                  {categoryData.map((d, idx) => <Cell key={d.name} fill={DONUT_COLORS[idx % DONUT_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e9ef', borderRadius: 10, color: '#070d1a' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="donut-center">
              <div className="n">{totalIssues}</div>
              <div className="l">Total</div>
            </div>
          </div>
        </ChartCard>
      </div>

      <div className="grid-2">
        <ChartCard title="Duplicate Detection Accuracy">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e6e9ef" />
              <XAxis dataKey="week" stroke="#6b7688" fontSize={11} />
              <YAxis domain={[85, 100]} stroke="#6b7688" fontSize={11} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e9ef', borderRadius: 10, color: '#070d1a' }} />
              <Line type="monotone" dataKey="accuracy" stroke="#22c55e" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Cluster Size Distribution">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={clusterSizeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e6e9ef" />
              <XAxis dataKey="bucket" stroke="#6b7688" fontSize={11} />
              <YAxis stroke="#6b7688" fontSize={11} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e9ef', borderRadius: 10, color: '#070d1a' }} />
              <Bar dataKey="count" fill="#22c55e" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </AppLayout>
  );
}
