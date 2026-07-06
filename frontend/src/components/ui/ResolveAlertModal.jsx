import React, { useState } from 'react';
import Button from './Button';

const ResolveAlertModal = ({ onClose, onSubmit }) => {
  const [resolution, setResolution] = useState('');
  const [repairDuration, setRepairDuration] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ 
      resolution, 
      repair_duration_minutes: parseInt(repairDuration) || 0 
    });
  };

  return (
    <div className="admin-login-overlay" onClick={onClose} style={{ zIndex: 100 }}>
      <div className="admin-login-card" onClick={e => e.stopPropagation()}>
        <h2 className="admin-login-title">Resolve Task</h2>
        <form onSubmit={handleSubmit}>
          <div className="admin-input-group" style={{ marginBottom: '16px' }}>
            <label>Resolution Notes</label>
            <textarea className="admin-input" value={resolution} onChange={e => setResolution(e.target.value)} required style={{ minHeight: '80px' }} />
          </div>
          <div className="admin-input-group" style={{ marginBottom: '24px' }}>
            <label>Repair Duration (minutes)</label>
            <input type="number" className="admin-input" value={repairDuration} onChange={e => setRepairDuration(e.target.value)} required />
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Button type="button" variant="ghost" onClick={onClose} style={{ flex: 1 }}>Cancel</Button>
            <Button type="submit" variant="primary" style={{ flex: 1 }}>Resolve</Button>
          </div>
        </form>
      </div>
    </div>
  );
};
export default ResolveAlertModal;
