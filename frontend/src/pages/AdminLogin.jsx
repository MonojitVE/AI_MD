import React, { useState, useRef, useEffect } from 'react';
import useAuthStore from '../store/useAuthStore';
import useAppStore from '../store/useAppStore';
import { ShieldCheck, Lock, LogIn, X, AlertTriangle } from 'lucide-react';
import './AdminLogin.css';

const AdminLogin = () => {
  const [employeeId, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');
  const [shaking, setShaking] = useState(false);
  const { login, loading, error, clearError } = useAuthStore();
  const { setActivePage } = useAppStore();
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password.trim()) return;

    try {
      await login(employeeId, password);
      // On success, navigate to dashboard
      setActivePage('dashboard');
    } catch {
      // Trigger shake animation
      setShaking(true);
      setTimeout(() => setShaking(false), 500);
    }
  };

  const handleClose = () => {
    clearError();
    setActivePage('dashboard');
  };

  return (
    <div className="admin-login-overlay" onClick={handleClose}>
      <div
        className={`admin-login-card ${shaking ? 'admin-login-shake' : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="admin-login-close"
          onClick={handleClose}
          aria-label="Close"
        >
          <X size={18} />
        </button>

        {/* Icon */}
        <div className="admin-login-icon-wrap">
          <ShieldCheck size={28} style={{ color: 'var(--color-accent-lime)' }} />
        </div>

        {/* Title */}
        <h2 className="admin-login-title">
          System <span style={{ color: 'var(--color-accent-lime)' }}>Access</span>
        </h2>
        <p className="admin-login-subtitle">
          Enter your Employee ID and password to access<br />
          the Sentry Fab Dashboard.
        </p>

        {/* Form */}
        <form className="admin-login-form" onSubmit={handleSubmit}>
          {error && (
            <div className="admin-login-error">
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          <div className="admin-input-group" style={{ marginBottom: '16px' }}>
            <label htmlFor="employee-id">Employee ID</label>
            <input
              id="employee-id"
              ref={inputRef}
              type="text"
              className="admin-input"
              placeholder="e.g. EMP001"
              value={employeeId}
              onChange={(e) => {
                setEmployeeId(e.target.value);
                if (error) clearError();
              }}
            />
          </div>

          <div className="admin-input-group">
            <label htmlFor="admin-password">Password</label>
            <Lock size={16} className="admin-input-icon" />
            <input
              id="admin-password"
              type="password"
              className="admin-input"
              placeholder="Enter password..."
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) clearError();
              }}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="admin-login-submit"
            disabled={loading || !password.trim() || !employeeId.trim()}
          >
            <LogIn size={18} />
            {loading ? 'Authenticating...' : 'Secure Login'}
          </button>
        </form>

        <p className="admin-login-footer" style={{ marginTop: '24px' }}>
          New Employee? <span style={{ color: 'var(--color-accent-lime)', cursor: 'pointer', fontWeight: 600 }} onClick={() => setActivePage('register')}>Register Here</span>
        </p>
      </div>
    </div>
  );
};

export default AdminLogin;
