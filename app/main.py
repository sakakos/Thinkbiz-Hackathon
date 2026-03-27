from fastapi import FastAPI, Request
from pydantic import BaseModel
import uuid

from app.graph.workflow import hitl_agent
from app.integrations.slack_client import send_approval_request

app = FastAPI(title="HITL Agent API")

class TaskRequest(BaseModel):
    task: str

@app.post("/start-task")
async def start_task(req: TaskRequest):
    """Kicks off the agent workflow."""
    # Generate a unique ID for this execution thread
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Start the graph. It will run until it hits the breakpoint.
    initial_state = {
        "thread_id": thread_id,
        "task_description": req.task,
        "human_approved": False
    }
    hitl_agent.invoke(initial_state, config)
    
    # Retrieve the state to see what the AI proposed
    current_state = hitl_agent.get_state(config)
    action_to_review = current_state.values.get("proposed_action")
    
    # Send the notification to the human
    send_approval_request(thread_id, action_to_review)
    
    return {
        "status": "AI paused. Waiting for human approval.",
        "thread_id": thread_id
    }

@app.post("/webhook/human-response")
async def human_webhook(request: Request):
    """Endpoint for Slack/Teams to hit when a button is clicked."""
    payload = await request.json()
    
    thread_id = payload.get("thread_id") 
    decision = payload.get("decision") # Expected: "approve" or "deny"
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Update the state with the human's decision
    is_approved = (decision == "approve")
    hitl_agent.update_state(config, {"human_approved": is_approved})
    
    # 2. Resume the graph execution
    hitl_agent.invoke(None, config)
    
    return {"status": f"Human feedback '{decision}' applied. AI resumed."}