import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts'

const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#06b6d4', '#ec4899']

const card = (children, title, span = 1) => (
  <div style={{
    background: '#1e293b', borderRadius: '12px', padding: '20px',
    border: '1px solid #334155', gridColumn: `span ${span}`
  }}>
    {title && <h3 style={{ color: '#94a3b8', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>{title}</h3>}
    {children}
  </div>
)

const tooltipStyle = {
  contentStyle: { background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' },
  labelStyle: { color: '#94a3b8' }
}

export default function AnalyticsPanel({ stats, hourly, detections }) {
  const eventBreakdown = stats?.event_breakdown || []

  // Road defect types for pie chart
  const defectTypes = detections?.filter(d =>
    ['pothole', 'waterlogging', 'missing_signboard', 'missing_zebra', 'missing_divider'].includes(d.event_type)
  ).reduce((acc, d) => {
    acc[d.event_type] = (acc[d.event_type] || 0) + 1
    return acc
  }, {})

  const defectData = Object.entries(defectTypes || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    value
  }))

  // Severity breakdown
  const severityCounts = detections?.reduce((acc, d) => {
    acc[d.severity] = (acc[d.severity] || 0) + 1
    return acc
  }, {})

  const severityData = ['critical', 'high', 'medium', 'low'].map(s => ({
    name: s.charAt(0).toUpperCase() + s.slice(1),
    count: severityCounts?.[s] || 0,
    color: { critical: '#dc2626', high: '#f59e0b', medium: '#3b82f6', low: '#10b981' }[s]
  }))

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>

      {/* Hourly trend */}
      {card(
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={hourly || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} interval={3} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
            <Tooltip {...tooltipStyle} />
            <Line type="monotone" dataKey="events" stroke="#3b82f6" strokeWidth={2.5} dot={false} name="Events" />
          </LineChart>
        </ResponsiveContainer>,
        '📈 Events Over 24 Hours', 2
      )}

      {/* Event breakdown */}
      {card(
        <>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={eventBreakdown} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis type="category" dataKey="type" tick={{ fill: '#94a3b8', fontSize: 11 }}
                tickFormatter={v => v.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                width={130}
              />
              <Tooltip {...tooltipStyle}
                formatter={(v, name) => [v, 'Count']}
                labelFormatter={l => l.replace(/_/g, ' ')}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {eventBreakdown.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </>,
        '📊 Event Type Breakdown'
      )}

      {/* Defect pie chart */}
      {card(
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <ResponsiveContainer width={200} height={200}>
            <PieChart>
              <Pie data={defectData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} dataKey="value">
                {defectData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip {...tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
          <div>
            {defectData.map((d, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '2px', background: COLORS[i % COLORS.length] }} />
                <span style={{ color: '#94a3b8', fontSize: '0.78rem' }}>{d.name}</span>
                <span style={{ color: '#f1f5f9', fontWeight: 700, marginLeft: 'auto', fontSize: '0.82rem' }}>{d.value}</span>
              </div>
            ))}
          </div>
        </div>,
        '🛣️ Road Defect Types'
      )}

      {/* Severity chart */}
      {card(
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={severityData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
            <Tooltip {...tooltipStyle} />
            <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Alerts">
              {severityData.map((d, i) => (
                <Cell key={i} fill={d.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>,
        '🔔 Alerts by Severity'
      )}

    </div>
  )
}
