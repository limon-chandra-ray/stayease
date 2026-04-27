import json
import re
from datetime import date
from langchain_groq import ChatGroq
from agent.state import AgentState
from agent.tools import (
    search_available_properties,
    get_listing_details,
    create_booking,
)

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
llm_json = ChatGroq(model="llama-3.1-8b-instant", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})


def detect_intent_and_extract(state: AgentState) -> AgentState:
    prompt = f"""
        You are an intent classifier for StayEase.

        Allowed intents:
        - search
        - details
        - book
        - human

        Return JSON only.

        User message:
        {state["user_message"]}

        JSON schema:
        {{
        "intent": "search|details|book|human",
        "location": "string or null",
        "guests": number or null,
        "nights": number or null,
        "max_price": number or null,
        "listing_id": number or null,
        "guest_name": "string or null",
        "check_in": "YYYY-MM-DD or null",
        "check_out": "YYYY-MM-DD or null"
        }}
        """

    result = llm_json.invoke(prompt)
    # Strip markdown code blocks if present
    content = result.content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    data = json.loads(content)

    state["intent"] = data.get("intent", "human")
    state["extracted"] = data
    return state


def search_node(state: AgentState) -> AgentState:
    data = state["extracted"] or {}

    result = search_available_properties.invoke({
        "location": data.get("location") or "",
        "guests": data.get("guests") or 1,
        "max_price": data.get("max_price"),
    })

    state["tool_result"] = result
    return state


def details_node(state: AgentState) -> AgentState:
    data = state["extracted"] or {}

    result = get_listing_details.invoke({
        "listing_id": data.get("listing_id")
    })

    state["tool_result"] = result
    return state


def booking_node(state: AgentState) -> AgentState:
    data = state["extracted"] or {}

    result = create_booking.invoke({
        "listing_id": data.get("listing_id"),
        "guest_name": data.get("guest_name") or "Guest",
        "guests": data.get("guests") or 1,
        "check_in": data.get("check_in"),
        "check_out": data.get("check_out"),
    })

    state["tool_result"] = result
    return state


def human_node(state: AgentState) -> AgentState:
    state["tool_result"] = {
        "message": "This request is outside StayEase supported actions. Please contact a human agent."
    }
    return state


def response_node(state: AgentState) -> AgentState:
    intent = state.get("intent")
    tool_result = state.get("tool_result")

    # 🧠 Use LLM to generate message (text only)
    prompt = f"""
You are StayEase booking assistant.

Write a short helpful response in natural language.
Use BDT pricing when prices exist.

User message:
{state["user_message"]}

Intent:
{intent}

Tool result:
{tool_result}
"""

    result = llm.invoke(prompt)
    message_text = result.content.strip()

    # ✅ Convert to JSON ONLY for search
    if intent == "search":
        data = []
        extracted = state.get("extracted") or {}
        total_nights = extracted.get("nights") or 1

        if tool_result:
            for item in tool_result:
                price = item["price_per_night"]
                data.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price_per_night": price,
                    "total_nights": total_nights,
                    "total_cost_amount": price * total_nights,
                })

        state["response"] = {
            "type": "search",
            "message": message_text,
            "data": data
        }
        return state

    # ✅ DETAILS JSON
    if intent == "details":
        state["response"] = {
            "type": "details",
            "data": tool_result
        }
        return state

    # ✅ BOOKING JSON
    if intent == "book":
        booking_data = None
        if tool_result:
            booking_data = {
                k: v.isoformat() if isinstance(v, date) else v
                for k, v in tool_result.items()
            }
        state["response"] = {
            "type": "booking",
            "message": message_text,
            "data": booking_data
        }
        return state

    # fallback
    state["response"] = {
        "type": "general",
        "message": message_text,
        "data": None
    }

    return state