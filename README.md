# 🏨 StayEase AI Agent

StayEase AI Agent is an LLM-powered conversational booking system built with **FastAPI, LangGraph, Groq (LLM), and PostgreSQL**.

This system enables users to:

* Search properties using natural language
* View listing details
* Create bookings through conversational interaction

---

# 🎯 Objective

This project demonstrates how to design a **stateful AI agent system** that separates:

* 🧠 Reasoning → LLM (Groq - LLaMA 3)
* 🔀 Orchestration → LangGraph
* ⚙️ Execution → Tools (PostgreSQL queries)

---

# 🏗️ System Architecture

```mermaid
graph TD
    A[User] -->|Message| B[FastAPI]
    B --> C[LangGraph Agent]
    C --> D[LLM]
    C --> E[Tools Layer]
    E --> F[PostgreSQL]
    C --> B
    B --> A
```

---

# 🔄 Agent Workflow

```mermaid
graph TD
    A[User Message] --> B[detect_intent]

    B -->|search| C[search_node]
    B -->|details| D[details_node]
    B -->|book| E[booking_node]
    B -->|fallback| F[human_node]

    C --> G[response_node]
    D --> G
    E --> G
    F --> G

    G --> H[Final Response]
```

---

# 🧠 State Management

The agent uses a **shared state object** across all nodes:

```python
class AgentState(TypedDict):
    user_message: str
    intent: Optional[str]
    extracted: Optional[dict]
    tool_result: Optional[Any]
    response: Optional[Any]
```

### Why State?

* Maintains conversation context
* Stores structured data (intent, extracted fields)
* Enables multi-step workflows

---

# Core Components

## 1. Nodes (Execution Units)

| Node          | Responsibility                                    |
| ------------- | ------------------------------------------------- |
| detect_intent | LLM-based intent classification + data extraction |
| search_node   | Query listings from DB                            |
| details_node  | Fetch specific listing info                       |
| booking_node  | Insert booking into DB                            |
| response_node | Generate final response                           |

---

## 2. Tools (Backend Logic)

Tools encapsulate **deterministic operations**:

* `search_available_properties` → SQL SELECT
* `get_listing_details` → SQL SELECT
* `create_booking` → SQL INSERT

👉 This prevents LLM hallucination and ensures reliability.

---

## 3. Graph (Decision Engine)

```mermaid
flowchart TD
    A[detect_intent] --> B{Intent}

    B -->|search| C[search_node]
    B -->|details| D[details_node]
    B -->|book| E[booking_node]
    B -->|other| F[human_node]

    C --> G[response_node]
    D --> G
    E --> G
    F --> G
```

---

# Database Design

```mermaid
erDiagram
    LISTINGS {
        int id PK
        string name
        string location
        int price_per_night
        int max_guests
    }

    BOOKINGS {
        int id PK
        int listing_id FK
        string guest_name
        int guests
        date check_in
        date check_out
        string status
    }

    CONVERSATIONS {
        int id PK
        text user_message
        text response
        timestamp created_at
    }

    LISTINGS ||--o{ BOOKINGS : has
```
---

# Key Design Decisions

### 1. Separation of Concerns

* LLM → reasoning
* Tools → execution
* Graph → control flow

---

### 2. Validation Before Execution

Booking is only executed when all required fields exist:

* listing_id
* guests
* check_in
* check_out

Otherwise → system asks for clarification.

---

### 3. Hybrid Intent Detection

* Rule-based → fast detection
* LLM-based → flexible extraction

---

# Installation

```bash
git clone https://github.com/your-repo/stayease-agent.git
cd stayease-agent

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

# Environment Setup

Create `.env`:

```env
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/stayease
```

---
# Run Server

```bash
uvicorn main:app --reload
```

---

# API Usage

## Send Message

```http
POST /api/chat/{conversation_id}/message
```

### Example
#Search message
```json
{
  "message": "I need a room in Cox’s Bazar for 2 nights for 2 guests"
}
```

---
# Details message
```json
{
  "message": "Show me details for listing 1"
}
```
---
# Booking message
```json
{
  "message": "Book listing 1 for John, 2 guests, check-in 2026-05-01, check-out 2026-05-03"
}
```

---

# Future Improvements

* Multi-turn memory (context-aware booking)
* Date parsing ("tomorrow", "next week")
* Multilingual support (Bangla + English)
* Redis caching
* LLM fallback (Groq + OpenAI)

---

# Key Insight

> This system demonstrates how to build a reliable AI agent by separating reasoning from execution, reducing hallucination risk and improving production readiness.

---

# Author

**Limon Chandra Ray**
Junior AI Engineer

---
