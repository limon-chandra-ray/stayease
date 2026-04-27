# StayEase AI Agent

An AI-powered hotel booking assistant for Bangladesh built with **FastAPI**, **LangGraph**, **Groq (LLaMA 3)**, and **Supabase (PostgreSQL)**.

---

## Architecture

```mermaid
flowchart TD
    User([User]) -->|POST /api/chat/{id}/message| API[FastAPI]
    API --> Graph[LangGraph Agent]

    Graph --> DetectIntent[detect_intent node\nGroq LLaMA 3]

    DetectIntent -->|search| SearchNode[search_node]
    DetectIntent -->|details| DetailsNode[details_node]
    DetectIntent -->|book| BookNode[booking_node]
    DetectIntent -->|human| HumanNode[human_node]

    SearchNode --> DB[(Supabase\nPostgreSQL)]
    DetailsNode --> DB
    BookNode --> DB

    SearchNode --> ResponseNode[response_node\nGroq LLaMA 3]
    DetailsNode --> ResponseNode
    BookNode --> ResponseNode
    HumanNode --> ResponseNode

    ResponseNode --> API
    API -->|Save to conversations| DB
    API -->|JSON response| User
```

---

## Features

- Natural language hotel search by location, guests, and budget (BDT)
- Listing detail lookup by ID
- Booking creation with confirmation
- Conversation history stored in database
- Human handoff for unsupported requests

---

## Project Structure

```
StayEase/
├── main.py              # FastAPI app & routes
├── migrate.py           # One-time DB schema runner
├── agent/
│   ├── db.py            # PostgreSQL connection (psycopg)
│   ├── graph.py         # LangGraph state machine
│   ├── nodes.py         # Agent node functions
│   ├── schema.sql       # DB schema & seed data
│   ├── state.py         # AgentState TypedDict
│   └── tools.py         # LangChain tools (search, details, book)
└── .env                 # Environment variables
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/your-username/stayease.git
cd stayease
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

> Get a free Groq API key at [console.groq.com](https://console.groq.com)
> Get a free Supabase database at [supabase.com](https://supabase.com)

### 3. Apply database schema

Run the SQL in `agent/schema.sql` via Supabase SQL Editor, or:

```bash
python migrate.py
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

API docs available at **http://127.0.0.1:8000/docs**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/{conversation_id}/message` | Send a message to the AI agent |
| `GET` | `/api/chat/{conversation_id}/history` | Get conversation history |

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/chat/1/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a room in Cox'\''s Bazar for 2 guests under 5000 BDT"}'
```

### Example response

```json
{
  "conversation_id": 1,
  "message": "I need a room in Cox's Bazar for 2 guests under 5000 BDT",
  "response": "Great news! I found a perfect match for you — Sea View Hotel in Cox's Bazar at 4,500 BDT per night. It accommodates up to 2 guests and includes WiFi, AC, and Breakfast. Would you like to book it?"
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| AI Orchestration | LangGraph |
| LLM | Groq — LLaMA 3.1 8B Instant |
| Database | Supabase (PostgreSQL) |
| DB Driver | psycopg3 |
| Validation | Pydantic v2 |

---

## License

MIT
