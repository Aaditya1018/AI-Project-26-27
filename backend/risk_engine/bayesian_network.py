"""
SafeStack AI - Module 5: Bayesian Belief Network (BBN) for Probabilistic Damage Inference
========================================================================================
Academic Alignment:
  - University Syllabus: Module 5 (Uncertainty - Probabilistic Reasoning)
  - Core Concepts:
      * Directed Acyclic Graph (DAG) Representation
      * Prior and Posterior Probabilities
      * Conditional Probability Tables (CPT)
      * Exact Inference by Enumeration via Bayes' Theorem
      * Latent / Hidden Variable Reasoning under Observation Uncertainty

Problem Formulation:
  Observable Evidence (E):
    - Fragility (F) in {Durable, Fragile, HighRisk}
    - DropHeight (H) in {Low, Medium, High}
    - ImpactShock (I) in {Mild, Moderate, Severe}
    - TiltHazard (T) in {Stable, Dangerous}

  Latent Target Hypothesis (D):
    - InternalDamage (D) in {Intact, Cosmetic, SevereLoss}

Joint Probability Distribution Factorization (Chain Rule):
  P(F, H, T, I, D) = P(F) * P(H) * P(T) * P(I | H) * P(D | F, I, T)

Inference by Bayes' Rule:
  P(D = d | e) = alpha * P(D = d, e)
               = alpha * sum_{hidden} P(F, H, T, I, D)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class BayesianInferenceResult(BaseModel):
    p_intact: float
    p_cosmetic: float
    p_severe_loss: float
    most_probable_state: str
    confidence_pct: float
    observed_evidence: Dict[str, str]
    mathematical_derivation: List[str]


class WarehouseDamageBayesianNetwork:
    """
    Exact Inference Bayesian Belief Network for Latent Package Damage.
    """

    # State Spaces
    STATES_FRAGILITY = ["Durable", "Fragile", "HighRisk"]
    STATES_DROP_HEIGHT = ["Low", "Medium", "High"]
    STATES_IMPACT = ["Mild", "Moderate", "Severe"]
    STATES_TILT = ["Stable", "Dangerous"]
    STATES_DAMAGE = ["Intact", "Cosmetic", "SevereLoss"]

    # 1. Prior: P(Fragility)
    # Reflects standard warehouse distribution of goods
    PRIOR_FRAGILITY: Dict[str, float] = {
        "Durable": 0.55,      # e.g., apparel, canned goods, metal parts
        "Fragile": 0.30,      # e.g., ceramics, glassware, liquids
        "HighRisk": 0.15      # e.g., laptops, precision opticals, medical vials
    }

    # 2. Prior: P(DropHeight)
    PRIOR_DROP_HEIGHT: Dict[str, float] = {
        "Low": 0.65,          # < 0.5 m (normal waist-to-conveyor transfer)
        "Medium": 0.25,       # 0.5 - 1.1 m (shoulder/table slip)
        "High": 0.10          # > 1.1 m (top rack / over-head drop)
    }

    # 3. Prior: P(TiltHazard)
    PRIOR_TILT: Dict[str, float] = {
        "Stable": 0.80,       # < 12 degrees tilt / normal overhang
        "Dangerous": 0.20     # >= 12 degrees tilt / overhang > 25%
    }

    # 4. Conditional Probability Table: P(ImpactShock | DropHeight)
    # P(I | H)
    CPT_IMPACT_GIVEN_HEIGHT: Dict[str, Dict[str, float]] = {
        "Low": {
            "Mild": 0.85,
            "Moderate": 0.12,
            "Severe": 0.03
        },
        "Medium": {
            "Mild": 0.25,
            "Moderate": 0.55,
            "Severe": 0.20
        },
        "High": {
            "Mild": 0.05,
            "Moderate": 0.25,
            "Severe": 0.70
        }
    }

    # 5. Conditional Probability Table: P(Damage | Fragility, ImpactShock, TiltHazard)
    # P(D | F, I, T)
    CPT_DAMAGE: Dict[tuple, Dict[str, float]] = {
        # (Fragility, ImpactShock, TiltHazard) -> {Intact, Cosmetic, SevereLoss}
        
        # --- Durable Goods ---
        ("Durable", "Mild", "Stable"):       {"Intact": 0.98, "Cosmetic": 0.02, "SevereLoss": 0.00},
        ("Durable", "Mild", "Dangerous"):    {"Intact": 0.92, "Cosmetic": 0.07, "SevereLoss": 0.01},
        ("Durable", "Moderate", "Stable"):   {"Intact": 0.80, "Cosmetic": 0.16, "SevereLoss": 0.04},
        ("Durable", "Moderate", "Dangerous"):{"Intact": 0.68, "Cosmetic": 0.24, "SevereLoss": 0.08},
        ("Durable", "Severe", "Stable"):     {"Intact": 0.45, "Cosmetic": 0.35, "SevereLoss": 0.20},
        ("Durable", "Severe", "Dangerous"):  {"Intact": 0.30, "Cosmetic": 0.40, "SevereLoss": 0.30},

        # --- Fragile Goods (Glassware, Ceramics, Liquids) ---
        ("Fragile", "Mild", "Stable"):       {"Intact": 0.88, "Cosmetic": 0.10, "SevereLoss": 0.02},
        ("Fragile", "Mild", "Dangerous"):    {"Intact": 0.72, "Cosmetic": 0.20, "SevereLoss": 0.08},
        ("Fragile", "Moderate", "Stable"):   {"Intact": 0.40, "Cosmetic": 0.35, "SevereLoss": 0.25},
        ("Fragile", "Moderate", "Dangerous"):{"Intact": 0.20, "Cosmetic": 0.35, "SevereLoss": 0.45},
        ("Fragile", "Severe", "Stable"):     {"Intact": 0.08, "Cosmetic": 0.22, "SevereLoss": 0.70},
        ("Fragile", "Severe", "Dangerous"):  {"Intact": 0.02, "Cosmetic": 0.13, "SevereLoss": 0.85},

        # --- High-Risk Precision Electronics & Optical Sensors ---
        ("HighRisk", "Mild", "Stable"):      {"Intact": 0.82, "Cosmetic": 0.14, "SevereLoss": 0.04},
        ("HighRisk", "Mild", "Dangerous"):   {"Intact": 0.60, "Cosmetic": 0.25, "SevereLoss": 0.15},
        ("HighRisk", "Moderate", "Stable"):  {"Intact": 0.25, "Cosmetic": 0.35, "SevereLoss": 0.40},
        ("HighRisk", "Moderate", "Dangerous"):{"Intact": 0.12, "Cosmetic": 0.28, "SevereLoss": 0.60},
        ("HighRisk", "Severe", "Stable"):    {"Intact": 0.04, "Cosmetic": 0.16, "SevereLoss": 0.80},
        ("HighRisk", "Severe", "Dangerous"): {"Intact": 0.01, "Cosmetic": 0.09, "SevereLoss": 0.90},
    }

    @classmethod
    def discretize_evidence(
        cls,
        product_category_str: str,
        drop_height_m: float,
        kinetic_energy_j: float,
        rough_decel_mps2: float,
        tilt_deg: float,
        overhang_pct: float
    ) -> Dict[str, str]:
        """
        Maps continuous computer-vision kinematic telemetry into discrete Bayesian node states.
        """
        cat_lower = product_category_str.lower()
        if "glass" in cat_lower or "ceramic" in cat_lower or "perishable" in cat_lower:
            f_state = "Fragile"
        elif "electronic" in cat_lower or "fragile" in cat_lower:
            f_state = "HighRisk"
        else:
            f_state = "Durable"

        # Discretize Drop Height
        if drop_height_m < 0.45:
            h_state = "Low"
        elif drop_height_m <= 1.05:
            h_state = "Medium"
        else:
            h_state = "High"

        # Discretize Impact (combines Deceleration and Kinetic Energy)
        if rough_decel_mps2 > 17.0 or kinetic_energy_j > 65.0:
            i_state = "Severe"
        elif rough_decel_mps2 > 9.0 or kinetic_energy_j > 25.0:
            i_state = "Moderate"
        else:
            i_state = "Mild"

        # Discretize Tilt & Stability
        if tilt_deg >= 12.0 or overhang_pct >= 22.0:
            t_state = "Dangerous"
        else:
            t_state = "Stable"

        return {
            "Fragility": f_state,
            "DropHeight": h_state,
            "ImpactShock": i_state,
            "TiltHazard": t_state
        }

    @classmethod
    def infer_damage_probability(
        cls,
        evidence: Dict[str, str]
    ) -> BayesianInferenceResult:
        """
        Exact Inference by Enumeration over the DAG using Bayes' Theorem.
        Computes P(InternalDamage = d | e).
        """
        f = evidence.get("Fragility", "Durable")
        h = evidence.get("DropHeight", "Low")
        i = evidence.get("ImpactShock", "Mild")
        t = evidence.get("TiltHazard", "Stable")

        # Unnormalized likelihoods: L(d) = P(F=f) * P(H=h) * P(T=t) * P(I=i | H=h) * P(D=d | F=f, I=i, T=t)
        p_f = cls.PRIOR_FRAGILITY.get(f, 0.33)
        p_h = cls.PRIOR_DROP_HEIGHT.get(h, 0.33)
        p_t = cls.PRIOR_TILT.get(t, 0.50)
        p_i_given_h = cls.CPT_IMPACT_GIVEN_HEIGHT.get(h, {}).get(i, 0.33)

        cpt_slice = cls.CPT_DAMAGE.get((f, i, t), {"Intact": 0.33, "Cosmetic": 0.33, "SevereLoss": 0.34})

        # Calculate joint numerator for each state of Damage
        unnorm = {}
        for d_state in cls.STATES_DAMAGE:
            p_d_given_fit = cpt_slice.get(d_state, 0.0)
            unnorm[d_state] = p_f * p_h * p_t * p_i_given_h * p_d_given_fit

        # Normalization constant (Marginal Evidence Likelihood alpha = 1 / sum)
        total = sum(unnorm.values())
        if total == 0:
            total = 1e-9

        posteriors = {d: round(unnorm[d] / total, 4) for d in cls.STATES_DAMAGE}

        # Determine most probable outcome
        best_state = max(posteriors.keys(), key=lambda k: posteriors[k])
        confidence = round(posteriors[best_state] * 100.0, 1)

        # Mathematical derivation for presentation / academic viva
        derivation = [
            f"1. Prior Evidence Instantiated: F={f} (P={p_f:.2f}), H={h} (P={p_h:.2f}), T={t} (P={p_t:.2f})",
            f"2. Kinematic Likelihood: P(Impact={i} | Height={h}) = {p_i_given_h:.2f}",
            f"3. CPT Slice Query P(Damage | F={f}, I={i}, T={t}): Intact={cpt_slice['Intact']}, Cosmetic={cpt_slice['Cosmetic']}, SevereLoss={cpt_slice['SevereLoss']}",
            f"4. Evidence Marginal P(e) = sum_d P(D=d, e) = {total:.6f}",
            f"5. Posterior via Bayes' Rule P(Damage=SevereLoss | e) = {posteriors['SevereLoss'] * 100.0:.1f}%"
        ]

        return BayesianInferenceResult(
            p_intact=posteriors["Intact"],
            p_cosmetic=posteriors["Cosmetic"],
            p_severe_loss=posteriors["SevereLoss"],
            most_probable_state=best_state,
            confidence_pct=confidence,
            observed_evidence=evidence,
            mathematical_derivation=derivation
        )

# Module singleton
bayesian_engine = WarehouseDamageBayesianNetwork()
