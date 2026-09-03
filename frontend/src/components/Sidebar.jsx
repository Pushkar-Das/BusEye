import { Bus, LayoutDashboard, AlertTriangle, BarChart3, Map, Wifi, WifiOff } from 'lucide-react'

const navItems = [
  { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { id: 'roads', icon: Map, label: 'Road Health' },
  { id: 'incidents', icon: AlertTriangle, label: 'Incidents' },
  { id: 'analytics', icon: BarChart3, label: 'Analytics' },
]

export default function Sidebar({ page, setPage, connected }) {
  return (
    <aside style={{
      width: '220px', background: '#0d1526', borderRight: '1px solid #1e293b',
      display: 'flex', flexDirection: 'column', padding: '0', flexShrink: 0
    }}>
      {/* Logo */}
      <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
            borderRadius: '10px', padding: '8px', display: 'flex'
          }}>
            <Bus size={20} color="white" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#f1f5f9' }}>BusEye</div>
            <div style={{ fontSize: '0.65rem', color: '#64748b', marginTop: '1px' }}>Urban Intelligence</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ padding: '12px 8px', flex: 1 }}>
        {navItems.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setPage(id)}
            style={{
              width: '100%', display: 'flex', alignItems: 'center', gap: '10px',
              padding: '10px 12px', borderRadius: '8px', border: 'none', cursor: 'pointer',
              marginBottom: '4px', textAlign: 'left', fontSize: '0.875rem', fontWeight: 500,
              background: page === id ? 'linear-gradient(135deg, #1d4ed8, #4f46e5)' : 'transparent',
              color: page === id ? '#fff' : '#94a3b8',
              transition: 'all 0.15s'
            }}
          >
            <Icon size={17} />
            {label}
          </button>
        ))}
      </nav>

      {/* Connection status */}
      <div style={{
        padding: '16px 20px', borderTop: '1px solid #1e293b',
        display: 'flex', alignItems: 'center', gap: '8px'
      }}>
        {connected
          ? <><Wifi size={14} color="#10b981" /><span style={{ fontSize: '0.75rem', color: '#10b981' }}>Live Connected</span></>
          : <><WifiOff size={14} color="#ef4444" /><span style={{ fontSize: '0.75rem', color: '#f59e0b' }}>Demo Mode</span></>
        }
      </div>
    </aside>
  )
}
