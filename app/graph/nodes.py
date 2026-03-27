from app.graph.state import AgentState

def agent_reasoning_node(state: AgentState) -> dict:
    """Simulates the AI deciding an action needs to be taken."""
    print(f"[AI Node] Analyzing task: {state.get('task_description')}")
    
    # In reality, you'd call an LLM here. We are mocking the decision.
    proposed = f"Execute high-privilege action for task: {state.get('task_description')}"
    
    return {"proposed_action": proposed}

def execution_node(state: AgentState) -> dict:
    """Executes the action ONLY if approved by the human."""
    if state.get("human_approved"):
        print(f"[Execution Node] SUCCESS: Executing '{state.get('proposed_action')}'")
        return {"task_description": "Action executed successfully."}
    else:
        print("[Execution Node] ABORTED: Action denied by human.")
        return {"task_description": "Action aborted."}