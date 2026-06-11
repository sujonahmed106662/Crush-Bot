# 💕 Crush Proposal Bot

A production-ready Telegram bot that lets users create beautiful romantic proposal pages to share with their crushes. When the crush clicks **Yes ❤️**, the creator gets a Telegram notification with a generated celebration image.

---

## Features

- 💌 Create unlimited romantic proposal pages
- 🎨 Customizable: message, background image, music, live emoji
- 🖼 Auto-generated celebration PNG image (Pillow)
- 📲 Telegram notification when crush says Yes
- 🎉 Confetti + celebration animation
- 💔 Escaping "No" button (moves away on hover/touch)
- 📊 Admin panel at `/admin`
- 🔒 User ban/unban system
- 📢 Admin broadcast to all users
- 🔥 Firebase Firestore database

---

## Local Development

```bash
cd crush-bot
pip install -r requirements.txt
cp .env.example .env   # fill in your values
python main.py
```

---

## Railway Deployment

### 1. Create a Firebase Project

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Create a new project
3. Enable **Firestore Database** (start in test mode)
4. Go to **Project Settings → Service Accounts**
5. Click **Generate new private key** → download the JSON
6. Minify the JSON to a single line (use [jsonformatter.org](https://jsonformatter.org/json-minify))

### 2. Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot` and follow the prompts
3. Copy your **bot token**

### 3. Deploy on Railway

1. Push this project to GitHub
2. Create a new Railway project → **Deploy from GitHub repo**
3. In **Variables**, set:

| Variable | Value |
|---|---|
| `BOT_TOKEN` | Your bot token from BotFather |
| `ADMIN_ID` | Your Telegram user ID |
| `FIREBASE_CREDENTIALS` | The minified Firebase JSON string |
| `BASE_URL` | Your Railway domain, e.g. `https://crush-bot.railway.app` |
| `ADMIN_SECRET` | A secret password for the admin panel |
| `WEBHOOK_MODE` | `true` (recommended for production) |

4. Railway auto-detects Python via `nixpacks.toml` and installs dependencies.

### 4. Update Bot Username in index.html

Open `templates/index.html` and replace `YourBotUsername` with your actual bot username:
```html
<a href="https://t.me/YourBotUsername" ...>
```

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/help` | Show help |
| `/create` | Create a new crush page |
| `/mylinks` | View your pages |
| `/stats` | Your statistics |
| `/delete` | Delete a page |
| `/setemoji` | Set live floating emoji |
| `/setbg` | Set background image URL |
| `/setmusic` | Set background music URL |
| `/setmessage` | Update message on a page |
| `/admin` | Admin panel (admin only) |
| `/broadcast` | Broadcast message (admin only) |
| `/ban {id}` | Ban a user (admin only) |
| `/unban {id}` | Unban a user (admin only) |

---

## Admin Panel

Visit `https://your-domain/admin` and enter your `ADMIN_SECRET` to access the admin dashboard.

---

## Project Structure

```
crush-bot/
├── main.py              # Entry point (uvicorn)
├── web.py               # FastAPI app + routes
├── bot.py               # Aiogram bot handlers + FSM
├── database.py          # Firebase Firestore operations
├── firebase_config.py   # Firebase initialization
├── image_generator.py   # Pillow image generation
├── templates/
│   ├── index.html       # Landing page
│   ├── proposal.html    # Proposal/crush page
│   └── admin.html       # Admin dashboard
├── static/
│   ├── css/style.css
│   └── js/
│       ├── hearts.js    # Floating hearts/emoji
│       └── proposal.js  # Yes/No logic, confetti, typing
├── generated/           # Auto-generated PNG images
├── requirements.txt
├── Procfile
├── railway.toml
└── nixpacks.toml
```
