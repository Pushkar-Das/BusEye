import { TrendingUp, AlertTriangle, Construction, Bus, Navigation, Activity } from 'lucide-react'

const Card = ({ icon: Icon, label, value, sub, color, bg }) => (
  <div style={{
    background: '#1e293b', borderRadius: '12px', padding: '20px',
    border: `1px solid ${color}33`, position: 'relative', overflow: 'hidden'
  }}>
    <div style={{
      position: 'absolute', top: 0, right: 0, width: '80px', height: '80px',
      background: `radial-gradient(circle at top right, ${color}15, transparent)`, borderRadius: '12px'
    }} />
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <div style={{ color: '#64748b', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </div>
        <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f1f5f9', marginTop: '6px', lineHeight: 1 }}>
          {value ?? '—'}
        </div>
        {sub && <div style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '6px' }}>{sub}</div>}
      </div>
      <div style={{ background: `${color}20`, padding: '10px', borderRadius: '10px' }}>
        <Icon size={22} color={color} />
      </div>
    </div>
  </div>
)

export default function StatsCards({ stats }) {
  if (!stats) return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '16px' }}>
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} style={{ background: '#1e293b', borderRadius: '12px', height: '100px', animation: 'pulse 1.5s infinite' }} />
      ))}
    </div>
  )

  const cards = [
    { icon: Activity, label: 'Events (24h)', value: stats.total_events_24h?.toLocaleString(), sub: 'All detection types', color: '#3b82f6' },
    { icon: AlertTriangle, label: 'Critical Alerts', value: stats.critical_alerts, sub: 'Needs immediate action', color: '#ef4444' },
    { icon: Construction, label: 'Potholes Found', value: stats.potholes_detected, sub: 'Road defects mapped', color: '#f59e0b' },
    { icon: TrendingUp, label: 'Incidents', value: stats.incidents_today, sub: 'Hit-and-run / rash drive', color: '#8b5cf6' },
    { icon: Bus, label: 'Active Buses', value: stats.active_buses, sub: 'Fleet deployed', color: '#10b981' },
    { icon: Navigation, label: 'Roads Scanned', value: `${stats.km_roads_scanned} km`, sub: 'Today\'s coverage', color: '#06b6d4' },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '16px' }}>
      {cards.map((c, i) => <Card key={i} {...c} />)}
    </div>
  )
}
