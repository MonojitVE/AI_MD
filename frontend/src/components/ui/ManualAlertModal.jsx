import React, { useState } from 'react';
import Button from './Button';

const ManualAlertModal = ({ onClose, onSubmit }) => {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [priority, setPriority] = useState('medium');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ title, message, priority, equipment_id: null });
  };

  return (
    <div className="admin-login-overlay" onClick={onClose} style={{ zIndex: 100 }}>
      <div className="admin-login-card" onClick={e => e.stopPropagation()}>
        <h2 className="admin-login-title">Report Issue</h2>
        <form onSubmit={handleSubmit}>
          <div className="admin-input-group" style={{ marginBottom: '16px' }}>
            <label>Title</label>
            <input className="admin-input" value={title} onChange={e => setTitle(e.target.value)} required />
          </div>
          <div className="admin-input-group" style={{ marginBottom: '16px' }}>
            <label>Description</label>
            <textarea className="admin-input" value={message} onChange={e => setMessage(e.target.value)} required style={{ minHeight: '80px' }} />
          </div>
          <div className="admin-input-group" style={{ marginBottom: '24px' }}>
            <label>Priority</label>
            <select className="admin-input" value={priority} onChange={e => setPriority(e.target.value)}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Button type="button" variant="ghost" onClick={onClose} style={{ flex: 1 }}>Cancel</Button>
            <Button type="submit" variant="primary" style={{ flex: 1 }}>Submit Issue</Button>
          </div>
        </form>
      </div>
    </div>
  );
};
export default ManualAlertModal;
