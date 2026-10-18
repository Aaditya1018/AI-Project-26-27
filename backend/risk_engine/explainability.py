"""
SafeStack AI - Explainability Engine
Produces clear, auditable evidence breakdowns and actionable coaching recommendations.
"""

from typing import List
from backend.models.schemas import (
    BehaviorType,
    ProductCategory,
    KinematicMetrics,
    ExplainabilityReport,
    ExplainabilityFactor
)
from backend.risk_engine.scorer import GradedRiskScorer

class ExplainabilityEngine:
    def __init__(self):
        self.scorer = GradedRiskScorer()

        self.PREVENTION_GUIDELINES = {
            BehaviorType.BEH_DROP: "Mandate two-person team lift for items >15kg; ensure hydraulic lift table is flush with conveyor.",
            BehaviorType.BEH_DRAG: "Equip bay with pneumatic roller tracks and heavy-duty hand dollies to eliminate surface drag abrasion.",
            BehaviorType.BEH_IMPROPER_STACK: "Restack pallet placing highest-density heavy cartons as foundation; avoid inverted pyramid configurations.",
            BehaviorType.BEH_PALLET_OVERHANG: "Reposition cargo within pallet perimeter; maintain zero overhang and strap with stretch wrap before transit.",
            BehaviorType.BEH_ROUGH_HANDLING: "Train loading team on controlled two-point landing; use rubber shock mats in high-throughput transfer zones.",
            BehaviorType.BEH_TOSS_THROW: "Enforce positive hand-to-hand parcel transfer; install gravity chutes to eliminate manual throwing.",
            BehaviorType.BEH_STEP_ON_CARGO: "Provide rolling safety step stools; reiterate strict policy against stepping or standing on cartons.",
            BehaviorType.BEH_OVERSTACK: "Reduce stack height below 2.0m bay safe clearance envelope to prevent ceiling/mast collisions.",
            BehaviorType.BEH_ROLLING_TUMBLE: "Utilize four-wheel platform trucks; cartons must be transferred upright without corner rolling.",
            BehaviorType.BEH_FORKLIFT_PINCH: "Enforce mandatory 3-meter pedestrian exclusion bubble; equip forklifts with blue perimeter spot lights."
        }

    def generate_report(
        self,
        behavior_type: BehaviorType,
        behavior_name: str,
        product_category: ProductCategory,
        metrics: KinematicMetrics,
        final_score: float,
        bay_frequency: int = 1
    ) -> ExplainabilityReport:
        factors: List[ExplainabilityFactor] = []

        # 1. Base behavior
        base_pts = self.scorer.BASE_BEHAVIOR_SCORES.get(behavior_type, 30.0)
        factors.append(ExplainabilityFactor(
            factor_name="Behavior Severity Signature",
            weight=0.40,
            contribution_pts=round(base_pts * 0.40, 1),
            evidence=f"Action recognized: {behavior_name}"
        ))

        # 2. Category sensitivity
        cat_mult = self.scorer.CATEGORY_FACTORS.get(product_category, 1.0)
        factors.append(ExplainabilityFactor(
            factor_name="Product Vulnerability Sensitivity",
            weight=0.25,
            contribution_pts=round(cat_mult * 15.0, 1),
            evidence=f"Product Classification: {product_category.value} (Multiplier: {cat_mult}x)"
        ))

        # 3. Kinematic metrics breakdown
        if metrics.drop_height_m > 0 or metrics.vertical_accel_mps2 > 0:
            factors.append(ExplainabilityFactor(
                factor_name="Kinematic Drop Dynamics",
                weight=0.20,
                contribution_pts=round(min(30.0, metrics.drop_height_m * 20.0), 1),
                evidence=f"Freefall a_y = {metrics.vertical_accel_mps2} m/s^2, Drop Height = {metrics.drop_height_m}m, Impact Energy = {metrics.kinetic_impact_energy_j} J"
            ))

        if metrics.pallet_overhang_pct > 0 or metrics.tilt_angle_deg > 0:
            factors.append(ExplainabilityFactor(
                factor_name="Stability & Overhang Mechanics",
                weight=0.20,
                contribution_pts=round(min(25.0, metrics.pallet_overhang_pct * 0.5 + metrics.tilt_angle_deg * 0.5), 1),
                evidence=f"Overhang = {metrics.pallet_overhang_pct}%, Tilt Lean Angle = {metrics.tilt_angle_deg}°"
            ))

        if metrics.drag_distance_m > 0:
            factors.append(ExplainabilityFactor(
                factor_name="Friction & Abrasion Exposure",
                weight=0.20,
                contribution_pts=round(min(25.0, metrics.drag_distance_m * 5.0), 1),
                evidence=f"Dragged continuously over {metrics.drag_distance_m}m on dock floor"
            ))

        if metrics.pedestrian_distance_m > 0:
            factors.append(ExplainabilityFactor(
                factor_name="Pedestrian Proximity Hazard",
                weight=0.25,
                contribution_pts=round(max(0.0, (2.0 - metrics.pedestrian_distance_m) * 20.0), 1),
                evidence=f"Proximity to personnel = {metrics.pedestrian_distance_m}m (Limit: 2.5m)"
            ))

        # 4. Frequency
        freq_mult = min(1.35, 1.0 + max(0, bay_frequency - 1) * 0.08)
        if bay_frequency > 1:
            factors.append(ExplainabilityFactor(
                factor_name="Repetition Recurrence Frequency",
                weight=0.15,
                contribution_pts=round((bay_frequency - 1) * 4.0, 1),
                evidence=f"Occurrence #{bay_frequency} detected in this loading bay during the active shift"
            ))

        summary = f"{behavior_name} observed for {product_category.value}. Assigned risk score {final_score}/100 based on kinematic physics, category vulnerability, and bay history."
        prevention = self.PREVENTION_GUIDELINES.get(
            behavior_type,
            "Review bay operational standards and verify handling equipment compliance."
        )

        return ExplainabilityReport(
            summary=summary,
            base_behavior_pts=base_pts,
            category_multiplier=cat_mult,
            kinematic_impact_pts=self.scorer.compute_impact_points(metrics),
            frequency_multiplier=freq_mult,
            final_score=final_score,
            factors=factors,
            prevention_recommendation=prevention
        )
