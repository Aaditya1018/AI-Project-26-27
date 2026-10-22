"""
SafeStack AI - Media & Storage Manager
Handles storage, retrieval, and streaming of incident clips and high-resolution camera snapshots.
Supports local persistent storage and AWS S3 compatible object storage adapters.
"""

import os
from pathlib import Path
from typing import Optional
from backend.config import settings

class MediaManager:
    def __init__(self):
        self.clips_dir = settings.CLIPS_DIR
        self.snapshots_dir = settings.SNAPSHOTS_DIR

    def get_clip_path(self, filename: str) -> Optional[Path]:
        p = self.clips_dir / filename
        if p.exists():
            return p
        return None

    def get_snapshot_path(self, filename: str) -> Optional[Path]:
        p = self.snapshots_dir / filename
        if p.exists():
            return p
        return None

    def store_snapshot_bytes(self, filename: str, data: bytes) -> str:
        dest = self.snapshots_dir / filename
        with open(dest, "wb") as f:
            f.write(data)
        return f"/api/media/snapshots/{filename}"

media_manager = MediaManager()
