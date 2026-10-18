"""
SafeStack AI - Native SQLite Persistence Module
Zero-dependency, thread-safe SQLite storage for events, loading bays, and reviews.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from backend.config import BASE_DIR, settings

DB_FILE = BASE_DIR / "safestack.db"

def get_connection():
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bays (
        bay_id TEXT PRIMARY KEY,
        bay_name TEXT NOT NULL,
        camera_active INTEGER DEFAULT 1,
        current_risk_level TEXT DEFAULT 'Low',
        active_workers INTEGER DEFAULT 2,
        active_packages INTEGER DEFAULT 14,
        last_event_time TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        bay_id TEXT NOT NULL,
        bay_name TEXT NOT NULL,
        behavior_type TEXT NOT NULL,
        behavior_name TEXT NOT NULL,
        product_category TEXT NOT NULL,
        risk_score REAL NOT NULL,
        risk_tier TEXT NOT NULL,
        kinematic_telemetry TEXT,
        explainability TEXT,
        clip_url TEXT,
        snapshot_url TEXT,
        status TEXT DEFAULT 'Pending Review',
        supervisor_notes TEXT DEFAULT '',
        reviewed_by TEXT,
        reviewed_at TEXT
    );
    """)
    conn.commit()
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bays")
    if cursor.fetchone()[0] == 0:
        bays = [
            ("BAY-01", "Bay-01 (Inbound Heavy Cargo)", 1, "Medium", 3, 24, datetime.utcnow().isoformat()),
            ("BAY-02", "Bay-02 (Electronics & Fragile)", 1, "Critical", 2, 18, datetime.utcnow().isoformat()),
            ("BAY-03", "Bay-03 (Express Parcel Sort)", 1, "Low", 4, 42, datetime.utcnow().isoformat()),
            ("BAY-04", "Bay-04 (Cold Chain FMCG)", 1, "High", 2, 16, datetime.utcnow().isoformat()),
        ]
        cursor.executemany("INSERT INTO bays VALUES (?, ?, ?, ?, ?, ?, ?)", bays)
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        now = datetime.utcnow()
        initial_events = [
            (
                "EVT-1001",
                (now - timedelta(minutes=48)).isoformat(),
                "BAY-02",
                "Bay-02 (Electronics & Fragile)",
                "BEH_DROP",
                "Product Dropped from Height",
                "Electronics & Fragile",
                92.5,
                "Critical",
                json.dumps({
                    "vertical_accel_mps2": 9.72,
                    "drop_velocity_mps": 4.12,
                    "drop_height_m": 1.25,
                    "kinetic_impact_energy_j": 84.6,
                    "tilt_angle_deg": 18.4,
                    "pallet_overhang_pct": 0.0,
                    "drag_distance_m": 0.0,
                    "rough_impact_decel_mps2": 19.8,
                    "stack_height_m": 1.1,
                    "pedestrian_distance_m": 2.4
                }),
                json.dumps({
                    "summary": "Severe freefall impact detected on high-value fragile electronics carton.",
                    "base_behavior_pts": 40.0,
                    "category_multiplier": 1.8,
                    "kinematic_impact_pts": 22.5,
                    "frequency_multiplier": 1.2,
                    "final_score": 92.5,
                    "factors": [
                        {"factor_name": "Freefall Acceleration", "weight": 0.35, "contribution_pts": 35.0, "evidence": "a_y = 9.72 m/s^2 matches freefall profile"},
                        {"factor_name": "Fragile Sensitivity", "weight": 0.25, "contribution_pts": 25.0, "evidence": "Category: Electronics & Fragile requires zero-drop tolerance"},
                        {"factor_name": "Impact Energy", "weight": 0.20, "contribution_pts": 20.0, "evidence": "Kinetic Energy = 84.6 Joules exceeds 35J carton rupture rating"},
                        {"factor_name": "Repetition in Bay", "weight": 0.20, "contribution_pts": 12.5, "evidence": "2nd dropping event in Bay-02 within 2 hours"}
                    ],
                    "prevention_recommendation": "Mandate two-person buddy lift for packages > 15kg; inspect conveyor transfer lip."
                }),
                "/api/media/clips/sample_drop.mp4",
                "/api/media/snapshots/sample_drop.jpg",
                "Verified Damage Prevented",
                "Audio coaching broadcast triggered in 42ms; worker stabilized load before interior OLED panel fractured.",
                "Supervisor",
                (now - timedelta(minutes=42)).isoformat()
            ),
            (
                "EVT-1002",
                (now - timedelta(minutes=32)).isoformat(),
                "BAY-01",
                "Bay-01 (Inbound Heavy Cargo)",
                "BEH_IMPROPER_STACK",
                "Inverted Pyramid Stacking",
                "Heavy Industrial Goods",
                78.0,
                "High",
                json.dumps({
                    "vertical_accel_mps2": 0.4,
                    "drop_velocity_mps": 0.0,
                    "drop_height_m": 0.0,
                    "kinetic_impact_energy_j": 0.0,
                    "tilt_angle_deg": 14.8,
                    "pallet_overhang_pct": 28.5,
                    "drag_distance_m": 0.0,
                    "rough_impact_decel_mps2": 2.1,
                    "stack_height_m": 1.95,
                    "pedestrian_distance_m": 3.1
                }),
                json.dumps({
                    "summary": "Heavy crate stacked atop light corrugated packaging causing structural instability.",
                    "base_behavior_pts": 35.0,
                    "category_multiplier": 1.4,
                    "kinematic_impact_pts": 15.0,
                    "frequency_multiplier": 1.1,
                    "final_score": 78.0,
                    "factors": [
                        {"factor_name": "Weight Gradient Inversion", "weight": 0.35, "contribution_pts": 32.0, "evidence": "38kg motor crate placed atop 8kg component carton"},
                        {"factor_name": "Pallet Overhang", "weight": 0.30, "contribution_pts": 26.0, "evidence": "28.5% overhang exceeds 15% safety limit"},
                        {"factor_name": "Stack Tilt", "weight": 0.35, "contribution_pts": 20.0, "evidence": "Center of gravity deflected by 14.8 degrees"}
                    ],
                    "prevention_recommendation": "Restack with heaviest industrial crates as the pallet foundation."
                }),
                "/api/media/clips/sample_stack.mp4",
                "/api/media/snapshots/sample_stack.jpg",
                "Pending Review",
                "",
                None,
                None
            ),
            (
                "EVT-1003",
                (now - timedelta(minutes=15)).isoformat(),
                "BAY-03",
                "Bay-03 (Express Parcel Sort)",
                "BEH_TOSS_THROW",
                "Carton Tossing / Throwing",
                "General Boxed Cargo",
                84.2,
                "Critical",
                json.dumps({
                    "vertical_accel_mps2": 6.8,
                    "drop_velocity_mps": 3.8,
                    "drop_height_m": 0.9,
                    "kinetic_impact_energy_j": 52.0,
                    "tilt_angle_deg": 35.0,
                    "pallet_overhang_pct": 0.0,
                    "drag_distance_m": 2.1,
                    "rough_impact_decel_mps2": 16.5,
                    "stack_height_m": 0.8,
                    "pedestrian_distance_m": 1.8
                }),
                json.dumps({
                    "summary": "Parcel tossed across sorting cage in parabolic arc without controlled hand transfer.",
                    "base_behavior_pts": 38.0,
                    "category_multiplier": 1.3,
                    "kinematic_impact_pts": 21.0,
                    "frequency_multiplier": 1.25,
                    "final_score": 84.2,
                    "factors": [
                        {"factor_name": "Airborne Trajectory", "weight": 0.40, "contribution_pts": 38.0, "evidence": "Carton airborne for 0.72s with horizontal velocity 3.8 m/s"},
                        {"factor_name": "Landing Impact Deceleration", "weight": 0.35, "contribution_pts": 28.0, "evidence": "Landing impact decel = 16.5 m/s^2"}
                    ],
                    "prevention_recommendation": "Remind team to hand-transfer parcel onto gravity rollers."
                }),
                "/api/media/clips/sample_throw.mp4",
                "/api/media/snapshots/sample_throw.jpg",
                "Pending Review",
                "",
                None,
                None
            )
        ]
        cursor.executemany("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", initial_events)
        conn.commit()

