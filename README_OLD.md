# AI Content Creator - Automated Video Generation Platform

🎬 Automated video content generation and distribution bot for TikTok, powered by Google Gemini AI and Veo video generation.

## 🚀 Features

### 🤖 AI Content Creator Bot
- **AI-powered script generation** using Google Gemini 2.0 Flash Thinking
- **Professional video creation** with Google Veo 3.1
- **Automated scheduling** (12:00 and 19:00 daily)
- **Multi-account rotation** for Labs API (4 accounts)
- **Telegram delivery** with formatted captions

### 📥 Link Downloader Bot
- **Download videos** from Instagram, TikTok, Facebook, YouTube, Twitter
- **Telegram integration** - send a link, get the video
- **Automatic cleanup** of temporary files
- **Platform detection** with format optimization

## 📁 Project Structure

```
bots/
├── content_creator_bot.py   # Main video generation bot
└── link_downloader_bot.py   # Social media downloader bot

services/
├── ai/
│   ├── screenwriter.py      # Script generation (Gemini)
│   └── marketer.py          # Marketing content (titles, hashtags)
├── video_generation/
│   ├── labs_veo_service.py  # Single account Veo service
│   ├── multi_account_labs_service.py  # Multi-account rotation
│   └── video_generator.py   # Video generation orchestrator
├── integrations/
│   ├── telegram_service.py  # Telegram Bot API wrapper
│   └── tiktok_service.py    # TikTok upload (manual)
└── downloads/
    └── video_downloader_service.py  # yt-dlp wrapper

config.py                     # Configuration management
```

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Google Gemini API key
- Google Labs API keys (4 accounts for rotation)
- Telegram Bot Token

### Setup

1. **Clone repository:**
```bash
git clone <repo-url>
cd "Post Tiktok"
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🎮 Usage

### AI Content Creator Bot (Video Generation)

```bash
# Run directly
python bots/content_creator_bot.py

# Run in background
nohup python bots/content_creator_bot.py > content_creator.log 2>&1 &
```

### Link Downloader Bot

```bash
# Run directly
python bots/link_downloader_bot. py

# Run in background
nohup python bots/link_downloader_bot.py > link_downloader.log 2>&1 &
```

Then send video links to your Telegram bot.

## 🏗️ Architecture

### Clean Code Principles Applied

- **Single Responsibility**: Each service has one clear purpose
- **Dependency Injection**: Services receive dependencies via constructor
- **Interface Segregation**: Small, focused interfaces
- **DRY**: Reusable formatters and utilities

### Service Layers

1. **AI Layer**: Script & marketing generation
2. **Video Generation**: Veo API integration with rotation
3. **Integration**: Telegram & TikTok
4. **Downloads**: Multi-platform video downloading

## 📊 Costs

- **Gemini**: FREE (1,500 req/day)
- **Veo**: FREE (40 videos/month with 4 accounts)
- **Telegram**: FREE (unlimited)

**Total: R$ 0.00/month**

## 🧹 Maintenance

```bash
# View logs
tail -f content_creator.log
tail -f link_downloader.log

# Stop bots
pkill -f content_creator_bot.py
pkill -f link_downloader_bot.py
```

## 📝 License

MIT License
