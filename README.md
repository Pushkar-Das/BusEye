# BusEye 🚌 — Urban Intelligence Platform

**Smart India Hackathon 2026 | Team Nexus Optimizers**

An AI-powered onboard and centralized software platform that transforms public transport buses into mobile urban sensing units.

---

## 🚀 What It Does

BusEye uses cameras mounted on city buses to automatically detect and report:
- 🕳️ **Potholes & road defects**
- 🚧 **Missing signboards & zebra crossings**
- 🚨 **Hit-and-run & rash driving** (with License Plate capture via EasyOCR)
- 🚗 **Traffic congestion**
- 💧 **Waterlogging**

All detections are sent to a real-time GIS dashboard accessible by city authorities.

---

## 🏗️ Architecture

```
[Bus Cameras] → [Edge AI: YOLOv8 + EasyOCR] → [Local SQLite (Store & Forward)]
                                                          ↓
                                              [FastAPI REST API (Cloud)]
                                              ↙              ↘
                                    [AWS S3 Images]    [AWS S3 Metadata]
                                              ↓
                              [Streamlit Dashboard + Folium Maps]
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Edge AI | YOLOv8, EasyOCR, OpenCV |
| Backend | FastAPI, SQLite (edge cache) |
| Cloud Storage | AWS S3 (dual buckets) |
| Frontend | Streamlit, Folium |
| Styling | Custom HTML/CSS/JS |

---

## ⚙️ How to Run

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

### 2. Dashboard
```bash
cd dashboard
# (activate the same venv)
streamlit run app.py
```

### 3. Environment Variables (AWS S3 — Optional)
Create a `.env` file in the `backend/` folder:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
S3_BUCKET_NAME=buseye-evidence
```

> ⚠️ The dashboard works without AWS S3 — detections are stored in SQLite locally.

---

## 👥 Team Nexus Optimizers
Smart India Hackathon 2026
