"""
SafeStack AI - Video Synthesizer & Warehouse Scene Generator
Generates realistic simulated warehouse loading bay video frames, kinematic trajectories,
and MP4/JPEG evidence files demonstrating the 10 damage-risk behaviors.
"""

import math
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from backend.config import settings

class WarehouseSceneSynthesizer:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height

    def render_base_warehouse(self) -> np.ndarray:
        """
        Renders a clean, realistic warehouse loading bay backdrop:
        Concrete floor, walls, yellow hazard transit lines, dock door, and shelving.
        """
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Upper wall (dark industrial slate)
        wall_h = int(self.height * 0.45)
        frame[0:wall_h, :] = [38, 42, 48]

        # Lower floor (polished industrial concrete)
        frame[wall_h:, :] = [75, 80, 85]

        # Perspective lines for depth
        try:
            import cv2
            # Dock roller door outline
            cv2.rectangle(frame, (int(self.width * 0.25), 20), (int(self.width * 0.75), wall_h), (55, 60, 68), -1)
            cv2.rectangle(frame, (int(self.width * 0.25), 20), (int(self.width * 0.75), wall_h), (90, 95, 105), 2)
            
            # Roll-up door horizontal slats
            for y in range(40, wall_h, 25):
                cv2.line(frame, (int(self.width * 0.25), y), (int(self.width * 0.75), y), (48, 52, 58), 1)

            # Yellow pedestrian hazard safety lines on the floor
            cv2.line(frame, (40, self.height - 10), (int(self.width * 0.32), wall_h), (20, 210, 240), 4)
            cv2.line(frame, (self.width - 40, self.height - 10), (int(self.width * 0.68), wall_h), (20, 210, 240), 4)
            
            # Dock leveling bridge plate
            cv2.rectangle(frame, (int(self.width * 0.35), wall_h - 10), (int(self.width * 0.65), wall_h + 35), (50, 55, 60), -1)
            cv2.rectangle(frame, (int(self.width * 0.35), wall_h - 10), (int(self.width * 0.65), wall_h + 35), (20, 210, 240), 2)
        except Exception:
            pass

        return frame

    def draw_entity(self, frame: np.ndarray, entity_type: str, bbox: List[float], label: str = "", color: Tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
        """
        Draws visual representation of person, carton, pallet, or forklift on the frame.
        bbox: [center_x, center_y, width, height]
        """
        cx, cy, w, h = bbox
        x1 = max(0, int(cx - w / 2))
        x2 = min(self.width, int(cx + w / 2))
        y1 = max(0, int(cy - h / 2))
        y2 = min(self.height, int(cy + h / 2))

        try:
            import cv2
            if entity_type == "pallet":
                # Wooden pallet
                cv2.rectangle(frame, (x1, y1), (x2, y2), (42, 85, 140), -1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (65, 120, 180), 2)
                # Pallet fork slots
                slot_w = int((x2 - x1) * 0.28)
                cv2.rectangle(frame, (x1 + 15, y2 - 12), (x1 + 15 + slot_w, y2), (25, 30, 35), -1)
                cv2.rectangle(frame, (x2 - 15 - slot_w, y2 - 12), (x2 - 15, y2), (25, 30, 35), -1)

            elif entity_type == "carton":
                # Corrugated cardboard box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (60, 130, 195), -1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (85, 160, 230), 2)
                # Packaging tape line
                cv2.line(frame, (x1, int(cy)), (x2, int(cy)), (45, 100, 150), 3)

            elif entity_type == "person":
                # Worker body & high-vis vest
                # Head
                cv2.circle(frame, (int(cx), int(y1 + h * 0.16)), int(w * 0.22), (180, 190, 205), -1)
                # High-vis yellow safety vest
                cv2.rectangle(frame, (int(cx - w * 0.35), int(y1 + h * 0.32)), (int(cx + w * 0.35), int(y1 + h * 0.70)), (15, 220, 235), -1)
                # Trousers / legs
                cv2.line(frame, (int(cx - w * 0.18), int(y1 + h * 0.70)), (int(cx - w * 0.18), y2), (70, 70, 80), int(w * 0.25))
                cv2.line(frame, (int(cx + w * 0.18), int(y1 + h * 0.70)), (int(cx + w * 0.18), y2), (70, 70, 80), int(w * 0.25))

            elif entity_type == "forklift":
                # Forklift chassis (Safety Yellow)
                cv2.rectangle(frame, (x1, y1 + int(h * 0.3)), (x2, y2), (10, 185, 235), -1)
                # Overhead cage
                cv2.rectangle(frame, (x1 + 10, y1), (x2 - 25, y1 + int(h * 0.35)), (40, 45, 50), 3)
                # Wheels
                cv2.circle(frame, (x1 + 25, y2), 16, (20, 22, 25), -1)
                cv2.circle(frame, (x2 - 25, y2), 16, (20, 22, 25), -1)
                # Fork mast
                cv2.line(frame, (x2, y1), (x2, y2), (60, 65, 75), 6)
                cv2.line(frame, (x2, y2 - 5), (x2 + 35, y2 - 5), (60, 65, 75), 5)

            if label:
                cv2.putText(frame, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
        except Exception:
            pass

        return frame

    def generate_scenario_frames(self, scenario_name: str, total_frames: int = 45) -> List[np.ndarray]:
        """
        Generates an animated sequence of frames illustrating a specific scenario.
        """
        frames: List[np.ndarray] = []
        total_frames = max(1, int(total_frames))

        for f in range(total_frames):
            frame = self.render_base_warehouse()
            progress = 0.0 if total_frames == 1 else f / float(total_frames - 1)  # 0.0 to 1.0

            # Base stationary pallet
            pallet_bbox = [self.width * 0.52, self.height * 0.82, self.width * 0.32, self.height * 0.12]
            frame = self.draw_entity(frame, "pallet", pallet_bbox, "Standard Pallet")

            if scenario_name == "BEH_DROP":
                # Worker carrying, then slips and carton freefalls
                worker_x = self.width * 0.35
                worker_y = self.height * 0.58
                frame = self.draw_entity(frame, "person", [worker_x, worker_y, 70, 160], "Operator #14")

                # Drop trajectory with acceleration (y ~ 0.5 * g * t^2)
                if progress < 0.35:
                    box_y = self.height * 0.55
                else:
                    t_drop = (progress - 0.35) / 0.65
                    box_y = min(self.height * 0.88, self.height * 0.55 + 240 * (t_drop ** 2))

                frame = self.draw_entity(frame, "carton", [self.width * 0.48, box_y, 65, 60], "Electronics Crate", (0, 0, 255) if progress >= 0.35 else (255, 255, 255))

            elif scenario_name == "BEH_DRAG":
                # Worker pulling carton along floor
                pull_x = self.width * 0.20 + (self.width * 0.45) * progress
                frame = self.draw_entity(frame, "person", [pull_x - 55, self.height * 0.68, 70, 150], "Worker")
                frame = self.draw_entity(frame, "carton", [pull_x, self.height * 0.88, 75, 55], "Heavy Crate (Dragging)", (0, 140, 255))

            elif scenario_name == "BEH_IMPROPER_STACK":
                # Inverted pyramid: large crate balanced precariously atop smaller crate
                base_crate = [self.width * 0.52, self.height * 0.72, 60, 50]
                tilt_offset = math.sin(progress * 6.28) * 12
                top_crate = [self.width * 0.52 + tilt_offset, self.height * 0.54, 110, 80]
                frame = self.draw_entity(frame, "carton", base_crate, "Base Box (Small)")
                frame = self.draw_entity(frame, "carton", top_crate, "Heavy Inverted Stack", (0, 69, 255))

            elif scenario_name == "BEH_PALLET_OVERHANG":
                # Carton hanging 35% over the edge of the pallet
                overhang_box = [pallet_bbox[0] + pallet_bbox[2] * 0.38, self.height * 0.73, 85, 65]
                frame = self.draw_entity(frame, "carton", overhang_box, "Overhanging Load (38%)", (0, 120, 255))
                frame = self.draw_entity(frame, "person", [self.width * 0.28, self.height * 0.65, 70, 160], "Operator")

            elif scenario_name == "BEH_TOSS_THROW":
                # Parabolic flight trajectory
                throw_x = self.width * 0.25 + (self.width * 0.48) * progress
                # Parabola: y = 4 * h * p * (1 - p)
                arc_h = 130
                throw_y = self.height * 0.65 - 4 * arc_h * progress * (1.0 - progress)
                frame = self.draw_entity(frame, "person", [self.width * 0.20, self.height * 0.65, 70, 160], "Sender")
                frame = self.draw_entity(frame, "person", [self.width * 0.82, self.height * 0.65, 70, 160], "Receiver")
                frame = self.draw_entity(frame, "carton", [throw_x, throw_y, 50, 45], "Airborne Parcel", (0, 0, 255))

            elif scenario_name == "BEH_FORKLIFT_PINCH":
                fl_x = self.width * 0.80 - (self.width * 0.35) * progress
                frame = self.draw_entity(frame, "forklift", [fl_x, self.height * 0.68, 140, 110], "Forklift #02")
                frame = self.draw_entity(frame, "person", [self.width * 0.32, self.height * 0.68, 70, 150], "Pedestrian (<1.5m)", (0, 0, 255))

            else:
                # Default normal loading operation
                frame = self.draw_entity(frame, "person", [self.width * 0.35, self.height * 0.65, 70, 160], "Operator")
                frame = self.draw_entity(frame, "carton", [self.width * 0.52, self.height * 0.73, 75, 65], "Secured Cargo")

            frames.append(frame)

        return frames

    def save_sample_evidence_files(self):
        """
        Synthesizes sample video clips and snapshot JPEGs into storage/media.
        """
        scenarios = {
            "sample_drop": "BEH_DROP",
            "sample_stack": "BEH_IMPROPER_STACK",
            "sample_throw": "BEH_TOSS_THROW",
            "sample_drag": "BEH_DRAG",
            "sample_forklift": "BEH_FORKLIFT_PINCH"
        }

        try:
            import cv2
            for clip_name, scenario_code in scenarios.items():
                frames = self.generate_scenario_frames(scenario_code, total_frames=30)
                
                # Save snapshot (mid frame)
                snap_path = settings.SNAPSHOTS_DIR / f"{clip_name}.jpg"
                cv2.imwrite(str(snap_path), frames[len(frames) // 2])

                # Save video clip
                clip_path = settings.CLIPS_DIR / f"{clip_name}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(clip_path), fourcc, 15.0, (self.width, self.height))
                for f in frames:
                    out.write(f)
                out.release()
        except Exception:
            pass
