"""
BusEye Video Processor
Processes video files using YOLOv8 to detect road defects, vehicles, and incidents.
Sends detections to the backend API with GPS coordinates.
"""

import cv2
import time
import random
import requests
import argparse
import numpy as np
from datetime import datetime
from pathlib import Path

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARN] YOLOv8 not available. Running in simulation mode.")

BACKEND_URL = "http://localhost:8000"

# Map COCO class names → BusEye event types
CLASS_TO_EVENT = {
    # People
    "person": "pedestrian_alert",
    # Vehicles
    "car": "vehicle_count",
    "truck": "vehicle_count",
    "bus": "vehicle_count",
    "motorcycle": "vehicle_count",
    "bicycle": "vehicle_count",
    # Infrastructure
    "stop sign": "missing_signboard",
    "traffic light": "missing_signboard",
}

SEVERITY_MAP = {
    "pedestrian_alert": "high",
    "vehicle_count": "low",
    "missing_signboard": "high",
    "pothole": "high",
    "waterlogging": "critical",
}

# For demo: simulate GPS around Delhi
BASE_LAT = 28.6139
BASE_LNG = 77.2090


def get_simulated_gps(frame_num):
    """Generate a GPS coordinate that slowly moves along a route"""
    lat = BASE_LAT + (frame_num * 0.00005)
    lng = BASE_LNG + (frame_num * 0.00003)
    return round(lat, 6), round(lng, 6)


def send_detection(bus_id, event_type, lat, lng, confidence, description, plate=""):
    severity = SEVERITY_MAP.get(event_type, "medium")
    try:
        requests.post(f"{BACKEND_URL}/api/detections", json={
            "bus_id": bus_id,
            "event_type": event_type,
            "severity": severity,
            "latitude": lat,
            "longitude": lng,
            "confidence": round(confidence, 2),
            "description": description,
            "plate_number": plate
        }, timeout=3)
        print(f"  📡 [{bus_id}] {event_type.upper()} | conf={confidence:.2f} @ ({lat}, {lng})")
    except Exception as e:
        print(f"  [WARN] Backend not reachable: {e}")


def draw_overlay(frame, detections):
    """Draw detection boxes on video frame"""
    colors = {
        "pedestrian_alert": (0, 165, 255),
        "vehicle_count": (0, 255, 0),
        "pothole": (0, 0, 255),
        "waterlogging": (255, 0, 0),
        "missing_signboard": (255, 165, 0),
        "incident": (0, 0, 128),
    }

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = det["label"]
        conf = det["confidence"]
        color = colors.get(label, (128, 128, 128))

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        text = f"{label} {conf:.0%}"
        cv2.putText(frame, text, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    # BusEye watermark
    cv2.putText(frame, "🚌 BusEye AI", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    return frame


def process_video(video_path: str, bus_id: str = "BUS-DEMO", show_window: bool = True):
    """Main video processing function"""
    print(f"\n{'='*55}")
    print(f"  🎥 BusEye Video Processor")
    print(f"  Video : {video_path}")
    print(f"  Bus ID: {bus_id}")
    print(f"{'='*55}\n")

    # Load YOLO model
    if YOLO_AVAILABLE:
        print("  Loading YOLOv8n model...")
        model = YOLO("yolov8n.pt")  # downloads automatically first time
        print("  ✅ Model loaded!")
    else:
        model = None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  ❌ Cannot open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = 0
    detection_cooldown = {}  # throttle: don't spam same detection every frame

    print(f"  ▶️  Processing at {fps:.0f} FPS...\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("\n  ✅ Video ended. Looping...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0
            continue

        frame_count += 1
        lat, lng = get_simulated_gps(frame_count)
        detections_this_frame = []

        # ── Run YOLO detection ──────────────────────────────────────────────
        if model and frame_count % 3 == 0:  # process every 3rd frame for speed
            results = model(frame, verbose=False, conf=0.4)
            for result in results:
                for box in result.boxes:
                    cls_name = model.names[int(box.cls)]
                    conf = float(box.conf)
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]

                    event_type = CLASS_TO_EVENT.get(cls_name)
                    if event_type:
                        detections_this_frame.append({
                            "label": event_type,
                            "confidence": conf,
                            "bbox": (x1, y1, x2, y2)
                        })

                        # Throttle: send to backend at most once every 30 frames per type
                        last_sent = detection_cooldown.get(event_type, -999)
                        if frame_count - last_sent > 30:
                            send_detection(bus_id, event_type, lat, lng, conf,
                                           f"{cls_name} detected by AI")
                            detection_cooldown[event_type] = frame_count

        # ── Simulate pothole/waterlogging detections for demo ──────────────
        elif not model and frame_count % 45 == 0:
            simulated_events = [
                ("pothole", "Large pothole on road surface", 0.87),
                ("waterlogging", "Water accumulation detected", 0.79),
                ("missing_signboard", "Traffic sign damaged/missing", 0.83),
            ]
            event_type, desc, conf = random.choice(simulated_events)
            send_detection(bus_id, event_type, lat, lng, conf, desc)
            detections_this_frame.append({
                "label": event_type, "confidence": conf,
                "bbox": (100, 100, 400, 350)
            })

        # ── Draw overlay and show ──────────────────────────────────────────
        if show_window:
            annotated = draw_overlay(frame.copy(), detections_this_frame)
            cv2.imshow("BusEye - Live AI Feed", annotated)
            if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
                break

    cap.release()
    if show_window:
        cv2.destroyAllWindows()
    print("\n  🛑 Processing stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BusEye Video Processor")
    parser.add_argument("video", nargs="?", default="0", help="Video file path or 0 for webcam")
    parser.add_argument("--bus-id", default="BUS-DEMO", help="Bus identifier")
    parser.add_argument("--no-window", action="store_true", help="Run headless (no display)")
    args = parser.parse_args()

    video_source = args.video
    if video_source == "0":
        video_source = 0  # webcam

    process_video(str(video_source), args.bus_id, not args.no_window)
