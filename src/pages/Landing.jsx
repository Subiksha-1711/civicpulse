import { useNavigate } from 'react-router-dom';
import { FileText, ScanSearch, Layers, CheckCircle2, Sparkles, TreePine, Wrench, Users, ShieldCheck } from 'lucide-react';
import PublicNavbar from '../components/PublicNavbar';
import { STATS } from '../data/issues';

const STEPS = [
  { num: '01', icon: FileText, title: 'Report', desc: 'Submit issues with photos & location.', color: 'var(--blue-500)' },
  { num: '02', icon: ScanSearch, title: 'Detect', desc: 'AI detects duplicate complaints.', color: 'var(--green-500)' },
  { num: '03', icon: Layers, title: 'Cluster', desc: 'Similar complaints are clustered into one issue.', color: 'var(--blue-500)' },
  { num: '04', icon: CheckCircle2, title: 'Resolve', desc: 'Authorities take action & update status.', color: 'var(--green-500)' },
];

const STAT_PILLS = [
  { icon: TreePine, cls: 'c-green', val: STATS.issuesReported, lbl: 'Issues Reported' },
  { icon: Wrench, cls: 'c-amber', val: STATS.issuesResolved, lbl: 'Issues Resolved' },
  { icon: Users, cls: 'c-blue', val: STATS.activeCitizens, lbl: 'Active Citizens' },
  { icon: ShieldCheck, cls: 'c-green', val: STATS.aiAccuracy, lbl: 'Detection Accuracy' },
];

/** Illustrated night skyline + park scene, right-aligned behind the hero copy */
function HeroScene() {
  return (
    <div className="hero-v2-scene">
      <svg viewBox="0 0 900 560" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="fadeLeft" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--navy-950)" stopOpacity="1" />
            <stop offset="35%" stopColor="var(--navy-950)" stopOpacity="0.55" />
            <stop offset="100%" stopColor="var(--navy-950)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {[[80,40],[160,90],[260,30],[340,70],[430,20],[520,55],[610,35],[700,80],[780,40],[830,100],[120,150],[600,140]].map(([x,y],i)=>(
          <circle key={i} cx={x} cy={y} r={i%3===0?1.6:1} fill="var(--gray-200)" opacity={0.7} />
        ))}
        <line x1="700" y1="30" x2="770" y2="90" stroke="var(--gray-200)" strokeWidth="1.4" opacity="0.7" />

        <g fill="var(--navy-700)">
          <rect x="380" y="230" width="46" height="200" />
          <rect x="432" y="180" width="34" height="250" />
          <rect x="472" y="260" width="50" height="170" />
          <rect x="528" y="150" width="38" height="280" />
          <rect x="572" y="210" width="44" height="220" />
          <rect x="622" y="120" width="40" height="310" />
          <rect x="668" y="240" width="52" height="190" />
          <rect x="726" y="170" width="36" height="260" />
          <rect x="768" y="220" width="60" height="210" />
        </g>
        <g>
          {[[390,250],[440,200],[540,175],[580,235],[635,150],[678,265],[736,195],[780,245]].map(([x,y],i)=>(
            <g key={i}>
              <rect x={x} y={y} width="6" height="8" fill="var(--amber-500)" opacity="0.5" />
              <rect x={x+14} y={y+20} width="6" height="8" fill="var(--amber-500)" opacity="0.35" />
            </g>
          ))}
        </g>

        <rect x="0" y="430" width="900" height="130" fill="var(--navy-800)" />
        <g fill="var(--green-500)" opacity="0.55">
          <circle cx="640" cy="420" r="34" />
          <circle cx="700" cy="435" r="44" />
          <circle cx="760" cy="415" r="30" />
          <circle cx="820" cy="440" r="38" />
        </g>

        <g>
          <circle cx="655" cy="470" r="9" fill="var(--navy-600)" />
          <rect x="644" y="479" width="22" height="26" rx="8" fill="var(--navy-600)" />
          <circle cx="690" cy="462" r="9" fill="var(--green-400)" />
          <rect x="679" y="471" width="22" height="30" rx="8" fill="var(--green-400)" />
          <circle cx="722" cy="472" r="8" fill="var(--gray-300)" />
          <rect x="712" y="480" width="20" height="24" rx="8" fill="var(--gray-300)" />
          <circle cx="752" cy="460" r="9" fill="var(--blue-400)" />
          <rect x="741" y="469" width="22" height="30" rx="8" fill="var(--blue-400)" />
        </g>

        <rect x="0" y="0" width="900" height="560" fill="url(#fadeLeft)" />
      </svg>
    </div>
  );
}

