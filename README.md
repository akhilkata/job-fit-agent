cd /Users/akhilkata/Desktop/job-agent

cat > README.md << 'EOF'
# Job-Fit Agent 💼🤖

Personal job helper that lets me paste a job description and instantly see how well it matches my profile.

- **Backend:** FastAPI (Python)
- **Frontend:** Angular (standalone components)
- **Scoring:** Offline, rule-based matching (no API keys, zero cost)
- **Use case:** Quickly decide which roles to prioritize and what to highlight in my resume / “Why me” section.

---

## ✨ Features

- Paste any job description (title, company, location, JD text)
- Get a **fit score (0–100)** based on:
  - Tech stack match (Java, Spring Boot, Kafka, AWS, etc.)
  - Seniority level
  - Location / remote hints
- See:
  - Short **match summary**
  - Bullet-point **reasons for the score**
  - Detected **tech stack**
  - A **“Why you’re a good fit”** paragraph you can reuse in applications

All of this works **fully offline** using a JSON profile file – no paid LLMs or API keys needed.

---

## 🧱 Project Structure

```text
job-fit-agent/
├── backend/          # FastAPI app (Python)
│   ├── app/
│   │   ├── main.py           # API entrypoint
│   │   ├── config.py         # loads profile/profile.json
│   │   ├── models.py         # Pydantic/SQLModel models
│   │   ├── llm_client.py     # rule-based scorer (no external APIs)
│   │   └── services/         # scoring & persistence services
│   └── requirements.txt
├── job-agent-ui/     # Angular frontend (standalone components)
│   └── src/app/
│       ├── app.component.*   # Job scoring UI
│       ├── models/           # JobIn / JobOut interfaces
│       └── services/         # HTTP client for backend
└── profile/
    └── profile.json  # My skills & preferences (used for scoring)
