# 🛡️ SafeStack AI
### An AI-Powered Video Intelligence Assistant for Damage-Free Warehouse Loading & Unloading

---

## 📖 Abstract

Warehouses lose significant value each year to preventable product damage caused not by equipment failure but by unsafe or careless handling behavior of dropping, dragging, rough stacking, and improper use of pallets or lifting equipment. Traditional CCTV systems record these incidents but cannot prevent them; damage is discovered only after the fact. 

**SafeStack AI** reimagines the warehouse camera as an active safety and quality partner. By combining object detection, multi-frame tracking, action recognition, and temporal reasoning, the system observes loading-bay activity in real time, recognises a curated taxonomy of damage-causing behaviours, assigns each event a graded risk score, and surfaces the finding through a live dashboard and a conversational AI assistant that supervisors can query in plain language. The goal is a shift from damage detection to damage prevention, and from passive surveillance to responsible, explainable operational intelligence.

---

## 🚀 Key System Capabilities

1. **AI + Computer-Vision Pipeline**:
   - Ingests live RTSP or recorded warehouse footage.
   - Detects workers, cartons, pallets, and forklifts across frames using YOLOv11 & DeepSORT tracking.
2. **Custom Video File Injection Hub**:
   - Upload and inject your own custom warehouse video files (`.mp4`, `.avi`, `.mov`, `.mkv`) via the interactive dashboard or CLI (`scripts/inject_video.py`).
   - Streams your custom video live into any loading bay with real-time detection bounding boxes, kinematic tracking, and privacy shielding.
   - Runs full offline video scans to detect all damage incidents and populate the incident audit log.
   - Offline scans use actual configured model detections only. If no model is available, the scan reports that detections are unavailable instead of substituting demo boxes or fabricated incidents.
3. **Curated 10-Behavior Damage-Risk Taxonomy**:
   - Sequence-level action recognition over 30–60 frame sliding windows (dropping, dragging, improper stacking, unsafe pallet use, rough handling, tossing/throwing, stepping on cargo, overstacking, rolling, forklift pinch hazard).
4. **Graded Risk-Scoring Model (Low → Medium → High → Critical)**:
   - Dynamic formula combining Base Behavior Severity ($40\%$), Product Fragility Multiplier ($25\%$), Kinematic Impact Energy & Drop Height ($20\%$), and Shift Recurrence Frequency ($15\%$).
5. **Real-Time Alerting Dashboard (React.js + Chart.js)**:
   - Live loading bay feeds (Bays 1 to 4) with bounding box tracking HUD.
   - Graded color-coded alerts with audio chime notifications.
   - Interactive Chart.js analytics: hourly risk trends, behavior distribution, bay comparison, and Damage Prevention ROI Calculator.
6. **Conversational AI Assistant (Zero-Fabrication Guarantee)**:
   - Answers supervisor queries strictly from computer-vision telemetry evidence without hallucinations.
   - Supports Claude API, Gemini API, LangChain, and a deterministic offline RAG engine.
7. **Responsible-AI Safeguards**:
   - **Edge Privacy Shield**: Real-time face blurring and anonymous ergonomic silhouette rendering.
   - **Non-Punitive Culture**: Measures handling physics and dock bottlenecks rather than penalizing individuals.
   - **Role-Based Access Control (RBAC)**: Distinct views for Warehouse Supervisors, Bay Leads, and Auditors.
   - **Human-in-the-Loop Review**: High/Critical incidents queued for supervisor validation with automated 5-Why Root Cause Analysis (RCA).

---

## 🛠️ Technology Stack

| Layer | Tools / Technologies |
|---|---|
| **Computer Vision** | OpenCV, YOLOv11, DeepSORT / ByteTrack |
| **AI / ML & Kinematics** | PyTorch, scikit-learn, NumPy |
| **Conversational AI** | Claude API / Gemini API / LangChain / Grounded Offline RAG Engine |
| **Backend & Storage** | FastAPI, SQLite (Native) / PostgreSQL, AWS S3 / Local Media Manager |
| **Dashboard** | React.js (React 18, Vite), Chart.js, Tailwind CSS, Lucide Icons |
| **Deployment** | Docker, docker-compose, NVIDIA Jetson / Cloud |

---

## 📦 10-Behavior Damage Taxonomy

| # | Code | Behavior Name | Telemetry Signature | Risk Tier |
|---|---|---|---|---|
| 01 | `BEH_DROP` | Product Dropped from Height | $a_y \ge 8.5\text{ m/s}^2$, freefall drop height $h > 0.5\text{m}$, impact $E_k > 45\text{J}$ | **Critical** |
| 02 | `BEH_DRAG` | Floor Dragging Cartons | Ground displacement $> 1.2\text{m}$ with 0cm vertical clearance | **High** |
| 03 | `BEH_IMPROPER_STACK` | Inverted Pyramid Stacking | Heavy crate placed atop light fragile base, tilt $\theta > 12^\circ$ | **Critical** |
| 04 | `BEH_PALLET_OVERHANG` | Unsafe Pallet Overhang & Tilt | Carton overhang $> 25\%$ outside pallet perimeter boundary | **High** |
| 05 | `BEH_ROUGH_HANDLING` | Rough Handling / Slamming | Impact landing deceleration $|a| > 14\text{ m/s}^2$ | **High** |
| 06 | `BEH_TOSS_THROW` | Carton Tossing / Throwing | Parabolic projectile flight trajectory without human contact | **Critical** |
| 07 | `BEH_STEP_ON_CARGO` | Stepping or Sitting on Cartons | Worker bounding box directly atop cargo bounding box with downward load | **Critical** |
| 08 | `BEH_OVERSTACK` | Over-Stacking Height Limit | Stack height exceeding 2.1m safe clearance threshold | **Medium** |
| 09 | `BEH_ROLLING_TUMBLE` | Rolling / Tumbling Cartons | Cyclic $90^\circ$ orientation shift along floor instead of lifting | **Medium** |
| 10 | `BEH_FORKLIFT_PINCH` | Forklift / Pedestrian Hazard | Moving forklift load within 1.5m pedestrian corridor | **Critical** |

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (optional: the backend serves the pre-built frontend distribution on port 8000 out of the box!)

