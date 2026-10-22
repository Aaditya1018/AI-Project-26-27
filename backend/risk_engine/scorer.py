"""
SafeStack AI - Graded Risk Scoring Model
Factors in:
1. Behavior Type (Base Severity)
2. Product Category (Fragility & Value Sensitivity)
3. Kinematic Impact / Drop Energy / Height
4. Repetition Frequency in Shift / Bay
Outputs: Graded score (0-100) mapped to Low, Medium, High, Critical.
"""

from typing import Tuple
from backend.models.schemas import BehaviorType, ProductCategory, RiskTier, KinematicMetrics
from backend.config import settings

class GradedRiskScorer:
    # Base behavior severities (0 - 100 scale)
    BASE_BEHAVIOR_SCORES = {
        BehaviorType.BEH_DROP: 45.0,
        BehaviorType.BEH_FORKLIFT_PINCH: 48.0,
        BehaviorType.BEH_STEP_ON_CARGO: 42.0,
        BehaviorType.BEH_TOSS_THROW: 38.0,
        BehaviorType.BEH_IMPROPER_STACK: 35.0,
        BehaviorType.BEH_PALLET_OVERHANG: 34.0,
        BehaviorType.BEH_ROUGH_HANDLING: 32.0,
        BehaviorType.BEH_DRAG: 30.0,
        BehaviorType.BEH_OVERSTACK: 26.0,
        BehaviorType.BEH_ROLLING_TUMBLE: 24.0,
    }

    # Product category sensitivity multipliers
    CATEGORY_FACTORS = {
        ProductCategory.GLASSWARE_CERAMICS: 1.95,
        ProductCategory.ELECTRONICS_FRAGILE: 1.85,
        ProductCategory.HEAVY_INDUSTRIAL: 1.45,
        ProductCategory.PERISHABLES_FOOD: 1.35,
        ProductCategory.GENERAL_CARGO: 1.00,
    }

    def compute_impact_points(self, metrics: KinematicMetrics) -> float:
        """
        Computes kinematic impact severity points (0 to 100).
        """
        points = 0.0

        # Drop height contribution (0 - 40 pts)
        if metrics.drop_height_m > 0:
            points += min(40.0, (metrics.drop_height_m / 1.5) * 40.0)

        # Kinetic energy contribution (0 - 30 pts)
        if metrics.kinetic_impact_energy_j > 0:
            points += min(30.0, (metrics.kinetic_impact_energy_j / 100.0) * 30.0)

        # Rough landing deceleration (0 - 20 pts)
        if metrics.rough_impact_decel_mps2 > 0:
            points += min(20.0, (metrics.rough_impact_decel_mps2 / 20.0) * 20.0)

        # Tilt / Overhang contribution (0 - 30 pts)
        if metrics.tilt_angle_deg > 0:
            points += min(20.0, (metrics.tilt_angle_deg / 30.0) * 20.0)
        if metrics.pallet_overhang_pct > 0:
            points += min(20.0, (metrics.pallet_overhang_pct / 50.0) * 20.0)

        # Dragging distance (0 - 25 pts)
        if metrics.drag_distance_m > 0:
            points += min(25.0, (metrics.drag_distance_m / 5.0) * 25.0)

        # Pedestrian pinch hazard (0 - 50 pts)
        if metrics.pedestrian_distance_m > 0 and metrics.pedestrian_distance_m < 2.0:
            points += min(50.0, (2.0 - metrics.pedestrian_distance_m) / 2.0 * 50.0)

        return min(100.0, points)

    def calculate_score(
        self,
        behavior_type: BehaviorType,
        product_category: ProductCategory,
        metrics: KinematicMetrics,
        bay_recent_frequency: int = 1
    ) -> Tuple[float, RiskTier]:
        """
        Calculates graded risk score:
        Final = clamp((Base * w_b + Impact * w_i) * Cat_Mult * Freq_Mult, 0, 100)
        """
        base = self.BASE_BEHAVIOR_SCORES.get(behavior_type, 30.0)
        impact = self.compute_impact_points(metrics)
        cat_mult = self.CATEGORY_FACTORS.get(product_category, 1.0)
        
        # Frequency factor: +8% per prior incident in shift up to 1.35x
        freq_mult = min(1.35, 1.0 + max(0, bay_recent_frequency - 1) * 0.08)

        # Combine weighted terms
        core_raw = (base * settings.WEIGHT_BEHAVIOR) + (impact * settings.WEIGHT_IMPACT)
        
        # Scale to 0 - 100 with category and frequency dynamics
        scaled = (core_raw * 2.2) * (cat_mult ** 0.65) * freq_mult
        final_score = round(max(5.0, min(99.5, scaled)), 1)

        # Map to Graded Tiers
        if final_score >= 85.0:
            tier = RiskTier.CRITICAL
        elif final_score >= 70.0:
            tier = RiskTier.HIGH
        elif final_score >= 40.0:
            tier = RiskTier.MEDIUM
        else:
            tier = RiskTier.LOW

        return final_score, tier
