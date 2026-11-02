# DiscordBots

A monorepo containing two dedicated, standalone Discord bots:

1. **`jokebot`** — Delivers Reddit and Québécois audio jokes, roasts, compliments, and text-to-speech (TTS) voice announcements using xAI & Edge-TTS.
2. **`musicbot`** — Handles music playback from YouTube, web radio streaming categories, and Suno AI song playback with interactive playback controls.

---

## Architecture Overview

```
DiscordBots/
├── jokebot/                       # Joke, Roast, & TTS Bot
│   ├── Audio/                     # Local MP3 audio jokes (.mp3)
│   ├── commands/                  # JokeBot slash commands
│   │   ├── jokes.py               # /joke and /jokeqc
│   │   ├── tts.py                 # /say-vc
│   │   ├── say.py                 # /say-tc
│   │   ├── roast.py               # /roast
│   │   ├── compliment.py          # /compliment
│   │   ├── bot_mention.py         # Dynamic AI mention responder
│   │   ├── moderation.py          # /bloque, /debloque, /queue
│   │   ├── util.py                # /leave, /history
│   │   └── help.py                # /help
│   ├── audio_player.py            # Voice queue & audio player
│   ├── bot_instance.py            # Discord client initialization
│   ├── gpt_util.py                # xAI (Grok) client & prompt helpers
│   ├── guild_settings.py          # Server-specific voice & style settings
│   ├── history.py                 # Command audit history
│   ├── reddit_loader.py           # Reddit jokes fetcher
│   ├── tts_util.py                # Voice synthesis engine
│   ├── utils.py                   # Discord embed formatters
│   ├── main.py                    # Entry point
│   ├── Dockerfile                 # JokeBot Docker container
│   ├── requirements.txt           # JokeBot dependencies
│   └── config.json                # Encrypted configuration (Ansible Vault)
│
├── musicbot/                      # Music & Audio Streaming Bot
│   ├── commands/                  # MusicBot slash commands
│   │   ├── music.py               # /music (category rotation)
│   │   ├── yt.py                  # /yt and /ytsearch
│   │   ├── suno.py                # /suno
│   │   ├── moderation.py          # /bloque, /debloque, /queue
│   │   ├── util.py                # /leave, /history
│   │   ├── bot_mention.py         # Music help responder
│   │   └── help.py                # /help
│   ├── audio_player.py            # Voice queue & yt-dlp audio stream player
│   ├── bot_instance.py            # Discord client initialization
│   ├── history.py                 # Command audit history
│   ├── music_sources.json         # Music categories & streams
│   ├── utils.py                   # Discord embed formatters
│   ├── main.py                    # Entry point
│   ├── Dockerfile                 # MusicBot Docker container
│   ├── requirements.txt           # MusicBot dependencies
│   └── config.json                # Encrypted configuration (Ansible Vault)
│
└── .github/workflows/
    ├── jokebot.yml                # Builds & pushes ghcr.io/<owner>/jokebot
    └── musicbot.yml               # Builds & pushes ghcr.io/<owner>/musicbot
```

---

## GitHub Container Registry (GHCR) & File-Based Releases

Each bot is versioned via a simple `VERSION` file:
- `jokebot/VERSION`
- `musicbot/VERSION`

No Git tags or GitHub releases are needed!

| Bot | GHCR Image | Version File | Example |
| :--- | :--- | :--- | :--- |
| **JokeBot** | `ghcr.io/<owner>/jokebot:<version>` | `jokebot/VERSION` | `1.0.0` |
| **MusicBot** | `ghcr.io/<owner>/musicbot:<version>` | `musicbot/VERSION` | `1.0.0` |

### How to Release an Update
Whenever you update code or bump the version:
1. Edit `jokebot/VERSION` (or `musicbot/VERSION`) with the new version string (e.g. `1.0.1`).
2. Commit and push to `main`:
   ```bash
   git commit -am "Bump JokeBot to 1.0.1"
   git push origin main
   ```
3. GitHub Actions automatically reads the `VERSION` file and publishes **strictly one image** to GHCR:
   `ghcr.io/<owner>/jokebot:1.0.1` (or `musicbot:1.0.1`).

---

## Configuration

Secrets are passed directly at runtime via **Environment Variables** (lowercase with hyphens):
- `discord-token` (or `jokebot-discord-token` / `musicbot-discord-token`): Discord bot token.
- `xai-api-key`: xAI API key for Grok (used by `jokebot`).

The `config.json` files in each bot folder are unencrypted and store only non-sensitive behavioral settings (TTS voices, prompts, diversity angles, command prefixes).

### JokeBot `jokebot/config.json`
Contains Grok prompt definitions, TTS voice parameters, and intensity labels.

### MusicBot `musicbot/config.json`
Contains command prefix and bot configuration.

---

## Running Locally

### JokeBot
```bash
cd jokebot
pip install -r requirements.txt
env jokebot-discord-token="your_token" xai-api-key="your_key" python main.py
```

### MusicBot
```bash
cd musicbot
pip install -r requirements.txt
env musicbot-discord-token="your_token" python main.py
```

---

## Running with Docker

### JokeBot
```bash
docker build -t jokebot jokebot/
docker run -d --name jokebot \
  -e discord-token="your_token" \
  -e xai-api-key="your_key" \
  jokebot
```

### MusicBot
```bash
docker build -t musicbot musicbot/
docker run -d --name musicbot \
  -e discord-token="your_token" \
  musicbot
```
