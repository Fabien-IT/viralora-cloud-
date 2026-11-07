#!/usr/bin/env python3
"""Build vertical motion-card MP4 drafts using Pillow, eSpeak NG and FFmpeg."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG1, BG2 = (12, 10, 25), (38, 18, 70)
WHITE, MUTED, ACCENT = (248, 246, 255), (190, 183, 210), (150, 105, 255)

def run(cmd):
    subprocess.run(cmd, check=True)

def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [Path("/usr/share/fonts/truetype/dejavu") / name,
                  Path("/usr/share/fonts/truetype/liberation2") / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf")]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def make_card(path, brand, title, label, idx, total):
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    # Vertical gradient, drawn in horizontal bands for reasonable runtime.
    for y in range(H):
        t = y / H
        color = tuple(int(BG1[k] * (1 - t) + BG2[k] * t) for k in range(3))
        draw.line((0, y, W, y), fill=color)
    draw.ellipse((690, 160, 1220, 690), outline=(82, 58, 130), width=8)
    draw.ellipse((-220, 1190, 390, 1810), outline=(70, 48, 112), width=8)
    draw.rounded_rectangle((76, 90, 1004, 180), radius=34, fill=(54, 36, 88))
    draw.text((112, 112), brand.upper(), font=font(40, True), fill=WHITE)
    draw.text((900, 117), f"{idx:02d}/{total:02d}", font=font(34, True), fill=MUTED)
    y = 480
    for line in wrap(draw, title, font(74, True), 850)[:3]:
        draw.text((100, y), line, font=font(74, True), fill=WHITE)
        y += 96
    draw.rounded_rectangle((88, 1050, 992, 1490), radius=44, fill=(29, 23, 48), outline=ACCENT, width=5)
    y = 1130
    for line in wrap(draw, label, font(54, True), 790)[:5]:
        draw.text((145, y), line, font=font(54, True), fill=WHITE)
        y += 76
    draw.text((100, 1760), "CONTENT WITHOUT BORDERS", font=font(30, True), fill=MUTED)
    im.save(path, quality=95)

def synthesize(text, lang, out):
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        raise RuntimeError("eSpeak NG is not installed")
    run([exe, "-v", lang, "-s", "148", "-w", str(out), text])

def audio_duration(ffprobe, audio):
    value = subprocess.check_output(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
        text=True
    ).strip()
    return max(float(value) + 0.45, 2.0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="content/queue.json")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("FFmpeg and ffprobe are required")
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    videos = data.get("videos", [])
    if len(videos) != 2 or {v.get("language") for v in videos} != {"fr", "en"}:
        raise ValueError("Queue must contain exactly one fr and one en video")
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    tmp = outdir / "_work"
    tmp.mkdir(exist_ok=True)
    try:
        for video in videos:
            lang = video["language"]
            scenes = video.get("scenes", [])
            if not scenes:
                raise ValueError(f"{lang}: no scenes")
            narration = [video.get("hook", "")] + [s["narration"] for s in scenes] + [video.get("cta", "")]
            labels = [video.get("hook", "")] + [s["screen_text"] for s in scenes] + [video.get("cta", "")]
            segments = []
            for i, (spoken, label) in enumerate(zip(narration, labels), 1):
                wav, png, mp4 = (tmp / f"{lang}_{i}.{ext}" for ext in ("wav", "png", "mp4"))
                synthesize(spoken, lang, wav)
                make_card(png, data.get("brand", "VIRALORA"), video["title"], label, i, len(narration))
                duration = audio_duration(ffprobe, wav)
                run([ffmpeg, "-y", "-loop", "1", "-framerate", "25", "-i", str(png),
                     "-i", str(wav), "-t", f"{duration:.3f}",
                     "-vf", "scale=1080:1920,zoompan=z='min(zoom+0.0005,1.04)':d=1:s=1080x1920:fps=25,format=yuv420p",
                     "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
                     "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", str(mp4)])
                segments.append(mp4)
            listing = tmp / f"{lang}_concat.txt"
            listing.write_text("".join(f"file '{p.resolve()}'\n" for p in segments), encoding="utf-8")
            final = outdir / f"viralora_{lang}.mp4"
            run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                 "-c", "copy", "-movflags", "+faststart", str(final)])
            print(f"Created {final}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
