import React, { useContext, useState } from 'react';
import { AuthContext } from '../AuthContext';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock } from 'lucide-react';

export default function Login() {
    const { login, register } = useContext(AuthContext);
    const navigate = useNavigate();
    
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                await login(email, password);
            } else {
                await register(email, password);
            }
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || "Authentication failed");
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="logo-section" style={{justifyContent: 'center', marginBottom: '20px'}}>
                    <Sparkles className="logo-icon" size={40} />
                    <h1 style={{fontSize: '2rem'}}>Aura-Dev</h1>
                </div>
                <h2>{isLogin ? 'Sign in to your account' : 'Create your SaaS account'}</h2>
                
                {error && <div style={{ color: '#ff4c4c', background: '#2a1212', padding: '10px', borderRadius: '5px', marginBottom: '15px' }}>{error}</div>}
                
                <form onSubmit={handleSubmit} className="input-group">
                    <div style={{display: 'flex', alignItems: 'center', background: '#1c1c1c', borderRadius: '12px', padding: '10px 15px', marginBottom: '15px', border: '1px solid #333'}}>
                        <Mail size={18} color="#666" style={{marginRight: '10px'}}/>
                        <input 
                            type="email" 
                            placeholder="Email address" 
                            required 
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            style={{background: 'transparent', border: 'none', color: '#fff', outline: 'none', width: '100%'}}
                        />
                    </div>
                    <div style={{display: 'flex', alignItems: 'center', background: '#1c1c1c', borderRadius: '12px', padding: '10px 15px', marginBottom: '20px', border: '1px solid #333'}}>
                        <Lock size={18} color="#666" style={{marginRight: '10px'}}/>
                        <input 
                            type="password" 
                            placeholder="Password" 
                            required 
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            style={{background: 'transparent', border: 'none', color: '#fff', outline: 'none', width: '100%'}}
                        />
                    </div>
                    
                    <button type="submit" className="btn-primary" style={{width: '100%'}}>
                        {isLogin ? 'Login to Dashboard' : 'Start Building with Aura'}
                    </button>
                    
                    <p style={{textAlign: 'center', marginTop: '15px', color: '#888', cursor: 'pointer'}} onClick={() => setIsLogin(!isLogin)}>
                        {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
                    </p>
                </form>
            </div>
            
            <style jsx="true">{`
                .login-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    background: radial-gradient(circle at top right, #111, #000);
                }
                .login-card {
                    background: rgba(20, 20, 20, 0.7);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 40px;
                    width: 100%;
                    max-width: 400px;
                    box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
                }
                .login-card h2 {
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 1.2rem;
                    font-weight: 400;
                    color: #ddd;
                }
            `}</style>
        </div>
    );
}
