import { useNavigate } from 'react-router-dom';
import { Sparkles, Layers, BarChart3, MapPinned, Eye, Users } from 'lucide-react';
import PublicNavbar from '../components/PublicNavbar';
import { STATS } from '../data/issues';

const FEATURES = [
  { icon: Sparkles, title: 'AI-Powered Deduplication', desc: 'Automatically detects when multiple citizens report the same underlying problem.' },
  { icon: Layers, title: 'Smart Clustering', desc: 'Groups similar complaints together into a single trackable issue for authorities.' },
  { icon: BarChart3, title: 'Data-Driven Insights', desc: 'Rich analytics dashboards help authorities identify trends and prioritize work.' },
  { icon: MapPinned, title: 'Geographic Intelligence', desc: 'Location-aware clustering pinpoints problem hotspots across the city.' },
  { icon: Eye, title: 'Transparent Reporting', desc: 'Citizens can track the real-time status of every issue they report.' },
  { icon: Users, title: 'Community Collaboration', desc: 'Bringing citizens and local authorities together to build better cities.' },
];

export default function About() {
  const navigate = useNavigate();
  return (
    <div className="public-page">
      <PublicNavbar />

      <section className="about-hero">
        <div>
          <h1 style={{ fontSize: 34, marginBottom: 16 }}>About CivicPulse</h1>
          <p className="muted" style={{ fontSize: 15.5, lineHeight: 1.7 }}>
            CivicPulse is an AI-powered civic intelligence platform that helps cities become smarter and more
            responsive. We connect citizens and local authorities by using artificial intelligence to detect
            duplicate complaints, cluster related issues, and surface actionable insights — helping communities
            resolve problems faster and more transparently than ever before.
          </p>
        </div>
        <div className="about-visual">
          <img
            src="https://images.unsplash.com/photo-1573164713988-8665fc963095?w=900&q=80"
            alt="Community members collaborating on civic issues"
          />
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">Core Features</h2>
        <p className="section-sub">Built with modern AI and civic technology at its core</p>
        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="card feature-card">
              <div className="how-icon"><f.icon size={22} /></div>
              <h3 style={{ margin: '0 0 8px' }}>{f.title}</h3>
              <p className="muted" style={{ margin: 0, fontSize: 14, lineHeight: 1.5 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="about-stats">
        <div className="stat-block"><div className="val">{STATS.activeCitizens}</div><div className="lbl">Active Citizens</div></div>
        <div className="stat-block"><div className="val">{STATS.aiAccuracy}</div><div className="lbl">AI Accuracy</div></div>
        <div className="stat-block"><div className="val">24</div><div className="lbl">Clusters Created</div></div>
        <div className="stat-block"><div className="val">15+</div><div className="lbl">Categories Supported</div></div>
      </div>

      <div className="about-cta">
        <h2 style={{ marginBottom: 10 }}>Join the movement for smarter cities</h2>
        <p className="muted" style={{ marginBottom: 26 }}>Report an issue today and help make your community better.</p>
        <button className="btn btn-primary" onClick={() => navigate('/report')}>Report an Issue</button>
      </div>

      <footer className="footer">
        © {new Date().getFullYear()} CivicPulse. AI-Powered Civic Intelligence Platform.
      </footer>
    </div>
  );
}
