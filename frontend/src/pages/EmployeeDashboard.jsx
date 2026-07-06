import React, { useEffect, useState } from 'react';
import useDashboardStore from '../store/useDashboardStore';
import api from '../api/client';
import StatCard from '../components/ui/StatCard';
import Card from '../components/ui/Card';
import Loader from '../components/ui/Loader';
import { formatDate } from '../utils/formatters';
import { 
  Briefcase, 
  CheckCircle, 
  Clock, 
  AlertTriangle 
} from 'lucide-react';
import './Dashboard.css';

const EmployeeDashboard = () => {
  const { overview, loading } = useDashboardStore();
  const [myJobs, setMyJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);

  useEffect(() => {
    const fetchMyJobs = async () => {
      setJobsLoading(true);
      try {
        const response = await api.get('/api/alerts/my-jobs');
        setMyJobs(response.data);
      } catch (err) {
        console.error('Failed to fetch jobs:', err);
      } finally {
        setJobsLoading(false);
      }
    };
    fetchMyJobs();
  }, []);

  if (loading && !overview) {
    return <Loader type="shimmer" count={6} height="120px" />;
  }

  const completedToday = myJobs.filter(j => j.status === 'resolved' || j.status === 'verified').length;
  const activeJobs = myJobs.filter(j => ['accepted', 'in_progress'].includes(j.status)).length;
  const pendingJobs = myJobs.filter(j => j.status === 'pending').length;

  return (
    <div className="animate-fade-in" style={{ position: 'relative' }}>
      <div className="starfield-bg"></div>

      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2 }}>
          Technician <span style={{ 
            backgroundColor: 'var(--color-accent-lime)', 
            color: 'var(--color-ink-deep)', 
            borderRadius: 'var(--rounded-xs)', 
            padding: '2px 12px',
            fontSize: '2.3rem'
          }}>Workspace</span>
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          Manage your assigned maintenance tasks and report new issues.
        </p>
      </div>

      <div className="stat-card-grid">
        <StatCard 
          title="Active Jobs" 
          value={activeJobs} 
          icon={Briefcase}
          desc="Jobs currently in progress"
        />
        <StatCard 
          title="Pending Jobs" 
          value={pendingJobs} 
          icon={AlertTriangle}
          desc="Jobs waiting for action"
        />
        <StatCard 
          title="Completed Today" 
          value={completedToday} 
          icon={CheckCircle}
          desc="Maintenance tasks resolved"
        />
        <StatCard 
          title="Average Resolution Time" 
          value="45m" 
          icon={Clock}
          desc="Your personal average"
        />
      </div>

      <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr', marginTop: '24px' }}>
        <Card className="dashboard-full-width">
          <h3 className="dashboard-card-title">
            <Briefcase size={18} style={{ color: 'var(--color-accent-lime)' }} />
            My Active Jobs
          </h3>
          <div className="recent-alert-list">
            {jobsLoading ? <Loader type="spinner" /> : myJobs.length > 0 ? myJobs.filter(j => ['pending', 'accepted', 'in_progress'].includes(j.status)).map((job) => (
              <div key={job.id} className="recent-alert-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                  <div className="recent-alert-dot" style={{ backgroundColor: 'var(--color-accent-lime)' }}></div>
                  <div>
                    <div style={{ fontWeight: 600 }}>{job.title}</div>
                    <div style={{ color: 'var(--color-on-dark-muted)', fontSize: '0.85rem' }}>{job.equipment_name || 'General'} • Status: {job.status}</div>
                  </div>
                </div>
                <span className="recent-alert-time">{formatDate(job.created_at)}</span>
              </div>
            )) : (
              <div style={{ color: 'var(--color-on-dark-muted)', padding: '24px 0' }}>No active jobs assigned to you.</div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default EmployeeDashboard;
