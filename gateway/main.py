import os
import uuid
import requests
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pymongo import MongoClient
from gateway.state import active_requests
from gateway.channels.router import route_to_chat, route_to_voice_sms

# Φόρτωση Ρυθμίσεων
load_dotenv()
app = FastAPI(title="HITL Asynchronous Message Broker")

# Σύνδεση με MongoDB χρησιμοποιώντας ΟΛΕΣ τις μεταβλητές του .env
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "HITL_Middleware")
COLLECTION_NAME = os.getenv("MONGODB_OPERATORS_COLLECTION", "Users")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

print(f"✅ Connected to MongoDB: {DB_NAME} -> {COLLECTION_NAME}")

# --- Pydantic Models ---
class UrgencyLevel(str, Enum):
    STANDARD = "standard"
    CRITICAL = "critical"

class AgentTaskRequest(BaseModel):
    agent_name: str
    operator_name: str
    task_metadata: str
    proposed_action: str
    urgency: UrgencyLevel = UrgencyLevel.STANDARD
    callback_url: str

class HumanDecisionPayload(BaseModel):
    request_id: str
    decision: str
    feedback: str = ""

# --- Helper Functions ---
def send_callback_to_agent(callback_url: str, payload: dict):
    """Επιστρέφει την απόφαση στον Agent (Webhook Style)"""
    try:
        print(f"[CALLBACK] 🔄 Επιστροφή στον Agent: {callback_url}")
        response = requests.post(callback_url, json=payload, timeout=5)
        response.raise_for_status()
        print("[CALLBACK] ✅ Ο Agent ενημερώθηκε επιτυχώς.")
    except Exception as e:
        print(f"[CALLBACK ERROR] ❌ Αποτυχία ενημέρωσης Agent: {e}")

# --- API ENDPOINTS ---

# 1. Λήψη αιτήματος από τον Agent
@app.post("/api/v1/hitl-request")
async def receive_agent_request(request: AgentTaskRequest):
    # Αναζήτηση στη MongoDB βάσει του ID (it_dept, finance_dept, κτλ)
    operator_id = request.operator_name.lower()
    operator_data = users_collection.find_one({"id": operator_id})
    
    if not operator_data:
        print(f"❌ DB ERROR: Το τμήμα '{operator_id}' δεν υπάρχει στη MongoDB.")
        raise HTTPException(status_code=404, detail=f"Department '{request.operator_name}' not found.")
    
    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Αποθήκευση στο State (για τη διάρκεια του session)
    active_requests[request_id] = {
        "agent_name": request.agent_name,
        "operator_name": operator_id,
        "task_metadata": request.task_metadata,
        "proposed_action": request.proposed_action,
        "callback_url": request.callback_url,
        "status": "pending_human",
        "created_at": now
    }
    
    print(f"\n[GATEWAY API] 📥 Νέο αίτημα για: {operator_data.get('name')} (Ανάκτηση από MongoDB)")

    # Χρήση του Teams Webhook URL από τη βάση
    operator_data["webhook_url"] = operator_data.get("webhooks_url_teams")

    # Routing ανάλογα με το Urgency
    if request.urgency == UrgencyLevel.CRITICAL:
        route_to_voice_sms(request_id, request.agent_name, request.proposed_action, operator_data)
    else:
        route_to_chat(request_id, request.agent_name, request.proposed_action, operator_data)
        
    return {"status": "success", "request_id": request_id}

# 2. Λήψη απόφασης (POST από Apps/Bots)
@app.post("/api/v1/human-response")
async def receive_human_decision(payload: HumanDecisionPayload, background_tasks: BackgroundTasks):
    request_id = payload.request_id
    if request_id not in active_requests:
        raise HTTPException(status_code=404, detail="Request ID not found.")
        
    state = active_requests[request_id]
    if state["status"] == "resolved":
        return {"status": "ignored", "message": "Ήδη απαντημένο."}

    state["status"] = "resolved"
    state["decided_at"] = datetime.now(timezone.utc).isoformat()
    state["human_decision"] = payload.decision
    
    agent_callback_payload = {
        "request_id": request_id,
        "decision": payload.decision,
        "feedback": payload.feedback,
        "resolved_at": state["decided_at"]
    }

    background_tasks.add_task(send_callback_to_agent, state["callback_url"], agent_callback_payload)
    return {"status": "success", "message": "Decision recorded."}

# 3. Λήψη απόφασης (GET από Browser/Teams Buttons)
@app.get("/api/v1/human-response-get", response_class=HTMLResponse)
async def receive_human_decision_get(request_id: str, decision: str, background_tasks: BackgroundTasks):
    if request_id not in active_requests:
        return "<h1>Σφάλμα</h1><p>Το αίτημα έληξε.</p>"
        
    state = active_requests[request_id]
    if state["status"] == "resolved":
        return "<h1>Ολοκληρώθηκε</h1><p>Έχει ήδη δοθεί απάντηση.</p>"

    state["status"] = "resolved"
    state["decided_at"] = datetime.now(timezone.utc).isoformat()
    state["human_decision"] = decision
    
    agent_callback_payload = {
        "request_id": request_id,
        "decision": decision,
        "feedback": "Action.OpenUrl Response",
        "resolved_at": state["decided_at"]
    }

    background_tasks.add_task(send_callback_to_agent, state["callback_url"], agent_callback_payload)

    color = "green" if decision == "approve" else "red"
    status_text = "ΕΓΚΡΙΘΗΚΕ" if decision == "approve" else "ΑΠΟΡΡΙΦΘΗΚΕ"
    
    return f"""
    <html>
        <body style="font-family: Arial; text-align: center; margin-top: 100px; background-color: #f4f4f4;">
            <h1 style="color: {color};">Η ενέργεια {status_text}</h1>
            <p>Το AI Agent ενημερώθηκε για την απόφασή σας.</p>
            <p>Μπορείτε να κλείσετε αυτό το παράθυρο.</p>
        </body>
    </html>
    """

# 4. Φωνητική απόφαση (Twilio Callback)
@app.post("/api/voice-response")
async def voice_response(request: Request, background_tasks: BackgroundTasks, request_id: str = None):
    form_data = await request.form()
    digits = form_data.get('Digits')
    
    decision = "approve" if digits == '1' else "deny"
    response_message = "Proceeding." if decision == "approve" else "Stopping agent."

    if request_id and request_id in active_requests:
        state = active_requests[request_id]
        if state["status"] != "resolved":
            state["status"] = "resolved"
            state["decided_at"] = datetime.now(timezone.utc).isoformat()
            
            agent_payload = {
                "request_id": request_id,
                "decision": decision,
                "feedback": "voice_input",
                "resolved_at": state["decided_at"]
            }
            background_tasks.add_task(send_callback_to_agent, state["callback_url"], agent_payload)

    twiml = f"<Response><Say voice='alice'>{response_message} Goodbye.</Say></Response>"
    return Response(content=twiml, media_type="text/xml")