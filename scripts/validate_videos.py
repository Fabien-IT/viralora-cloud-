#!/usr/bin/env python3
"""Validate that both expected vertical MP4 files exist and have the right dimensions."""
import shutil
import subprocess
import sys
from pathlib import Path

ffprobe = shutil.which("ffprobe")
if not ffprobe:
    raise SystemExit("ffprobe is required")
folder = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
for name in ("viralora_fr.mp4", "viralora_en.mp4"):
    path = folder / name
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    result = subprocess.check_output([
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(path)
    ], text=True).strip()
    if result != "1080x1920":
        raise SystemExit(f"{name}: expected 1080x1920, got {result}")
    print(f"OK {name}: {result}")
