"""
SafeStack AI - Kinematics & Physics Engine
Computes vertical acceleration, drop velocities, kinetic impact energy, tilt angles,
pallet overhang ratios, and pedestrian clearance distances.
"""

import math
from typing import List, Tuple, Dict, Any

class KinematicsEngine:
    def __init__(self, pixels_per_meter: float = 120.0, default_package_mass_kg: float = 10.0):
        self.ppm = pixels_per_meter
        self.default_mass = default_package_mass_kg

    def px_to_meters(self, px: float) -> float:
        return px / self.ppm

    def calculate_vertical_acceleration(self, track_accelerations: List[Tuple[float, float]]) -> float:
        """
        Calculates vertical acceleration in m/s^2.
        In image coords, positive Y is downwards.
        """
        if not track_accelerations:
            return 0.0
        # Take the most recent downwards acceleration
        recent_ay = [self.px_to_meters(a[1]) for a in list(track_accelerations)[-5:] if a[1] > 0]
        if not recent_ay:
            return 0.0
        return max(recent_ay)

    def calculate_drop_velocity(self, track_velocities: List[Tuple[float, float]]) -> float:
        """
        Calculates max downward velocity in m/s.
        """
        if not track_velocities:
            return 0.0
        downward_v = [self.px_to_meters(v[1]) for v in list(track_velocities)[-10:] if v[1] > 0]
        if not downward_v:
            return 0.0
        return max(downward_v)

    def calculate_kinetic_impact_energy(self, velocity_mps: float, mass_kg: float = None) -> float:
        """
        Kinetic energy formula: E_k = 0.5 * m * v^2 (Joules)
        """
        m = mass_kg if mass_kg is not None else self.default_mass
        return round(0.5 * m * (velocity_mps ** 2), 2)

    def calculate_landing_deceleration(self, pre_impact_velocity: float, impact_time_s: float = 0.05) -> float:
        """
        Deceleration upon striking floor / pallet: a = v / dt (m/s^2)
        """
        if impact_time_s <= 0:
            impact_time_s = 0.05
        return round(pre_impact_velocity / impact_time_s, 2)

    def calculate_tilt_angle(self, top_center: Tuple[float, float], base_center: Tuple[float, float]) -> float:
        """
        Calculates lean/tilt angle from vertical in degrees.
        """
        dx = top_center[0] - base_center[0]
        dy = base_center[1] - top_center[1]  # positive upwards
        if dy == 0:
            return 90.0
        radians = math.atan2(abs(dx), dy)
        return round(math.degrees(radians), 2)

    def calculate_pallet_overhang(self, box_bbox: List[float], pallet_bbox: List[float]) -> float:
        """
        Calculates percentage of box overhang outside pallet edges.
        bbox format: [center_x, center_y, width, height]
        """
        box_left = box_bbox[0] - box_bbox[2] / 2
        box_right = box_bbox[0] + box_bbox[2] / 2
        
        pallet_left = pallet_bbox[0] - pallet_bbox[2] / 2
        pallet_right = pallet_bbox[0] + pallet_bbox[2] / 2

        overhang_left = max(0.0, pallet_left - box_left)
        overhang_right = max(0.0, box_right - pallet_right)
        total_overhang_px = overhang_left + overhang_right

        if box_bbox[2] <= 0:
            return 0.0
        
        overhang_pct = (total_overhang_px / box_bbox[2]) * 100.0
        return round(min(100.0, overhang_pct), 2)

    def calculate_distance(self, bboxA: List[float], bboxB: List[float]) -> float:
        """
        Calculates Euclidean distance between centers in meters.
        """
        dx = self.px_to_meters(bboxA[0] - bboxB[0])
        dy = self.px_to_meters(bboxA[1] - bboxB[1])
        return round(math.sqrt(dx * dx + dy * dy), 2)
