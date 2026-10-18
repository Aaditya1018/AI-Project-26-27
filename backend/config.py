"""
SafeStack AI - Configuration Module
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "storage" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR = MEDIA_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR = MEDIA_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR = MEDIA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    PROJECT_NAME: str = "SafeStack AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    BASE_DIR: Path = BASE_DIR
    MEDIA_DIR: Path = MEDIA_DIR
    CLIPS_DIR: Path = CLIPS_DIR
    SNAPSHOTS_DIR: Path = SNAPSHOTS_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/safestack.db")
    
    # LLM Settings (Claude API / Gemini / LangChain / Offline Fallback)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini" if os.getenv("GEMINI_API_KEY") else ("claude" if os.getenv("ANTHROPIC_API_KEY") else "offline"))
    
    # Kinematic & Detection Thresholds
    FREEFALL_ACCEL_MIN: float = 8.5      # m/s^2 for freefall drop detection
    DROP_HEIGHT_MIN_METERS: float = 0.50 # min height to qualify as dangerous drop
    DRAG_DISTANCE_MIN_METERS: float = 1.2 # floor friction dragging threshold
    TILT_ANGLE_THRESHOLD_DEG: float = 12.0 # degrees lean for stack/pallet
    PALLET_OVERHANG_THRESHOLD_PCT: float = 25.0 # percent box footprint outside pallet edge
    ROUGH_IMPACT_DECEL_MIN: float = 14.0 # m/s^2 rapid impact shock
    STACK_MAX_HEIGHT_METERS: float = 2.10 # safe stack height envelope
    
    # Risk Engine Weights
    WEIGHT_BEHAVIOR: float = 0.40
    WEIGHT_CATEGORY: float = 0.25
    WEIGHT_IMPACT: float = 0.20
    WEIGHT_FREQUENCY: float = 0.15
    
    # Active Loading Bays
    ACTIVE_BAYS: list[str] = ["Bay-01 (Inbound Cargo)", "Bay-02 (Heavy Industrial)", "Bay-03 (Express Parcels)", "Bay-04 (Cold Chain / FMCG)"]
    
    # Responsible AI Privacy Shield defaults
    ENABLE_PRIVACY_SHIELD_DEFAULT: bool = True
    ANONYMIZE_FACES: bool = True
    RENDER_SILHOUETTES: bool = True

settings = Settings()
