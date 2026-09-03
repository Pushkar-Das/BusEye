import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import StatsCards from './components/StatsCards'
import MapView from './components/MapView'
import AlertPanel from './components/AlertPanel'
import IncidentTable from './components/IncidentTable'
import AnalyticsPanel from './components/AnalyticsPanel'
import Sidebar from './components/Sidebar'

const API = 'http://localhost:8000'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [detections, setDetections] = useState([])
  const [buses, setBuses] = useState([])
  const [incidents, setIncidents] = useState([])
  const [liveAlerts, setLiveAlerts] = useState([])
  const [hourly, setHourly] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  // Fetch initial data
  const fetchData = async () => {
    try {
      const [statsRes, detectRes, busRes, incRes, hourlyRes] = await Promise.all([
        axios.get(`${API}/api/stats/summary`),
        axios.get(`${API}/api/detections?hours=24&limit=300`),
        axios.get(`${API}/api/buses`),
        axios.get(`${API}/api/incidents`),
        axios.get(`${API}/api/stats/hourly`),
      ])
      setStats(statsRes.data)
      setDetections(detectRes.data)
      setBuses(busRes.data)
      setIncidents(incRes.data)
      setHourly(hourlyRes.data)
    } catch (e) {
      console.warn('API not reachable, using demo data', e)
      loadDemoData()
    }
  }

  // Demo data for when backend is not running
  const loadDemoData = () => {
    setStats({
      total_events_24h: 347,
      critical_alerts: 12,
      potholes_detected: 89,
      incidents_today: 4,
      active_buses: 5,
      km_roads_scanned: 226.5,
      event_breakdown: [
        { type: 'pothole', count: 89 },
        { type: 'traffic_congestion', count: 124 },
        { type: 'pedestrian_alert', count: 67 },
        { type: 'missing_signboard', count: 38 },
        { type: 'waterlogging', count: 25 },
        { type: 'hit_and_run', count: 4 },
      ]
    })
    const demoDetections = generateDemoDetections()
    setDetections(demoDetections)
    setIncidents(demoDetections.filter(d => ['hit_and_run', 'rash_driving'].includes(d.event_type)))
    setBuses(generateDemoBuses())
    setHourly(generateDemoHourly())
  }

  // WebSocket for live updates
  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket('ws://localhost:8000/ws/live')
        wsRef.current = ws

        ws.onopen = () => {
          setConnected(true)
          console.log('✅ WebSocket connected')
        }

        ws.onmessage = (event) => {
          const msg = JSON.parse(event.data)

          if (msg.type === 'new_detection') {
            setDetections(prev => [msg.data, ...prev].slice(0, 300))
            setLiveAlerts(prev => [msg.data, ...prev].slice(0, 50))
            if (['hit_and_run', 'rash_driving'].includes(msg.data.event_type)) {
              setIncidents(prev => [msg.data, ...prev])
            }
          } else if (msg.type === 'bus_position') {
            setBuses(prev => {
              const updated = prev.filter(b => b.bus_id !== msg.data.bus_id)
              return [...updated, msg.data]
            })
          }
        }

        ws.onclose = () => {
          setConnected(false)
          setTimeout(connect, 3000) // reconnect
        }

        ws.onerror = () => {
          setConnected(false)
        }
      } catch (e) {
        setConnected(false)
      }
    }

    fetchData()
    connect()

    // Refresh stats every 30s
    const interval = setInterval(fetchData, 30000)
    return () => {
      clearInterval(interval)
      wsRef.current?.close()
    }
  }, [])

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f172a', overflow: 'hidden' }}>
      <Sidebar page={page} setPage={setPage} connected={connected} />

      <main style={{ flex: 1, overflow: 'auto', padding: '24px' }}>
        {page === 'dashboard' && (
          <>
            <PageHeader title="🏙️ Urban Intelligence Dashboard" subtitle="Real-time city monitoring via bus fleet" />
            <StatsCards stats={stats} />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '20px', marginTop: '20px' }}>
              <MapView detections={detections} buses={buses} />
              <AlertPanel alerts={liveAlerts} />
            </div>
          </>
        )}

        {page === 'incidents' && (
          <>
            <PageHeader title="🚨 Incident Reports" subtitle="Hit-and-run, rash driving & safety alerts" />
            <IncidentTable incidents={incidents} />
          </>
        )}

        {page === 'analytics' && (
          <>
            <PageHeader title="📊 Traffic Analytics" subtitle="Patterns, trends and congestion insights" />
            <AnalyticsPanel stats={stats} hourly={hourly} detections={detections} />
          </>
        )}

        {page === 'roads' && (
          <>
            <PageHeader title="🛣️ Road Health Monitor" subtitle="Defect density and maintenance priorities" />
            <MapView detections={detections.filter(d => ['pothole','waterlogging','missing_signboard','missing_zebra','missing_divider'].includes(d.event_type))} buses={[]} filterMode="roads" />
          </>
        )}
      </main>
    </div>
  )
}

