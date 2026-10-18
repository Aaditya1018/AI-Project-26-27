# SafeStack AI — REST & WebSocket API Specification

Base URL: `http://localhost:8000/api`
WebSocket Endpoint: `ws://localhost:8000/ws/alerts`

---

## 1. Health & Status

### `GET /api/health`
Returns system status, active version, and timestamp.
```json
{
  "status": "healthy",
  "service": "SafeStack AI",
  "version": "1.0.0",
  "active_bays": 4,
  "timestamp": "2026-10-18T06:30:00Z"
}
```

---

## 2. Bays & Live Video Streaming

### `GET /api/bays`
Returns array of active loading bays, risk level, and worker counts.

### `GET /api/bays/{bay_id}/stream`
Streams live multipart JPEG video (`multipart/x-mixed-replace; boundary=frame`) with detection bounding boxes and Privacy Shield overlays.
- Query Parameters:
  - `privacy` (`bool`): `true` to enable face blurring / anonymization.
  - `silhouettes` (`bool`): `true` to render anonymous ergonomic avatar silhouettes.

### `GET /api/bays/{bay_id}/frame`
Returns a single JPEG image frame snapshot.

---

## 3. Events & Incidents

### `GET /api/events`
Query parameters:
- `bay_id` (`string`, optional): e.g. `BAY-01`
- `risk_tier` (`string`, optional): `Low` | `Medium` | `High` | `Critical`
- `status` (`string`, optional): `Pending Review` | `Verified Damage Prevented` | `False Positive` | `Coaching Logged`
- `limit` (`int`, optional, default 50)

### `GET /api/events/{event_id}`
Returns single event object with full kinematic metrics and explainability breakdown.

### `POST /api/events/{event_id}/review`
Body:
```json
{
  "event_id": "EVT-1001",
  "action": "Verified Damage Prevented",
  "notes": "Coached operator on 2-person lift; interior OLED display saved from fracture.",
  "supervisor_name": "Supervisor"
}
```

### `GET /api/events/{event_id}/rca`
Returns automated 5-Why Root Cause Analysis and Corrective and Preventive Action (CAPA) plan.

---

## 4. Simulation & Scenario Testing

### `POST /api/simulate/trigger`
Injects any of the 10 predefined damage-risk behaviors in real time:
- Query parameters:
  - `bay_id`: `BAY-01` to `BAY-04`
  - `scenario`: `BEH_DROP` | `BEH_DRAG` | `BEH_IMPROPER_STACK` | `BEH_PALLET_OVERHANG` | `BEH_ROUGH_HANDLING` | `BEH_TOSS_THROW` | `BEH_STEP_ON_CARGO` | `BEH_OVERSTACK` | `BEH_ROLLING_TUMBLE` | `BEH_FORKLIFT_PINCH`
  - `product_category`: `Electronics & Fragile` | `Glassware & Ceramics` | `Heavy Industrial Goods` | `Perishables & Cold Chain` | `General Boxed Cargo`

---

## 5. Analytics & Conversational AI

### `GET /api/analytics/summary`
Returns KPI metrics, damage prevented financial savings, hourly shift risk trends, behavior distributions, and bay comparisons.

### `POST /api/chat`
Body:
```json
{
  "query": "Which bay had the most dropping incidents?",
  "bay_id": null
}
```
Response:
```json
{
  "query": "Which bay had the most dropping incidents?",
  "answer": "Based on verified computer-vision telemetry, Bay-02 (Electronics & Fragile) has recorded the highest frequency of drop incidents...",
  "citations": [
    {
      "event_id": "EVT-1001",
      "bay_id": "BAY-02",
      "behavior_name": "Product Dropped from Height",
      "timestamp": "2026-10-18T05:42:00Z",
      "risk_tier": "Critical"
    }
  ],
  "evidence_count": 5,
  "grounded_in_cv": true,
  "provider_used": "SafeStack Evidence-Grounded Engine (Zero-Fabrication)"
}
```
