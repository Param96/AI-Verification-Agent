import React from 'react';

export default function Dashboard() {
  return (
    <div className="dashboard-container">
      <header style={{ marginBottom: '3rem' }}>
        <h1 className="animate-fade-in" style={{ fontSize: '2.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>
          Overview
        </h1>
        <p className="animate-fade-in delay-1" style={{ color: 'var(--text-secondary)' }}>
          Monitor your document ingestion and AI verification pipelines.
        </p>
      </header>

      <section className="metrics-grid">
        <div className="glass-panel metric-card animate-fade-in delay-1">
          <div className="metric-title">Total Records Parsed</div>
          <div className="metric-value" style={{ color: 'var(--accent-primary)' }}>1,432</div>
        </div>
        <div className="glass-panel metric-card animate-fade-in delay-2">
          <div className="metric-title">Successfully Verified</div>
          <div className="metric-value" style={{ color: 'var(--success)' }}>1,105</div>
        </div>
        <div className="glass-panel metric-card animate-fade-in delay-3">
          <div className="metric-title">Pending Manual Review</div>
          <div className="metric-value" style={{ color: 'var(--warning)' }}>28</div>
        </div>
        <div className="glass-panel metric-card animate-fade-in delay-3">
          <div className="metric-title">Invalid / Broken Links</div>
          <div className="metric-value" style={{ color: 'var(--danger)' }}>299</div>
        </div>
      </section>

      <section className="glass-panel animate-fade-in delay-2" style={{ padding: '2rem', marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          Recent Jobs
        </h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Filename</th>
                <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Status</th>
                <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Progress</th>
                <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <strong>Q3_University_Catalog.pdf</strong>
                </td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: 'var(--success)', padding: '0.25rem 0.75rem', borderRadius: '99px', fontSize: '0.75rem', fontWeight: 600 }}>COMPLETED</span>
                </td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ width: '100%', background: 'rgba(255,255,255,0.1)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: '100%', background: 'var(--success)', height: '100%' }}></div>
                  </div>
                </td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>Just now</td>
              </tr>
              <tr>
                <td style={{ padding: '1rem' }}>
                  <strong>Tender_Specs_2026.pdf</strong>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span style={{ background: 'rgba(59, 130, 246, 0.2)', color: 'var(--accent-primary)', padding: '0.25rem 0.75rem', borderRadius: '99px', fontSize: '0.75rem', fontWeight: 600 }}>PROCESSING</span>
                </td>
                <td style={{ padding: '1rem' }}>
                  <div style={{ width: '100%', background: 'rgba(255,255,255,0.1)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: '45%', background: 'var(--accent-primary)', height: '100%' }}></div>
                  </div>
                </td>
                <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>2 mins ago</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
