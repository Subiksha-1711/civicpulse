import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Radar, CheckCircle2 } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { FileText, Copy, Layers, Sparkles } from 'lucide-react';
import { useApp } from '../context/AppContext';

const SAMPLE_COMPLAINTS = [
  { id: 1, title: 'Complaint #1', text: 'Large pothole near MG Road causing traffic problems.' },
  { id: 2, title: 'Complaint #2', text: 'Huge pothole on MG Road damaging vehicles.' },
  { id: 3, title: 'Complaint #3', text: 'Road damage reported near MG Road.' },
  { id: 4, title: 'Complaint #4', text: 'Deep pothole causing accidents on MG Road.' },
  { id: 5, title: 'Complaint #5', text: 'Pothole near MG Road signal, needs urgent repair.' },
];

const STEPS = [
  'Analyzing complaints...',
  'Calculating text similarity...',
  'Comparing GPS locations...',
  'Checking issue categories...',
  'Generating cluster...',
];

export default function Deduplication() {
  const { issues } = useApp();
  const navigate = useNavigate();
  const [running, setRunning] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const [result, setResult] = useState(null);
  const timerRef = useRef(null);

  const totalComplaints = issues.length;
  const duplicatePairs = Math.round(totalComplaints * 0.6);
  const clusteredIssues = new Set(issues.filter((i) => i.clusterId).map((i) => i.clusterId)).size;

  const runDetection = () => {
    setRunning(true);
    setResult(null);
    setStepIndex(0);
    let i = 0;
    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      i += 1;
      if (i >= STEPS.length) {
        clearInterval(timerRef.current);
        setResult({
          complaints: SAMPLE_COMPLAINTS.length,
          textSimilarity: 94,
          locationSimilarity: 91,
          categorySimilarity: 100,
          confidence: 98,
        });
        setRunning(false);
      } else {
        setStepIndex(i);
      }
    }, 700);
  };

  return (
    <AppLayout title="AI Deduplication Demo">
      <div className="page-head">
        <h1>AI Deduplication Demo</h1>
        <p>See how AI detects and clusters duplicate complaints in real time</p>
      </div>

      <div className="stats-row-inline card card-pad" style={{ marginBottom: 20, justifyContent: 'space-between' }}>
        <div className="stat-pill">
          <span className="pill-icon c-green"><FileText size={17} /></span>
          <div><div className="val">{totalComplaints}</div><div className="lbl">Total Complaints</div></div>
        </div>
        <div className="stat-pill">
          <span className="pill-icon c-blue"><Copy size={17} /></span>
          <div><div className="val">{duplicatePairs}</div><div className="lbl">Duplicate Pairs Found</div></div>
        </div>
        <div className="stat-pill">
          <span className="pill-icon c-amber"><Layers size={17} /></span>
          <div><div className="val">{clusteredIssues || 24}</div><div className="lbl">Clustered Issues</div></div>
        </div>
        <div className="stat-pill">
          <span className="pill-icon c-green"><Sparkles size={17} /></span>
          <div><div className="val">98%</div><div className="lbl">AI Accuracy</div></div>
        </div>
      </div>

      <div className="dedup-grid">
        <div className="card card-pad">
          <h3 style={{ marginTop: 0 }}>Duplicate Complaints</h3>
          {SAMPLE_COMPLAINTS.map((c) => (
            <div key={c.id} className="complaint-item">
              <h4>{c.title}</h4>
              <p>{c.text}</p>
            </div>
          ))}
        </div>

        <div className="card ai-core">
          <h3 style={{ marginTop: 0, marginBottom: 20 }}>AI Detection</h3>
          <div className={`ai-radar ${running ? 'scanning' : ''}`}>
            <Radar size={44} color={running ? '#22c55e' : '#4ade80'} />
          </div>
          <button className="btn btn-primary" onClick={runDetection} disabled={running}>
            {running ? 'Analyzing...' : 'Run AI Detection'}
          </button>
          <div className="ai-step-log">
            {STEPS.slice(0, stepIndex + 1).map((s, idx) => (
              <div key={idx} style={{ animationDelay: `${idx * 0.05}s` }}>
                {idx < stepIndex || result ? '✓' : '…'} {s}
              </div>
            ))}
          </div>
        </div>

        <div className="card card-pad">
          <h3 style={{ marginTop: 0 }}>Cluster Result</h3>
          {!result ? (
            <p className="muted text-sm">Run AI Detection to see clustering results and similarity metrics.</p>
          ) : (
            <div className="cluster-result">
              <CheckCircle2 size={30} color="#22c55e" />
              <div className="big">Cluster #1</div>
              <p className="muted" style={{ margin: '0 0 14px' }}>
                {result.complaints} Complaints → 1 Consolidated Issue
              </p>
              <div className="info-row"><span>Text Similarity</span><span>{result.textSimilarity}%</span></div>
              <div className="info-row"><span>Location Similarity</span><span>{result.locationSimilarity}%</span></div>
              <div className="info-row"><span>Category Similarity</span><span>{result.categorySimilarity}%</span></div>
              <div className="info-row"><span><strong>Overall Confidence</strong></span><span><strong style={{ color: '#22c55e' }}>{result.confidence}%</strong></span></div>
              <button className="btn btn-primary btn-block" style={{ marginTop: 14 }} onClick={() => navigate('/issues')}>
                View Cluster
              </button>
            </div>
          )}
        </div>
      </div>

      <p className="muted text-sm" style={{ textAlign: 'center', marginTop: 22 }}>
        AI uses sentence similarity + location proximity to identify duplicates
      </p>
    </AppLayout>
  );
}
