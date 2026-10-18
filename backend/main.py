import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from backend.config import settings
from backend.models.database import init_db, EventDBManager, BayDBManager
from backend.models.schemas import (
    EventResponse,
    SupervisorReviewRequest,
    ChatQueryRequest,
    ChatQueryResponse,
    BayStatus,
    AnalyticsSummary,
    ProductCategory,
    ReviewStatus
)
from backend.simulation.scenario_runner import simulator
from backend.conversational_ai.assistant import GroundedWarehouseAssistant
from backend.conversational_ai.rca_generator import RcaGenerator
from backend.storage.media_manager import media_manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SafeStack AI: Real-Time Video Intelligence for Warehouse Damage Prevention"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AlertConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, event_data: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps({
                    "type": "NEW_ALERT",
                    "event": event_data
                }))
            except Exception:
                self.disconnect(connection)

manager = AlertConnectionManager()
assistant = GroundedWarehouseAssistant()
rca_gen = RcaGenerator()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "active_bays": len(settings.ACTIVE_BAYS),
        "timestamp": datetime.utcnow().isoformat()
    }

# ----------------- Bays & Live Video Streaming -----------------

@app.get("/api/bays", response_model=List[BayStatus])
def get_bays():
    bays = BayDBManager.get_all_bays()
    result = []
    for b in bays:
        recent_count = len(EventDBManager.get_events(bay_id=b["bay_id"]))
        last_dt = None
        if b.get("last_event_time"):
            try:
                last_dt = datetime.fromisoformat(b["last_event_time"])
            except Exception:
                pass
        result.append(BayStatus(
            bay_id=b["bay_id"],
            bay_name=b["bay_name"],
            camera_active=bool(b["camera_active"]),
            current_risk_level=b["current_risk_level"],
            active_workers=b["active_workers"],
            active_packages=b["active_packages"],
            last_event_time=last_dt,
            recent_events_count=recent_count
        ))
    return result

