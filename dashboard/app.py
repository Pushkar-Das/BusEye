"""
BusEye — Urban Intelligence Platform
Streamlit Dashboard with Folium GIS Maps + AWS S3 Evidence Storage
Team Nexus Optimizers | Smart India Hackathon 2026
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MiniMap, Fullscreen
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BusEye — Urban Intelligence",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "BusEye | Team Nexus Optimizers | SIH 2026"}
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & Base ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #070d1a !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080e1e 0%, #0a1128 100%) !important;
    border-right: 1px solid #1a2744 !important;
    min-width: 250px !important;
    max-width: 250px !important;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] hr { border-color: #1a2744 !important; opacity: 1 !important; }

/* Nav radio buttons */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
/* Hide the 'nav' label text */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] .stRadio > label {
    display: none !important;
}
section[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    cursor: pointer;
    transition: all 0.2s !important;
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #1e3a5f22 !important;
    color: #e2e8f0 !important;
}


/* ── Typography ───────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 { color: #f8fafc !important; font-family: 'Inter', sans-serif !important; }
p, li { color: #94a3b8 !important; }
.stMarkdown p { color: #94a3b8 !important; }
label { color: #64748b !important; }

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr { border-color: #1e293b !important; margin: 1rem 0 !important; }

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #4f46e5 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    font-size: 0.84rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(79,70,229,0.45) !important;
}

/* ── Select / Multiselect ─────────────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── DataFrames ───────────────────────────────────────────────────────────── */
.stDataFrame {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
.stDataFrame thead th {
    background: #0a0f1e !important;
    color: #64748b !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
.stDataFrame tbody td { color: #cbd5e1 !important; font-size: 0.83rem !important; }

/* ── Streamlit chrome ─────────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }

/* ── Section container ────────────────────────────────────────────────────── */
.section-box {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2d4f7c; }
</style>
""", unsafe_allow_html=True)


# ─── Utility: Custom metric card ─────────────────────────────────────────────
def metric_card(label, value, icon, color, sub=""):
    sub_html = f'<div style="font-size:0.7rem;color:#475569;margin-top:6px">{sub}</div>' if sub else ''
    # NOTE: No leading spaces — Streamlit markdown treats indented HTML as code blocks
    return (
        f'<div style="background:linear-gradient(145deg,{color}0d,#0f172a);border:1px solid {color}30;border-radius:16px;padding:20px 20px 16px;position:relative;overflow:hidden;height:100%;">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{color},{color}55);border-radius:16px 16px 0 0"></div>'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        f'<div style="flex:1">'
        f'<div style="font-size:0.65rem;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">{label}</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#f8fafc;line-height:1">{value}</div>'
        f'{sub_html}'
        f'</div>'
        f'<div style="background:{color}18;border-radius:12px;padding:10px 11px;font-size:1.3rem;flex-shrink:0;margin-left:12px;border:1px solid {color}25">{icon}</div>'
        f'</div>'
        f'</div>'
    )


# ─── Utility: Page header ─────────────────────────────────────────────────────
def page_header(title, subtitle, icon=""):
    # If icon is an SVG, render it natively, else treat as emoji
    icon_html = icon if "<svg" in icon else f'<span style="margin-right:8px">{icon}</span>'
    st.markdown(f"""
    <div style="margin-bottom:24px">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
            <div style="display:flex;align-items:center;justify-content:center;color:#f8fafc;width:28px;height:28px">
                {icon_html}
            </div>
            <div style="font-size:1.75rem;font-weight:800;color:#f8fafc;
                background:linear-gradient(135deg,#f8fafc,#94a3b8);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                letter-spacing:-0.02em">{title}</div>
        </div>
        <div style="font-size:0.82rem;color:#475569;margin-top:2px">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Utility: Section card wrapper ───────────────────────────────────────────
def section_header(text, color="#3b82f6"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:4px 0 14px">
        <div style="width:3px;height:18px;background:{color};border-radius:2px"></div>
        <span style="font-size:0.82rem;font-weight:700;color:#94a3b8;
            text-transform:uppercase;letter-spacing:0.08em">{text}</span>
    </div>""", unsafe_allow_html=True)


# ─── Data Fetching ───────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def fetch(endpoint, params=None):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=3)
        return r.json()
    except Exception:
        return None

def backend_online():
    try:
        requests.get(f"{API_URL}/api/stats/summary", timeout=2)
        return True
    except Exception:
        return False

def s3_status():
    try:
        r = requests.get(f"{API_URL}/api/storage/status", timeout=2)
        return r.json()
    except Exception:
        return {"connected": False}


