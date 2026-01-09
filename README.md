# NightPaws (WIP)
### Job Application Tracker (response-tracker branch)
An automated platform designed to replace manual Excel spreadsheets for tracking job applications. It connects to a user's Gmail via OAuth2 to monitor recruiter responses.

The backend is built with FastAPI and AsyncIO to handle concurrent email queries efficiently. To ensure user privacy, the analysis of email content happens via a Local LLM (running on the server), which determines the application status (e.g. Rejected, Interview, Ghosted, Offer etc.) and updates the PostgreSQL database. The system runs hourly or so syncs via Cron, with an option for manual syncs and status overrides if the model misinterprets a response.

### Tech Stack

    Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery

    Frontend: React.js, Tailwind CSS

    Auth: OAuth2, JWT, Fernet Cryptography

    AI/ML: Hugging Face (SetFit), trained on personal emails

### Current JSON Response Example
``` json
  {
    "id": "2e631127-ed71-4204-a3f9-32e4a9a80029",
    "user_id": "fd473ef0-f27b-40c8-b3b5-4a9a1fa1536b",
    "job_title": "Junior Data Engineer",
    "company_name": "Builtmind",
    "current_status": "rejection",
    "email_chain": [
      {
        "message_id": "197837356e4fd7bb",
        "thread_id": "197837356e4fd7bb",
        "sender": {
          "name": "BuiltMind s.r.o. / cez profesia.sk",
          "email": "web@profesia.sk"
        },
        "subject": "Vyjadrenie k Vášmu záujmu o pozíciu v BuiltMind ",
        "status": "rejection",
        "received_at": "2025-06-18T14:31:03Z"
      },
      {
        "message_id": "19768bc0ba91faeb",
        "thread_id": "19768bc0ba91faeb",
        "sender": {
          "name": "BuiltMind s.r.o. / cez profesia.sk",
          "email": "web@profesia.sk"
        },
        "subject": "Zadanie",
        "status": "test_task",
        "received_at": "2025-06-13T10:00:42Z"
      }
    ],
    "updated_at": "2026-01-09T02:12:45.071974+01:00",
    "created_at": "2026-01-09T02:12:39.045492+01:00"
  }
```
