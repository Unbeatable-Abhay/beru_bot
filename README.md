# ⚡ Beru Bot — AI Content Studio

> **Hackathon Project** · AI-powered social media content agent with a live web dashboard

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3.2-5865F2?style=flat-square&logo=discord)](https://discordpy.readthedocs.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-orange?style=flat-square)](https://groq.com)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat-square)](https://render.com)

---

## 🌐 Live Dashboard

**[beru-bot-t7c6.onrender.com](https://beru-bot-t7c6.onrender.com)**

Use all AI tools directly in your browser — no Discord account needed.

---

## 💡 What is Beru Bot?

Beru is a full-stack AI content agent built for the modern creator. It combines a **Discord bot** with a **web dashboard**, allowing anyone — with or without Discord — to generate professional social media content in seconds using the power of LLaMA 3.1 via Groq.

Whether you're a content creator, marketer, or startup founder, Beru handles the hardest part of content creation — writing.

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ **All-in-One Create** | Trend score + post + hashtags + virality prediction simultaneously |
| ✍️ **Post Generator** | Platform-optimised posts for YouTube, Instagram, LinkedIn, Twitter, WhatsApp |
| 🪝 **Hook Generator** | 5 scroll-stopping opening lines using proven psychological triggers |
| 🎬 **Script Writer** | Full 30–60s reel scripts with stage directions |
| 📸 **Caption Writer** | AI captions for photos and videos |
| 📊 **Trend Score** | Real-time trend analysis with momentum, urgency and best platform |
| 🏷️ **Hashtag Finder** | Hashtags grouped by reach (broad / medium / niche) |
| 🎙️ **Brand Voice** | Save your personal writing style — all content adapts to it |
| 💬 **Chat** | Talk to Beru directly for strategy and content advice |
| 🌗 **Dark / Light Mode** | Dashboard supports both themes with one click |

---

## 🛠️ Tech Stack

```
Discord.py      →  Bot framework
Groq API        →  LLaMA 3.1 8B Instant inference (ultra-fast)
Replicate       →  AI video generation (minimax/video-01)
Flask           →  Web dashboard backend
Python 3.11     →  Runtime
Render          →  Cloud deployment
GitHub          →  Version control & CI/CD
```

---

## 🚀 Commands

All commands use the `,` prefix.

```
,create   <platform> <topic>   All-in-one content suite
,post     <platform> <topic>   Write a social media post
,hook     <topic>              5 scroll-stopping hooks
,script   <topic>              30–60s reel script
,caption  <platform> <desc>    Caption for a photo/video
,trendscore <topic>            Trend score & analysis
,hashtags <platform> <topic>   Platform hashtag sets
,setvoice <description>        Save your brand voice
,myvoice                       View saved brand voice
,video    <prompt>             AI video generation
,poll     <question>           Create a Discord poll
,dashboard                     Get the dashboard link
,help                          Show all commands
```

**Supported platforms:** `youtube` · `instagram` · `linkedin` · `twitter` · `whatsapp`

---

## 📁 Project Structure

```
beru-bot/
├── main.py          # Discord bot + event handlers + all commands
├── dashboard.py     # Flask web dashboard (UI + API routes)
├── utils.py         # Groq AI content generators + brand voice system
├── config.py        # Environment variable loader
├── requirements.txt # Python dependencies
├── Procfile         # Render start command
└── render.yaml      # Render deployment config
```

---

## ⚙️ Setup & Deployment

### 1. Clone the repo
```bash
git clone https://github.com/Unbeatable-Abhay/beru-bot.git
cd beru-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
Create a `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token
GROQ_API_KEY=your_groq_api_key
REPLICATE_API_TOKEN=your_replicate_token
```

### 4. Run locally
```bash
python main.py
```

### 5. Deploy to Render
- Push to GitHub
- Connect repo on [render.com](https://render.com)
- Add env vars in Render dashboard
- Set start command: `python main.py`
- Done ✅

---

## 🏆 Built For

This project was built as a **hackathon submission** to demonstrate how modern AI APIs can be combined into a production-ready, user-friendly tool that serves both Discord users and the general web.

**Key achievements:**
- Full-stack deployment (bot + web dashboard) on a single service
- Sub-second AI responses using Groq's LLaMA inference
- Zero-login web interface — accessible to anyone with the URL
- Persistent brand voice system per user
- Dark/light theme support

---

## 👨‍💻 Author

**Abhay** — [@Unbeatable-Abhay](https://github.com/Unbeatable-Abhay)

> Built with 💖 and way too much coffee
