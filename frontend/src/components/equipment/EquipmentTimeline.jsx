import React, { useEffect, useState } from 'react';
import api from '../../api/client';
import Loader from '../ui/Loader';
import { formatDate } from '../../utils/formatters';
import { ShieldAlert, Wrench, CheckCircle } from 'lucide-react';
import './EquipmentTimeline.css';

const EquipmentTimeline = ({ equipmentId }) => {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await api.get(`/api/equipment/${equipmentId}/timeline`);
        setTimeline(res.data);
      } catch (err) {
        console.error('Failed to load timeline', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, [equipmentId]);

  if (loading) return <Loader type="spinner" />;

  if (timeline.length === 0) {
    return <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-on-dark-muted)' }}>No historical events found for this asset.</div>;
  }

  return (
    <div className="equipment-timeline">
      {timeline.map((event, idx) => {
        const isAlert = event.type === 'alert';
        const Icon = isAlert ? ShieldAlert : Wrench;
        const color = isAlert 
          ? (event.severity === 'critical' ? 'var(--color-accent-pink)' : 'var(--color-accent-peach)')
          : 'var(--color-accent-lime)';
          
        return (
          <div key={`${event.type}-${event.id}`} className="timeline-event">
            <div className="timeline-connector">
              <div className="timeline-dot" style={{ backgroundColor: color }}>
                <Icon size={12} color="var(--color-primary)" />
              </div>
              {idx !== timeline.length - 1 && <div className="timeline-line" />}
            </div>
            
            <div className="timeline-content">
              <div className="timeline-header">
                <span className="timeline-title">{event.title}</span>
                <span className="timeline-time">{formatDate(event.timestamp)}</span>
              </div>
              {event.description && <p className="timeline-desc">{event.description}</p>}
              <div className="timeline-meta">
                {isAlert && <span>Status: {event.status?.toUpperCase() || 'PENDING'}</span>}
                {!isAlert && event.duration > 0 && <span>Duration: {event.duration}m</span>}
                {!isAlert && event.cost > 0 && <span>Cost: ${event.cost}</span>}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default EquipmentTimeline;
