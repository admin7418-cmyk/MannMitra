# API

## POST /api/analyze
Request:
```json
{"text":"I feel happy today"}
```

Response:
```json
{"score":0.6,"mood":"Positive"}
```

## POST /api/chat
Request:
```json
{"message":"I am stressed about exams"}
```

Response contains:
- type
- reply
- optional gita reference
