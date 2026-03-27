from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone
import uuid
import requests

from gateway.state import active_requests
from gateway.channels.router import route_to_chat, route_to_voice_sms

app = FastAPI(title="HITL Asynchronous Message Broker")

# --- MED GAP 1: Constrain urgency to an Enum ---
class UrgencyLevel(str, Enum):
    STANDARD = "standard"
    CRITICAL = "critical"

class AgentTaskRequest(BaseModel):
    agent_name: str = Field(..., description="Το όνομα ή το ID του AI Agent")
    task_metadata: str = Field(..., description="Περιγραφή του task και του context")
    proposed_action: str = Field(..., description="Η ενέργεια που θέλει να εκτελέσει ο Agent")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.STANDARD, description="Επίπεδο κρισιμότητας")
    callback_url: str = Field(..., description="Το URL του agent για να του επιστρέψουμε την απάντηση")

class HumanDecisionPayload(BaseModel):
    request_id: str
    decision: str = Field(..., description="'approve' ή 'deny'")
    feedback: str = Field(default="", description="Προαιρετικό σχόλιο από τον άνθρωπο")

def send_callback_to_agent(callback_url: str, payload: dict):
    """Background task για να μην μπλοκάρουμε το response προς το Teams/Slack"""
    try:
        print(f"[CALLBACK] 🔄 Επιστροφή απόφασης στον Agent στο: {callback_url}")
        response = requests.post(callback_url, json=payload, timeout=5)
        response.raise_for_status()
        print("[CALLBACK] ✅ Ο Agent έλαβε την απάντηση επιτυχώς.")
    except Exception as e:
        print(f"[CALLBACK ERROR] ❌ Αποτυχία επικοινωνίας με τον Agent: {e}")

@app.post("/api/v1/hitl-request")
async def receive_agent_request(request: AgentTaskRequest):
    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # --- MED GAP 2: Lifecycle timestamps & status transitions ---
    active_requests[request_id] = {
        "agent_name": request.agent_name,
        "task_metadata": request.task_metadata,
        "proposed_action": request.proposed_action,
        "callback_url": request.callback_url,
        "status": "pending_human",
        "created_at": now,
        "notified_at": now,
        "decided_at": None
    }
    
    print(f"\n[GATEWAY API] 📥 Νέο αίτημα από: {request.agent_name} | Urgency: {request.urgency.value.upper()}")
    
    # Routing Logic
    if request.urgency == UrgencyLevel.CRITICAL:
        route_to_voice_sms(request_id, request.agent_name, request.proposed_action)
    else:
        route_to_chat(request_id, request.agent_name, request.proposed_action)
        
    return {"status": "success", "request_id": request_id}

# --- HIGH GAP 1 & 2: Human Ingress Path & Agent Callback ---
@app.post("/api/v1/human-response")
async def receive_human_decision(payload: HumanDecisionPayload, background_tasks: BackgroundTasks):
    """
    Το endpoint που καλείται από το Teams/Slack όταν ο άνθρωπος πατάει Approve/Deny.
    """
    request_id = payload.request_id
    
    if request_id not in active_requests:
        raise HTTPException(status_code=404, detail="Request ID not found or expired.")
        
    state = active_requests[request_id]
    
    # Αποτροπή διπλής απάντησης (Idempotency)
    if state["status"] == "resolved":
        return {"status": "ignored", "message": "Αυτό το αίτημα έχει ήδη απαντηθεί."}

    # Update lifecycle
    state["status"] = "resolved"
    state["decided_at"] = datetime.now(timezone.utc).isoformat()
    state["human_decision"] = payload.decision
    
    print(f"\n[GATEWAY API] 👤 Ο άνθρωπος απάντησε: {payload.decision.upper()} για το request {request_id}")

    # Προετοιμασία του payload για τον Agent
    agent_callback_payload = {
        "request_id": request_id,
        "decision": payload.decision,
        "feedback": payload.feedback,
        "resolved_at": state["decided_at"]
    }

    # HIGH GAP 2: Χρήση του callback_url για να κλείσουμε τη λούπα (ασύγχρονα)
    background_tasks.add_task(send_callback_to_agent, state["callback_url"], agent_callback_payload)

    return {"status": "success", "message": "Η απόφαση καταγράφηκε και προωθείται στον Agent."}