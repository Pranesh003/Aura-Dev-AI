import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import { 
  Folder, File, Play, Save, Cpu, Layers, HardDrive, 
  Terminal as TerminalIcon, Search, Settings, ShieldCheck, 
  ChevronRight, ChevronDown, Trash2, Upload, Box, CheckCircle2, 
  Circle, PlusSquare, Layout, RefreshCcw, Zap, FileText, Eye, 
  Bug, Brain, Leaf
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const RecursiveTree = ({ nodes, onFileClick, currentPath, openPaths, setOpenPaths }) => {
  const toggleDir = (path) => {
    setOpenPaths(prev => ({ ...prev, [path]: !prev[path] }));
  };

  const renderNode = (node) => {
    const isOpen = openPaths[node.path];
    const isActive = currentPath === node.path;

    return (
      <div key={node.path}>
        <div 
          className={`tree-item ${isActive ? 'active' : ''}`}
          style={{ paddingLeft: `${node.path.split('/').length * 12}px` }}
          onClick={() => node.isDir ? toggleDir(node.path) : onFileClick(node)}
        >
          {node.isDir ? (
            <>
              {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              <Folder size={18} className="folder-icon" />
            </>
          ) : (
            <File size={18} className="file-icon" />
          )}
          <span>{node.name}</span>
        </div>
        {node.isDir && isOpen && node.children && (
          <div>{node.children.map(renderNode)}</div>
        )}
      </div>
    );
  };

  return <div>{nodes.map(renderNode)}</div>;
};

function App() {
  const [activeTab, setActiveTab] = useState('aura');
  const [files, setFiles] = useState([]);
  const [currentFile, setCurrentFile] = useState(null);
  const [content, setContent] = useState('');
  const [openPaths, setOpenPaths] = useState({ '.': true }); // Root open by default
  const [auraStatus, setAuraStatus] = useState({ 
    status: 'Idle', progress: 0, is_running: false, logs: [], 
    phases: { Vision: 'pending', Architect: 'pending', Developer: 'pending', Debug: 'pending', Optimization: 'pending', Sustainability: 'pending' } 
  });
  const [userDesc, setUserDesc] = useState('');
  const [voiceReqs, setVoiceReqs] = useState('');
  const [imageUrl, setImageUrl] = useState(null);

  const terminalRef = useRef(null);
  const xterm = useRef(null);
  const editorRef = useRef(null);

  useEffect(() => {
    fetchFiles();
    initTerminal();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const initTerminal = () => {
    if (!terminalRef.current || xterm.current) return;
    xterm.current = new XTerm({
      theme: { background: '#000000', foreground: '#e1e1e3' },
      fontSize: 14,
      fontFamily: 'JetBrains Mono',
      cursorBlink: true,
      lineHeight: 1.2
    });
    const fitAddon = new FitAddon();
    xterm.current.loadAddon(fitAddon);
    xterm.current.open(terminalRef.current);
    fitAddon.fit();
    xterm.current.writeln('\x1b[1;34m⚡ AURA-IDE SUPER-ULTIMATE TERMINAL V1.0\x1b[0m');
    window.addEventListener('resize', () => fitAddon.fit());
  };

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/files/tree`);
      setFiles(res.data);
    } catch (err) {}
  };

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/status`);
      const wasRunning = auraStatus.is_running;
      setAuraStatus(res.data);
      if (wasRunning && res.data.is_running === false) {
        fetchFiles();
      }
    } catch (err) {}
  };

  const handleFileClick = async (file) => {
    try {
      const res = await axios.get(`${API_BASE}/api/file?path=${file.path}`);
      setCurrentFile(file);
      setContent(res.data.content);
    } catch (err) {}
  };

  const handleSave = async () => {
    if (!currentFile) return;
    try {
      await axios.post(`${API_BASE}/api/file`, { path: currentFile.path, content });
      xterm.current.writeln(`\x1b[32m✔ SAVED:\x1b[0m ${currentFile.path}`);
      fetchFiles();
    } catch (err) {
      xterm.current.writeln(`\x1b[31m✘ ERROR SAVING:\x1b[0m ${err.message}`);
    }
  };

  const handleCreateFile = async () => {
    const name = prompt('Filename (e.g. app.py):');
    if (!name) return;
    try {
      await axios.post(`${API_BASE}/api/file`, { path: name, content: '# Aura-Dev Generated File' });
      fetchFiles();
    } catch (err) {}
  };

  const handleRunAura = async () => {
    try {
      await axios.post(`${API_BASE}/api/run`, {
        user_desc: userDesc,
        voice_reqs: voiceReqs,
        model_id: 'gemini-2.0-flash',
        image_data: imageUrl
      });
      xterm.current.writeln('\x1b[1;36m🚀 INITIATING SUPER-ULTIMATE 6-AGENT ORCHESTRATION...\x1b[0m');
      setActiveTab('aura');
    } catch (err) {
      xterm.current.writeln(`\x1b[31m⚠ ERROR:\x1b[0m ${err.message}`);
    }
  };

  const runCode = async () => {
    if (!currentFile) return;
    const cmd = currentFile.path.endsWith('.py') ? `python "${currentFile.path}"` : `type "${currentFile.path}"`;
    xterm.current.writeln(`\x1b[1;34m$ ${cmd}\x1b[0m`);
    try {
      const res = await axios.get(`${API_BASE}/api/terminal/run?command=${cmd}`);
      if (res.data.full_output) xterm.current.writeln(res.data.full_output);
      else if (res.data.error) xterm.current.writeln(`\x1b[31m${res.data.error}\x1b[0m`);
    } catch (err) {
      xterm.current.writeln(`\x1b[31mExecution Error: ${err.message}\x1b[0m`);
    }
  };

  const handleAutomation = async (tool) => {
    xterm.current.writeln(`\x1b[1;33m⚙ TRIGGERING ${tool.toUpperCase()} AUTOMATION...\x1b[0m`);
    try {
      const res = await axios.post(`${API_BASE}/api/automation/run?tool_name=${tool}&target_file=${currentFile?.path || ''}`);
      if (res.data.output) xterm.current.writeln(res.data.output);
      if (res.data.error) xterm.current.writeln(`\x1b[31mError: ${res.data.error}\x1b[0m`);
      fetchFiles();
    } catch (err) {
      xterm.current.writeln(`\x1b[31mAutomation Error: ${err.message}\x1b[0m`);
    }
  };

  const clearTerminal = () => {
    xterm.current?.clear();
    xterm.current?.writeln('\x1b[1;34m⚡ TERMINAL CLEARED\x1b[0m');
  };

  return (
    <div className="app-wrapper">
      <div className="nav-rail">
        <Zap className={`rail-icon ${activeTab === 'aura' ? 'active' : ''}`} size={24} onClick={() => setActiveTab('aura')} />
        <Layout className={`rail-icon ${activeTab === 'automation' ? 'active' : ''}`} size={24} onClick={() => setActiveTab('automation')} />
        <Box className={`rail-icon ${activeTab === 'explorer' ? 'active' : ''}`} size={24} onClick={() => setActiveTab('explorer')} />
        <div style={{ flex: 1 }}></div>
        <Settings className="rail-icon" size={24} />
      </div>

      <div className="sidebar-container">
        <div className="section-header">
          {activeTab === 'aura' ? 'AURA-DEV ULTIMATE' : activeTab === 'automation' ? 'INTELLIGENT AUTOMATION' : 'PROJECT EXPLORER'}
        </div>
        <div className="sidebar-scrollable">
          {activeTab === 'aura' ? (
            // ... (Aura Code) ...
            <div>
              <input className="input-super" placeholder="What are we building today?" value={userDesc} onChange={(e) => setUserDesc(e.target.value)} />
              <textarea className="input-super" placeholder="Detailed requirements & architecture..." style={{ height: '120px', resize: 'none' }} value={voiceReqs} onChange={(e) => setVoiceReqs(e.target.value)} />
              
              <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <label className="btn-ultimate" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', background: 'var(--bg-header)', cursor: 'pointer' }}>
                  <Upload size={18} /> {imageUrl ? 'Update' : 'Sketch'}
                  <input type="file" style={{ display: 'none' }} onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      const r = new FileReader(); r.onloadend = () => setImageUrl(r.result); r.readAsDataURL(file);
                    }
                  }} />
                </label>
                <button className="btn-ultimate" style={{ flex: 2 }} onClick={handleRunAura} disabled={auraStatus.is_running}>
                  {auraStatus.is_running ? 'BUILDING...' : 'INITIATE BUILD'}
                </button>
              </div>

              {imageUrl && <img src={imageUrl} alt="preview" style={{ width: '100%', borderRadius: '12px', marginBottom: '20px', border: '1px solid var(--border)' }} />}

              <div className="section-header" style={{ padding: 0, background: 'transparent', border: 'none', height: 'auto', marginBottom: '16px' }}>7-AGENT STATUS</div>
              {Object.entries(auraStatus.phases || {}).map(([name, status]) => (
                <div key={name} className={`agent-row ${status === 'running' ? 'running' : ''}`}>
                  <div className={`agent-dot ${status}`}></div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '14px', fontWeight: '600' }}>{name} Agent</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{status.toUpperCase()}</div>
                  </div>
                  {status === 'complete' && <CheckCircle2 size={18} color="var(--success)" />}
                </div>
              ))}

              {/* Solution & Reports — shown when run is complete and we have outputs */}
              {!auraStatus.is_running && (auraStatus.vision || auraStatus.blueprint || (auraStatus.files_created && auraStatus.files_created.length) || auraStatus.debug_report || auraStatus.opt_report || auraStatus.cog_report || auraStatus.audit) && (
                <div style={{ marginTop: '24px', borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
                  <div className="section-header" style={{ padding: 0, background: 'transparent', border: 'none', height: 'auto', marginBottom: '12px' }}>SOLUTION & REPORTS</div>
                  {auraStatus.vision && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><Eye size={16} /> Vision</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '11px', maxHeight: '200px', overflow: 'auto', marginTop: '8px', padding: '10px', background: 'var(--bg-header)', borderRadius: '8px' }}>{auraStatus.vision}</pre>
                    </details>
                  )}
                  {auraStatus.blueprint && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><Layers size={16} /> Blueprint</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '11px', maxHeight: '200px', overflow: 'auto', marginTop: '8px', padding: '10px', background: 'var(--bg-header)', borderRadius: '8px' }}>{auraStatus.blueprint}</pre>
                    </details>
                  )}
                  {auraStatus.files_created && auraStatus.files_created.length > 0 && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><FileText size={16} /> Generated files ({auraStatus.files_created.length})</summary>
                      <ul style={{ marginTop: '8px', paddingLeft: '18px', fontSize: '12px' }}>
                        {auraStatus.files_created.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                  {auraStatus.debug_report && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><Bug size={16} /> Debug report</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '11px', maxHeight: '200px', overflow: 'auto', marginTop: '8px', padding: '10px', background: 'var(--bg-header)', borderRadius: '8px' }}>{auraStatus.debug_report}</pre>
                    </details>
                  )}
                  {auraStatus.opt_report && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><Zap size={16} /> Optimization</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '11px', maxHeight: '200px', overflow: 'auto', marginTop: '8px', padding: '10px', background: 'var(--bg-header)', borderRadius: '8px' }}>{auraStatus.opt_report}</pre>
                    </details>
                  )}
                  {auraStatus.cog_report && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><Brain size={16} /> DX & cognitive audit</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '11px', maxHeight: '200px', overflow: 'auto', marginTop: '8px', padding: '10px', background: 'var(--bg-header)', borderRadius: '8px' }}>{auraStatus.cog_report}</pre>
                    </details>
                  )}
                  {auraStatus.audit && (
                    <details className="result-details" style={{ marginBottom: '10px' }}>
                      <summary style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600' }}><Leaf size={16} /> Sustainability audit</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '11px', maxHeight: '200px', overflow: 'auto', marginTop: '8px', padding: '10px', background: 'var(--bg-header)', borderRadius: '8px' }}>{auraStatus.audit}</pre>
                    </details>
                  )}
                </div>
              )}
            </div>
          ) : activeTab === 'automation' ? (
            <div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
                Tools to enhance developer efficiency and automate software development.
              </p>
              
              <div className="agent-row" style={{ cursor: 'pointer' }} onClick={() => handleAutomation('auto_doc')}>
                <ShieldCheck size={20} color="var(--accent)" />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', fontWeight: '600' }}>AI Doc Generator</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>PRODUCTIVITY TOOL</div>
                </div>
                <Play size={16} />
              </div>

              <div className="agent-row" style={{ cursor: 'pointer' }} onClick={() => handleAutomation('test_oracle')}>
                <Cpu size={20} color="var(--success)" />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', fontWeight: '600' }}>Test Oracle</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>AUTOMATION FRAMEWORK</div>
                </div>
                <Play size={16} />
              </div>

              <div className="agent-row" style={{ cursor: 'pointer' }} onClick={() => handleAutomation('ci_cd')}>
                <RefreshCcw size={20} color="#f59e0b" />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', fontWeight: '600' }}>CI/CD Architect</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>DEPLOYMENT AUTOMATION</div>
                </div>
                <Play size={16} />
              </div>

              <div className="header" style={{ padding: 0, background: 'transparent', border: 'none', height: 'auto', marginTop: '30px', marginBottom: '16px' }}>AUTOMATION METRICS</div>
              <div style={{ fontSize: '13px', display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span>Efficiency Boost</span>
                <span style={{ color: 'var(--success)' }}>+42%</span>
              </div>
              <div style={{ fontSize: '13px', display: 'flex', justifyContent: 'space-between' }}>
                <span>Automation Level</span>
                <span style={{ color: 'var(--accent)' }}>Super-Ultimate</span>
              </div>
            </div>
          ) : (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>ROOT / GENERATED_PROJECT</span>
                <PlusSquare size={18} className="rail-icon" style={{ padding: 0 }} onClick={handleCreateFile} />
              </div>
              <RecursiveTree nodes={files} onFileClick={handleFileClick} currentPath={currentFile?.path} openPaths={openPaths} setOpenPaths={setOpenPaths} />
            </div>
          )}
        </div>
      </div>

      <div className="editor-workspace">
        <div className="section-header" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <File size={16} color="var(--accent)" />
            <span>{currentFile ? currentFile.path : 'Welcome to Aura-IDE Super-Ultimate'}</span>
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <RefreshCcw size={18} className="rail-icon" style={{ padding: 0 }} onClick={fetchFiles} />
            <Save size={20} className="rail-icon" style={{ padding: 0 }} onClick={handleSave} />
            <Play size={20} className="rail-icon" style={{ padding: 0, color: 'var(--success)' }} onClick={runCode} />
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={content}
            onChange={(v) => setContent(v)}
            options={{ 
              fontSize: 15, 
              fontFamily: 'JetBrains Mono',
              minimap: { enabled: true },
              padding: { top: 20 },
              lineHeight: 1.6,
              cursorBlink: "smooth",
              formatOnPaste: true,
              suggestOnTriggerCharacters: true
            }}
          />
        </div>
        <div className="terminal-panel">
          <div className="terminal-header">
             <span>TERMINAL › {auraStatus.status || 'READY'}</span>
             <div style={{ display: 'flex', gap: '15px' }}>
                <span onClick={clearTerminal} style={{ cursor: 'pointer' }}>CLEAR</span>
                <span style={{ color: 'var(--accent)' }}>{auraStatus.progress}%</span>
             </div>
          </div>
          <div style={{ flex: 1, padding: '12px' }} ref={terminalRef}></div>
        </div>
      </div>
    </div>
  );
}

export default App;
