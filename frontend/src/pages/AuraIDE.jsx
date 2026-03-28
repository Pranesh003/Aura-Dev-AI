import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import { 
  Cpu, Layers, Upload, CheckCircle2, 
  Zap, FileText, Eye, Bug, Brain, Leaf, Sparkles
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function AuraIDE() {
  const navigate = useNavigate();
  const { token, user, fetchUser } = useContext(AuthContext);

  const [auraStatus, setAuraStatus] = useState({ 
    status: 'Idle',
    progress: 0,
    is_running: false,
    logs: [],
    phases: { Vision: 'pending', Architect: 'pending', Developer: 'pending', Debug: 'pending', Optimization: 'pending', Sustainability: 'pending' },
    started_at: null,
    updated_at: null,
    current_phase: null,
    phase_timings: {},
    errors: [],
  });
  const [userDesc, setUserDesc] = useState('');
  const [voiceReqs, setVoiceReqs] = useState('');
  const [imageUrl, setImageUrl] = useState(null);
  const [wsLogs, setWsLogs] = useState([]);
  const [activeJobId, setActiveJobId] = useState(null);

  useEffect(() => {
    if (!activeJobId || !token) return;
    const ws = new WebSocket(`ws://localhost:8000/api/ws/logs/${activeJobId}?token=${token}`);
    ws.onmessage = (event) => {
      setWsLogs((prev) => [...prev, event.data].slice(-50)); // Keep last 50 logs
    };
    return () => ws.close();
  }, [activeJobId, token]);

  useEffect(() => {
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [activeJobId]);

  const formatDuration = (seconds) => {
    if (!seconds || seconds < 0) return '0s';
    const s = Math.floor(seconds);
    const m = Math.floor(s / 60);
    const rem = s % 60;
    if (m === 0) return `${rem}s`;
    return `${m}m ${rem}s`;
  };

  const fetchStatus = async () => {
    if (!activeJobId) return;
    try {
      const res = await axios.get(`${API_BASE}/api/status/${activeJobId}`);
      setAuraStatus(res.data);
    } catch (err) {}
  };

  const handleRunAura = async () => {
    try {
      const res = await axios.post(`${API_BASE}/api/run`, {
        user_desc: userDesc,
        voice_reqs: voiceReqs,
        model_id: 'gemini-2.0-flash',
        image_data: imageUrl
      });
      if (res.data && res.data.job_id) {
        setActiveJobId(res.data.job_id);
        setAuraStatus(prev => ({ ...prev, is_running: true, phases: {} }));
        setWsLogs(['Initializing context... connected to isolated job instance.']);
        fetchUser(); // Refresh credits
      }
    } catch (err) {
      console.error(err);
      if (err.response?.status === 402) {
          alert('Insufficient Aura Credits to run. Please purchase more!');
      }
    }
  };

  return (
    <div className="app-container">
      <header className="app-header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div className="logo-section">
          <Sparkles className="logo-icon" size={32} />
          <h1>Aura-Dev Studio</h1>
        </div>
        <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
           ← Back to Dashboard
        </button>
      </header>

      <main className="dashboard-grid">
        <section className="input-card">
          <div className="card-header">
            <Zap size={20} />
            <h2>Initiate New Build</h2>
          </div>
          <div className="input-group">
            <input 
              className="input-super" 
              placeholder="What are we building today?" 
              value={userDesc} 
              onChange={(e) => setUserDesc(e.target.value)} 
            />
            <textarea 
              className="input-super" 
              placeholder="Detailed requirements & architecture..." 
              style={{ height: '120px', resize: 'none' }} 
              value={voiceReqs} 
              onChange={(e) => setVoiceReqs(e.target.value)} 
            />
            
            <div className="action-row">
              <label className="btn-secondary">
                <Upload size={18} /> {imageUrl ? 'Update Sketch' : 'Upload Sketch'}
                <input type="file" style={{ display: 'none' }} onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const r = new FileReader(); r.onloadend = () => setImageUrl(r.result); r.readAsDataURL(file);
                  }
                }} />
              </label>
              <button className="btn-primary" onClick={handleRunAura} disabled={auraStatus.is_running}>
                {auraStatus.is_running ? 'ORCHESTRATING...' : `RUN AURA AI (10 Credits)`}
              </button>
            </div>
            {imageUrl && <img src={imageUrl} alt="preview" className="sketch-preview" />}
          </div>
        </section>

        <section className="status-card">
          <div className="card-header">
            <Brain size={20} />
            <h2>7-Agent Orchestration Status</h2>
          </div>
          <div className="status-content">
            <div className="status-overview">
              <span className={`status-badge ${auraStatus.is_running ? 'running' : 'idle'}`}>
                {auraStatus.is_running ? `ACTIVE: ${auraStatus.current_phase || 'Initializing'}` : 'SYSTEM IDLE'}
              </span>
              <span className="timer">
                {auraStatus.started_at
                  ? `Elapsed: ${formatDuration(
                      (auraStatus.is_running ? Date.now() / 1000 : auraStatus.updated_at || auraStatus.started_at) -
                      auraStatus.started_at
                    )}`
                  : 'Elapsed: 0s'}
              </span>
            </div>

            <div className="agents-grid">
              {Object.entries(auraStatus.phases || {}).map(([name, status]) => (
                <div key={name} className={`agent-tile ${status}`}>
                  <div className="agent-info">
                    <span className="agent-name">{name} Agent</span>
                    <span className="agent-duration">
                      {auraStatus.phase_timings && auraStatus.phase_timings[name] && (
                        formatDuration(
                          ((auraStatus.phase_timings[name].ended_at || (auraStatus.updated_at || auraStatus.started_at || 0)) -
                            auraStatus.phase_timings[name].started_at) || 0
                        )
                      )}
                    </span>
                  </div>
                  {status === 'complete' ? <CheckCircle2 size={16} className="success-icon" /> : status === 'running' ? <div className="pulse-dot"></div> : <div className="pending-dot"></div>}
                </div>
              ))}
            </div>

            {auraStatus.errors && auraStatus.errors.length > 0 && (
              <div className="error-log">
                <h3>System Alerts</h3>
                <ul>
                  {auraStatus.errors.slice(-3).map((e, idx) => (
                    <li key={idx}>[{e.phase || 'System'}] {e.message}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="live-terminal" style={{ marginTop: '20px', background: '#0a0a0a', border: '1px solid #333', padding: '15px', borderRadius: '8px', fontFamily: 'monospace', color: '#00ffcc', fontSize: '12px', height: '150px', overflowY: 'auto' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#fff', borderBottom: '1px solid #333', paddingBottom: '5px' }}>Terminal Output (Live)</h3>
              {wsLogs.map((log, i) => (
                <div key={i}>{log}</div>
              ))}
              {!activeJobId && <div style={{ color: '#555' }}>Awaiting transmission... Enter a vision sketch to begin.</div>}
            </div>
          </div>
        </section>

        {(auraStatus.vision || auraStatus.blueprint || auraStatus.debug_report || auraStatus.opt_report || auraStatus.cog_report || auraStatus.audit) && (
          <section className="results-card">
            <div className="card-header">
              <Sparkles size={20} />
              <h2>Solution Intelligence Reports</h2>
            </div>
            <div className="results-grid">
              {auraStatus.vision && (
                <ReportItem icon={<Eye size={16} />} title="Vision Analysis" content={auraStatus.vision} />
              )}
              {auraStatus.blueprint && (
                <ReportItem icon={<Layers size={16} />} title="Architecture Blueprint" content={auraStatus.blueprint} />
              )}
              {auraStatus.debug_report && (
                <ReportItem icon={<Bug size={16} />} title="Debug & Quality" content={auraStatus.debug_report} />
              )}
              {auraStatus.opt_report && (
                <ReportItem icon={<Zap size={16} />} title="Optimization Path" content={auraStatus.opt_report} />
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

const ReportItem = ({ icon, title, content }) => (
  <details className="report-details">
    <summary>
      {icon}
      <span>{title}</span>
    </summary>
    <pre>{content}</pre>
  </details>
);

export default AuraIDE;
