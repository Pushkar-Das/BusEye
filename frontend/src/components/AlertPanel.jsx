import { useState, useEffect } from 'react'
import { Bell, AlertTriangle, Droplets, Construction, Car } from 'lucide-react'

const EVENT_ICONS = {
  pothole: { icon: Construction, color: '#ef4444', bg: '#fef2f2' },
  traffic_congestion: { icon: Car, color: '#f59e0b', bg: '#fffbeb' },
  waterlogging: { icon: Droplets, color: '#06b6d4', bg: '#ecfeff' },
  hit_and_run: { icon: AlertTriangle, color: '#dc2626', bg: '#fef2f2' },
  rash_driving: { icon: AlertTriangle, color: '#b91c1c', bg: '#fef2f2' },
  default: { icon: Bell, color: '#8b5cf6', bg: '#f5f3ff' }
}

const SEVERITY_STYLE = {
  critical: { color: '#dc2626', label: 'CRITICAL' },
  high: { color: '#f59e0b', label: 'HIGH' },
  medium: { color: '#3b82f6', label: 'MEDIUM' },
  low: { color: '#10b981', label: 'LOW' },
}

function timeAgo(ts) {
  const secs = Math.floor((Date.now() - new Date(ts)) / 1000)
  if (secs < 60) return `${secs}s ago`
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  return `${Math.floor(secs / 3600)}h ago`
}

export default function AlertPanel({ alerts }) {
  const [pulse, setPulse] = useState(false)

  useEffect(() => {
    if (alerts.length > 0) {
      setPulse(true)
      setTimeout(() => setPulse(false), 600)
    }
  }, [alerts.length])

  return (
    <div style={{
      background: '#1e293b', borderRadius: '12px', border: '1px solid #334155',
      display: 'flex', flexDirection: 'column', height: '540px'
    }}>
      {/* Header */}
      <div style={{
        padding: '14px 16px', borderBottom: '1px solid #334155',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px', height: '8px', borderRadius: '50%', background: '#10b981',
            boxShadow: '0 0 6px #10b981',
            animation: pulse ? 'none' : 'pulse-dot 2s infinite'
          }} />
          <span style={{ fontWeight: 600, color: '#f1f5f9', fontSize: '0.9rem' }}>Live Alerts</span>
        </div>
        <span style={{
          background: '#ef4444', color: 'white', borderRadius: '10px',
          padding: '2px 8px', fontSize: '0.72rem', fontWeight: 700
        }}>
          {alerts.length || 0}
        </span>
      </div>

      {/* Alert list */}
      <div style={{ overflow: 'auto', flex: 1, padding: '8px' }}>
        {alerts.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#475569', padding: '40px 16px', fontSize: '0.85rem' }}>
            <Bell size={32} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.4 }} />
            Waiting for live alerts...
          </div>
        ) : alerts.map((alert, i) => {
          const cfg = EVENT_ICONS[alert.event_type] || EVENT_ICONS.default
          const Icon = cfg.icon
          const sev = SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.low
          return (
            <div
              key={alert.id || i}
              style={{
                display: 'flex', gap: '10px', padding: '10px 8px',
                borderRadius: '8px', marginBottom: '4px',
                background: i === 0 ? '#1a2744' : 'transparent',
                border: i === 0 ? '1px solid #2d4a8a' : '1px solid transparent',
                transition: 'all 0.3s'
              }}
            >
              <div style={{
                width: '32px', height: '32px', borderRadius: '8px',
                background: `${cfg.color}20`, display: 'flex', alignItems: 'center',
                justifyContent: 'center', flexShrink: 0
              }}>
                <Icon size={15} color={cfg.color} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#e2e8f0' }}>
                    {alert.event_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </span>
                  <span style={{
                    fontSize: '0.65rem', fontWeight: 700, color: sev.color,
                    background: `${sev.color}20`, padding: '1px 5px', borderRadius: '4px'
                  }}>
                    {sev.label}
                  </span>
                </div>
                <div style={{ fontSize: '0.73rem', color: '#64748b', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {alert.description}
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '3px' }}>
                  <span style={{ fontSize: '0.68rem', color: '#475569' }}>🚌 {alert.bus_id}</span>
                  <span style={{ fontSize: '0.68rem', color: '#475569' }}>{timeAgo(alert.timestamp)}</span>
                  {alert.plate_number && (
                    <span style={{ fontSize: '0.68rem', color: '#ef4444', fontWeight: 700 }}>
                      🚗 {alert.plate_number}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <style>{`
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}