### 2. 1-Click Launch (macOS & Linux)
```bash
git clone <repo-url>
cd safestack-ai
./start.sh
```

### 3. 1-Click Launch (Windows)
```cmd
start.bat
```

### 4. Docker Deployment
```bash
docker-compose up --build
```

- **Live Application Dashboard**: [http://localhost:5173](http://localhost:5173) (or [http://localhost:8000](http://localhost:8000))
- **Interactive REST API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **WebSocket Live Alert Stream**: `ws://localhost:8000/ws/alerts`

### Video detection model

Ultralytics is included for YOLO inference. By default, the detector loads `yolo11n.pt`; to use warehouse-specific labels, set `SAFESTACK_DETECTION_MODEL` to the path of your trained weights before starting the backend. Custom weights should label cargo as `carton` (or `box`/`package`), and relevant equipment as `pallet`, `forklift`, or `pallet_jack`. The default general-purpose model may not recognize these warehouse classes. If no usable model is available, uploaded footage still plays, but scans explicitly report detector unavailability; no incidents does not mean the video is safe.

---

## 🧪 Running Automated Tests

Run the full unit and integration test suite:
```bash
PYTHONPATH=. python3 -m pytest backend/tests -v
```

All 14 tests covering kinematics, sequence-level action recognition, graded risk scoring, API routes, and 5-Why RCA generation pass out of the box.

---

## 📁 Repository Structure

```
safestack-ai/
├── README.md                           # Project overview & quickstart
├── docker-compose.yml                  # Full stack container orchestration
├── Dockerfile.backend                  # Backend Docker container
├── Dockerfile.frontend                 # Frontend Docker container
├── start.sh                            # 1-click startup script (macOS/Linux)
├── start.bat                           # 1-click startup script (Windows)
├── backend/
│   ├── requirements.txt                # Python dependencies
│   ├── main.py                         # FastAPI application entrypoint with WebSockets
│   ├── config.py                       # Configuration & threshold constants
│   ├── models/
│   │   ├── database.py                 # SQLite persistence & initial seeds
│   │   └── schemas.py                  # Pydantic schemas for events, telemetries, reviews
│   ├── cv_pipeline/
│   │   ├── detector.py                 # Object detector interface (YOLOv11 / OpenCV)
│   │   ├── tracker.py                  # Multi-frame tracker (DeepSORT / ByteTrack logic)
│   │   ├── kinematics.py               # Physics engine (ay, drop velocity, impact, tilt)
│   │   ├── action_recognizer.py        # Sequence-level 10-behavior action classifier
│   │   └── privacy_shield.py           # Face blur and silhouette anonymizer
│   ├── risk_engine/
│   │   ├── scorer.py                   # Graded risk scoring formula (Low, Med, High, Crit)
│   │   └── explainability.py           # Explainable feature attributions & recommendations
│   ├── conversational_ai/
│   │   ├── assistant.py                # Grounded RAG assistant (Claude/Gemini/Offline engine)
│   │   └── rca_generator.py            # Automated 5-Why Root Cause Analysis builder
│   ├── simulation/
│   │   ├── video_synthesizer.py        # OpenCV synthetic warehouse frame generator
│   │   └── scenario_runner.py          # Real-time multi-bay feed simulator
│   ├── storage/
│   │   └── media_manager.py            # Clip and snapshot media storage
│   └── tests/
│       ├── test_cv_pipeline.py         # Kinematics and action recognition unit tests
│       ├── test_risk_scorer.py         # Risk scoring model unit tests
│       └── test_api.py                 # API and WebSocket integration tests
├── frontend/
│   ├── package.json                    # React 18, Vite, Chart.js, Tailwind CSS
│   ├── index.html                      # HTML root with Chart.js CDN
│   ├── vite.config.js                  # Proxy configuration
│   ├── tailwind.config.js              # Dark-mode styling system
│   ├── src/
│   │   ├── App.jsx                     # Core application layout and state
│   │   ├── components/
│   │   │   ├── Header.jsx              # App header with RBAC
│   │   │   ├── LiveBaysGrid.jsx        # Multi-bay live camera stream & privacy toggles
│   │   │   ├── AlertFeed.jsx           # Real-time graded alert stream
│   │   │   ├── AnalyticsDashboard.jsx  # Chart.js shift analytics & ROI calculator
│   │   │   ├── EventReviewModal.jsx    # Human-in-the-loop review & 5-Why RCA modal
│   │   │   ├── AssistantDrawer.jsx     # Conversational AI assistant drawer
│   │   │   └── SimulationControls.jsx  # 10-behavior scenario injector
│   │   └── services/
│   │       ├── api.js                  # REST API client
│   │       └── websocket.js            # WebSocket real-time subscription client
│   └── dist/                           # Production-ready pre-built frontend distribution
└── docs/
    ├── ARCHITECTURE.md                 # System architecture and data flow diagrams
    ├── TAXONOMY.md                     # Detailed 10-behavior taxonomy and kinematic parameters
    ├── RESPONSIBLE_AI.md               # Responsible AI, privacy safeguards & non-punitive policies
    └── API_SPECIFICATION.md            # REST and WebSocket API documentation
```

---

## ⚖️ License
Academic and Prototype License.
