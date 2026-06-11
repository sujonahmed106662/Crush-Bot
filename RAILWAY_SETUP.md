# 🚀 Railway Deploy Guide (বাংলা)

## ✅ Deploy এর আগে config.py তে ২টা জিনিস বদলাও

ফাইল: `config.py` (৭ ও ৯ নম্বর লাইন)

```python
BASE_URL     = "https://তোমার-railway-domain.up.railway.app"   # ← এটা বদলাও
WEBHOOK_MODE = True   # ← False থেকে True করো
```

---

## Step 1 — GitHub এ push করো

```bash
# crush-bot ফোল্ডারের ভেতরে যাও
cd crush-bot

git init
git add .
git commit -m "Crush Bot v1"

# GitHub এ নতুন repo বানাও (crush-bot নামে)
git remote add origin https://github.com/তোমার-username/crush-bot.git
git push -u origin main
```

---

## Step 2 — Railway তে deploy করো

1. [railway.app](https://railway.app) → **New Project**
2. **Deploy from GitHub repo** → তোমার `crush-bot` repo সিলেক্ট করো
3. Deploy হবে (২-৩ মিনিট লাগবে)
4. **Settings → Domains → Generate Domain** click করো
5. Domain copy করো (যেমন: `crush-bot-production.up.railway.app`)

---

## Step 3 — config.py আপডেট করো

```python
BASE_URL     = "https://crush-bot-production.up.railway.app"  # তোমার domain
WEBHOOK_MODE = True
```

তারপর:
```bash
git add config.py
git commit -m "Set Railway domain"
git push
```

Railway automatically redeploy করবে।

---

## Step 4 — Bot test করো

Telegram এ [@HeartFlowLove_Bot](https://t.me/HeartFlowLove_Bot) → `/start`

---

## ❌ "Not Found" error দেখলে

Railway dashboard → তোমার service → **Logs** tab এ error দেখো।

সবচেয়ে common কারণ:
| সমস্যা | সমাধান |
|---|---|
| Port bind হচ্ছে না | PORT env var auto-set হয়, নতুন করে set করতে হবে না |
| Build fail | Logs এ error দেখো |
| `BASE_URL` ভুল | config.py তে সঠিক domain দাও |

---

## ✅ Checklist

- [ ] `BASE_URL` → তোমার actual Railway domain
- [ ] `WEBHOOK_MODE = True`
- [ ] `ADMIN_ID = 8502686983` (already set)
- [ ] Firebase credentials (already set in config.py)
- [ ] GitHub push সফল
- [ ] Railway deploy সফল
- [ ] `/healthz` endpoint কাজ করছে: `https://তোমার-domain.up.railway.app/healthz`
