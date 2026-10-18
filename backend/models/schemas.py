"""
SafeStack AI - Pydantic Schemas
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class RiskTier(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ProductCategory(str, Enum):
    ELECTRONICS_FRAGILE = "Electronics & Fragile"
    GLASSWARE_CERAMICS = "Glassware & Ceramics"
    HEAVY_INDUSTRIAL = "Heavy Industrial Goods"
    PERISHABLES_FOOD = "Perishables & Cold Chain"
    GENERAL_CARGO = "General Boxed Cargo"

class BehaviorType(str, Enum):
    BEH_DROP = "BEH_DROP"
    BEH_DRAG = "BEH_DRAG"
    BEH_IMPROPER_STACK = "BEH_IMPROPER_STACK"
    BEH_PALLET_OVERHANG = "BEH_PALLET_OVERHANG"
    BEH_ROUGH_HANDLING = "BEH_ROUGH_HANDLING"
    BEH_TOSS_THROW = "BEH_TOSS_THROW"
    BEH_STEP_ON_CARGO = "BEH_STEP_ON_CARGO"
    BEH_OVERSTACK = "BEH_OVERSTACK"
    BEH_ROLLING_TUMBLE = "BEH_ROLLING_TUMBLE"
    BEH_FORKLIFT_PINCH = "BEH_FORKLIFT_PINCH"

class ReviewStatus(str, Enum):
    PENDING_REVIEW = "Pending Review"
    VERIFIED_DAMAGE_PREVENTED = "Verified Damage Prevented"
    FALSE_POSITIVE = "False Positive"
    COACHING_LOGGED = "Coaching Logged"

class BoundingBox(BaseModel):
    track_id: int
    class_name: str
    confidence: float
    x: float
    y: float
    w: float
    h: float

class KinematicMetrics(BaseModel):
    vertical_accel_mps2: float = 0.0
    drop_velocity_mps: float = 0.0
    drop_height_m: float = 0.0
    kinetic_impact_energy_j: float = 0.0
    tilt_angle_deg: float = 0.0
    pallet_overhang_pct: float = 0.0
    drag_distance_m: float = 0.0
    rough_impact_decel_mps2: float = 0.0
    stack_height_m: float = 0.0
    pedestrian_distance_m: float = 0.0

class ExplainabilityFactor(BaseModel):
    factor_name: str
    weight: float
    contribution_pts: float
    evidence: str

class ExplainabilityReport(BaseModel):
    summary: str
    base_behavior_pts: float
    category_multiplier: float
    kinematic_impact_pts: float
    frequency_multiplier: float
    final_score: float
    factors: List[ExplainabilityFactor]
    prevention_recommendation: str

class EventBase(BaseModel):
    bay_id: str
    bay_name: str
    behavior_type: BehaviorType
    behavior_name: str
    product_category: ProductCategory
    risk_score: float
    risk_tier: RiskTier
    kinematic_telemetry: KinematicMetrics
    explainability: ExplainabilityReport
    clip_url: Optional[str] = None
    snapshot_url: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: str
    timestamp: datetime
    status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    supervisor_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

class SupervisorReviewRequest(BaseModel):
    event_id: str
    action: ReviewStatus
    notes: Optional[str] = ""
    supervisor_name: str = "Supervisor"

class ChatQueryRequest(BaseModel):
    query: str
    bay_id: Optional[str] = None
    time_window_hours: Optional[int] = 24
    provider: Optional[str] = None

class ChatCitation(BaseModel):
    event_id: str
    bay_id: str
    behavior_name: str
    timestamp: str
    risk_tier: str

class ChatQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[ChatCitation]
    evidence_count: int
    grounded_in_cv: bool = True
    provider_used: str

class BayStatus(BaseModel):
    bay_id: str
    bay_name: str
    camera_active: bool
    current_risk_level: RiskTier
    active_workers: int
    active_packages: int
    last_event_time: Optional[datetime] = None
    recent_events_count: int

class AnalyticsSummary(BaseModel):
    total_events: int
    damage_prevented_count: int
    critical_events: int
    high_events: int
    medium_events: int
    low_events: int
    prevented_value_est_usd: float
    hourly_trends: List[Dict[str, Any]]
    behavior_distribution: List[Dict[str, Any]]
    bay_comparison: List[Dict[str, Any]]
