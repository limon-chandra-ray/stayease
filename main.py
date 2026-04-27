from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import graph
from agent.db import get_connection
import json

app = FastAPI(title="StayEase AI Agent")


class MessageRequest(BaseModel):
    message: str


@app.post("/api/chat/{conversation_id}/message")
def send_guest_message(conversation_id: int, payload: MessageRequest):
    try:
        result = graph.invoke({
            "conversation_id": conversation_id,
            "user_message": payload.message,
            "intent": None,
            "extracted": None,
            "tool_result": None,
            "response": None,
        })

        with get_connection() as conn:
            with conn.cursor() as cur:
                response = result["response"]
                response_text = json.dumps(response) if isinstance(response, dict) else response
                cur.execute(
                    """
                    INSERT INTO conversations (user_message, response)
                    VALUES (%s, %s)
                    """,
                    (payload.message, response_text),
                )
                conn.commit()

        return {
            "conversation_id": conversation_id,
            "message": payload.message,
            "response": result["response"],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/chat/{conversation_id}/history")
def get_conversation_history(conversation_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_message, response, created_at
                FROM conversations
                ORDER BY created_at ASC
                LIMIT 50
                """
            )
            rows = cur.fetchall()

    return {
        "conversation_id": conversation_id,
        "messages": rows,
    }