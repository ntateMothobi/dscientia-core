# Property Sales Intelligence (Mini)

Property Sales Intelligence (Mini) is a modular backend MVP built with FastAPI
to manage leads and follow-ups in property sales workflows.
The project emphasizes clean architecture, testability, and extensibility,
making it suitable as a foundation for data-driven sales intelligence
and social impact platforms.

---

## 🎯 Problem Statement

Many independent property agents and small sales teams manage leads using
spreadsheets, chat applications, or personal notes.
This often results in:
- Missed follow-ups
- Inconsistent lead handling
- Lack of performance insights
- Difficulty scaling operations

This project demonstrates how a lightweight backend system can centralize
lead data, track follow-up activities, and provide a solid foundation
for future analytics and automation.

---

## 🧠 Target Users

- Independent property agents
- Small sales teams and UMKM
- Developers building sales or CRM MVPs
- Social impact and community engagement platforms

---

## 🧱 Architecture Overview

The application follows a modular and layered architecture:

```text
app/
├── api/v1/             # Versioned API routes
│   ├── lead.py         # Lead endpoints
│   └── followup.py     # Follow-up endpoints
├── models/             # SQLAlchemy ORM models
├── schemas/            # Pydantic request/response schemas
├── services/           # Business logic layer
├── core/               # Database configuration & settings
└── main.py             # FastAPI application entry point
tests/                  # Automated API tests
scripts/                # Utility scripts (e.g. DB init)
ui/                     # Lightweight UI (Streamlit prototype)
```


This structure ensures:
- Clear separation of concerns
- Easy testing and maintenance
- Flexibility for future extensions

---

## 🚀 Technology Stack

- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Data Validation**: Pydantic
- **Database**: SQLite (development & testing)
- **Testing**: Pytest + HTTPX

---

## 🔧 Local Development Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/littlepasluv/property-sales-intelligence-mini.git
cd property-sales-intelligence-mini

2️⃣ Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # macOS / Linux

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the application
uvicorn app.main:app --reload


Open:

http://127.0.0.1:8000/docs

🧪 Testing

The project includes automated API tests that cover:

Core lead and follow-up workflows

Validation errors and edge cases

API response consistency

Run all tests with:

pytest

🔮 Roadmap

Planned improvements include:

Analytics and reporting dashboard

Lead scoring and prioritization

Authentication and role-based access

Integration with messaging or advertising platforms

🌍 Reusability & Extensibility

Although this project uses property sales as a domain example,
the architecture is intentionally domain-agnostic.
With minimal changes, it can be adapted for:

Community engagement tracking

NGO program monitoring

Research data collection systems

Customer relationship management (CRM) tools

📌 Project Status

Current version: v0.1.0

Stage: MVP foundation

Focus: Stability, clarity, and extensibility

🧭 License

This project is currently shared for learning and demonstration purposes.
A formal license can be added in future iterations.


⬆️ **END OF README** ⬆️
