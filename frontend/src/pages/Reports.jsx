import React, { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { getAiReports, getAiReportDetail, generateAiReport } from '../api/reports';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import { formatDate } from '../utils/formatters';
import { FileText, Plus, Download, Printer } from 'lucide-react';
import './Reports.css';

const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateType, setGenerateType] = useState('executive');
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  // Viewer state
  const [viewReportId, setViewReportId] = useState(null);
  const [activeReport, setActiveReport] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);

  const printRef = useRef();

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data = await getAiReports();
      setReports(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await generateAiReport(generateType);
      setShowGenerateModal(false);
      await fetchReports();
    } catch (err) {
      console.error("Failed to generate report", err);
      alert("Failed to generate report.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleView = async (id) => {
    setViewReportId(id);
    setViewLoading(true);
    try {
      const detail = await getAiReportDetail(id);
      setActiveReport(detail);
    } catch (err) {
      console.error(err);
    } finally {
      setViewLoading(false);
    }
  };

  const closeViewer = () => {
    setViewReportId(null);
    setActiveReport(null);
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading && reports.length === 0) {
    return <Loader type="shimmer" count={3} height="120px" />;
  }

  return (
    <div className="reports-container animate-fade-in">
      <div className="reports-header">
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
            Executive <span style={{ backgroundColor: 'var(--color-accent-blue)', color: 'white', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Reports</span>
          </h2>
          <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
            AI-generated strategic insights, operational summaries, and scheduled reporting.
          </p>
        </div>
        
        <Button onClick={() => setShowGenerateModal(true)} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <Plus size={18} /> Generate New Report
        </Button>
      </div>

      <div className="reports-grid">
        {reports.length === 0 ? (
          <div style={{ color: 'var(--color-on-dark-muted)' }}>No reports generated yet.</div>
        ) : (
          reports.map(report => (
            <Card key={report.id} className="report-card" onClick={() => handleView(report.id)}>
              <div className="report-card-header">
                <div>
                  <div className="report-title">{report.title}</div>
                  <div className="report-type">{report.report_type}</div>
                </div>
                <FileText color="var(--color-on-dark-muted)" size={24} />
              </div>
              <div className="report-date">
                Generated {formatDate(report.created_at)}
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Generate Modal */}
      <Modal isOpen={showGenerateModal} onClose={() => !isGenerating && setShowGenerateModal(false)} title="Generate AI Report">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <p style={{ color: 'var(--color-on-dark-muted)' }}>Select the type of report you want the AI Executive Assistant to generate based on current dashboard data.</p>
          
          <select 
            value={generateType} 
            onChange={e => setGenerateType(e.target.value)}
            disabled={isGenerating}
            style={{ padding: '8px', borderRadius: 'var(--rounded-sm)', backgroundColor: 'var(--color-surface-night)', color: 'var(--color-on-primary)', border: '1px solid var(--color-hairline-violet)' }}
          >
            <option value="executive">Executive Summary (All Metrics)</option>
            <option value="maintenance">Maintenance Overview</option>
            <option value="equipment">Equipment Health Analysis</option>
            <option value="inventory">Inventory Status</option>
          </select>

          <Button onClick={handleGenerate} disabled={isGenerating}>
            {isGenerating ? <Loader type="spinner" size={16} /> : 'Generate Report'}
          </Button>
        </div>
      </Modal>

      {/* Report Viewer Modal */}
      <Modal isOpen={viewReportId !== null} onClose={closeViewer} title={activeReport?.title || "Loading Report..."}>
        {viewLoading ? (
          <Loader type="spinner" />
        ) : activeReport ? (
          <div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
              <Button onClick={handlePrint} variant="ghost" style={{ display: 'flex', gap: '8px' }}>
                <Printer size={16} /> Print / Save PDF
              </Button>
            </div>
            <div className="print-area markdown-body" ref={printRef}>
              <ReactMarkdown>{activeReport.content}</ReactMarkdown>
            </div>
          </div>
        ) : (
          <div>Failed to load report content.</div>
        )}
      </Modal>
    </div>
  );
};

export default ReportsPage;
