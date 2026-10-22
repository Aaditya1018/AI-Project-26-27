#!/usr/bin/env python3
"""
SafeStack AI - Custom Video Injection CLI Utility
Injects an arbitrary video file into a loading bay feed and processes it through
the computer-vision damage detection and risk scoring pipeline.
"""

import argparse
import sys
import os
import shutil
from pathlib import Path

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings
from backend.cv_pipeline.video_processor import InjectedVideoProcessor
from backend.simulation.scenario_runner import simulator
from backend.models.schemas import ProductCategory

def main():
    parser = argparse.ArgumentParser(description="Inject a video file into SafeStack AI")
    parser.add_argument("--video", "-v", required=True, help="Path to input video file (.mp4, .avi, .mov)")
    parser.add_argument("--bay", "-b", default="BAY-01", choices=["BAY-01", "BAY-02", "BAY-03", "BAY-04"], help="Target loading bay")
    parser.add_argument("--category", "-c", default="Electronics & Fragile", help="Cargo vulnerability category")
    parser.add_argument("--process-offline", action="store_true", help="Run full offline incident scan on video")

    args = parser.parse_args()
    video_path = Path(args.video).resolve()

    if not video_path.exists():
        print(f"❌ Error: Video file not found at {video_path}")
        sys.exit(1)

    print("==================================================================")
    print("  🛡️  SafeStack AI: Custom Video Injection Utility  ")
    print("==================================================================")
    print(f"• Input Video: {video_path.name} ({round(video_path.stat().st_size / (1024*1024), 2)} MB)")
    print(f"• Target Bay:  {args.bay}")
    print(f"• Category:    {args.category}")

    # Copy video to uploads directory
    dest = settings.UPLOADS_DIR / video_path.name
    shutil.copy2(video_path, dest)
    print(f"✅ Video copied to SafeStack media store: {dest}")

    # Set as active feed for bay
    simulator.set_bay_video(args.bay, str(dest))
    print(f"✅ Live camera stream for {args.bay} updated to display {video_path.name}!")
    print(f"🌐 View live at: http://localhost:8000/api/bays/{args.bay}/stream")

    if args.process_offline:
        print("\n🔍 Running full computer-vision damage detection scan...")
        processor = InjectedVideoProcessor(str(dest))
        try:
            cat_enum = ProductCategory(args.category)
        except Exception:
            cat_enum = ProductCategory.GENERAL_CARGO

        incidents = processor.process_and_detect_events(
            bay_id=args.bay,
            category=cat_enum
        )
        print(f"✅ Analysis complete! Detected {len(incidents)} damage-risk incidents.")
        for inc in incidents:
            print(f"  • [{inc['id']}] {inc['behavior_name']} — Risk {inc['risk_score']} ({inc['risk_tier']})")

    print("\n🚀 Ready! Open your dashboard at http://localhost:5173 or http://localhost:8000")

if __name__ == "__main__":
    main()
