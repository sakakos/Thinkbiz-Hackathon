from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone
import uuid
import requests
from fastapi.responses import HTMLResponse

from gateway.state import active_requests
from gateway.users_db import OPERATORS
from gateway.channels.router import route_to_chat, route_to_voice_sms

app = FastAPI(title="HITL Asynchronous Message Broker")

class UrgencyLevel(str, Enum):
    STANDARD = "standard"
    CRITICAL = "critical"

class AgentTaskRequest(BaseModel):
    agent_name: str = Field(..., description="Το όνομα ή το ID του AI Agent")
    # ΝΕΟ ΠΕΔΙΟ: Σε ποιον απευθύνεται το αίτημα;
    operator_name: str = Field(..., description="Το username του διαχειριστή (π.χ. 'giannis')")
    task_metadata: str = Field(..., description="Περιγραφή του task και του context")
    proposed_action: str = Field(..., description="Η ενέργεια που θέλει να εκτελέσει ο Agent")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.STANDARD, description="Επίπεδο κρισιμότητας")
    callback_url: str = Field(..., description="Το URL του agent για να του επιστρέψουμε την απάντηση")

class HumanDecisionPayload(BaseModel):
    request_id: str
    decision: str = Field(..., description="'approve' ή 'deny'")
    feedback: str = Field(default="", description="Προαιρετικό σχόλιο από τον άνθρωπο")


def send_callback_to_agent(callback_url: str, payload: dict):
    """Background task για να μην μπλοκάρουμε το response προς το Teams/Browser"""
    try:
        print(f"[CALLBACK] 🔄 Επιστροφή απόφασης στον Agent στο: {callback_url}")
        # Κάνει το HTTP POST πίσω στον dummy agent
        response = requests.post(callback_url, json=payload, timeout=5)
        response.raise_for_status()
        print("[CALLBACK] ✅ Ο Agent έλαβε την απάντηση επιτυχώς.")
    except Exception as e:
        print(f"[CALLBACK ERROR] ❌ Αποτυχία επικοινωνίας με τον Agent: {e}")

@app.post("/api/v1/hitl-request")
async def receive_agent_request(request: AgentTaskRequest):
    # Έλεγχος αν ο χρήστης υπάρχει στη βάση μας
    operator_username = request.operator_name.lower()
    if operator_username not in OPERATORS:
        raise HTTPException(status_code=404, detail=f"Operator '{request.operator_name}' not found in database.")
        
    operator_data = OPERATORS[operator_username]
    
    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    active_requests[request_id] = {
        "agent_name": request.agent_name,
        "operator_name": operator_username,
        "task_metadata": request.task_metadata,
        "proposed_action": request.proposed_action,
        "callback_url": request.callback_url,
        "status": "pending_human",
        "created_at": now,
        "notified_at": now,
        "decided_at": None
    }
    
    print(f"\n[GATEWAY API] 📥 Νέο αίτημα από: {request.agent_name} για τον/την {operator_data['full_name']}")
    
    # Δυναμικό Routing (Περνάμε πλέον τα στοιχεία του operator στον router)
    if request.urgency == UrgencyLevel.CRITICAL:
        route_to_voice_sms(request_id, request.agent_name, request.proposed_action, operator_data)
    else:
        route_to_chat(request_id, request.agent_name, request.proposed_action, operator_data)
        
    return {"status": "success", "request_id": request_id}

# Το /api/v1/human-response παραμένει ακριβώς όπως το είχαμε!

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



@app.get("/api/v1/human-response-get", response_class=HTMLResponse)
async def receive_human_decision_get(request_id: str, decision: str, background_tasks: BackgroundTasks):
    """
    Αυτό ανοίγει στον browser του χρήστη όταν πατήσει το κουμπί στο Teams.
    """
    if request_id not in active_requests:
        return "<h1>Σφάλμα</h1><p>Το αίτημα δεν βρέθηκε ή έχει λήξει.</p>"
        
    state = active_requests[request_id]
    
    # Idempotency: Αν έχει ήδη απαντηθεί, δεν κάνουμε τίποτα
    if state["status"] == "resolved":
        return "<h1>Ολοκληρώθηκε</h1><p>Αυτό το αίτημα έχει ήδη απαντηθεί.</p>"

    # Update lifecycle
    state["status"] = "resolved"
    state["decided_at"] = datetime.now(timezone.utc).isoformat()
    state["human_decision"] = decision
    
    print(f"\n[GATEWAY API] 👤 Ο άνθρωπος απάντησε (μέσω Browser): {decision.upper()} για το {request_id}")

    # Προετοιμασία του payload για τον Agent
    agent_callback_payload = {
        "request_id": request_id,
        "decision": decision,
        "feedback": "Απαντήθηκε μέσω Teams Action.OpenUrl",
        "resolved_at": state["decided_at"]
    }

    # Ασύγχρονη ενημέρωση του Agent
    background_tasks.add_task(send_callback_to_agent, state["callback_url"], agent_callback_payload)

    # Φτιάχνουμε μια όμορφη απάντηση για τον Browser του χρήστη
    color = "green" if decision == "approve" else "red"
    status_text = "ΕΓΚΡΙΘΗΚΕ" if decision == "approve" else "ΑΠΟΡΡΙΦΘΗΚΕ"
    
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background-color: #f9f9f9;">
            <h1 style="color: {color};">Η ενέργεια {status_text}</h1>
            <p>Η απόφασή σου καταγράφηκε επιτυχώς και το AI ενημερώθηκε.</p>
            <p>Μπορείς να κλείσεις αυτή την καρτέλα και να επιστρέψεις στο Teams.</p>
        </body>
    </html>
    """