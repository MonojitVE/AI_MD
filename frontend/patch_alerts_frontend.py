import os

def patch_alerts_api():
    content = """import client from './client';

export const getAlertsList = async (filters = {}) => {
  const response = await client.get('/api/alerts', { params: filters });
  return response.data;
};

export const getAlertCounts = async () => {
  const response = await client.get('/api/alerts/count');
  return response.data;
};

export const markAlertRead = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/read`);
  return response.data;
};

export const markAllAlertsRead = async () => {
  const response = await client.patch('/api/alerts/read-all');
  return response.data;
};

export const dismissAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/dismiss`);
  return response.data;
};

// CMMS Endpoints
export const acceptAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/accept`);
  return response.data;
};

export const startAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/start`);
  return response.data;
};

export const resolveAlert = async (id, data) => {
  const response = await client.patch(`/api/alerts/${id}/resolve`, data);
  return response.data;
};

export const verifyAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/verify`);
  return response.data;
};

export const createManualAlert = async (data) => {
  const response = await client.post('/api/alerts/manual', data);
  return response.data;
};
"""
    with open(r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\api\alerts.js", "w") as f:
        f.write(content)

def create_manual_modal():
    content = """import React, { useState } from 'react';
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
"""
    with open(r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\components\ui\ManualAlertModal.jsx", "w") as f:
        f.write(content)

def create_resolve_modal():
    content = """import React, { useState } from 'react';
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
"""
    with open(r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\components\ui\ResolveAlertModal.jsx", "w") as f:
        f.write(content)

def patch_alerts_jsx():
    path = r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\pages\Alerts.jsx"
    with open(path, "r") as f:
        content = f.read()

    # Imports
    import_target = "import { getAlertsList, markAlertRead, markAllAlertsRead, dismissAlert, getAlertCounts } from '../api/alerts';"
    import_replacement = """import { getAlertsList, markAlertRead, markAllAlertsRead, dismissAlert, getAlertCounts, acceptAlert, startAlert, resolveAlert, verifyAlert, createManualAlert } from '../api/alerts';
import ManualAlertModal from '../components/ui/ManualAlertModal';
import ResolveAlertModal from '../components/ui/ResolveAlertModal';"""
    content = content.replace(import_target, import_replacement)

    # State variables
    state_target = "const [typeFilter, setTypeFilter] = useState('');"
    state_replacement = """const [typeFilter, setTypeFilter] = useState('');
  const [showManualModal, setShowManualModal] = useState(false);
  const [resolvingAlertId, setResolvingAlertId] = useState(null);
  const { user } = useAuthStore();"""
    content = content.replace(state_target, state_replacement)

    # Functions
    fns_target = "const handleDismiss = async (id) => {"
    fns_replacement = """const handleAccept = async (id) => { await acceptAlert(id); fetchData(); };
  const handleStart = async (id) => { await startAlert(id); fetchData(); };
  const handleResolveSubmit = async (data) => { 
    await resolveAlert(resolvingAlertId, data); 
    setResolvingAlertId(null);
    fetchData(); 
  };
  const handleVerify = async (id) => { await verifyAlert(id); fetchData(); };
  const handleManualSubmit = async (data) => {
    await createManualAlert(data);
    setShowManualModal(false);
    fetchData();
  };

  const handleDismiss = async (id) => {"""
    content = content.replace(fns_target, fns_replacement)

    # Add Reporting Button
    btn_target = """{isAdmin && counts && counts.unread > 0 && (
          <Button variant="ghost" onClick={handleMarkAllRead}>
            <CheckCheck size={16} /> Mark all read
          </Button>
        )}"""
    btn_replacement = btn_target + """
        <Button variant="primary" onClick={() => setShowManualModal(true)} style={{ marginLeft: 'auto' }}>
          Report Issue
        </Button>"""
    content = content.replace(btn_target, btn_replacement)

    # Add UI buttons inside alert item
    action_target = "{isAdmin && ("
    action_replacement = """<div className="alert-feed-actions" style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
                {user?.role === 'employee' && alert.status === 'pending' && <Button onClick={() => handleAccept(alert.id)} variant="primary" size="small">Accept</Button>}
                {user?.role === 'employee' && alert.status === 'accepted' && alert.assigned_to === user?.id && <Button onClick={() => handleStart(alert.id)} variant="primary" size="small">Start Work</Button>}
                {user?.role === 'employee' && alert.status === 'in_progress' && alert.assigned_to === user?.id && <Button onClick={() => setResolvingAlertId(alert.id)} variant="primary" size="small">Resolve</Button>}
                {user?.role === 'admin' && alert.status === 'resolved' && <Button onClick={() => handleVerify(alert.id)} variant="primary" size="small">Verify</Button>}
                </div>
                """ + action_target
    content = content.replace(action_target, action_replacement)

    # Display status
    meta_target = "<span>Category: {alert.type.toUpperCase()}</span>"
    meta_replacement = meta_target + "\n                  <span>Status: {alert.status?.toUpperCase() || 'PENDING'}</span>"
    content = content.replace(meta_target, meta_replacement)

    # Inject Modals at bottom
    end_target = "</div>\n    </div>\n  );\n};\n\nexport default AlertsPage;"
    end_replacement = """</div>
      {showManualModal && <ManualAlertModal onClose={() => setShowManualModal(false)} onSubmit={handleManualSubmit} />}
      {resolvingAlertId && <ResolveAlertModal onClose={() => setResolvingAlertId(null)} onSubmit={handleResolveSubmit} />}
    </div>
  );
};

export default AlertsPage;"""
    content = content.replace(end_target, end_replacement)

    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    patch_alerts_api()
    create_manual_modal()
    create_resolve_modal()
    patch_alerts_jsx()
    print("Alerts frontend patched.")
