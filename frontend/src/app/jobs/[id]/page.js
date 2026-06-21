"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function JobDetail() {
  const params = useParams();
  const [selectedRecord, setSelectedRecord] = useState(null);

  // Mock data for scaffolding
  const records = [
    { id: 1, course: "B.Sc Computer Science", institute: "Tech University", status: "VALID", confidence: 95 },
    { id: 2, course: "M.A. History", institute: "Liberal Arts College", status: "INVALID", confidence: 88 },
    { id: 3, course: "Ph.D Physics", institute: "Science Academy", status: "PENDING_REVIEW", confidence: 60 }
  ];

  const statusColors = {
    "VALID": "rgba(16, 185, 129, 0.2)",
    "INVALID": "rgba(239, 68, 68, 0.2)",
    "PENDING_REVIEW": "rgba(245, 158, 11, 0.2)"
  };

  const textColors = {
    "VALID": "var(--success)",
    "INVALID": "var(--danger)",
    "PENDING_REVIEW": "var(--warning)"
  };

  return (
    <div className="dashboard-container">
      <Link href="/" style={{ color: 'var(--accent-primary)', marginBottom: '1.5rem', display: 'inline-block' }}>
        &larr; Back to Dashboard
      </Link>
      
      <header style={{ marginBottom: '2rem' }}>
        <h1 className="animate-fade-in" style={{ fontSize: '2rem', fontWeight: 600 }}>
          Job ID: {params?.id || 'Q3_University_Catalog.pdf'}
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>Detailed validation results for 135 courses.</p>
      </header>

      <div className="glass-panel" style={{ padding: '2rem' }}>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>ID</th>
              <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Course Name</th>
              <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Institute</th>
              <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Status</th>
              <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Confidence</th>
              <th style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id} style={{ transition: 'background 0.2s', cursor: 'pointer' }} onClick={() => setSelectedRecord(record)}>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>#{record.id}</td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}><strong>{record.course}</strong></td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>{record.institute}</td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <span style={{ 
                    background: statusColors[record.status], 
                    color: textColors[record.status], 
                    padding: '0.25rem 0.75rem', 
                    borderRadius: '99px', 
                    fontSize: '0.75rem', 
                    fontWeight: 600 
                  }}>
                    {record.status}
                  </span>
                </td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>{record.confidence}%</td>
                <td style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <button style={{ 
                    background: 'transparent', 
                    border: '1px solid var(--accent-primary)', 
                    color: 'var(--accent-primary)', 
                    padding: '0.5rem 1rem', 
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}>
                    Deep Dive
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Verification Deep Dive Modal */}
      {selectedRecord && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '90%', maxWidth: '1000px', maxHeight: '90vh', overflowY: 'auto', padding: '2.5rem', position: 'relative' }}>
            <button 
              onClick={() => setSelectedRecord(null)}
              style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '1.5rem', cursor: 'pointer' }}
            >
              &times;
            </button>
            
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Evidence Reasoning</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Detailed breakdown for <strong>{selectedRecord.course}</strong></p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div>
                <h3 style={{ color: 'var(--accent-primary)', marginBottom: '1rem', fontSize: '1.1rem' }}>Original PDF Data</h3>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <p><strong>Course:</strong> {selectedRecord.course}</p>
                  <p><strong>Institute:</strong> {selectedRecord.institute}</p>
                  <p><strong>Fees:</strong> $12,000</p>
                </div>

                <h3 style={{ color: 'var(--accent-primary)', marginTop: '2rem', marginBottom: '1rem', fontSize: '1.1rem' }}>AI Reasoning Log</h3>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <p><strong>Layer 2 (ML Embeddings):</strong> Confidence 45% (Uncertain)</p>
                  <p><strong>Layer 4 (LLM Deep Check):</strong> Fallback activated. Gemma-4-31b determined that the fees listed on the website ($14,000) do not match the PDF ($12,000).</p>
                  <div style={{ marginTop: '1rem', padding: '1rem', borderLeft: `4px solid ${textColors[selectedRecord.status]}`, background: 'rgba(255,255,255,0.05)' }}>
                    Final Verdict: <strong>{selectedRecord.status}</strong>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 style={{ color: 'var(--accent-primary)', marginBottom: '1rem', fontSize: '1.1rem' }}>Website Evidence (Screenshot)</h3>
                <div style={{ 
                  background: 'rgba(0,0,0,0.3)', 
                  height: '400px', 
                  borderRadius: '12px', 
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--text-secondary)'
                }}>
                  [ Web Snapshot Viewer Placeholder ]
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
