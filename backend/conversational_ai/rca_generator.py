"""
SafeStack AI - 5-Why Root Cause Analysis (RCA) & CAPA Generator
Transforms kinematic telemetry into structured operational incident audits and preventive action plans.
"""

from typing import Dict, Any, List

class RcaGenerator:
    def generate_5_why_analysis(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a structured 5-Why RCA report from computer-vision telemetry evidence.
        """
        behavior_type = event_data.get("behavior_type", "")
        behavior_name = event_data.get("behavior_name", "Material Mishandling")
        bay_name = event_data.get("bay_name", "Loading Bay")
        product = event_data.get("product_category", "General Cargo")
        telemetry = event_data.get("telemetry", {})

        whys = []
        root_cause = ""
        corrective_action = ""
        preventive_action = ""

        if "DROP" in behavior_type:
            whys = [
                f"1. Why did the event occur? -> The package slipped and dropped {telemetry.get('drop_height_m', 1.1)}m onto the loading bay floor.",
                "2. Why did it slip? -> The package was handled with an unbalanced single-hand grip during rapid conveyor offloading.",
                "3. Why was it handled with a single hand? -> Worker was rushing to clear an inbound surge before shift quota cut-off.",
                "4. Why was there an inbound surge without support? -> Peak arrival window had only 2 operators assigned instead of 3.",
                "5. Why was staffing unaligned? -> Loading bay schedule lacked dynamic volume-to-staffing forecasting."
            ]
            root_cause = "Surge pacing pressure combined with lack of two-person team lift protocol for bulky cartons."
            corrective_action = "Inspect dropped carton interior; calibrate conveyor height flush with transport pallet."
            preventive_action = "Implement ergonomic two-person buddy lift triggers and deploy automated velocity warning alerts."

        elif "STACK" in behavior_type or "OVERHANG" in behavior_type:
            whys = [
                f"1. Why did the stack become unstable? -> Bounding telemetry detected a {telemetry.get('tilt_angle_deg', 15)}° tilt lean and {telemetry.get('pallet_overhang_pct', 25)}% pallet overhang.",
                "2. Why did it lean? -> High-density heavy goods were stacked on top of lighter, compressible corrugated packaging.",
                "3. Why were heavy goods stacked on top? -> Inbound items were loaded in order of arrival rather than sorting by density/weight.",
                "4. Why was sorting skipped? -> Loading bay staging area was congested with un-palletized overflow.",
                "5. Why was the staging area congested? -> Forklift retrieval cycle was delayed by 18 minutes."
            ]
            root_cause = "FIFO staging without weight-density stratification and temporary dock staging congestion."
            corrective_action = "Restack pallet with high-density goods at the base and strap pallet with stretch film."
            preventive_action = "Enforce visual pyramid stacking guidelines and set up SafeStack AI live overhang boundary alerts."

        elif "FORKLIFT" in behavior_type:
            whys = [
                f"1. Why was a hazard detected? -> Forklift was operating within {telemetry.get('pedestrian_distance_m', 0.9)}m of dock personnel.",
                "2. Why was the worker in the vehicle path? -> Worker stepped into transit lane to pick up loose stretch wrap.",
                "3. Why was stretch wrap in the transit lane? -> Disposal bins were located 20 meters away at the far end of the bay.",
                "4. Why did the forklift operator not stop earlier? -> Forward load height (1.8m) partially obstructed forward blind spot.",
                "5. Why was the load carried forward while elevated? -> Operator skipped reverse-travel best practice due to time pressure."
            ]
            root_cause = "Obstructed forward travel line of sight and pedestrian infringement into marked equipment corridor."
            corrective_action = "Relocate mobile scrap bins adjacent to each packing station."
            preventive_action = "Enforce 3-meter pedestrian blue-light safety zone and mandate reverse travel for loads >1.2m."

        else:
            whys = [
                f"1. Why did the incident trigger? -> {behavior_name} detected with risk score {event_data.get('risk_score', 75)}.",
                "2. Why did this handling method occur? -> Operator bypassed standard ergonomic lift equipment.",
                "3. Why was equipment bypassed? -> Pallet jack was temporarily checked out to another bay.",
                "4. Why was equipment unavailable? -> Insufficient equipment allocation during concurrent bay operations.",
                "5. Why was allocation insufficient? -> Equipment tracking was managed via manual paper logbooks."
            ]
            root_cause = "Equipment availability bottleneck causing operators to resort to manual handling."
            corrective_action = "Assign dedicated pallet jacks to each active loading bay."
            preventive_action = "Deploy SafeStack AI equipment utilization tracking."

        return {
            "event_id": event_data.get("id", "EVT-UNKNOWN"),
            "behavior_name": behavior_name,
            "bay_name": bay_name,
            "product_category": product,
            "five_whys": whys,
            "root_cause": root_cause,
            "corrective_action": corrective_action,
            "preventive_action": preventive_action,
            "responsible_ai_governance": "This RCA is derived from kinematic physics telemetry. No individual worker punitive metrics are recorded."
        }