# ─── Demo Data ────────────────────────────────────────────────────────────────
def demo_data():
    random.seed(99)
    base_lat, base_lng = 28.6139, 77.2090
    templates = [
        ("pothole",           "high",     "Large pothole detected on road surface"),
        ("pothole",           "medium",   "Minor road surface crack detected"),
        ("traffic_congestion","high",     "Heavy traffic — 50+ vehicles counted"),
        ("traffic_congestion","medium",   "Moderate traffic buildup at junction"),
        ("pedestrian_alert",  "high",     "School children crossing — no guard present"),
        ("missing_signboard", "high",     "Traffic signboard missing or damaged"),
        ("waterlogging",      "critical", "Road waterlogged — 15 cm depth estimated"),
        ("missing_zebra",     "medium",   "Zebra crossing faded or missing"),
        ("hit_and_run",       "critical", "Vehicle fled scene after collision"),
        ("rash_driving",      "high",     "Dangerous overtaking detected"),
        ("missing_divider",   "medium",   "Road divider section damaged"),
    ]
    plates = ["DL3CAB1234", "MH12AB5678", "KA01MC9999", "UP32GH7654", "TN09XZ2345"]
    dets = []
    for i in range(160):
        t = templates[i % len(templates)]
        plate = random.choice(plates) if t[0] in ("hit_and_run", "rash_driving") else ""
        dets.append({
            "id": i + 1,
            "bus_id": f"BUS-00{(i % 5) + 1}",
            "event_type": t[0], "severity": t[1], "description": t[2],
            "latitude":  base_lat + (random.random() - 0.5) * 0.15,
            "longitude": base_lng + (random.random() - 0.5) * 0.15,
            "confidence": round(random.uniform(0.72, 0.98), 2),
            "plate_number": plate,
            "timestamp": (datetime.now() - timedelta(hours=random.random() * 23)).isoformat(),
            "image_path": ""
        })
    buses = [
        {"bus_id": "BUS-001", "latitude": 28.6315, "longitude": 77.2167, "speed": 32, "route": "Route 401 — CP → India Gate"},
        {"bus_id": "BUS-002", "latitude": 28.5700, "longitude": 77.2373, "speed": 28, "route": "Route 502 — Lajpat Nagar → AIIMS"},
        {"bus_id": "BUS-003", "latitude": 28.6680, "longitude": 77.2285, "speed": 41, "route": "Route 603 — Kashmere Gate → Red Fort"},
        {"bus_id": "BUS-004", "latitude": 28.5921, "longitude": 77.0460, "speed": 19, "route": "Route 704 — Dwarka → Janakpuri"},
        {"bus_id": "BUS-005", "latitude": 28.7350, "longitude": 77.1130, "speed": 35, "route": "Route 805 — Rohini → Pitampura"},
    ]
    stats = {
        "total_events_24h": 347, "critical_alerts": 12,
        "potholes_detected": 89, "incidents_today": 4,
        "active_buses": 5, "km_roads_scanned": 226.5,
        "event_breakdown": [
            {"type": "pothole",           "count": 89},
            {"type": "traffic_congestion","count": 124},
            {"type": "pedestrian_alert",  "count": 67},
            {"type": "missing_signboard", "count": 38},
            {"type": "waterlogging",      "count": 25},
            {"type": "hit_and_run",       "count": 4},
        ]
    }
    hourly = [
        {"hour": f"{h:02d}:00",
         "events": int(5 + random.random()*20 + (40 if 8<=h<=10 else 0) + (35 if 17<=h<=19 else 0))}
        for h in range(24)
    ]
    return stats, dets, buses, hourly


# ─── Folium Map Builder ───────────────────────────────────────────────────────
EVENT_CFG = {
    "pothole":            ("#ef4444", "🕳️"),
    "traffic_congestion": ("#f59e0b", "🚗"),
    "pedestrian_alert":   ("#8b5cf6", "🚸"),
    "missing_signboard":  ("#ec4899", "🚧"),
    "waterlogging":       ("#06b6d4", "💧"),
    "missing_zebra":      ("#f97316", "🦓"),
    "missing_divider":    ("#84cc16", "🛡️"),
    "hit_and_run":        ("#dc2626", "🚨"),
    "rash_driving":       ("#b91c1c", "⚠️"),
    "vehicle_count":      ("#3b82f6", "📊"),
}
SEV_RADIUS = {"critical": 80, "high": 55, "medium": 35, "low": 20}
SEV_COLOR  = {"critical": "#dc2626", "high": "#f59e0b", "medium": "#3b82f6", "low": "#10b981"}


