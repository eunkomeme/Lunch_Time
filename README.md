# 🍱 오늘 오장? (Lunch Sync)

> A real-time lunch coordination app built for a small team at Samsung Electronics Suwon campus.

Instead of juggling KakaoTalk messages every day — *"Are you going to lunch?" "Which cafeteria?" "What time?"* — this app lets teammates see each other's lunch status at a glance and sync up instantly.

🔗 **Live Demo:** https://bit.ly/ojang
🚀 **Deployed on:** Railway

---

## ✨ Features

- **Real-time presence** — join/leave status syncs instantly across all connected clients via WebSocket
- **Cafeteria menu lookup** — automatically fetches today's menus from internal cafeteria APIs (no manual entry needed)
- **Smart meal tab** — auto-selects breakfast / lunch / dinner based on current time
- **Preset names & custom entry** — quick-select for regulars, open input for guests
- **Meal time selection** — choose between the usual 11:50 or set a custom time
- **Custom venue input** — for days when the team goes somewhere off-campus
- **Graceful fallback** — cafeterias without an API (e.g. 패밀리홀) fall back to free-text input

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Backend | Flask + Flask-SocketIO |
| Async runtime | eventlet |
| Production server | Gunicorn |
| Real-time transport | WebSocket (Socket.IO) |
| External APIs | Samsung Welstory, CJ프레시밀 |
| Caching | In-memory dict with 1-hour TTL |
| Deployment | Railway |
| Frontend | HTML, CSS, Vanilla JS |

---

## 🔌 Menu API Integration

Two cafeteria data sources are integrated:

**Samsung Welstory** (R3 / R4 / R5)
- Endpoint: `POST /menu/getSuwonMenuList.do`
- Filters by `first_row_yn=Y` to return only set-meal representative items
- Returns breakfast / lunch / dinner menus per hall

**CJ프레시밀** (투게더홀)
- Endpoint: `GET /meal/v1/today-all-meal?storeIdx=6413`
- `storeIdx` was discovered via the `near-store` API using the campus GPS coordinates
- Returns per-corner menu items with corner labels

Both sources are cached for 1 hour to avoid redundant API calls.

---

## ⚙️ How It Works

```
Client A changes status
  → emits "update" via Socket.IO
    → server updates in-memory state
      → broadcasts "player_list" to all clients
        → every connected browser re-renders instantly
```

No database. State lives in a Python dict for the duration of the server process — intentional for a lightweight, ephemeral use case.

---

## 📂 Project Structure

```
.
├── server.py          # Flask app, SocketIO handlers, menu API fetchers
├── requirements.txt
└── templates/
    └── index.html     # Single-page frontend (HTML + CSS + Vanilla JS)
```

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
python server.py
```

Or with Gunicorn:

```bash
gunicorn -k eventlet -w 1 server:app
```

---

## 📎 Notes

Built for a real use case with a team of ~3 people. Intentionally minimal — the goal was to solve a specific daily friction point, not to over-engineer it. Focus was on real-time sync and API integration rather than persistence or auth.
