from typing import TypedDict, Optional, Literal, Any


class AgentState(TypedDict):
    conversation_id: int
    user_message: str
    intent: Optional[Literal["search", "details", "book", "human"]]
    extracted: Optional[dict[str, Any]]
    tool_result: Optional[Any]
    response: Optional[str]