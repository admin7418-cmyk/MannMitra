# MannMitra Architecture

## 1. Presentation Layer
HTML templates, CSS and JavaScript provide the responsive user interface.

## 2. Route Layer
The `routes/` package receives HTTP requests and selects the required service.

## 3. Service Layer
The `services/` package contains business logic:
- sentiment_service.py
- chat_service.py
- gita_service.py
- safety_service.py
- auth_service.py
- report_service.py

## 4. Model Layer
The `models/` package handles persistence operations.

## 5. Database Layer
`database/connection.py` provides the current local development adapter.
`database/collections.py` defines the MongoDB collection design.

## Request flow example
Journal form
→ journal_routes.py
→ sentiment_service.py
→ journal_model.py
→ database/connection.py
→ database

Chat form
→ chat_routes.py
→ chat_service.py
→ safety/sentiment/Gita services
→ chat_model.py
→ database
