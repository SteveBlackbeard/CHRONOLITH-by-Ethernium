import { Network } from 'lucide-react';
import NetworkGraph from './components/NetworkGraph';
import './index.css';

function App() {
  return (
    <div className="dashboard-container">
      {/* 3D Graph Background */}
      <div className="graph-container">
        <NetworkGraph />
      </div>

      {/* Futuristic Glassmorphic Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="brand-header">
          <div className="brand-icon">
            <Network size={20} color="#fff" />
          </div>
          <div>
            <h1 className="text-gradient" style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '0.5px' }}>
              CONTINUITY OMEGA
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
              v2.1.0 // SOVEREIGN EDITION
            </p>
          </div>
        </div>

        <div style={{ padding: '20px 0', borderBottom: '1px solid var(--glass-border)' }}>
          <h2 style={{ fontSize: '0.9rem', color: '#fff', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="pulse-dot"></span>
            SYSTEM STATUS
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            All continuity daemons online. DNA lineage intact.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="stat-box">
            <div className="stat-label">Crystallized Atoms</div>
            <div className="stat-value">14</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">DNA Integrity</div>
            <div className="stat-value text-gradient" style={{ display: 'inline-block' }}>100.0%</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Merkle Root Entropy</div>
            <div className="stat-value" style={{ fontFamily: 'monospace', fontSize: '1.2rem' }}>0x9A4F...</div>
          </div>
        </div>

        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <p className="stat-label" style={{ marginBottom: 0 }}>RECENT PROTOCOLS</p>
          <div className="activity-feed">
            <div className="activity-item">
              <span className="activity-time">10:41</span>
              <span className="activity-text">Removed hardware binding for sovereign collaboration.</span>
            </div>
            <div className="activity-item">
              <span className="activity-time">10:30</span>
              <span className="activity-text">Installed Fail-Closed Sentinel Guardian.</span>
            </div>
            <div className="activity-item">
              <span className="activity-time">10:15</span>
              <span className="activity-text">RFC 6962 Merkle Hardening completed.</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Floating Action Controls */}
      <div className="overlay-ui glass-panel">
        <button className="btn">
          <span>Explore DNA</span>
        </button>
        <button className="btn primary">
          <span>Run Cycle</span>
        </button>
      </div>
    </div>
  );
}

export default App;
