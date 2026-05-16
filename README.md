# 🤖 Active Dream Bot

> **A permission-based private Telegram bot for virtual phone numbers and automated OTP verification.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-Private-red)](#)

---

## 📋 Overview

Active Dream is a fully modular, production-ready Telegram bot that provides virtual phone numbers for OTP (One-Time Password) verification across 13+ services and 20+ countries. Unlike public OTP bots, Active Dream operates as a **closed, private system** where only admin-approved users can access services.

### Key Highlights
- 🔐 **Private & Secure** — Admin-approved access only
- 📱 **13+ Services** — Facebook, Instagram, WhatsApp, Google, TikTok, and more
- 🌍 **20+ Countries** — Ethiopia, Indonesia, India, USA, UK, and more
- 🔑 **Automated OTP** — Background polling with instant delivery
- 💰 **Credit System** — Balance-based purchases with automatic refunds
- 🧪 **Free Test Mode** — Built-in mock provider for testing without API costs

---

## ✨ Features

### User Features
| Feature | Description |
|---------|-------------|
| 🔐 Permission System | New users must request access; admins approve/reject |
| 📱 Get Number | Select service → select country → receive a virtual number |
| 🔑 Auto OTP | Bot automatically polls for OTP and delivers it to chat |
| 📊 Balance | View balance, transaction history |
| 📢 OTP Group | All OTPs are forwarded to a dedicated group for team visibility |

### Admin Features
| Feature | Description |
|---------|-------------|
| 👑 Admin Panel | `/admin` — Real-time stats, user counts, number stats |
| ✅ Approve/Reject | Approve or reject user access requests |
| 💰 Add Balance | `/addbal USER_ID AMOUNT` — Credit user accounts |
| 📣 Broadcast | `/broadcast MESSAGE` — Message all users at once |
| 🚫 Ban/Unban | `/ban USER_ID` and `/unban USER_ID` |

### Technical Features
| Feature | Description |
|---------|-------------|
| 🧪 Mock Provider | Test entire flow for free — no API key needed |
| 🔄 Auto-Refund | Failed/expired numbers are automatically refunded |
| 🏗️ Modular Design | Abstract SMS provider interface — add new providers easily |
| 📦 Async Architecture | Built with `python-telegram-bot` v21+ and `asyncio` |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Telegram Bot Token** — from [@BotFather](https://t.me/BotFather)
- **5sim.net API Key** *(optional for testing)* — from [5sim.net](https://5sim.net)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/workmail1803-ai/active_dream_bot.git
cd active_dream_bot

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# 5. Edit .env with your values (see Configuration below)

# 6. Run the bot
python bot.py
```

---

## ⚙️ Configuration

Create a `.env` file from the template and fill in your values:

```env
# Telegram Bot Token (from @BotFather)
BOT_TOKEN=your_bot_token_here

# Admin Telegram User ID (from @userinfobot)
ADMIN_IDS=your_user_id_here

# 5sim.net API Key (leave blank for FREE test mode)
FIVESIM_API_KEY=

# OTP Group (set to 0 to disable)
OTP_GROUP_ID=0
OTP_GROUP_LINK=https://t.me/your_group

# Channel
CHANNEL_LINK=https://t.me/your_channel

# Bot Settings
BOT_NAME=Active Dream
OTP_CHECK_INTERVAL=5
OTP_MAX_WAIT=300
```

### How to Get Each Value

| Variable | Source | Instructions |
|----------|--------|-------------|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) | Send `/newbot`, follow prompts |
| `ADMIN_IDS` | [@userinfobot](https://t.me/userinfobot) | Send `/start`, copy the ID |
| `FIVESIM_API_KEY` | [5sim.net](https://5sim.net) | Profile → API Key → Generate |
| `OTP_GROUP_ID` | [@RawDataBot](https://t.me/RawDataBot) | Add to group, copy Chat ID |

> **💡 Testing Mode:** Leave `FIVESIM_API_KEY` blank to use the free mock provider. The bot will generate fake numbers and simulate OTP delivery — perfect for testing the entire flow without spending money.

---

## 🤖 Bot Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot / Show main menu |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/admin` | Open admin dashboard |
| `/addbal USER_ID AMOUNT` | Add balance to a user |
| `/broadcast MESSAGE` | Send message to all approved users |
| `/ban USER_ID` | Ban a user |
| `/unban USER_ID` | Unban a user |

---

## 📱 Supported Services

| Service | Code | Service | Code |
|---------|------|---------|------|
| Facebook | `facebook` | TikTok | `tiktok` |
| Instagram | `instagram` | Snapchat | `snapchat` |
| WhatsApp | `whatsapp` | Discord | `discord` |
| Telegram | `telegram` | Microsoft | `microsoft` |
| Twitter/X | `twitter` | Yahoo | `yahoo` |
| Google | `google` | Amazon | `amazon` |

## 🌍 Supported Countries

Russia, USA, UK, India, Indonesia, Philippines, Ethiopia, Kenya, Nigeria, Bangladesh, Pakistan, Brazil, Egypt, Vietnam, Ukraine, Kazakhstan, Myanmar, Colombia, Mexico, Thailand — and more can be added easily.

---

## 📁 Project Structure

```
active_dream_bot/
├── bot.py                    # Main entry point & handler registration
├── config.py                 # Environment config loader & validator
├── Procfile                  # Railway.app deployment config
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
├── .gitignore                # Git ignore rules
│
├── database/
│   ├── __init__.py
│   ├── db.py                 # SQLite connection & schema (auto-creates)
│   └── models.py             # CRUD operations for users, numbers, transactions
│
├── handlers/
│   ├── __init__.py
│   ├── start.py              # /start command & access request flow
│   ├── menu.py               # Main menu navigation
│   ├── numbers.py            # Number purchase & OTP polling
│   ├── balance.py            # Balance display & withdrawal
│   └── admin.py              # Admin panel & management
│
├── services/
│   ├── __init__.py
│   ├── sms_provider.py       # Abstract base class for SMS providers
│   ├── fivesim.py            # 5sim.net API implementation
│   └── mock_provider.py      # Free testing mock (no API needed)
│
└── utils/
    ├── __init__.py
    ├── constants.py           # Messages, service/country definitions
    ├── keyboards.py           # Inline keyboard layouts
    └── decorators.py          # @require_approved, @require_admin
```

---

## 🚢 Deployment

### Railway.app (Easiest)
1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add all `.env` variables in the Variables tab
4. Railway auto-deploys!

### VPS (Recommended for Production)
```bash
# On your Ubuntu VPS:
cd /opt/active_dream_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env  # Fill in values

# Set up as systemd service for 24/7 operation
sudo systemctl enable activedream
sudo systemctl start activedream
```

---

## 🏗️ Architecture

```
User (Telegram) → Bot (python-telegram-bot) → Handler Layer
                                                    ↓
                                              Service Layer (5sim.net API / Mock)
                                                    ↓
                                              Database Layer (SQLite / aiosqlite)
```

- **Async throughout** — Uses `asyncio`, `aiohttp`, `aiosqlite`
- **Provider Pattern** — Abstract `SmsProvider` interface; swap providers without changing handlers
- **Decorator-based Auth** — `@require_approved` and `@require_admin` on every handler
- **Background OTP Polling** — `asyncio.create_task()` for non-blocking SMS checks

---

## 📄 Documentation

Full 38-page technical documentation is available in the `docs/` directory (LaTeX source). Covers:
- Project overview & feature details
- Architecture & file-by-file explanation
- Why 5sim.net (Bangladesh perspective)
- Setup guide & deployment instructions
- Future improvements roadmap

---

## 🔒 Security Notes

- **Never commit `.env`** — It contains your bot token and API keys
- **Admin-only access** — All sensitive operations require admin approval
- **Auto-refund** — Failed purchases are automatically refunded
- **Rate limiting ready** — Architecture supports per-user rate limits

---

## 📝 License

This is a private project. All rights reserved.

---

<p align="center">
  <b>Active Dream Bot</b> — Built with ❤️ by <b>NHM Development</b>
  <br>
  <sub>Nafis Hossain Momen • May 2026</sub>
</p>
