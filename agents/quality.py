#!/usr/bin/env python3
"""Editorial safety and completeness checks for VIRALORA draft scripts."""
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--queue",default="content/queue.json"); a=p.parse_args()
    data=json.loads(Path(a.queue).read_text(encoding="utf-8"))
    videos=data.get("videos",[])
    if len(videos)!=2 or {v.get("language") for v in videos}!={"fr","en"}:
        raise SystemExit("Expected exactly one fr and one en video.")
    for v in videos:
        lang=v["language"]
        for field in ("title","hook","scenes","cta"):
            if not v.get(field): raise SystemExit(f"{lang}: missing {field}")
        if len(v["scenes"]) < 3: raise SystemExit(f"{lang}: at least 3 scenes required.")
        for i,s in enumerate(v["scenes"],1):
            if not s.get("narration") or not s.get("screen_text"):
                raise SystemExit(f"{lang}: scene {i} needs narration and screen_text.")
            if len(s["narration"].split()) > 45:
                raise SystemExit(f"{lang}: scene {i} narration is too long for a short video.")
        print(f"OK {lang}: {v['title']} ({len(v['scenes'])} scenes)")
    print("Editorial structure checks passed. Human factual review is still required.")

if __name__=="__main__": main()
