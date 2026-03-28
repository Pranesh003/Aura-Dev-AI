import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('aura_token') || null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('aura_token', token);
            fetchUser();
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('aura_token');
            setUser(null);
            setLoading(false);
        }
    }, [token]);

    const fetchUser = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/auth/me');
            setUser(res.data);
        } catch (error) {
            console.error(error);
            setToken(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const res = await axios.post('http://localhost:8000/api/auth/token', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        setToken(res.data.access_token);
    };

    const register = async (email, password) => {
        await axios.post('http://localhost:8000/api/auth/register', { email, password });
        await login(email, password);
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout, fetchUser }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