class EventDBManager:
    @staticmethod
    def get_events(bay_id=None, risk_tier=None, status=None, limit=50) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        if bay_id:
            query += " AND bay_id = ?"
            params.append(bay_id)
        if risk_tier:
            query += " AND risk_tier = ?"
            params.append(risk_tier)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result

    @staticmethod
    def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_event_review(event_id: str, status: str, notes: str, supervisor_name: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.utcnow().isoformat()
        cursor.execute(
            "UPDATE events SET status = ?, supervisor_notes = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?",
            (status, notes, supervisor_name, now_str, event_id)
        )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    @staticmethod
    def insert_event(event_dict: Dict[str, Any]):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                event_dict["id"],
                event_dict["timestamp"],
                event_dict["bay_id"],
                event_dict["bay_name"],
                event_dict["behavior_type"],
                event_dict["behavior_name"],
                event_dict["product_category"],
                event_dict["risk_score"],
                event_dict["risk_tier"],
                json.dumps(event_dict["kinematic_telemetry"]),
                json.dumps(event_dict["explainability"]),
                event_dict.get("clip_url"),
                event_dict.get("snapshot_url"),
                event_dict.get("status", "Pending Review"),
                event_dict.get("supervisor_notes", ""),
                event_dict.get("reviewed_by"),
                event_dict.get("reviewed_at")
            )
        )
        # Update bay risk level
        cursor.execute(
            "UPDATE bays SET current_risk_level = ?, last_event_time = ? WHERE bay_id = ?",
            (event_dict["risk_tier"], event_dict["timestamp"], event_dict["bay_id"])
        )
        conn.commit()
        conn.close()

class BayDBManager:
    @staticmethod
    def get_all_bays() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bays")
        rows = cursor.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result

    @staticmethod
    def get_bay_by_id(bay_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bays WHERE bay_id = ?", (bay_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

# Auto-initialize database tables and seeds if not already present
init_db()