/** Light silhouette band used above the footer copyright line */
function FooterIllustration() {
  return (
    <div className="footer-illustration">
      <svg viewBox="0 0 1200 170" preserveAspectRatio="xMidYMax meet" xmlns="http://www.w3.org/2000/svg">
        <g fill="var(--gray-300)" opacity="0.9">
          <rect x="40" y="60" width="30" height="90" />
          <rect x="80" y="30" width="24" height="120" />
          <rect x="900" y="40" width="28" height="110" />
          <rect x="940" y="70" width="34" height="80" />
          <rect x="990" y="20" width="26" height="130" />
          <rect x="1030" y="55" width="30" height="95" />
          <rect x="1080" y="35" width="24" height="115" />
          <rect x="1120" y="65" width="32" height="85" />
        </g>
        <g fill="var(--green-500)" opacity="0.7">
          <circle cx="130" cy="120" r="22" />
          <circle cx="1000" cy="115" r="20" />
        </g>
        <g fill="var(--gray-500)">
          <circle cx="240" cy="118" r="8" /><rect x="230" y="126" width="20" height="30" rx="7" />
          <circle cx="440" cy="112" r="9" /><rect x="429" y="121" width="22" height="34" rx="7" />
          <circle cx="470" cy="112" r="9" /><rect x="459" y="121" width="22" height="34" rx="7" />
          <circle cx="660" cy="110" r="9" /><rect x="649" y="119" width="22" height="36" rx="7" />
          <circle cx="1080" cy="118" r="8" /><rect x="1070" y="126" width="20" height="30" rx="7" />
        </g>
      </svg>
    </div>
  );
}

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="public-page">
      <PublicNavbar />

      <section className="hero-v2">
        <HeroScene />
        <div className="hero-v2-content">
          <span className="hero-badge"><Sparkles size={14} /> AI-Powered Civic Intelligence</span>
          <h1>
            Stronger Communities,
            <br />
            <span className="accent">Smarter Solutions.</span>
          </h1>
          <p>
            CivicPulse leverages AI to detect duplicate complaints, cluster them into real
            issues, and help authorities resolve problems faster.
          </p>
          <div className="hero-v2-actions">
            <button className="btn btn-primary" onClick={() => navigate('/report')}>Report an Issue</button>
            <button className="btn btn-outline" onClick={() => navigate('/issues')}>Explore Issues</button>
          </div>
        </div>

        <div className="stats-row-inline">
          {STAT_PILLS.map((s) => (
            <div key={s.lbl} className="stat-pill">
              <span className={`pill-icon ${s.cls}`}><s.icon size={17} /></span>
              <div>
                <div className="val">{s.val}</div>
                <div className="lbl">{s.lbl}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="how-section-light" id="features">
        <h2 className="section-title">How CivicPulse Works</h2>
        <p className="section-sub">A simple four-step process powered by artificial intelligence</p>
        <div className="how-grid-light">
          {STEPS.map((s) => (
            <div key={s.num} className="how-card-light">
              <div className="how-icon-circle" style={{ background: s.color }}><s.icon size={20} /></div>
              <h3>{s.num.replace('0','')} {s.title}</h3>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>
        <FooterIllustration />
      </section>

      <footer className="footer-copy">
        © {new Date().getFullYear()} CivicPulse. AI-Powered Civic Intelligence Platform. Built for stronger communities.
      </footer>
    </div>
  );
}
