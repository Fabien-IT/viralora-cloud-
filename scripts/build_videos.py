#!/usr/bin/env python3
"""Create illustrated vertical VIRALORA drafts with scene-matched voice and captions."""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG_TOP, BG_BOTTOM = (8, 13, 31), (27, 18, 53)
WHITE, MUTED, PURPLE = (250, 248, 255), (190, 195, 218), (151, 113, 255)
GREEN, SOIL = (106, 205, 145), (91, 62, 49)

def run(cmd):
    subprocess.run(cmd, check=True)

def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for p in (Path("/usr/share/fonts/truetype/dejavu") / name,
              Path("/usr/share/fonts/truetype/liberation2") / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf")):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def centered(draw, text, y, fnt, fill, max_width=900):
    lines = wrap(draw, text, fnt, max_width)
    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (box[2] - box[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += (box[3] - box[1]) + 18
    return y

def draw_plant(draw, stage):
    # A clear visual metaphor: seed -> germination -> sprout -> young tree.
    ground = 1120
    draw.rectangle((0, ground, W, H), fill=(20, 31, 42))
    draw.rectangle((0, ground, W, ground + 24), fill=SOIL)
    for x in range(40, W, 95):
        draw.ellipse((x, ground + 70, x + 10, ground + 80), fill=(111, 91, 80))
    cx = W // 2
    if stage == 0:
        draw.ellipse((cx-95, ground-90, cx+95, ground+75), fill=(193, 144, 83), outline=(244, 203, 137), width=8)
        draw.arc((cx-48, ground-45, cx+48, ground+30), 10, 170, fill=(111, 72, 48), width=8)
        draw.text((cx-180, ground+220), "01  •  THE SEED", font=font(34, True), fill=MUTED)
    else:
        # Root system grows downward in visible branches.
        root_len = min(stage, 3) * 95
        draw.line((cx, ground-5, cx, ground+root_len), fill=(226, 194, 142), width=18)
        if stage >= 2:
            for sign in (-1, 1):
                draw.line((cx, ground+65, cx+sign*95, ground+155), fill=(226,194,142), width=12)
                draw.line((cx+sign*95, ground+155, cx+sign*145, ground+220), fill=(226,194,142), width=8)
        height = 190 if stage == 1 else (390 if stage == 2 else 570)
        draw.line((cx, ground, cx, ground-height), fill=GREEN, width=25)
        if stage >= 2:
            draw.ellipse((cx-185, ground-height+80, cx-5, ground-height+210), fill=(73, 174, 111))
            draw.ellipse((cx+5, ground-height+10, cx+185, ground-height+145), fill=(89, 194, 125))
        if stage >= 3:
            draw.ellipse((cx-250, ground-height-130, cx-35, ground-height+40), fill=(77, 181, 113))
            draw.ellipse((cx+35, ground-height-170, cx+250, ground-height+10), fill=(91, 198, 125))
            draw.ellipse((cx-115, ground-height-270, cx+115, ground-height-40), fill=(111, 211, 139))
        draw.text((cx-180, ground+220), f"0{stage+1}  •  GROWTH", font=font(34, True), fill=MUTED)

def make_scene(path, brand, title, caption, idx, total, language):
    im = Image.new("RGB", (W, H))
    pix = im.load()
    for y in range(H):
        t = y / H
        c = tuple(int(BG_TOP[k]*(1-t)+BG_BOTTOM[k]*t) for k in range(3))
        for x in range(W):
            pix[x,y] = c
    d = ImageDraw.Draw(im)
    # Branded header and subtle graphic accents.
    d.rounded_rectangle((58, 70, 1022, 166), radius=42, fill=(40, 35, 73), outline=(91, 76, 139), width=2)
    d.text((100, 94), brand.upper(), font=font(42, True), fill=WHITE)
    d.text((865, 103), f"{idx:02d}/{total:02d}", font=font(32, True), fill=MUTED)
    centered(d, title, 245, font(66, True), WHITE, 900)
    stage = min(max(idx-1, 0), 3)
    draw_plant(d, stage)
    # Caption panel sits above illustration to stay readable on phones.
    panel=(70, 1390, 1010, 1705)
    d.rounded_rectangle(panel, radius=42, fill=(12, 17, 36), outline=PURPLE, width=4)
    lines=wrap(d, caption, font(49, True), 800)[:4]
    heights=sum(d.textbbox((0,0),s,font=font(49,True))[3]+22 for s in lines)
    y=panel[1]+(panel[3]-panel[1]-heights)//2
    for line in lines:
        box=d.textbbox((0,0),line,font=font(49,True))
        d.text(((W-(box[2]-box[0]))//2,y),line,font=font(49,True),fill=WHITE)
        y += box[3]+22
    footer = "DÉCOUVRIR • APPRENDRE • PARTAGER" if language=="fr" else "DISCOVER • LEARN • SHARE"
    centered(d, footer, 1790, font(27, True), MUTED, 950)
    im.save(path, quality=94)

def synthesize(text, lang, out):
    """Neural speech from offline Piper voice models; never silently fall back to eSpeak."""
    import os
    exe=shutil.which("piper")
    if not exe:
        raise RuntimeError("Piper TTS is missing. Install piper-tts.")
    model=Path("models") / ("fr_FR-tom-medium.onnx" if lang=="fr" else "en_US-ryan-medium.onnx")
    if not model.exists() or not Path(str(model)+".json").exists():
        raise RuntimeError(f"Missing neural voice model: {model}")
    # Slightly slower speech for a documentary cadence. Pitch is intrinsic to the voice.
    result=subprocess.run([exe,"--model",str(model),"--output_file",str(out),
                           "--length_scale","1.12"],
                          input=text,text=True,check=True,capture_output=True)
    if not out.exists() or out.stat().st_size < 1000:
        raise RuntimeError(f"Voice generation failed: {result.stderr}")


def duration_of(ffprobe, audio):
    s=subprocess.check_output([ffprobe,"-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],text=True).strip()
    return max(float(s)+0.65,2.2)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="content/queue.json")
    ap.add_argument("--output",default="dist")
    a=ap.parse_args()
    ffmpeg,ffprobe=shutil.which("ffmpeg"),shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("FFmpeg and ffprobe are required")
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    videos=data.get("videos",[])
    if len(videos)!=2 or {v.get("language") for v in videos}!={"fr","en"}:
        raise ValueError("Queue must contain exactly one fr and one en video")
    out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    tmp=out/"_work"; tmp.mkdir(exist_ok=True)
    try:
        for video in videos:
            lang=video["language"]; scenes=video.get("scenes",[])
            if not scenes: raise ValueError(f"{lang}: no scenes")
            spoken=[video.get("hook","")]+[s["narration"] for s in scenes]+[video.get("cta","")]
            captions=[video.get("hook","")]+[s["screen_text"] for s in scenes]+[video.get("cta","")]
            clips=[]
            for i,(words,caption) in enumerate(zip(spoken,captions),1):
                wav=tmp/f"{lang}_{i}.wav"; png=tmp/f"{lang}_{i}.png"; mp4=tmp/f"{lang}_{i}.mp4"
                synthesize(words,lang,wav)
                make_scene(png,data.get("brand","VIRALORA"),video["title"],caption,i,len(spoken),lang)
                dur=duration_of(ffprobe,wav)
                # Gentle zoom and full-duration narration; each caption remains visible for its spoken scene.
                run([ffmpeg,"-y","-loop","1","-framerate","25","-i",str(png),"-i",str(wav),
                     "-t",f"{dur:.3f}","-vf","scale=1080:1920,zoompan=z='min(zoom+0.00035,1.025)':d=1:s=1080x1920:fps=25,format=yuv420p",
                     "-c:v","libx264","-preset","ultrafast","-crf","24","-c:a","aac","-b:a","112k",
                     "-shortest","-movflags","+faststart",str(mp4)])
                clips.append(mp4)
            listing=tmp/f"{lang}_concat.txt"
            listing.write_text("".join(f"file '{p.resolve()}'\n" for p in clips),encoding="utf-8")
            final=out/f"viralora_{lang}.mp4"
            run([ffmpeg,"-y","-f","concat","-safe","0","-i",str(listing),"-c","copy","-movflags","+faststart",str(final)])
            print(f"Created {final}")
    finally:
        shutil.rmtree(tmp,ignore_errors=True)

if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"ERROR: {e}",file=sys.stderr); sys.exit(1)
