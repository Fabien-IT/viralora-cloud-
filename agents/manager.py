#!/usr/bin/env python3
"""VIRALORA manager: coordinates a zero-cost, human-reviewed production pipeline."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def run_step(label: str, command: list[str]) -> None:
    print(f"\n=== {label} ===", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default="content/queue.json")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    queue = ROOT / args.queue
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    data = json.loads(queue.read_text(encoding="utf-8"))
    languages = [v.get("language") for v in data.get("videos", [])]
    if len(languages) != 2 or sorted(languages) != ["en", "fr"]:
        raise SystemExit("Manager stopped: queue must contain exactly one French and one English video.")
    run_step("Quality agent — validate editorial queue", [sys.executable, "agents/quality.py", "--queue", args.queue])
    run_step("Production agent — render vertical videos", [sys.executable, "scripts/build_videos.py", "--input", args.queue, "--output", args.output])
    run_step("Quality agent — validate MP4 outputs", [sys.executable, "scripts/validate_videos.py", args.output])
    manifest = {
        "brand": "VIRALORA",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_human_review",
        "publishing_enabled": False,
        "videos": [{"language": v["language"], "title": v["title"], "file": f"viralora_{v['language']}.mp4", "reviewed": False} for v in data["videos"]],
        "review_instructions": "Watch both MP4s and approve them manually. No social publishing is connected in this release."
    }
    (output / "review-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nVIRALORA pipeline completed. Both drafts are awaiting human review.")
    print("No social post was published.")

if __name__ == "__main__":
    main()
