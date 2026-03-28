import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../AuthContext';
import { useNavigate } from 'react-router-dom';
import { Zap, LogOut, Code, CreditCard, Sparkles, FolderDot } from 'lucide-react';
import axios from 'axios';

export default function Dashboard() {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/projects');
                setProjects(res.data);
            } catch (err) {
                console.error("Failed to fetch projects");
            }
        };
        fetchProjects();
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleDownload = async (jobId) => {
        try {
            const res = await axios.get(`http://localhost:8000/api/projects/${jobId}/download`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `AuraProject_${jobId.substring(0,8)}.zip`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch(e) {
            alert("Project archive could not be generated. It may have expired.");
        }
    };

    if (!user) return <div style={{color: 'white', padding: '20px'}}>Loading Profile...</div>;

    return (
        <div className="app-container" style={{maxWidth: '1000px', margin: '0 auto'}}>
            <header className="app-header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div className="logo-section">
                    <Sparkles className="logo-icon" size={32} />
                    <h1>Aura-Dev Dashboard</h1>
                </div>
                <div style={{display: 'flex', gap: '15px', alignItems: 'center'}}>
                    <div style={{background: 'rgba(0, 255, 204, 0.1)', border: '1px solid #00ffcc', padding: '8px 15px', borderRadius: '20px', color: '#00ffcc', display: 'flex', gap: '8px', alignItems: 'center'}}>
                        <CreditCard size={16} />
                        <strong>{user.credit_balance} Credits</strong>
                    </div>
                    <button className="btn-secondary" onClick={handleLogout} style={{padding: '8px', borderRadius: '50%'}}>
                        <LogOut size={18} />
                    </button>
                </div>
            </header>

            <main>
                <section className="input-card" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px'}}>
                    <div>
                        <h2 style={{color: 'white', marginBottom: '5px'}}>Build Something New</h2>
                        <p style={{color: '#888'}}>Launch the 7-Agent Orchestration Engine. Costs 10 credits.</p>
                    </div>
                    <button className="btn-primary" onClick={() => navigate('/ide')}>
                        <Zap size={18} /> Open Aura IDE
                    </button>
                </section>

                <h2 style={{color: '#fff', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px'}}>
                    <FolderDot size={24} color="#00ffcc"/> 
                    My Project History
                </h2>
                
                <div style={{display: 'grid', gap: '15px'}}>
                    {projects.length === 0 ? (
                        <div className="status-card" style={{textAlign: 'center', padding: '40px', color: '#888'}}>
                            <Code size={40} style={{margin: '0 auto 15px auto', opacity: 0.5}}/>
                            <p>You haven't built anything yet.</p>
                        </div>
                    ) : (
                        projects.map(proj => (
                            <div key={proj.id} className="status-card" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                                <div>
                                    <h3 style={{color: '#fff', fontSize: '1.1rem', margin: '0 0 5px 0'}}>{proj.prompt_desc.substring(0, 50)}...</h3>
                                    <p style={{color: '#888', margin: 0, fontSize: '0.9rem'}}>Job ID: {proj.id.split('-')[0]} • {new Date(proj.created_at).toLocaleString()}</p>
                                </div>
                                <div style={{display: 'flex', gap: '15px', alignItems: 'center'}}>
                                    <span className={`status-badge ${proj.status.toLowerCase() === 'completed' ? 'idle' : 'running'}`}>
                                        {proj.status.toUpperCase()}
                                    </span>
                                    {proj.status.toLowerCase() === 'completed' && (
                                        <button className="btn-secondary" onClick={() => handleDownload(proj.id)} style={{padding: '5px 10px', fontSize: '0.8rem'}}>
                                            Download ZIP
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </main>
        </div>
    );
}
