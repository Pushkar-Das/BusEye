import { AlertTriangle, Camera } from 'lucide-react'

const SEVERITY_COLOR = {
  critical: '#dc2626',
  high: '#f59e0b',
  medium: '#3b82f6',
  low: '#10b981'
}

function formatDate(ts) {
  return new Date(ts).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

export default function IncidentTable({ incidents }) {
  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <AlertTriangle size={18} color="#ef4444" />
        <span style={{ fontWeight: 600, color: '#f1f5f9' }}>Incident Log</span>
        <span style={{ marginLeft: 'auto', background: '#ef444420', color: '#ef4444', borderRadius: '8px', padding: '2px 8px', fontSize: '0.75rem', fontWeight: 700 }}>
          {incidents.length} recorded
        </span>
      </div>

      {incidents.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#475569' }}>
          <AlertTriangle size={40} style={{ margin: '0 auto 12px', display: 'block', opacity: 0.3 }} />
          <p>No incidents recorded yet.</p>
          <p style={{ fontSize: '0.8rem', marginTop: '4px' }}>Incidents will appear here when detected by the AI system.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ background: '#0f172a' }}>
                {['#', 'Type', 'Plate Number', 'Bus ID', 'Location', 'Confidence', 'Severity', 'Timestamp'].map(h => (
                  <th key={h} style={{
                    padding: '10px 14px', textAlign: 'left', color: '#64748b',
                    fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase',
                    letterSpacing: '0.05em', borderBottom: '1px solid #334155'
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {incidents.map((inc, i) => (
                <tr
                  key={inc.id || i}
                  style={{
                    borderBottom: '1px solid #1e293b',
                    background: i % 2 === 0 ? 'transparent' : '#0f172a18'
                  }}
                >
                  <td style={{ padding: '12px 14px', color: '#475569' }}>{i + 1}</td>
                  <td style={{ padding: '12px 14px' }}>
                    <span style={{
                      background: '#ef444420', color: '#ef4444',
                      padding: '2px 8px', borderRadius: '6px', fontWeight: 600, fontSize: '0.78rem'
                    }}>
                      {inc.event_type === 'hit_and_run' ? '🚨 Hit & Run' : '⚠️ Rash Driving'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    {inc.plate_number ? (
                      <span style={{
                        background: '#1e3a5f', color: '#60a5fa', fontFamily: 'monospace',
                        padding: '3px 10px', borderRadius: '6px', fontWeight: 700, fontSize: '0.88rem',
                        border: '1px solid #2563eb'
                      }}>
                        {inc.plate_number}
                      </span>
                    ) : (
                      <span style={{ color: '#475569' }}>Not captured</span>
                    )}
                  </td>
                  <td style={{ padding: '12px 14px', color: '#94a3b8' }}>{inc.bus_id}</td>
                  <td style={{ padding: '12px 14px', color: '#94a3b8', fontSize: '0.78rem' }}>
                    {inc.latitude?.toFixed(4)}°N, {inc.longitude?.toFixed(4)}°E
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <div style={{
                        width: `${(inc.confidence || 0.8) * 60}px`, height: '6px',
                        background: '#10b981', borderRadius: '3px', maxWidth: '60px'
                      }} />
                      <span style={{ color: '#94a3b8', fontSize: '0.78rem' }}>
                        {((inc.confidence || 0.8) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <span style={{
                      color: SEVERITY_COLOR[inc.severity] || '#64748b',
                      fontWeight: 700, fontSize: '0.75rem',
                      background: `${SEVERITY_COLOR[inc.severity]}20`, padding: '2px 8px', borderRadius: '6px'
                    }}>
                      {inc.severity?.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '12px 14px', color: '#64748b', fontSize: '0.78rem' }}>
                    {formatDate(inc.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
