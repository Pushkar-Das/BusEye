"""
BusEye GPS Simulator
Simulates 5 buses moving along realistic routes in Delhi/Mumbai.
Sends position updates to the backend API every 2 seconds.
"""

import time
import math
import random
import requests
import threading

BACKEND_URL = "http://localhost:8000"

# ── Realistic city routes (Delhi coordinates) ─────────────────────────────────
# Each route is a list of [lat, lng] waypoints

ROUTES = {
    "BUS-001": {
        "name": "Route 401 - Connaught Place → India Gate",
        "waypoints": [
            [28.6315, 77.2167],
            [28.6280, 77.2215],
            [28.6245, 77.2263],
            [28.6210, 77.2295],
            [28.6180, 77.2320],
            [28.6152, 77.2350],
        ],
        "color": "#3b82f6"
    },
    "BUS-002": {
        "name": "Route 502 - Lajpat Nagar → AIIMS",
        "waypoints": [
            [28.5700, 77.2373],
            [28.5680, 77.2320],
            [28.5655, 77.2270],
            [28.5630, 77.2210],
            [28.5610, 77.2090],
        ],
        "color": "#10b981"
    },
    "BUS-003": {
        "name": "Route 603 - Kashmere Gate → Red Fort",
        "waypoints": [
            [28.6680, 77.2285],
            [28.6650, 77.2340],
            [28.6620, 77.2395],
            [28.6595, 77.2430],
            [28.6575, 77.2410],
        ],
        "color": "#f59e0b"
    },
    "BUS-004": {
        "name": "Route 704 - Dwarka → Janakpuri",
        "waypoints": [
            [28.5921, 77.0460],
            [28.5940, 77.0520],
            [28.5960, 77.0600],
            [28.5975, 77.0680],
            [28.5990, 77.0750],
        ],
        "color": "#ef4444"
    },
    "BUS-005": {
        "name": "Route 805 - Rohini → Pitampura",
        "waypoints": [
            [28.7350, 77.1130],
            [28.7310, 77.1200],
            [28.7275, 77.1260],
            [28.7240, 77.1310],
            [28.7210, 77.1350],
        ],
        "color": "#8b5cf6"
    }
}

# Detection event templates
DETECTION_TEMPLATES = [
    {"event_type": "pothole", "severity": "high", "description": "Large pothole detected on road surface"},
    {"event_type": "pothole", "severity": "medium", "description": "Medium pothole - road maintenance required"},
    {"event_type": "pothole", "severity": "low", "description": "Minor road surface crack"},
    {"event_type": "traffic_congestion", "severity": "high", "description": "Heavy traffic detected - 45+ vehicles"},
    {"event_type": "traffic_congestion", "severity": "medium", "description": "Moderate traffic - 20-30 vehicles"},
    {"event_type": "missing_signboard", "severity": "high", "description": "Traffic signboard missing or damaged"},
    {"event_type": "missing_zebra", "severity": "medium", "description": "Zebra crossing faded/missing"},
    {"event_type": "waterlogging", "severity": "critical", "description": "Waterlogging detected - road partially submerged"},
    {"event_type": "pedestrian_alert", "severity": "high", "description": "School children crossing - no crossing guard"},
    {"event_type": "hit_and_run", "severity": "critical", "description": "Hit-and-run incident detected"},
    {"event_type": "rash_driving", "severity": "high", "description": "Rash driving behavior detected"},
    {"event_type": "missing_divider", "severity": "medium", "description": "Road divider missing or damaged"},
    {"event_type": "vehicle_count", "severity": "low", "description": "Traffic density measurement"},
]

INCIDENT_PLATES = ["DL3CAB1234", "MH12AB5678", "KA01MC9999", "UP32GH7654", "TN09XZ2345"]


def interpolate(p1, p2, t):
    """Smoothly interpolate between two GPS points"""
    return [
        p1[0] + (p2[0] - p1[0]) * t,
        p1[1] + (p2[1] - p1[1]) * t
    ]


def send_position(bus_id, lat, lng, route_name, speed):
    try:
        requests.post(f"{BACKEND_URL}/api/buses/position", json={
            "bus_id": bus_id,
            "latitude": lat,
            "longitude": lng,
            "speed": speed,
            "route": route_name,
            "status": "active"
        }, timeout=3)
    except Exception as e:
        print(f"  [WARN] Could not send position for {bus_id}: {e}")


def send_detection(bus_id, lat, lng, template, plate=""):
    try:
        confidence = round(random.uniform(0.72, 0.98), 2)
        payload = {
            "bus_id": bus_id,
            "event_type": template["event_type"],
            "severity": template["severity"],
            "latitude": lat + random.uniform(-0.002, 0.002),
            "longitude": lng + random.uniform(-0.002, 0.002),
            "confidence": confidence,
            "description": template["description"],
            "plate_number": plate
        }
        resp = requests.post(f"{BACKEND_URL}/api/detections", json=payload, timeout=3)
        if resp.status_code == 200:
            print(f"  ✅ [{bus_id}] {template['event_type'].upper()} @ ({lat:.4f}, {lng:.4f}) | conf={confidence}")
    except Exception as e:
        print(f"  [WARN] Could not send detection: {e}")


def run_bus(bus_id, route_info):
    """Continuously move a bus along its route and generate detections"""
    waypoints = route_info["waypoints"]
    route_name = route_info["name"]
    detection_counter = 0

    print(f"🚌 Starting {bus_id} on {route_name}")

    while True:
        # Forward pass
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]
            steps = 30  # smooth movement
            for step in range(steps):
                t = step / steps
                pos = interpolate(p1, p2, t)
                speed = round(random.uniform(18, 45), 1)
                send_position(bus_id, pos[0], pos[1], route_name, speed)

                detection_counter += 1
                # Send a detection every ~8-15 steps (random)
                if detection_counter % random.randint(8, 15) == 0:
                    template = random.choice(DETECTION_TEMPLATES)
                    plate = ""
                    if template["event_type"] in ["hit_and_run", "rash_driving"]:
                        plate = random.choice(INCIDENT_PLATES)
                    send_detection(bus_id, pos[0], pos[1], template, plate)

                time.sleep(2)

        # Reverse pass (bus goes back on same route)
        for i in range(len(waypoints) - 1, 0, -1):
            p1 = waypoints[i]
            p2 = waypoints[i - 1]
            steps = 30
            for step in range(steps):
                t = step / steps
                pos = interpolate(p1, p2, t)
                speed = round(random.uniform(18, 45), 1)
                send_position(bus_id, pos[0], pos[1], route_name, speed)
                time.sleep(2)


def main():
    print("=" * 55)
    print("  🚌 BusEye GPS Simulator Starting...")
    print("  📡 Backend:", BACKEND_URL)
    print("=" * 55)
    print()

    # Start all buses in separate threads
    threads = []
    for bus_id, route_info in ROUTES.items():
        t = threading.Thread(target=run_bus, args=(bus_id, route_info), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(1)  # Stagger start times

    print(f"\n✅ All {len(ROUTES)} buses deployed. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")


if __name__ == "__main__":
    main()
