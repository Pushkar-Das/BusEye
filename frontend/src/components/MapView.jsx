import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix Leaflet's default icon path issue with Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// Event type styling config
const EVENT_CONFIG = {
  pothole:            { color: '#ef4444', emoji: '🕳️', label: 'Pothole' },
  traffic_congestion: { color: '#f59e0b', emoji: '🚗', label: 'Traffic' },
  pedestrian_alert:   { color: '#8b5cf6', emoji: '🚸', label: 'Pedestrian' },
  missing_signboard:  { color: '#ec4899', emoji: '🚧', label: 'Missing Sign' },
  waterlogging:       { color: '#06b6d4', emoji: '💧', label: 'Waterlogging' },
  missing_zebra:      { color: '#f97316', emoji: '🦓', label: 'Zebra Missing' },
  missing_divider:    { color: '#84cc16', emoji: '🛡️', label: 'Divider Missing' },
  hit_and_run:        { color: '#dc2626', emoji: '🚨', label: 'Hit & Run' },
  rash_driving:       { color: '#b91c1c', emoji: '⚠️', label: 'Rash Driving' },
  vehicle_count:      { color: '#3b82f6', emoji: '🚌', label: 'Vehicle Count' },
}

const SEVERITY_RADIUS = { critical: 80, high: 55, medium: 35, low: 20 }

function createBusIcon(busId) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background: linear-gradient(135deg, #1d4ed8, #4f46e5);
      color: white; border-radius: 20px; padding: 4px 8px;
      font-size: 11px; font-weight: 700; white-space: nowrap;
      border: 2px solid #60a5fa; box-shadow: 0 2px 8px rgba(59,130,246,0.6);
      font-family: sans-serif;
    ">🚌 ${busId}</div>`,
    iconAnchor: [32, 16]
  })
}

function createEventIcon(eventType) {
  const cfg = EVENT_CONFIG[eventType] || { emoji: '📍', color: '#64748b' }
  return L.divIcon({
    className: '',
    html: `<div style="
      background: ${cfg.color}; border-radius: 50%; width: 28px; height: 28px;
      display: flex; align-items: center; justify-content: center;
      font-size: 14px; border: 2px solid white;
      box-shadow: 0 2px 6px ${cfg.color}66;
    ">${cfg.emoji}</div>`,
    iconAnchor: [14, 14]
  })
}

// Legend overlay component
function MapLegend() {
  return (
    <div style={{
      position: 'absolute', bottom: '20px', right: '10px', zIndex: 1000,
      background: 'rgba(15,23,42,0.92)', borderRadius: '10px', padding: '12px 14px',
      border: '1px solid #1e293b', backdropFilter: 'blur(10px)', maxWidth: '180px'
    }}>
      <div style={{ color: '#94a3b8', fontSize: '0.7rem', fontWeight: 700, marginBottom: '8px', textTransform: 'uppercase' }}>
        Legend
      </div>
      {Object.entries(EVENT_CONFIG).slice(0, 7).map(([key, cfg]) => (
        <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: cfg.color, flexShrink: 0 }} />
          <span style={{ color: '#cbd5e1', fontSize: '0.72rem' }}>{cfg.label}</span>
        </div>
      ))}
    </div>
  )
}

export default function MapView({ detections, buses, filterMode }) {
  const [activeFilter, setActiveFilter] = useState('all')

  const filteredDetections = detections.filter(d => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'critical') return d.severity === 'critical'
    return d.event_type === activeFilter
  })

  const filterButtons = [
    { id: 'all', label: '🗺️ All' },
    { id: 'pothole', label: '🕳️ Potholes' },
    { id: 'traffic_congestion', label: '🚗 Traffic' },
    { id: 'waterlogging', label: '💧 Waterlogging' },
    { id: 'critical', label: '🔴 Critical' },
  ]

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', overflow: 'hidden', border: '1px solid #334155' }}>
      {/* Filter bar */}
      <div style={{
        padding: '12px 16px', borderBottom: '1px solid #334155',
        display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap'
      }}>
        <span style={{ color: '#64748b', fontSize: '0.8rem', fontWeight: 600 }}>Filter:</span>
        {filterButtons.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setActiveFilter(id)}
            style={{
              padding: '4px 10px', borderRadius: '20px', border: 'none', cursor: 'pointer',
              fontSize: '0.75rem', fontWeight: 500,
              background: activeFilter === id ? '#3b82f6' : '#334155',
              color: activeFilter === id ? '#fff' : '#94a3b8',
            }}
          >
            {label}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', color: '#64748b', fontSize: '0.75rem' }}>
          {filteredDetections.length} events
        </span>
      </div>

      {/* Map */}
      <div style={{ height: '460px', position: 'relative' }}>
        <MapContainer
          center={[28.6139, 77.2090]}
          zoom={12}
          style={{ height: '100%', width: '100%', background: '#0f172a' }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          />

          {/* Bus markers */}
          {buses.map(bus => (
            <Marker key={bus.bus_id} position={[bus.latitude, bus.longitude]} icon={createBusIcon(bus.bus_id)}>
              <Popup>
                <div style={{ minWidth: '160px' }}>
                  <strong>🚌 {bus.bus_id}</strong><br />
                  <span style={{ color: '#666' }}>{bus.route}</span><br />
                  Speed: <strong>{bus.speed} km/h</strong><br />
                  Status: <span style={{ color: '#10b981' }}>{bus.status}</span>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Detection event markers */}
          {filteredDetections.slice(0, 200).map(d => {
            const cfg = EVENT_CONFIG[d.event_type] || { color: '#64748b', emoji: '📍', label: d.event_type }
            const radius = SEVERITY_RADIUS[d.severity] || 30
            return (
              <div key={d.id}>
                <Circle
                  center={[d.latitude, d.longitude]}
                  radius={radius}
                  pathOptions={{ color: cfg.color, fillColor: cfg.color, fillOpacity: 0.15, weight: 1 }}
                />
                <Marker position={[d.latitude, d.longitude]} icon={createEventIcon(d.event_type)}>
                  <Popup>
                    <div style={{ minWidth: '200px' }}>
                      <strong>{cfg.emoji} {cfg.label}</strong>
                      <div style={{
                        display: 'inline-block', marginLeft: '6px',
                        padding: '1px 6px', borderRadius: '10px', fontSize: '0.7rem',
                        background: d.severity === 'critical' ? '#fef2f2' : '#fefce8',
                        color: d.severity === 'critical' ? '#dc2626' : '#92400e'
                      }}>
                        {d.severity?.toUpperCase()}
                      </div><br />
                      <span style={{ color: '#666', fontSize: '0.85rem' }}>{d.description}</span><br />
                      <span style={{ color: '#999', fontSize: '0.75rem' }}>Bus: {d.bus_id}</span><br />
                      <span style={{ color: '#999', fontSize: '0.75rem' }}>Confidence: {(d.confidence * 100).toFixed(0)}%</span>
                      {d.plate_number && <><br /><strong style={{ color: '#dc2626' }}>Plate: {d.plate_number}</strong></>}
                      <br /><span style={{ color: '#bbb', fontSize: '0.7rem' }}>{new Date(d.timestamp).toLocaleString()}</span>
                    </div>
                  </Popup>
                </Marker>
              </div>
            )
          })}
        </MapContainer>
        <MapLegend />
      </div>
    </div>
  )
}
