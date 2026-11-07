# VIRALORA AI Studio

A free-first, human-reviewed production pipeline for two vertical video drafts per run: one French and one English.

## Current release
- GitHub Actions cloud runner (public repository; standard GitHub-hosted runner).
- Offline Piper neural TTS voices (French and English).
- Pillow + FFmpeg vertical video rendering at 1080 × 1920.
- Manager coordinates editorial validation, rendering, technical validation and a review manifest.
- Drafts are uploaded as a GitHub Actions artifact for review.
- **No social publishing integration is enabled. No paid APIs, purchases, subscriptions or billing are used.**

## Run the Studio
1. Open the repository's **Actions** tab.
2. Select **VIRALORA AI Studio - Production**.
3. Press **Run workflow**.
4. Wait for the workflow to complete.
5. Download **viralora-review-package** from the run.
6. Watch both MP4s; the manifest marks them as awaiting human review.

Repository: https://github.com/Fabien-IT/viralora-cloud-

## Architecture
- `agents/manager.py`: orchestrates editorial validation, rendering and quality checks.
- `agents/quality.py`: checks bilingual queue completeness and script structure.
- `scripts/build_videos.py`: renders MP4s and synthesizes narration with Piper.
- `scripts/validate_videos.py`: validates 1080 × 1920 output.
- `studio/config.json`: declares free-only and human-review policies.
- `.github/workflows/studio.yml`: cloud production workflow.

## Honest limitations
This is a working production foundation, not yet a fully autonomous multi-agent AI newsroom. The scripts still come from `content/queue.json`; fresh trend research, LLM-generated scripts, advanced generative visuals, a web dashboard and official social publishing integrations remain future phases. The renderer currently creates motion-card visuals rather than fully generative cinematic footage. Offline voices are neural TTS, not studio voice actors.

GitHub Actions is event-triggered cloud compute, not an always-on server. Free quotas and retention limits apply. The workflow is manual and not scheduled daily. Do not add paid runners, API keys or billing without explicit approval.

## Local run
Python 3.11+, FFmpeg and Piper TTS are required.
```bash
python -m pip install -r requirements.txt piper-tts==1.3.0
python agents/quality.py --queue content/queue.json
python agents/manager.py --queue content/queue.json --output dist
python -m unittest discover -s tests -v
```

## Review and publishing policy
Every MP4 must be reviewed by a person. This repository does not publish to YouTube, Instagram, Facebook or TikTok. Publishing integrations require official API eligibility, OAuth authorization and explicit user approval.
