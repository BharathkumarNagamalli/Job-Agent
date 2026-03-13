# 🤖 Job Agent — AI-Powered Job Search & Tracker

A full-featured Flask web app to search, track, and land jobs using AI.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Job Search** | Search 10,000+ jobs via JSearch API (Indeed-powered) |
| 📋 **Application Tracker** | Track every job across 5 statuses with notes |
| ✍️ **AI Cover Letters** | Gemini-powered personalized cover letters |
| 🎯 **Interview Prep** | Custom questions, technical prep, and tips |
| 📄 **Resume Advisor** | AI suggestions to improve your resume |
| 💬 **Chat Assistant** | Ask anything about your job search |
| 📊 **Dashboard** | Visual pipeline of your application progress |

## 🚀 Quick Setup

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd job_agent
pip install -r requirements.txt
```

### 2. Get API Keys

**JSearch API (Job Search) — FREE**
1. Go to [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Sign up → Subscribe to FREE plan (500 req/month)
3. Copy your `X-RapidAPI-Key`

**Gemini API (AI Features) — FREE**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 4. Run the App

```bash
python app.py
```

Visit `http://localhost:5000`

## 📁 Project Structure

```
job_agent/
├── app.py                  # Flask app entry point
├── database.py             # SQLite DB setup
├── routes/
│   ├── jobs.py             # Job search + dashboard
│   ├── applications.py     # Application CRUD tracker
│   ├── ai_assistant.py     # Gemini AI features
│   └── profile.py          # User profile
├── templates/
│   ├── base.html           # Navigation + layout
│   ├── dashboard.html      # Stats + pipeline
│   ├── search.html         # Job search UI
│   ├── applications.html   # Tracker board
│   ├── ai_assistant.html   # Cover letter + chat
│   ├── job_detail.html     # Full job view
│   └── profile.html        # Profile editor
├── static/
│   ├── css/style.css       # Dark theme styles
│   └── js/main.js          # Toast + utilities
├── instance/jobs.db        # SQLite database (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Tech Stack

- **Backend:** Flask 3, SQLite, Python 3.10+
- **AI:** Google Gemini 1.5 Flash (free tier)
- **Job Data:** JSearch API via RapidAPI
- **Frontend:** Vanilla JS, CSS3, DM Sans + Space Mono fonts
- **No heavy frameworks** — lightweight and fast

## 📌 Application Statuses

| Status | Meaning |
|--------|---------|
| 🔖 Saved | Found and saved for later |
| ✉️ Applied | Application submitted |
| 🎯 Interviewing | In interview process |
| 🏆 Offered | Received an offer |
| ❌ Rejected | Not selected |

## 🔮 Possible Extensions

- [ ] Email reminders for follow-ups
- [ ] Auto-apply with form filling (Selenium)
- [ ] LinkedIn scraper integration
- [ ] Export applications to CSV/PDF
- [ ] Salary comparison charts
- [ ] Resume PDF upload + parsing

## 👨‍💻 Author

Built by **BharathKumar Nagamalli**  
GitHub: [BharathkumarNagamalli](https://github.com/BharathkumarNagamalli)
