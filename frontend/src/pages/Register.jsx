import React, { useState } from 'react';
import { register } from '../api/auth';
import useAppStore from '../store/useAppStore';
import { UserPlus, Mail, Lock, X, AlertTriangle, Briefcase, CheckCircle } from 'lucide-react';
import './AdminLogin.css'; // Reuse the overlay/shake styles

const Register = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    department: '',
    password: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successData, setSuccessData] = useState(null);
  const [shaking, setShaking] = useState(false);
  
  const { setActivePage } = useAppStore();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.first_name || !formData.email || !formData.password) return;

    setLoading(true);
    try {
      const data = await register(formData);
      setSuccessData(data); // { employee_id, first_name }
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      setShaking(true);
      setTimeout(() => setShaking(false), 500);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setActivePage('dashboard');
  };

  const handleGoToLogin = () => {
    setActivePage('admin_login');
  };

  return (
    <div className="admin-login-overlay" onClick={handleClose}>
      <div
        className={`admin-login-card ${shaking ? 'admin-login-shake' : ''}`}
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '450px' }}
      >
        <button
          className="admin-login-close"
          onClick={handleClose}
          aria-label="Close"
        >
          <X size={18} />
        </button>

        {successData ? (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <CheckCircle size={48} style={{ color: 'var(--color-accent-lime)', margin: '0 auto 16px' }} />
            <h2 className="admin-login-title" style={{ marginBottom: '16px' }}>Registration Successful!</h2>
            <p style={{ color: 'var(--color-on-dark-muted)', marginBottom: '24px' }}>
              Welcome aboard, {successData.first_name}! Your account has been created.
            </p>
            <div style={{ 
              background: 'rgba(194, 239, 78, 0.1)', 
              border: '1px solid var(--color-accent-lime)',
              borderRadius: 'var(--rounded-md)',
              padding: '24px',
              marginBottom: '24px'
            }}>
              <p style={{ color: 'var(--color-accent-lime)', fontWeight: 'bold', marginBottom: '8px' }}>Your Employee ID</p>
              <h1 style={{ fontSize: '2rem', letterSpacing: '2px', color: '#fff' }}>{successData.employee_id}</h1>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
                Please save this ID. You will need it to log in.
              </p>
            </div>
            <button className="admin-login-submit" onClick={handleGoToLogin}>
              Go to Login
            </button>
          </div>
        ) : (
          <>
            {/* Icon */}
            <div className="admin-login-icon-wrap" style={{ margin: '0 auto 16px', display: 'flex', justifyContent: 'center' }}>
              <UserPlus size={28} style={{ color: 'var(--color-accent-lime)' }} />
            </div>

            {/* Title */}
            <h2 className="admin-login-title" style={{ textAlign: 'center' }}>
              Employee <span style={{ color: 'var(--color-accent-lime)' }}>Registration</span>
            </h2>
            <p className="admin-login-subtitle" style={{ textAlign: 'center', marginBottom: '24px' }}>
              Create an account to access the factory dashboard.
            </p>

            {/* Form */}
            <form className="admin-login-form" onSubmit={handleSubmit}>
              {error && (
                <div className="admin-login-error">
                  <AlertTriangle size={16} />
                  {error}
                </div>
              )}

              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <div className="admin-input-group" style={{ flex: 1 }}>
                  <label>First Name</label>
                  <input
                    name="first_name"
                    type="text"
                    className="admin-input"
                    placeholder="John"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="admin-input-group" style={{ flex: 1 }}>
                  <label>Last Name</label>
                  <input
                    name="last_name"
                    type="text"
                    className="admin-input"
                    placeholder="Doe"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="admin-input-group" style={{ marginBottom: '16px' }}>
                <label>Email Address</label>
                <input
                  name="email"
                  type="email"
                  className="admin-input"
                  placeholder="john.doe@factory.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="admin-input-group" style={{ marginBottom: '16px' }}>
                <label>Department</label>
                <input
                  name="department"
                  type="text"
                  className="admin-input"
                  placeholder="e.g. Maintenance, Assembly"
                  value={formData.department}
                  onChange={handleChange}
                />
              </div>

              <div className="admin-input-group">
                <label>Password</label>
                <input
                  name="password"
                  type="password"
                  className="admin-input"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <button
                type="submit"
                className="admin-login-submit"
                disabled={loading || !formData.password || !formData.email || !formData.first_name}
                style={{ marginTop: '24px' }}
              >
                <UserPlus size={18} />
                {loading ? 'Creating Account...' : 'Register Account'}
              </button>
            </form>

            <p className="admin-login-footer" style={{ marginTop: '24px' }}>
              Already have an account? <span style={{ color: 'var(--color-accent-lime)', cursor: 'pointer', fontWeight: 600 }} onClick={handleGoToLogin}>Login here</span>
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default Register;