function PageHeader({ title, subtitle }) {
  return (
    <div style={{ marginBottom: '20px' }}>
      <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: '#f1f5f9' }}>{title}</h1>
      <p style={{ color: '#64748b', marginTop: '4px' }}>{subtitle}</p>
    </div>
  )
}

// ── Demo Data Generators ──────────────────────────────────────────────────────

function generateDemoDetections() {
  const types = [
    { type: 'pothole', sev: 'high', desc: 'Large pothole on road surface' },
    { type: 'pothole', sev: 'medium', desc: 'Road surface crack' },
    { type: 'traffic_congestion', sev: 'high', desc: 'Heavy traffic - 50+ vehicles' },
    { type: 'traffic_congestion', sev: 'medium', desc: 'Moderate traffic buildup' },
    { type: 'pedestrian_alert', sev: 'high', desc: 'School children crossing - no guard' },
    { type: 'missing_signboard', sev: 'high', desc: 'Traffic sign missing' },
    { type: 'waterlogging', sev: 'critical', desc: 'Road waterlogged - 15cm depth' },
    { type: 'missing_zebra', sev: 'medium', desc: 'Zebra crossing faded/missing' },
    { type: 'hit_and_run', sev: 'critical', desc: 'Vehicle fled scene after collision', plate: 'DL3CAB1234' },
    { type: 'rash_driving', sev: 'high', desc: 'Dangerous overtaking detected', plate: 'MH12AB5678' },
    { type: 'missing_divider', sev: 'medium', desc: 'Road divider damaged' },
  ]
  const baseLat = 28.6139, baseLng = 77.2090
  return Array.from({ length: 120 }, (_, i) => {
    const t = types[i % types.length]
    return {
      id: i + 1,
      bus_id: `BUS-00${(i % 5) + 1}`,
      event_type: t.type,
      severity: t.sev,
      latitude: baseLat + (Math.random() - 0.5) * 0.12,
      longitude: baseLng + (Math.random() - 0.5) * 0.12,
      confidence: +(0.72 + Math.random() * 0.26).toFixed(2),
      description: t.desc,
      plate_number: t.plate || '',
      timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString()
    }
  })
}

function generateDemoBuses() {
  return [
    { bus_id: 'BUS-001', latitude: 28.6315, longitude: 77.2167, speed: 32, route: 'Route 401', status: 'active' },
    { bus_id: 'BUS-002', latitude: 28.5700, longitude: 77.2373, speed: 28, route: 'Route 502', status: 'active' },
    { bus_id: 'BUS-003', latitude: 28.6680, longitude: 77.2285, speed: 41, route: 'Route 603', status: 'active' },
    { bus_id: 'BUS-004', latitude: 28.5921, longitude: 77.0460, speed: 19, route: 'Route 704', status: 'active' },
    { bus_id: 'BUS-005', latitude: 28.7350, longitude: 77.1130, speed: 35, route: 'Route 805', status: 'active' },
  ]
}

function generateDemoHourly() {
  return Array.from({ length: 24 }, (_, i) => ({
    hour: `${String(i).padStart(2, '0')}:00`,
    events: Math.floor(5 + Math.random() * 30 + (i >= 8 && i <= 10 ? 40 : 0) + (i >= 17 && i <= 19 ? 35 : 0))
  }))
}
