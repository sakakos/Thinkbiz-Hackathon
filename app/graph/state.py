from typing import TypedDict

class AgentState(TypedDict):
    """The memory object passed between nodes."""
    thread_id: str
    task_description: str
    proposed_action: str
    human_approved: bool