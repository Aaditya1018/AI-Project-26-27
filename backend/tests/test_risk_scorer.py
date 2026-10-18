"""
SafeStack AI - Graded Risk Scorer Unit Tests
"""

import pytest
from backend.risk_engine.scorer import GradedRiskScorer
from backend.risk_engine.explainability import ExplainabilityEngine
from backend.models.schemas import BehaviorType, ProductCategory, RiskTier, KinematicMetrics

def test_risk_scorer_critical_fragile_drop():
    scorer = GradedRiskScorer()
    metrics = KinematicMetrics(
        vertical_accel_mps2=9.8,
        drop_velocity_mps=4.5,
        drop_height_m=1.4,
        kinetic_impact_energy_j=90.0,
        rough_impact_decel_mps2=22.0
    )
    score, tier = scorer.calculate_score(
        BehaviorType.BEH_DROP,
        ProductCategory.ELECTRONICS_FRAGILE,
        metrics,
        bay_recent_frequency=2
    )
    assert score >= 85.0
    assert tier == RiskTier.CRITICAL

def test_risk_scorer_low_risk():
    scorer = GradedRiskScorer()
    metrics = KinematicMetrics(
        vertical_accel_mps2=0.0,
        drop_velocity_mps=0.0,
        drop_height_m=0.0
    )
    score, tier = scorer.calculate_score(
        BehaviorType.BEH_ROLLING_TUMBLE,
        ProductCategory.GENERAL_CARGO,
        metrics,
        bay_recent_frequency=1
    )
    assert score < 70.0
    assert tier in (RiskTier.LOW, RiskTier.MEDIUM)

def test_explainability_report_structure():
    engine = ExplainabilityEngine()
    metrics = KinematicMetrics(
        drop_height_m=1.2,
        vertical_accel_mps2=9.7,
        kinetic_impact_energy_j=75.0
    )
    report = engine.generate_report(
        BehaviorType.BEH_DROP,
        "Product Dropped from Height",
        ProductCategory.GLASSWARE_CERAMICS,
        metrics,
        final_score=91.0,
        bay_frequency=2
    )
    assert report.final_score == 91.0
    assert len(report.factors) >= 3
    assert "two-person" in report.prevention_recommendation.lower()
