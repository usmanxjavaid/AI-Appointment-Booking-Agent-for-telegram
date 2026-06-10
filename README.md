# 🏥 AI Appointment Booking Agent for Telegram

An intelligent appointment booking agent for Telegram powered by Groq AI. Built for clinics, salons, consultants and any service-based business to automate appointment booking 24/7.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-supported-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 📅 **Smart Booking Flow** — Book appointments through clean button navigation
- 🧠 **AI Powered** — Groq AI answers questions naturally outside booking flow
- 🟢 **Live Slot Availability** — Shows available and booked slots in real time
- ⏰ **Automatic Reminders** — Sends reminder 1 hour before appointment automatically
- ❌ **Cancel Appointments** — Users can cancel their own bookings
- 🔔 **Admin Notifications** — Instant Telegram notification for every new booking
- 📊 **Admin Panel** — View all appointments and today's schedule
- 📝 **Proper Logging** — All events logged with timestamps
- 🐳 **Docker Support** — Fully containerized for easy deployment
- ✅ **CI/CD** — GitHub Actions automatically tests Docker build on every push

---

## 📁 Project Structure

```
├── handlers/
│   ├── user.py         → booking conversation flow
│   └── admin.py        → admin commands and panel
├── core/
│   ├── ai.py           → Groq AI integration
│   ├── database.py     → SQLite operations
│   ├── scheduler.py    → automatic reminders
│   ├── validator.py    → name, phone, date validation
│   └── logger.py       → logging setup
├── config.py           → all settings in one place
├── bot.py              → entry point
├── Dockerfile          → Docker configuration
├── .github/workflows/  → GitHub Actions CI
└── requirements.txt    → Python dependencies
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/usmanxjavaid/appointment-booking-agent
cd appointment-booking-agent
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
ADMIN_ID=your_telegram_user_id
```

### 5. Customize for your client in `config.py`
```python
COMPANY_NAME = "Your Client Clinic Name"
AGENT_NAME   = "Your Bot Name"
SERVICES     = ["Service 1", "Service 2", "Service 3"]
TIME_SLOTS   = ["09:00 AM", "10:00 AM", "11:00 AM"]
WORKING_DAYS = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday"]
```

### 6. Run the bot
```bash
python bot.py
```

---

## 📊 Admin Commands

| Command | Usage | What it does |
|---|---|---|
| `/admin` | `/admin` | Shows stats + action buttons |
| Click 📋 | View Appointments button | Shows last 10 appointments |
| Click 📅 | Today's Schedule button | Shows today's bookings |
| `/cancelappointment` | `/cancelappointment 5` | Cancel appointment by ID |

---

## 🔄 Booking Flow

```
/start
↓
Main menu — Book / View / Cancel
↓
Select service
↓
Select date (next 3 working days)
↓
Select time slot (live availability)
↓
Enter name
↓
Enter phone
↓
Appointment confirmed ✅
↓
Admin notified instantly 🔔
↓
Reminder sent 1 hour before ⏰
```

---

## 🐳 Docker

```bash
docker build -t appointment-booking-agent .
docker run --env-file .env appointment-booking-agent
```

---

## 🔑 API Keys (All Free)

| Service | Purpose | Get it |
|---|---|---|
| Telegram BotFather | Bot token | [@BotFather](https://t.me/botfather) |
| Groq | AI responses | [console.groq.com](https://console.groq.com) |

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Telegram Framework | python-telegram-bot 21.5 |
| AI | Groq API (LLaMA 3.1) |
| Database | SQLite |
| Scheduling | APScheduler |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

## 📦 Per Client Customization

Only update `config.py`:

```python
COMPANY_NAME = "Client Business Name"
AGENT_NAME   = "Assistant Name"
SERVICES     = ["Their", "Service", "Options"]
TIME_SLOTS   = ["09:00 AM", "10:00 AM", ...]
WORKING_DAYS = ["Monday", "Tuesday", ...]
```

Delivery time per client: under 30 minutes ⚡

---

## 📄 License

MIT License — free to use for commercial purposes.

---

## 👨‍💻 Author

**Usman Javaid**
- GitHub: [@usmanxjavaid](https://github.com/usmanxjavaid)