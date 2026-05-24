# ⚡ PathAI 360 — Free Career Matching App for Students

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56-FF4B4B?logo=streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

**PathAI 360** is a free, personality-driven career guidance web app built with Streamlit. Answer 24 questions about how you think and work and get ranked matches across 23 tech career paths, complete with 7-step learning roadmaps, side-by-side comparisons, and MBTI personality profiling.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [App Pages](#-app-pages)
- [How It Works](#-how-it-works)
- [Tech Stack](#️-tech-stack)
- [Database Schema](#-database-schema)
- [Career Domains](#-career-domains)
- [MBTI Personality Types](#-mbti-personality-types)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Environment Variables](#-environment-variables)
- [Important Note](#-important-note-about-ai-generated-code)
- [Author](#-author)

---

## 🌍 Overview

PathAI 360 helps students and career-changers find the right tech path by analyzing their **personality traits** — not grades or test scores. The assessment maps 24 questions to 20 personality traits and scores them against 23 career domains using a weighted matching algorithm.

**Who it's for:** Students unsure about which tech career to pursue, especially those with limited guidance or resources.

**What makes it different:** It's 100% free, requires no signup, works offline (with local MongoDB), and gives detailed career roadmaps rather than just a generic suggestion.

---

## 🚀 Live Demo

```
streamlit run app.py
```
Opens at: `http://localhost:8501`

---

## ✨ Features

### 🧠 Assessment Engine
- 24 personality questions with 5-point Likert scale responses (Strongly Agree → Strongly Disagree)
- Stronger answers (Strongly Agree/Disagree) carry **2× weight** vs standard responses
- Live trait profile builds in real time as you answer
- Previous/Next navigation — go back and change answers
- Auto-advances to results when all questions are answered

### 🎯 Career Matching
- Scores all 23 career domains against your 20 personality traits
- Weighted matching formula: `score = Σ(trait_value × domain_weight)`
- Full ranking of all 23 careers from best fit to least fit
- Top 3 matches displayed with gold/silver/bronze medals

### 🧬 MBTI Personality Profiling
- Derives your MBTI type (all 16 types supported) from your answers
- Maps E/I from extrovert vs introvert scores
- Maps N/S from creative vs structured scores
- Maps T/F from analytical vs supportive scores
- Maps J/P from structured vs flexible scores
- Displays personality title and description for your type

### 🗺️ Learning Roadmaps
- 7-step roadmap for every one of 23 career domains
- Personalized roadmap for your #1 career match shown automatically
- Browse all roadmaps in the Explore tab with live search

### 📊 Side-by-Side Comparison
- Compare up to 4 career domains simultaneously
- Shows roadmaps and compatibility scores side-by-side
- Helps narrow down between similar-sounding careers

### 💾 MongoDB Integration
- Saves results to 3 collections: `users`, `answers`, `results`
- Prevents duplicate saves per session with `db_saved` guard
- Works offline (falls back gracefully when MongoDB unavailable)
- Set `MONGO_URI` env var for Atlas cloud or uses localhost by default

---

## 📱 App Pages

| Page | Description |
|------|-------------|
| 🏠 **Home** | Hero landing, feature overview, stats row (24 questions, 23 careers, 16 types) |
| 🧠 **Assessment** | The 24-question test with live trait bars, progress tracker, results + roadmap |
| 🗺️ **Explore** | Browse all 23 career paths by category with searchable roadmaps |
| 📊 **Comparison** | Select up to 4 domains and compare roadmaps + scores side-by-side |
| ℹ️ **How It Works** | Full explanation of the algorithm, trait dimensions, and methodology |
| 🏗️ **Architecture** | Full technical spec — ML pipeline, REST API endpoints, MongoDB schema |

---

## ⚙️ How It Works

### Step 1 — Answer 24 Questions
Each question maps to one or two personality traits. Example:
```
"I solve complex problems step-by-step using logic and reasoning."
→ Strongly Agree adds 4 pts to 'analytical', 2 pts to opposing trait
→ Neutral adds 0 pts to anything
```

### Step 2 — Build Your Personality Profile
20 traits are tracked across 10 opposing dimensions:

| Dimension | Trait A | Trait B |
|---|---|---|
| Thinking style | Analytical | Creative |
| Work preference | Introvert | Extrovert |
| Organization | Structured | Flexible |
| Role | Leadership | Supportive |
| Risk appetite | Risk-taking | Stable |
| Approach | Theoretical | Practical |
| Focus | Detail-oriented | Big-picture |
| Direction | Independent | Collaborative |
| Fast vs slow | Fast-decision | Careful-decision |
| Motivation | Money-oriented | Passion-oriented |

### Step 3 — Score All 23 Career Domains
Each domain has weighted trait requirements. Example:
```python
"Data Science": {"analytical": 3, "structured": 2, "detail_oriented": 2, "theoretical": 1}
"UI/UX Design": {"creative": 3, "big_picture": 2, "flexible": 2, "extrovert": 1}
```
Your trait score × domain weight = domain score. All 23 are ranked by total score.

### Step 4 — MBTI + Confidence Score
MBTI type is derived from trait balance. A confidence score (55–98%) is calculated from how strongly your traits cluster around one learning style archetype.

---

## 🛠️ Tech Stack

```
Python 3.11
├── streamlit==1.56.0       # Web app framework & multi-page UI
├── pymongo==4.6.0          # MongoDB driver for saving results
├── pandas==2.3.1           # Data handling
├── scikit-learn==1.8.0     # ML utilities (future: Random Forest)
├── numpy==2.3.1            # Numerical operations
├── plotly==6.2.0           # Interactive charts
└── python-dateutil         # Timestamp handling for MongoDB docs
```

**Database:** MongoDB 7 (local or Atlas via `MONGO_URI`)
**Fonts:** Syne (headings), DM Sans (body), JetBrains Mono (code/chips) — via Google Fonts

---

## 🗄️ Database Schema

Three MongoDB collections are written on assessment completion:

### `users`
```json
{
  "_id": "uuid-string",
  "name": "Azhar Ali",
  "grade": 10,
  "role": "student",
  "created_at": "2025-01-01T12:00:00Z"
}
```

### `answers`
```json
{
  "_id": "uuid-string",
  "user_id": "ref → users._id",
  "traits": { "analytical": 8, "creative": 4, "introvert": 6, "..." },
  "time_secs": 142,
  "submitted_at": "2025-01-01T12:02:22Z"
}
```

### `results`
```json
{
  "_id": "uuid-string",
  "user_id": "ref → users._id",
  "personality_type": "INTJ",
  "description": "Strategic mastermind...",
  "career_interests": ["Data Science", "Machine Learning", "AI Engineering"],
  "ml_predictions": { "mbti_type": "INTJ", "confidence": 87.3, "learning_style": "Analytical Thinker" },
  "top_match": "Data Science",
  "all_scores": [{ "domain": "Data Science", "pts": 18 }, "..."],
  "duration_seconds": 142,
  "created_at": "2025-01-01T12:02:22Z"
}
```

**Indexes:**
- `users.email` — unique
- `answers.user_id`
- `results.user_id`, `results.personality_type`

---

## 🗂️ Career Domains

PathAI 360 covers **23 career paths** across 4 categories:

| Category | Domains |
|---|---|
| 🤖 AI & Data | Data Science, Machine Learning, Deep Learning, AI Engineering, Data Engineering, Business Intelligence, Quantitative Finance |
| 💻 Software | Software Engineering, Web Dev (Frontend), Web Dev (Backend), Full Stack, Mobile App Dev, DevOps & SRE, Cloud Computing |
| ⚡ Emerging Tech | Cybersecurity, Blockchain, IoT, Embedded Systems, AR/VR, Game Development |
| 🎨 Creative & Biz | UI/UX Design, Digital Marketing, Product Management |

Each domain has a **7-step ordered learning roadmap** and a **weighted trait profile** for matching.

---

## 🧬 MBTI Personality Types

All 16 MBTI types are supported with custom titles and descriptions:

| Type | Title | Best Fit Domains |
|---|---|---|
| INTJ | The Architect | Data Science, AI Engineering |
| INTP | The Logician | Machine Learning, Deep Learning |
| ENTJ | The Commander | Product Management, Software Engineering |
| ENTP | The Debater | Blockchain, AI Engineering |
| INFP | The Mediator | UI/UX Design, Digital Marketing |
| ISTP | The Virtuoso | Cybersecurity, Embedded Systems |
| ... | ... | ... |

---

## 📂 Project Structure

```
PathAi-360/
│
├── app.py              # Full Streamlit application (single-file)
│                       # Contains: UI, assessment logic, MBTI engine,
│                       # domain scoring, MongoDB integration, all 6 pages
│
├── requirements.txt    # Python dependencies (pinned versions)
└── README.md           # Project documentation
```

> The entire application — all 6 pages, 23 career roadmaps, 24 questions, MBTI logic, MongoDB schema, and custom CSS theme — lives in a single `app.py` file (~900 lines).

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- MongoDB (local) or a [MongoDB Atlas](https://www.mongodb.com/atlas) free account

### 1. Clone the Repository
```bash
git clone https://github.com/Azharaliii/PathAi-360.git
cd PathAi-360
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install core packages manually:
```bash
pip install streamlit pymongo pandas numpy plotly scikit-learn
```

### 3. Run the App
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🔐 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MONGO_URI` | `mongodb://localhost:27017/` | MongoDB connection string (set for Atlas) |
| `DB_NAME` | `pathai360` | MongoDB database name |

```bash
# Example: use Atlas
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
streamlit run app.py
```

> **Offline mode:** If MongoDB is unreachable, the app runs fully without saving — no crash, no error screen. An info banner is shown instead.



The core packages actually needed are:
```
streamlit
pymongo
pandas
numpy
plotly
scikit-learn
python-dateutil
```

---

## 🔮 Future Improvements

- 🤖 Real ML model (Random Forest / DistilBERT) for MBTI classification
- 📄 PDF report download for career results
- 🔐 User login with email/password and history tracking
- 📊 Admin dashboard with aggregated analytics
- 🌍 Multi-language support (Urdu for Pakistan)
- 📱 Mobile-responsive layout improvements
- 🔔 WhatsApp bot integration for career guidance

---

## 👤 Author

**Azhar Ali Soomro**
[![GitHub](https://img.shields.io/badge/GitHub-Azharaliii-181717?logo=github&logoColor=white)](https://github.com/Azharaliii)
[![Kaggle](https://img.shields.io/badge/Kaggle-azharalisoomro-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/azharalisoomro)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

⭐ **If this helped you, give it a star — it keeps the project alive!**
