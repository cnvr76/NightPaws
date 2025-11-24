# NightPaws
### Job Application Tracker
An automated platform designed to replace manual Excel spreadsheets for tracking job applications. It connects to a user's Gmail via OAuth2 to monitor recruiter responses.

The backend is built with FastAPI and AsyncIO to handle concurrent email queries efficiently. To ensure user privacy, the analysis of email content happens via a Local LLM (running on the server), which determines the application status (e.g. Rejected, Interview, Ghosted, Offer etc.) and updates the PostgreSQL database. The system runs hourly or so syncs via Cron, with an option for manual syncs and status overrides if the model misinterprets a response.

### Tech Stack

    Core: Python, FastAPI, SQLAlchemy, PostgreSQL

    Auth: Custom OAuth2 flow (Google), JWT, Cryptography (Fernet)

    Concurrency: asyncio + asyncio.gather for parallel I/O operations

    AI/ML: Hugging Face Transformers (bart-large-mnli) running locally

    Infra: Docker, Railway (planned)
