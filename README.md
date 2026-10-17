# MannMitra V5 — Advanced TYCS Build

MannMitra is a modular Flask wellness and reflection platform with journaling, VADER sentiment analysis, context-aware supportive chat, selected Bhagavad Gita wisdom, habits, community and dashboard analytics.

## V5 upgrades
- Optional **MongoDB Atlas + PyMongo** storage, with SQLite fallback for offline college demos
- Context-aware chat using recent conversation history
- Chat intent labels and stored Gita reference
- Protected JSON APIs
- 7-day dashboard metrics
- Improved data models with UUID IDs in Mongo mode
- Existing V4 responsive UI, Calm Mode, journal CRUD, Gita search, habits and community retained

## Run locally
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## MongoDB Atlas
Copy `.env.example` to `.env` and set `MONGO_URI` and `DB_NAME`. On startup, MannMitra automatically uses MongoDB Atlas when `MONGO_URI` is available.

For production deployment, keep secrets in environment variables and never commit `.env`.

## Important project boundary
MannMitra is a supportive wellness/reflection tool, not a medical diagnosis system or a replacement for professional care. Safety responses should remain generic and encourage reaching out to a trusted person or local emergency support when immediate danger is involved.