@app.get("/api/bays/{bay_id}/stream")
def stream_bay_video(
    bay_id: str,
    privacy: bool = True,
    silhouettes: bool = False
):
    stream = simulator.get_bay_stream(bay_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Bay not found")

    def frame_generator():
        try:
            import cv2
            import time
            while True:
                frame = stream.get_current_frame(enable_privacy=privacy, render_silhouettes=silhouettes)
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if not ret:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.065)
        except Exception:
            return

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/bays/{bay_id}/frame")
def get_bay_single_frame(
    bay_id: str,
    privacy: bool = True,
    silhouettes: bool = False
):
    stream = simulator.get_bay_stream(bay_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Bay not found")
    
    try:
        import cv2
        frame = stream.get_current_frame(enable_privacy=privacy, render_silhouettes=silhouettes)
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if ret:
            return Response(content=buffer.tobytes(), media_type="image/jpeg")
    except Exception:
        pass
    raise HTTPException(status_code=500, detail="Could not encode frame")

# ----------------- Events & Incidents -----------------

@app.get("/api/events")
def get_events(
    bay_id: Optional[str] = None,
    risk_tier: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    events = EventDBManager.get_events(bay_id=bay_id, risk_tier=risk_tier, status=status, limit=limit)
    results = []
    for e in events:
        try:
            t = json.loads(e["kinematic_telemetry"]) if e.get("kinematic_telemetry") else {}
            exp = json.loads(e["explainability"]) if e.get("explainability") else {}
        except Exception:
            t, exp = {}, {}
        results.append({
            "id": e["id"],
            "timestamp": e["timestamp"],
            "bay_id": e["bay_id"],
            "bay_name": e["bay_name"],
            "behavior_type": e["behavior_type"],
            "behavior_name": e["behavior_name"],
            "product_category": e["product_category"],
            "risk_score": e["risk_score"],
            "risk_tier": e["risk_tier"],
            "kinematic_telemetry": t,
            "explainability": exp,
            "clip_url": e.get("clip_url"),
            "snapshot_url": e.get("snapshot_url"),
            "status": e.get("status", "Pending Review"),
            "supervisor_notes": e.get("supervisor_notes", ""),
            "reviewed_by": e.get("reviewed_by"),
            "reviewed_at": e.get("reviewed_at")
        })
    return results

@app.get("/api/events/{event_id}")
def get_event_detail(event_id: str):
    e = EventDBManager.get_event_by_id(event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    try:
        t = json.loads(e["kinematic_telemetry"]) if e.get("kinematic_telemetry") else {}
        exp = json.loads(e["explainability"]) if e.get("explainability") else {}
    except Exception:
        t, exp = {}, {}
    return {
        "id": e["id"],
        "timestamp": e["timestamp"],
        "bay_id": e["bay_id"],
        "bay_name": e["bay_name"],
        "behavior_type": e["behavior_type"],
        "behavior_name": e["behavior_name"],
        "product_category": e["product_category"],
        "risk_score": e["risk_score"],
        "risk_tier": e["risk_tier"],
        "kinematic_telemetry": t,
        "explainability": exp,
        "clip_url": e.get("clip_url"),
        "snapshot_url": e.get("snapshot_url"),
        "status": e.get("status", "Pending Review"),
        "supervisor_notes": e.get("supervisor_notes", ""),
        "reviewed_by": e.get("reviewed_by"),
        "reviewed_at": e.get("reviewed_at")
    }

@app.post("/api/events/{event_id}/review")
def review_event(event_id: str, review: SupervisorReviewRequest):
    updated = EventDBManager.update_event_review(
        event_id=event_id,
        status=review.action.value,
        notes=review.notes or "",
        supervisor_name=review.supervisor_name
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "message": "Review recorded successfully",
        "event_id": event_id,
        "new_status": review.action.value,
        "reviewed_by": review.supervisor_name
    }

@app.get("/api/events/{event_id}/rca")
def get_event_rca(event_id: str):
    e = EventDBManager.get_event_by_id(event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    
    t = json.loads(e["kinematic_telemetry"]) if e.get("kinematic_telemetry") else {}
    rca_data = {
        "id": e["id"],
        "behavior_type": e["behavior_type"],
        "behavior_name": e["behavior_name"],
        "bay_name": e["bay_name"],
        "product_category": e["product_category"],
        "risk_score": e["risk_score"],
        "telemetry": t
    }
    return rca_gen.generate_5_why_analysis(rca_data)

# ----------------- Scenario Injection / Simulation -----------------

@app.post("/api/simulate/trigger")
async def trigger_simulation_scenario(
    bay_id: str = "BAY-02",
    scenario: str = "BEH_DROP",
    product_category: ProductCategory = ProductCategory.ELECTRONICS_FRAGILE
):
    event_response = simulator.trigger_behavior_scenario(bay_id, scenario, product_category)
    event_dict = event_response.model_dump()
    event_dict["timestamp"] = event_dict["timestamp"].isoformat()
    await manager.broadcast_alert(event_dict)

    return {
        "message": f"Successfully injected scenario {scenario} into {bay_id}",
        "event": event_dict
    }

# ----------------- Analytics & Reporting -----------------

@app.get("/api/analytics/summary", response_model=AnalyticsSummary)
def get_analytics():
    events = EventDBManager.get_events(limit=200)
    total = len(events)
    critical = sum(1 for e in events if e["risk_tier"] == "Critical")
    high = sum(1 for e in events if e["risk_tier"] == "High")
    medium = sum(1 for e in events if e["risk_tier"] == "Medium")
    low = sum(1 for e in events if e["risk_tier"] == "Low")
    prevented = sum(1 for e in events if "Prevented" in str(e.get("status", "")))

    savings = round(prevented * 185.0 + critical * 65.0, 2)

    now = datetime.utcnow()
    hourly_trends = []
    for i in range(7, -1, -1):
        h_end = now - timedelta(hours=i)
        cnt = max(0, int((i * 3 + total) % 6))
        hourly_trends.append({
            "hour": h_end.strftime("%H:00"),
            "incidents": cnt,
            "risk_index": round(min(100.0, 20.0 + cnt * 14.5), 1)
        })

    behavior_counts: Dict[str, int] = {}
    for e in events:
        name = e["behavior_name"]
        behavior_counts[name] = behavior_counts.get(name, 0) + 1
    
    behavior_distribution = [
        {"behavior": k, "count": v}
        for k, v in sorted(behavior_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    bays = BayDBManager.get_all_bays()
    bay_comparison = []
    for b in bays:
        b_events = [e for e in events if e["bay_id"] == b["bay_id"]]
        avg_score = round(sum(e["risk_score"] for e in b_events) / len(b_events), 1) if b_events else 15.0
        bay_comparison.append({
            "bay_id": b["bay_id"],
            "bay_name": b["bay_name"],
            "total_incidents": len(b_events),
            "critical_count": sum(1 for e in b_events if e["risk_tier"] == "Critical"),
            "average_risk_score": avg_score
        })

    return AnalyticsSummary(
        total_events=total,
        damage_prevented_count=prevented,
        critical_events=critical,
        high_events=high,
        medium_events=medium,
        low_events=low,
        prevented_value_est_usd=savings,
        hourly_trends=hourly_trends,
        behavior_distribution=behavior_distribution,
        bay_comparison=bay_comparison
    )

# ----------------- Conversational AI Assistant -----------------

@app.post("/api/chat", response_model=ChatQueryResponse)
def query_assistant(req: ChatQueryRequest):
    return assistant.query(req)

# ----------------- Media Storage -----------------

@app.get("/api/media/clips/{filename}")
def get_media_clip(filename: str):
    p = media_manager.get_clip_path(filename)
    if not p:
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(p, media_type="video/mp4")

@app.get("/api/media/snapshots/{filename}")
def get_media_snapshot(filename: str):
    p = media_manager.get_snapshot_path(filename)
    if not p:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return FileResponse(p, media_type="image/jpeg")

# ----------------- Video Injection & Processing Endpoints -----------------

from fastapi import UploadFile, File
import shutil
from backend.cv_pipeline.video_processor import InjectedVideoProcessor

class InjectVideoRequest(BaseModel):
    bay_id: str = "BAY-01"
    filename: str

class ProcessVideoRequest(BaseModel):
    filename: str
    bay_id: str = "BAY-01"
    product_category: ProductCategory = ProductCategory.GENERAL_CARGO

@app.post("/api/video/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a custom video file to be injected into the SafeStack AI CV pipeline.
    """
    safe_name = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
    dest_path = settings.UPLOADS_DIR / safe_name
    
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Video uploaded successfully",
        "filename": safe_name,
        "original_name": file.filename,
        "path": str(dest_path),
        "url": f"/api/video/file/{safe_name}"
    }

@app.get("/api/video/uploads")
def list_uploaded_videos():
    """
    List all uploaded videos available for injection.
    """
    files = []
    if settings.UPLOADS_DIR.exists():
        for f in settings.UPLOADS_DIR.glob("*"):
            if f.is_file() and f.suffix.lower() in ('.mp4', '.avi', '.mov', '.mkv', '.webm'):
                files.append({
                    "filename": f.name,
                    "size_bytes": f.stat().st_size,
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "url": f"/api/video/file/{f.name}"
                })
    return sorted(files, key=lambda x: x["modified"], reverse=True)

@app.post("/api/video/inject")
def inject_video_to_bay(req: InjectVideoRequest):
    """
    Sets an uploaded video as the active live feed for a specific bay.
    The bay camera stream will now display and process this video!
    """
    video_path = settings.UPLOADS_DIR / req.filename
    if not video_path.exists():
        # Check clips dir as fallback
        video_path = settings.CLIPS_DIR / req.filename
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video file {req.filename} not found")

    success = simulator.set_bay_video(req.bay_id, str(video_path))
    if not success:
        raise HTTPException(status_code=400, detail="Could not set video on bay stream")

    return {
        "message": f"Successfully injected video {req.filename} into {req.bay_id}",
        "bay_id": req.bay_id,
        "video_filename": req.filename,
        "active_stream_url": f"/api/bays/{req.bay_id}/stream"
    }

@app.post("/api/video/reset/{bay_id}")
def reset_bay_video(bay_id: str):
    """
    Resets a bay back to default simulated live camera stream.
    """
    success = simulator.clear_bay_video(bay_id)
    return {
        "message": f"Reset {bay_id} back to standard CCTV feed",
        "bay_id": bay_id,
        "success": success
    }

@app.post("/api/video/process")
async def process_custom_video(req: ProcessVideoRequest):
    """
    Runs the full CV pipeline on an uploaded video, discovers damage-risk behaviors,
    records incidents to the DB, and broadcasts alerts over WebSocket.
    """
    if Path(req.filename).name != req.filename:
        raise HTTPException(status_code=400, detail="Invalid video filename")

    video_path = settings.UPLOADS_DIR / req.filename
    if not video_path.exists():
        video_path = settings.CLIPS_DIR / req.filename
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")

    bay_name = f"Bay {req.bay_id}"
    bay_rec = BayDBManager.get_bay_by_id(req.bay_id)
    if bay_rec:
        bay_name = bay_rec["bay_name"]

    processor = InjectedVideoProcessor(str(video_path))
    try:
        incidents = processor.process_and_detect_events(
            bay_id=req.bay_id,
            bay_name=bay_name,
            category=req.product_category
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Broadcast all discovered alerts over WebSocket
    for inc in incidents:
        await manager.broadcast_alert(inc)

    scan_summary = processor.last_scan_summary
    if scan_summary["detector_status"] == "unavailable":
        message = (
            f"Scanned {scan_summary['frames_analyzed']} frames, but no object-detection model "
            "is available. No real-video safety conclusion can be made."
        )
    else:
        message = (
            f"Scanned {scan_summary['frames_analyzed']} frames, found "
            f"{sum(scan_summary['detection_counts'].values())} model detections, and "
            f"{len(incidents)} damage-risk incidents."
        )
        if not {"carton", "pallet"}.issubset(scan_summary["warehouse_classes_supported"]):
            message += (
                " The selected model does not support all cargo classes, so this scan cannot assess "
                "carton or pallet handling."
            )

    return {
        "message": message,
        "filename": req.filename,
        "incidents_count": len(incidents),
        "incidents": incidents,
        "scan": scan_summary
    }

@app.get("/api/video/file/{filename}")
def stream_uploaded_video_file(filename: str):
    p = settings.UPLOADS_DIR / filename
    if not p.exists():
        p = settings.CLIPS_DIR / filename
        if not p.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(p, media_type="video/mp4")


# ----------------- WebSockets -----------------

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# ----------------- Serve Frontend Static Distribution -----------------
try:
    from fastapi.staticfiles import StaticFiles
    dist_dir = settings.BASE_DIR.parent / "frontend" / "dist"
    if dist_dir.exists():
        app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
except Exception:
    pass
