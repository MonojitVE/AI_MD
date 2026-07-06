import React from 'react';
import Button from './Button';
import { formatDate } from '../../utils/formatters';
import { CheckCircle, Clock, Check, Wrench, ShieldAlert } from 'lucide-react';

const TimelineModal = ({ alert, onClose }) => {
  const steps = [
    { label: 'Created', time: alert.created_at, icon: ShieldAlert },
    { label: 'Accepted', time: alert.accepted_at, icon: Check },
    { label: 'Started', time: alert.started_at, icon: Wrench },
    { label: 'Resolved', time: alert.completed_at, icon: CheckCircle },
    { label: 'Verified', time: alert.verified_at, icon: CheckCircle }
  ];

  return (
    <div className="admin-login-overlay" onClick={onClose} style={{ zIndex: 100 }}>
      <div className="admin-login-card" onClick={e => e.stopPropagation()} style={{ minWidth: '400px' }}>
        <h2 className="admin-login-title">Maintenance Timeline</h2>
        <div style={{ padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {steps.map((step, idx) => {
            const isCompleted = !!step.time;
            const Icon = step.icon;
            return (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '16px', opacity: isCompleted ? 1 : 0.4 }}>
                <div style={{
                  width: '32px', height: '32px', borderRadius: '16px',
                  backgroundColor: isCompleted ? 'var(--color-accent-lime)' : 'var(--color-canvas-dark)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: isCompleted ? 'var(--color-primary)' : 'var(--color-on-dark-muted)',
                  border: isCompleted ? 'none' : '1px solid var(--color-hairline-violet)'
                }}>
                  <Icon size={16} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600 }}>{step.label}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--color-on-dark-muted)' }}>
                    {isCompleted ? formatDate(step.time) : 'Pending'}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <Button variant="ghost" onClick={onClose} style={{ width: '100%' }}>Close</Button>
      </div>
    </div>
  );
};
export default TimelineModal;
