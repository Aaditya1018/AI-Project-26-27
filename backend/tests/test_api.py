"""
SafeStack AI - FastAPI Integration Tests
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "team" not in data

def test_get_bays():
    res = client.get("/api/bays")
    assert res.status_code == 200
    bays = res.json()
    assert len(bays) >= 4

def test_get_events():
    res = client.get("/api/events")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1

def test_event_rca():
    res_events = client.get("/api/events")
    first_id = res_events.json()[0]["id"]
    res_rca = client.get(f"/api/events/{first_id}/rca")
    assert res_rca.status_code == 200
    rca = res_rca.json()
    assert len(rca["five_whys"]) == 5
    assert "root_cause" in rca

def test_chat_query():
    res = client.post("/api/chat", json={"query": "Which bay had the most drop incidents?"})
    assert res.status_code == 200
    ans = res.json()
    assert "Bay" in ans["answer"]
    assert ans["grounded_in_cv"] is True

def test_simulation_trigger():
    res = client.post("/api/simulate/trigger?bay_id=BAY-02&scenario=BEH_DROP")
    assert res.status_code == 200
    data = res.json()
    assert data["event"]["risk_tier"] in ("High", "Critical")

def test_video_uploads_list():
    res = client.get("/api/video/uploads")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_video_inject_and_reset():
    # Create test dummy video in uploads dir
    from backend.config import settings
    test_video = settings.UPLOADS_DIR / "sample_test.mp4"
    test_video.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00")

    # Inject sample clip into BAY-01
    res = client.post("/api/video/inject", json={"bay_id": "BAY-01", "filename": "sample_test.mp4"})
    assert res.status_code == 200
    data = res.json()
    assert "injected" in data["message"].lower()

    # Reset bay
    res_reset = client.post("/api/video/reset/BAY-01")
    assert res_reset.status_code == 200