def build_folium_map(detections, buses):
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=12, tiles=None)

    # Free dark tiles — ESRI World Dark Gray Canvas (no API key required)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ",
        name="Dark Map",
        max_zoom=16
    ).add_to(m)

    groups = {
        "buses":      folium.FeatureGroup(name="🚌 Active Buses",        show=True),
        "pothole":    folium.FeatureGroup(name="🕳️ Potholes",            show=True),
        "traffic":    folium.FeatureGroup(name="🚗 Traffic Congestion",   show=True),
        "incident":   folium.FeatureGroup(name="🚨 Incidents",            show=True),
        "hazard":     folium.FeatureGroup(name="⚠️ Road Hazards",         show=True),
        "pedestrian": folium.FeatureGroup(name="🚸 Pedestrian Alerts",    show=True),
    }

    for b in buses:
        popup_html = f"""<div style='font-family:Inter,sans-serif;min-width:190px;font-size:13px;padding:4px'>
          <b style='color:#3b82f6;font-size:14px'>🚌 {b['bus_id']}</b><br>
          <span style='color:#666;font-size:12px'>{b.get('route','')}</span><br><br>
          <b>Speed:</b> {b.get('speed',0)} km/h &nbsp; <b>Status:</b>
          <span style='color:#10b981'>● Active</span></div>"""
        icon = folium.DivIcon(
            html=f"""<div style="background:linear-gradient(135deg,#1d4ed8,#4f46e5);color:white;
                border-radius:20px;padding:5px 12px;font-size:11px;font-weight:700;
                white-space:nowrap;border:2px solid #60a5fa;
                box-shadow:0 4px 12px rgba(59,130,246,0.5);font-family:sans-serif;
                letter-spacing:0.02em">🚌 {b['bus_id']}</div>""",
            icon_size=(110, 30), icon_anchor=(55, 15)
        )
        folium.Marker([b["latitude"], b["longitude"]], icon=icon,
                      popup=folium.Popup(popup_html, max_width=240),
                      tooltip=f"🚌 {b['bus_id']} — {b.get('speed',0)} km/h").add_to(groups["buses"])

    type_to_group = {
        "pothole": "pothole", "traffic_congestion": "traffic",
        "hit_and_run": "incident", "rash_driving": "incident",
        "pedestrian_alert": "pedestrian",
        "missing_signboard": "hazard", "waterlogging": "hazard",
        "missing_zebra": "hazard", "missing_divider": "hazard",
    }

    for d in detections[:250]:
        color, emoji = EVENT_CFG.get(d["event_type"], ("#64748b", "📍"))
        radius = SEV_RADIUS.get(d["severity"], 30)
        sc = SEV_COLOR.get(d["severity"], "#64748b")
        gname = type_to_group.get(d["event_type"], "hazard")
        ts = d.get("timestamp", "")[:19].replace("T", " ")
        plate_html = f"<br><b style='color:#ef4444'>🚗 Plate: {d['plate_number']}</b>" if d.get("plate_number") else ""

        popup_html = f"""<div style='font-family:Inter,sans-serif;min-width:220px;font-size:13px;padding:4px'>
          <b style='font-size:14px'>{emoji} {d['event_type'].replace('_',' ').title()}</b>
          <span style='background:{sc}20;color:{sc};padding:1px 7px;border-radius:4px;
                font-size:10px;font-weight:700;margin-left:6px'>{d['severity'].upper()}</span><br>
          <span style='color:#555;font-size:12px'>{d.get('description','')}</span><br>
          <b>Bus:</b> {d.get('bus_id','')} &nbsp; <b>Conf:</b> {int(d.get('confidence',0)*100)}%
          {plate_html}<br><span style='color:#999;font-size:11px'>{ts}</span></div>"""

        folium.Circle([d["latitude"], d["longitude"]], radius=radius,
                      color=color, fill=True, fill_color=color,
                      fill_opacity=0.12, weight=1).add_to(groups[gname])
        folium.Marker([d["latitude"], d["longitude"]],
            icon=folium.DivIcon(
                html=f"""<div style="background:{color};border-radius:50%;width:26px;height:26px;
                    display:flex;align-items:center;justify-content:center;font-size:13px;
                    border:2px solid rgba(255,255,255,0.8);
                    box-shadow:0 2px 8px {color}88;">{emoji}</div>""",
                icon_size=(26, 26), icon_anchor=(13, 13)),
            popup=folium.Popup(popup_html, max_width=270),
            tooltip=f"{emoji} {d['event_type'].replace('_',' ').title()} | {d['severity']}"
        ).add_to(groups[gname])

    heat_data = [[d["latitude"], d["longitude"]] for d in detections]
    if heat_data:
        HeatMap(heat_data, name="🔥 Congestion Heatmap", min_opacity=0.3,
                radius=22, blur=18,
                gradient={"0.4": "#3b82f6", "0.65": "#f59e0b", "1.0": "#ef4444"},
                show=False).add_to(m)

    for fg in groups.values():
        m.add_child(fg)

    MiniMap(toggle_display=True, position="bottomleft").add_to(m)
    Fullscreen(position="topright").add_to(m)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)
    return m


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:24px 16px 20px;text-align:center">
        <div style="display:inline-flex;align-items:center;justify-content:center;
            width:52px;height:52px;border-radius:16px;margin-bottom:12px;
            background:linear-gradient(135deg,#1d4ed8,#6366f1);
            box-shadow:0 8px 24px rgba(99,102,241,0.4);font-size:1.6rem">🚌</div>
        <div style="font-size:1.3rem;font-weight:800;color:#f8fafc;letter-spacing:-0.02em">BusEye</div>
        <div style="font-size:0.7rem;color:#334155;margin-top:3px;font-weight:500;
            letter-spacing:0.05em;text-transform:uppercase">Urban Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio("", [
        "🏙️  Dashboard",
        "🗺️  Live Map",
        "🚨  Incidents",
        "📊  Analytics",
        "☁️  S3 Storage",
    ], label_visibility="collapsed")

    st.divider()

    # Status indicators
    online = backend_online()
    if online:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;
            background:#052e16;border:1px solid #14532d;border-radius:8px;margin-bottom:8px">
            <div style="width:8px;height:8px;border-radius:50%;background:#22c55e;
                box-shadow:0 0 6px #22c55e"></div>
            <span style="font-size:0.78rem;color:#86efac;font-weight:600">Backend Connected</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;
            background:#1c1205;border:1px solid #422006;border-radius:8px;margin-bottom:8px">
            <div style="width:8px;height:8px;border-radius:50%;background:#f59e0b"></div>
            <span style="font-size:0.78rem;color:#fcd34d;font-weight:600">Demo Mode</span>
        </div>""", unsafe_allow_html=True)

    s3 = s3_status()
    if s3.get("connected"):
        st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;
            background:#052e16;border:1px solid #14532d;border-radius:8px">
            <span style="font-size:0.78rem;color:#86efac;font-weight:600">☁️ S3 Active</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;
            background:#0c1a2e;border:1px solid #1e3a5f;border-radius:8px">
            <span style="font-size:0.78rem;color:#60a5fa;font-weight:500">☁️ S3: Add .env keys</span>
        </div>""", unsafe_allow_html=True)

    st.divider()

    if st.button("🔄  Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:16px;padding-top:16px;border-top:1px solid #1a2744">
        <div style="font-size:0.68rem;color:#1e3a5f;font-weight:600;letter-spacing:0.05em">
            SMART INDIA HACKATHON 2026
        </div>
        <div style="font-size:0.65rem;color:#1e3a5f;margin-top:2px">Team Nexus Optimizers</div>
    </div>""", unsafe_allow_html=True)


# ─── Load Data ────────────────────────────────────────────────────────────────
raw_stats  = fetch("/api/stats/summary")
raw_dets   = fetch("/api/detections", {"hours": 24, "limit": 400})
raw_buses  = fetch("/api/buses")
raw_inc    = fetch("/api/incidents")
raw_hourly = fetch("/api/stats/hourly")

_demo_stats, _demo_dets, _demo_buses, _demo_hourly = demo_data()
stats     = raw_stats   or _demo_stats
dets      = raw_dets    or _demo_dets
buses     = raw_buses   or _demo_buses
hourly    = raw_hourly  or _demo_hourly
incidents = raw_inc     or [d for d in _demo_dets if d["event_type"] in ("hit_and_run", "rash_driving")]

SEV_EMOJI  = {"critical": "🔴", "high": "🟠", "medium": "🔵", "low": "🟢"}
SEV_BORDER = {"critical": "#dc2626", "high": "#f59e0b", "medium": "#3b82f6", "low": "#10b981"}

# Plotly dark theme shared config
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#111827", plot_bgcolor="#0a0f1e",
    font=dict(color="#64748b", family="Inter, sans-serif"),
    margin=dict(l=12, r=12, t=12, b=12),
    height=270,
    xaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", tickfont=dict(color="#475569", size=11)),
    yaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", tickfont=dict(color="#475569", size=11)),
)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ▶ DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏙️  Dashboard":
    header_svg = '<svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>'
    page_header("Urban Intelligence Dashboard",
                "Real-time city monitoring through the public bus fleet · Updates every 30s", header_svg)

    # ── Metric Cards ─────────────────────────────────────────────────────────
    # Lucide SVGs for metric cards
    ic_activity = '<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
    ic_alert = '<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
    ic_pin = '<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>'
    ic_trend = '<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
    ic_bus = '<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><path d="M2 17h20"></path><path d="M6 17v2"></path><path d="M18 17v2"></path><path d="M2 9h20"></path></svg>'
    ic_nav = '<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"></polygon></svg>'

    cols = st.columns(6)
    cards = [
        ("Events (24h)",    f"{stats['total_events_24h']:,}", ic_activity, "#3b82f6", "All detection types"),
        ("Critical Alerts", str(stats['critical_alerts']),    ic_alert,    "#ef4444", "Needs immediate action"),
        ("Potholes Found",  str(stats['potholes_detected']),  ic_pin,      "#f59e0b", "Road defects mapped"),
        ("Incidents",       str(stats['incidents_today']),    ic_trend,    "#8b5cf6", "Hit-and-run / rash drive"),
        ("Active Buses",    str(stats['active_buses']),       ic_bus,      "#10b981", "Fleet deployed"),
        ("Roads Scanned",   f"{stats['km_roads_scanned']} km",ic_nav,      "#06b6d4", "Today's coverage"),
    ]
    for col, (label, value, icon, color, sub) in zip(cols, cards):
        with col:
            st.markdown(metric_card(label, value, icon, color, sub), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Map + Alerts ──────────────────────────────────────────────────────────
    map_col, alert_col = st.columns([2.3, 1.2], gap="large")

    with map_col:
        st.markdown("""<div style="background:#111827;border:1px solid #1e293b;
            border-radius:16px;overflow:hidden">
            <div style="padding:14px 18px;border-bottom:1px solid #1e293b;
                display:flex;align-items:center;gap:10px">
                <div style="width:8px;height:8px;border-radius:50%;background:#22c55e;
                    box-shadow:0 0 8px #22c55e;animation:pulse 2s infinite"></div>
                <span style="font-size:0.82rem;font-weight:700;color:#e2e8f0">Live Detection Map</span>
                <span style="margin-left:auto;font-size:0.72rem;color:#334155">
                    Toggle layers · Click markers for details</span>
            </div>""", unsafe_allow_html=True)
        m = build_folium_map(dets, buses)
        # Fix: use_container_width instead of width=None keeps the flex layout strict
        st_folium(m, use_container_width=True, height=430, returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)

    with alert_col:
        total_alerts = len(dets)
        
        # Build the entire HTML block without leading spaces (otherwise markdown thinks it's a code block)
        html_str = (
            '<div style="background:#111827;border:1px solid #1e293b;border-radius:16px;overflow:hidden;">'
            '<div style="padding:14px 18px;border-bottom:1px solid #1e293b;display:flex;align-items:center;gap:10px">'
            '<span style="font-size:0.82rem;font-weight:700;color:#e2e8f0">🔔 Live Alerts</span>'
            f'<span style="margin-left:auto;background:#ef444420;color:#ef4444;border-radius:20px;padding:1px 8px;font-size:0.7rem;font-weight:700">{total_alerts}</span>'
            '</div>'
            '<div style="padding:12px;height:430px;overflow-y:auto;background:#111827;">'
        )

        recent = sorted(dets, key=lambda x: x.get("timestamp",""), reverse=True)[:30]
        
        # Mapping emoji specific to the reference image style
        ALT_EMOJI = {
            "pothole": "🕳️", "traffic_congestion": "🚗", "pedestrian_alert": "🚸", 
            "missing_signboard": "🚧", "waterlogging": "💧", "missing_zebra": "🦓",
            "missing_divider": "🛡️", "hit_and_run": "🚨", "rash_driving": "⚠️"
        }
        
        for a in recent:
            sev   = a.get("severity", "medium")
            etype = a.get("event_type", "").replace("_", " ").title()
            ts    = a.get("timestamp","")[:16].replace("T", " ")
            desc  = a.get("description", "")
            busid = a.get("bus_id","")
            plate = a.get("plate_number","")
            
            sev_color = SEV_BORDER.get(sev, "#3b82f6")
            icon = ALT_EMOJI.get(a.get("event_type"), "📍")
            
            if plate:
                desc = f"<b style='color:#ef4444'>[{plate}]</b> {desc}"
                
            # No leading spaces in HTML chunks!
            html_str += (
                f'<div style="background:#151e32;border:1px solid #1e293b;border-radius:10px;padding:12px;margin-bottom:10px;display:flex;align-items:center;gap:12px;font-family:sans-serif;">'
                f'<div style="background:#1e293b;padding:8px 10px;border-radius:8px;font-size:1.1rem;display:flex;align-items:center;justify-content:center;">{icon}</div>'
                f'<div style="flex:1;">'
                f'<div style="font-size:0.8rem;font-weight:700;color:#f8fafc;line-height:1.2">{etype}</div>'
                f'<div style="font-size:0.7rem;color:#64748b;margin-top:3px;line-height:1.3">{desc}</div>'
                f'<div style="font-size:0.65rem;color:#475569;margin-top:5px;font-weight:600">🚌 {busid} &middot; {ts}</div>'
                f'</div>'
                f'<div style="font-size:0.65rem;font-weight:800;color:{sev_color};text-transform:uppercase;letter-spacing:0.05em;align-self:flex-start;padding-top:4px;">{sev}</div>'
                f'</div>'
            )

        html_str += "</div></div>"
        st.markdown(html_str, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ▶ LIVE MAP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️  Live Map":
    page_header("Live GIS Map", "Interactive map with toggleable layers · Heatmap available via layer control", "🗺️")

    # Filter bar
    st.markdown("""<div style="background:#111827;border:1px solid #1e293b;
        border-radius:12px;padding:14px 18px;margin-bottom:16px">""", unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        ftype = st.selectbox("Event type", [
            "All Events", "Pothole", "Traffic Congestion", "Waterlogging",
            "Hit And Run", "Rash Driving", "Pedestrian Alert"
        ])
    with fc2:
        fsev = st.multiselect("Severity", ["critical","high","medium","low"],
                              default=["critical","high","medium","low"])
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        ftype_key = ftype.lower().replace(" ", "_")
        fd = [d for d in dets if d["severity"] in fsev and
              (ftype_key == "all_events" or d["event_type"] == ftype_key)]
        st.markdown(f"""<div style="background:#0d1626;border:1px solid #1e293b;border-radius:10px;
            padding:10px 14px;text-align:center">
            <div style="font-size:1.4rem;font-weight:800;color:#3b82f6">{len(fd)}</div>
            <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;
                letter-spacing:0.05em">Events</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""<div style="background:#111827;border:1px solid #1e293b;
        border-radius:16px;overflow:hidden">""", unsafe_allow_html=True)
    m2 = build_folium_map(fd, buses)
    map_data = st_folium(m2, width=None, height=580, returned_objects=["last_object_clicked"])
    st.markdown("</div>", unsafe_allow_html=True)

    if map_data and map_data.get("last_object_clicked"):
        clicked = map_data["last_object_clicked"]
        st.markdown(f"""<div style="margin-top:10px;background:#111827;border:1px solid #1e3a5f;
            border-radius:10px;padding:10px 16px;font-size:0.82rem;color:#60a5fa">
            📍 Clicked: <b>{clicked.get('lat',0):.5f}°N, {clicked.get('lng',0):.5f}°E</b>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ▶ INCIDENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🚨  Incidents":
    page_header("Incident Report",
                "Hit-and-run & rash driving — license plates captured by EasyOCR · Evidence stored on AWS S3", "🚨")

    if not incidents:
        st.markdown("""<div style="background:#111827;border:1px solid #1e293b;border-radius:16px;
            padding:60px;text-align:center;color:#334155">
            <div style="font-size:2.5rem;margin-bottom:12px">🚨</div>
            <div style="font-size:0.9rem;font-weight:600">No incidents recorded yet</div>
            <div style="font-size:0.78rem;margin-top:4px">Incidents will appear here as AI detects them</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Summary metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(metric_card("Total Incidents", len(incidents), "🚨", "#ef4444"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Plates Captured", len([i for i in incidents if i.get("plate_number")]), "🔍", "#8b5cf6"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("Critical", len([i for i in incidents if i["severity"]=="critical"]), "🔴", "#dc2626"), unsafe_allow_html=True)
        with c4: st.markdown(metric_card("S3 Evidence", len([i for i in incidents if i.get("image_path")]), "☁️", "#06b6d4"), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        for inc in incidents:
            sev   = inc.get("severity","high")
            etype = inc.get("event_type","").replace("_"," ").title()
            plate = inc.get("plate_number","")
            conf  = int(inc.get("confidence",0.8)*100)
            ts    = inc.get("timestamp","")[:19].replace("T"," ")
            sc    = SEV_COLOR.get(sev,"#64748b")
            s3url = inc.get("image_path","")

            plate_html = (
                f'<span style="background:#0c1f3d;color:#60a5fa;border:1px solid #1d4ed8;'
                f'border-radius:6px;padding:3px 10px;font-size:0.82rem;font-weight:700;'
                f'font-family:monospace;letter-spacing:0.05em">{plate}</span>'
                if plate else '<span style="color:#334155;font-size:0.82rem">Not captured</span>'
            )
            s3_html = (
                f'<a href="{s3url}" target="_blank" style="color:#3b82f6;font-size:0.75rem;'
                f'text-decoration:none;border:1px solid #1e3a5f;padding:2px 8px;border-radius:5px">☁️ S3 Evidence</a>'
                if s3url
                else '<span style="color:#1e3a5f;font-size:0.75rem">☁️ No image</span>'
            )

            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e293b;border-left:4px solid {sc};
                border-radius:14px;padding:16px 20px;margin-bottom:12px">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <span style="font-size:1rem;font-weight:700;color:#f8fafc">🚨 {etype}</span>
                <span style="background:{sc}18;color:{sc};padding:3px 12px;border-radius:20px;
                    font-size:0.7rem;font-weight:700;letter-spacing:0.06em">{sev.upper()}</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px">
                <div>
                  <div style="font-size:0.62rem;color:#334155;font-weight:700;
                      text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">License Plate</div>
                  {plate_html}
                </div>
                <div>
                  <div style="font-size:0.62rem;color:#334155;font-weight:700;
                      text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">Bus ID</div>
                  <span style="color:#94a3b8;font-size:0.85rem;font-weight:600">{inc.get('bus_id','')}</span>
                </div>
                <div>
                  <div style="font-size:0.62rem;color:#334155;font-weight:700;
                      text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">AI Confidence</div>
                  <div style="background:#0a0f1e;border-radius:6px;height:6px;margin-bottom:4px">
                    <div style="background:linear-gradient(90deg,#10b981,#06b6d4);
                        width:{conf}%;height:6px;border-radius:6px"></div>
                  </div>
                  <span style="color:#64748b;font-size:0.75rem">{conf}%</span>
                </div>
                <div>
                  <div style="font-size:0.62rem;color:#334155;font-weight:700;
                      text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">Timestamp</div>
                  <span style="color:#64748b;font-size:0.78rem">{ts}</span>
                </div>
              </div>
              <div style="margin-top:12px;padding-top:12px;border-top:1px solid #1e293b;
                  display:flex;gap:16px;align-items:center">
                <span style="color:#334155;font-size:0.75rem">
                    📍 {inc.get('latitude',0):.4f}°N, {inc.get('longitude',0):.4f}°E</span>
                {s3_html}
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        section_header("Incident Locations on Map")
        st.markdown("""<div style="background:#111827;border:1px solid #1e293b;
            border-radius:16px;overflow:hidden">""", unsafe_allow_html=True)
        inc_map = build_folium_map(incidents, buses)
        st_folium(inc_map, width=None, height=380, returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ▶ ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Analytics":
    page_header("Traffic Analytics", "Patterns, trends and congestion insights from the bus fleet", "📊")

    c1, c2 = st.columns(2, gap="medium")

    with c1:
        section_header("Events Over 24 Hours", "#3b82f6")
        df_h = pd.DataFrame(hourly)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_h["hour"], y=df_h["events"],
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
            line=dict(color="#3b82f6", width=2.5),
            name="Events"
        ))
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        section_header("Event Type Breakdown", "#6366f1")
        df_ev = pd.DataFrame(stats.get("event_breakdown",[]))
        if not df_ev.empty:
            df_ev["type"] = df_ev["type"].str.replace("_"," ").str.title()
            colors = ["#3b82f6","#6366f1","#8b5cf6","#ec4899","#f59e0b","#10b981","#06b6d4"]
            fig2 = go.Figure(go.Bar(
                x=df_ev["count"], y=df_ev["type"], orientation="h",
                marker=dict(
                    color=colors[:len(df_ev)],
                    cornerradius=5
                )
            ))
            fig2.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    c3, c4 = st.columns(2, gap="medium")

    with c3:
        section_header("Road Defect Distribution", "#f59e0b")
        defect_keys = ["pothole","waterlogging","missing_signboard","missing_zebra","missing_divider"]
        dc = {}
        for d in dets:
            if d["event_type"] in defect_keys:
                dc[d["event_type"]] = dc.get(d["event_type"], 0) + 1
        if dc:
            colors_pie = ["#ef4444","#06b6d4","#ec4899","#f97316","#84cc16"]
            fig3 = go.Figure(go.Pie(
                labels=[k.replace("_"," ").title() for k in dc],
                values=list(dc.values()),
                hole=0.55,
                marker=dict(colors=colors_pie, line=dict(color="#070d1a", width=2))
            ))
            fig3.update_layout(**PLOTLY_LAYOUT)
            fig3.update_traces(textfont_color="#94a3b8")
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with c4:
        section_header("Alerts by Severity", "#ef4444")
        sc_counts = {}
        for d in dets:
            sc_counts[d["severity"]] = sc_counts.get(d["severity"], 0) + 1
        order = ["critical","high","medium","low"]
        bar_x = [s.capitalize() for s in order if s in sc_counts]
        bar_y = [sc_counts[s] for s in order if s in sc_counts]
        bar_c = ["#dc2626","#f59e0b","#3b82f6","#10b981"][:len(bar_x)]
        fig4 = go.Figure(go.Bar(
            x=bar_x, y=bar_y,
            marker=dict(color=bar_c, cornerradius=5)
        ))
        fig4.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    # Fleet table
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Bus Fleet Performance", "#10b981")
    bus_stats = {}
    for d in dets:
        bid = d["bus_id"]
        if bid not in bus_stats:
            bus_stats[bid] = {"Detections": 0, "Critical": 0, "Incidents": 0}
        bus_stats[bid]["Detections"] += 1
        if d["severity"] == "critical": bus_stats[bid]["Critical"] += 1
        if d["event_type"] in ("hit_and_run","rash_driving"): bus_stats[bid]["Incidents"] += 1
    df_bus = pd.DataFrame([{"Bus ID":k,**v} for k,v in bus_stats.items()])
    st.dataframe(df_bus, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ▶ S3 STORAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "☁️  S3 Storage":
    page_header("AWS S3 Evidence Storage",
                "Detection frame images uploaded by the AI engine are stored securely in AWS S3", "☁️")

    s3_info = s3_status()
    if s3_info.get("connected"):
        st.markdown(f"""<div style="background:#052e16;border:1px solid #14532d;border-radius:12px;
            padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:12px">
            <div style="font-size:1.3rem">✅</div>
            <div>
                <div style="color:#86efac;font-weight:700;font-size:0.9rem">S3 Connected</div>
                <div style="color:#4ade80;font-size:0.78rem;margin-top:2px">
                    Bucket: <code>{s3_info.get('bucket')}</code> &nbsp;|&nbsp;
                    Region: <code>{s3_info.get('region')}</code></div>
            </div>
        </div>""", unsafe_allow_html=True)

        img_data = fetch("/api/storage/images", {"limit": 50})
        if img_data and img_data.get("images"):
            imgs = img_data["images"]
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(metric_card("Total Images", len(imgs), "🖼️", "#3b82f6"), unsafe_allow_html=True)
            with c2: st.markdown(metric_card("Storage Used", f"{sum(i.get('size_kb',0) for i in imgs):.0f} KB", "💾", "#10b981"), unsafe_allow_html=True)
            with c3: st.markdown(metric_card("Latest Upload", imgs[0].get("last_modified","")[:10] if imgs else "—", "⏱️", "#8b5cf6"), unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            df_imgs = pd.DataFrame(imgs)
            df_imgs["filename"] = df_imgs["key"].apply(lambda k: k.split("/")[-1])
            st.dataframe(
                df_imgs[["filename","size_kb","last_modified"]].rename(columns={
                    "filename":"Filename","size_kb":"Size (KB)","last_modified":"Uploaded At"
                }),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No images uploaded yet. Start the AI video processor to capture evidence.")
    else:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e293b;border-radius:16px;padding:32px 36px">
            <div style="font-size:1.5rem;margin-bottom:16px">☁️ Setup AWS S3</div>
        """, unsafe_allow_html=True)
        st.code("""# Step 1: Copy .env.example to .env
# Step 2: Fill in your AWS credentials:

AWS_ACCESS_KEY_ID     = your_key_here
AWS_SECRET_ACCESS_KEY = your_secret_here
AWS_REGION            = ap-south-1
AWS_BUCKET_NAME       = buseye-detections

# Step 3: Restart START_BACKEND.bat""", language="bash")
        st.markdown("""
        <div style="margin-top:16px;padding:12px 16px;background:#0c1f3d;border:1px solid #1e3a5f;
            border-radius:10px;font-size:0.82rem;color:#60a5fa">
            💡 <b>Demo note:</b> S3 is optional. Everything else (map, alerts, incidents, analytics)
            works perfectly without it.
        </div></div>""", unsafe_allow_html=True)
