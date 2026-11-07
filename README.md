# VIRALORA Cloud Starter

A zero-cost-first starter for building two vertical video drafts (French + English) on GitHub-hosted runners. It does not publish to social networks.

## What this version does
- Reads exactly two original scripts from `content/queue.json` (one French, one English).
- Creates 1080x1920 MP4 motion-card drafts using Pillow, FFmpeg and eSpeak NG.
- Runs manually from GitHub Actions; no paid API, token, or social password is required.
- Uploads MP4 drafts as workflow artifacts retained for 3 days.

## Honest limitations
This is a motion-card video generator, not generative AI text-to-video. eSpeak NG voices are synthetic and basic. The sample queue is demonstration content, not a daily trend-researched feed. This repository does not automatically research trends, write fresh scripts, or publish posts. Free services have quotas and policy limits; do not enable paid runners or billing.

GitHub Actions is event-triggered cloud execution, not a continuously running server. Scheduled content generation is intentionally not enabled until a reliable, authorized source for fresh scripts is connected.

## Run
1. Open **Actions** in this repository and enable workflows if prompted.
2. Select **VIRALORA - Build Draft Videos**.
3. Select **Run workflow**.
4. When the run completes, download the `viralora-drafts` artifact.

## Edit the content
Update `content/queue.json`. It must contain exactly one `fr` and one `en` entry. Each scene contains narration and on-screen text.

## Local requirements
Python 3.11+, FFmpeg, eSpeak NG, and the packages in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python scripts/build_videos.py --input content/queue.json --output dist
python scripts/validate_videos.py dist
```

## Publishing and security
Publishing is deliberately absent. Do not add social publishing until official API eligibility, permissions, OAuth authorization, and user consent are verified. Never commit passwords, access tokens, OTPs, or private account data. No purchase or social publication is performed by this project.
