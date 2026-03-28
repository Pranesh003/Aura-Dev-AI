import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './AuthContext';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AuraIDE from './pages/AuraIDE';

const ProtectedRoute = ({ children }) => {
    const { user } = useContext(AuthContext);
    if (!user) return <Navigate to="/login" replace />;
    return children;
};

export default function AppRouter() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/dashboard" element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/ide" element={
                        <ProtectedRoute>
                            <AuraIDE />
                        </ProtectedRoute>
                    } />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}
