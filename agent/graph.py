from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    detect_intent_and_extract,
    search_node,
    details_node,
    booking_node,
    human_node,
    response_node,
)


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent")

    if intent == "search":
        return "search"
    if intent == "details":
        return "details"
    if intent == "book":
        return "book"

    return "human"


builder = StateGraph(AgentState)

builder.add_node("detect_intent", detect_intent_and_extract)
builder.add_node("search", search_node)
builder.add_node("details", details_node)
builder.add_node("book", booking_node)
builder.add_node("human", human_node)
builder.add_node("response", response_node)

builder.set_entry_point("detect_intent")

builder.add_conditional_edges(
    "detect_intent",
    route_by_intent,
    {
        "search": "search",
        "details": "details",
        "book": "book",
        "human": "human",
    },
)

builder.add_edge("search", "response")
builder.add_edge("details", "response")
builder.add_edge("book", "response")
builder.add_edge("human", "response")
builder.add_edge("response", END)

graph = builder.compile()