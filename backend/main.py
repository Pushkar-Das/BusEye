from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

from database import get_db, init_db, DetectionEvent, BusPosition
from s3_handler import get_s3


app = FastAPI(title="BusEye API", version="1.0.0")

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for live alerts
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class DetectionCreate(BaseModel):
    bus_id: str
    event_type: str
    severity: str = "medium"
    latitude: float
    longitude: float
    confidence: float
    description: str = ""
    plate_number: str = ""

class BusPositionUpdate(BaseModel):
    bus_id: str
    latitude: float
    longitude: float
    speed: float = 0
    route: str = ""
    status: str = "active"


# ─── Startup ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    init_db()
    print("[OK] BusEye API started. Database ready.")


# ─── WebSocket for live dashboard ────────────────────────────────────────────

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─── Detection Events ─────────────────────────────────────────────────────────

@app.post("/api/detections")
async def create_detection(detection: DetectionCreate, db: Session = Depends(get_db)):
    """AI engine calls this to report a detection"""
    event = DetectionEvent(
        bus_id=detection.bus_id,
        event_type=detection.event_type,
        severity=detection.severity,
        latitude=detection.latitude,
        longitude=detection.longitude,
        confidence=detection.confidence,
        description=detection.description,
        plate_number=detection.plate_number,
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Broadcast to all connected dashboards
    await manager.broadcast({
        "type": "new_detection",
        "data": {
            "id": event.id,
            "bus_id": event.bus_id,
            "event_type": event.event_type,
            "severity": event.severity,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "confidence": event.confidence,
            "description": event.description,
            "plate_number": event.plate_number,
            "timestamp": event.timestamp.isoformat()
        }
    })

    return {"success": True, "id": event.id}


@app.get("/api/detections")
def get_detections(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24,
    limit: int = 500,
    db: Session = Depends(get_db)
):
    """Get recent detections with optional filters"""
    since = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(DetectionEvent).filter(DetectionEvent.timestamp >= since)

    if event_type:
        query = query.filter(DetectionEvent.event_type == event_type)
    if severity:
        query = query.filter(DetectionEvent.severity == severity)

    events = query.order_by(desc(DetectionEvent.timestamp)).limit(limit).all()

    return [
        {
            "id": e.id,
            "bus_id": e.bus_id,
            "event_type": e.event_type,
            "severity": e.severity,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "confidence": round(e.confidence, 2),
            "description": e.description,
            "plate_number": e.plate_number,
            "timestamp": e.timestamp.isoformat()
        }
        for e in events
    ]


@app.get("/api/detections/heatmap")
def get_heatmap_data(event_type: Optional[str] = None, db: Session = Depends(get_db)):
    """Get lat/lng points for heatmap rendering"""
    query = db.query(DetectionEvent.latitude, DetectionEvent.longitude, DetectionEvent.severity)
    if event_type:
        query = query.filter(DetectionEvent.event_type == event_type)
    rows = query.all()
    return [{"lat": r.latitude, "lng": r.longitude, "severity": r.severity} for r in rows]


@app.get("/api/incidents")
def get_incidents(db: Session = Depends(get_db)):
    """Get incident events (hit-and-run, rash driving)"""
    events = db.query(DetectionEvent).filter(
        DetectionEvent.event_type.in_(["incident", "hit_and_run", "rash_driving"])
    ).order_by(desc(DetectionEvent.timestamp)).limit(100).all()

    return [
        {
            "id": e.id,
            "bus_id": e.bus_id,
            "event_type": e.event_type,
            "severity": e.severity,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "confidence": round(e.confidence, 2),
            "plate_number": e.plate_number,
            "description": e.description,
            "timestamp": e.timestamp.isoformat()
        }
        for e in events
    ]


# ─── Bus Positions ────────────────────────────────────────────────────────────

@app.post("/api/buses/position")
async def update_bus_position(pos: BusPositionUpdate, db: Session = Depends(get_db)):
    """Update a bus's current GPS position"""
    bus = db.query(BusPosition).filter(BusPosition.bus_id == pos.bus_id).first()
    if bus:
        bus.latitude = pos.latitude
        bus.longitude = pos.longitude
        bus.speed = pos.speed
        bus.route = pos.route
        bus.status = pos.status
        bus.last_updated = datetime.utcnow()
    else:
        bus = BusPosition(
            bus_id=pos.bus_id,
            latitude=pos.latitude,
            longitude=pos.longitude,
            speed=pos.speed,
            route=pos.route,
            status=pos.status
        )
        db.add(bus)
    db.commit()

    # Broadcast bus position update
    await manager.broadcast({
        "type": "bus_position",
        "data": {
            "bus_id": pos.bus_id,
            "latitude": pos.latitude,
            "longitude": pos.longitude,
            "speed": pos.speed,
            "route": pos.route,
            "status": pos.status
        }
    })
    return {"success": True}


@app.get("/api/buses")
def get_buses(db: Session = Depends(get_db)):
    """Get all active bus positions"""
    buses = db.query(BusPosition).filter(BusPosition.status == "active").all()
    return [
        {
            "bus_id": b.bus_id,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "speed": b.speed,
            "route": b.route,
            "status": b.status,
            "last_updated": b.last_updated.isoformat()
        }
        for b in buses
    ]


# ─── Analytics ────────────────────────────────────────────────────────────────

@app.get("/api/stats/summary")
def get_summary(db: Session = Depends(get_db)):
    """Summary stats for dashboard cards"""
    today = datetime.utcnow() - timedelta(hours=24)

    total_events = db.query(DetectionEvent).filter(DetectionEvent.timestamp >= today).count()
    critical_events = db.query(DetectionEvent).filter(
        DetectionEvent.timestamp >= today,
        DetectionEvent.severity == "critical"
    ).count()
    potholes = db.query(DetectionEvent).filter(
        DetectionEvent.timestamp >= today,
        DetectionEvent.event_type == "pothole"
    ).count()
    incidents = db.query(DetectionEvent).filter(
        DetectionEvent.timestamp >= today,
        DetectionEvent.event_type.in_(["incident", "hit_and_run", "rash_driving"])
    ).count()
    active_buses = db.query(BusPosition).filter(BusPosition.status == "active").count()

    # Event breakdown
    event_counts = db.query(
        DetectionEvent.event_type,
        func.count(DetectionEvent.id).label("count")
    ).filter(DetectionEvent.timestamp >= today).group_by(DetectionEvent.event_type).all()

    return {
        "total_events_24h": total_events,
        "critical_alerts": critical_events,
        "potholes_detected": potholes,
        "incidents_today": incidents,
        "active_buses": active_buses,
        "km_roads_scanned": round(active_buses * 45.3, 1),
        "event_breakdown": [{"type": r.event_type, "count": r.count} for r in event_counts]
    }


@app.get("/api/stats/hourly")
def get_hourly_trend(db: Session = Depends(get_db)):
    """Hourly event count for trend chart"""
    results = []
    for h in range(23, -1, -1):
        start = datetime.utcnow() - timedelta(hours=h+1)
        end = datetime.utcnow() - timedelta(hours=h)
        count = db.query(DetectionEvent).filter(
            DetectionEvent.timestamp >= start,
            DetectionEvent.timestamp < end
        ).count()
        results.append({
            "hour": f"{(datetime.utcnow() - timedelta(hours=h)).strftime('%H:00')}",
            "events": count
        })
    return results


# ─── S3 Storage Endpoints ─────────────────────────────────────────────────────

@app.post("/api/detections/upload-image")
async def upload_detection_image(
    bus_id: str,
    event_type: str,
    detection_id: Optional[int] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a detection frame image to AWS S3.
    Called by the AI engine when it captures an incident frame.
    Returns the S3 URL stored against the detection record.
    """
    s3 = get_s3()

    if not s3.is_connected:
        return {"success": False, "message": "S3 not configured. Set AWS credentials in .env", "url": ""}

    # Read uploaded image bytes
    image_bytes = await file.read()

    # Upload to S3
    url = s3.upload_image(image_bytes, bus_id, event_type)

    if not url:
        raise HTTPException(status_code=500, detail="S3 upload failed")

    # Update the detection record with the S3 URL
    if detection_id:
        event = db.query(DetectionEvent).filter(DetectionEvent.id == detection_id).first()
        if event:
            event.image_path = url
            db.commit()

    return {"success": True, "url": url, "bus_id": bus_id, "event_type": event_type}


@app.get("/api/storage/images")
def list_s3_images(limit: int = 50):
    """List recently uploaded detection images from S3"""
    s3 = get_s3()
    if not s3.is_connected:
        return {"connected": False, "images": [], "message": "S3 not configured"}

    images = s3.list_recent_images(limit=limit)
    return {"connected": True, "images": images, "count": len(images)}


@app.get("/api/storage/status")
def s3_status():
    """Check if S3 connection is working"""
    s3 = get_s3()
    return {
        "connected": s3.is_connected,
        "bucket": s3.bucket,
        "region": s3.region,
        "message": "S3 connected and ready" if s3.is_connected else "S3 not configured — set AWS credentials in .env"
    }
