import requests

GATEWAY_URL = "http://localhost:8000/api/v1/hitl-request"

payload = {
    "agent_name": "Finance-Bot",
    "operator_name": "giannis",  # Ζητάμε συγκεκριμένα τον Γιάννη!
    "task_metadata": "Ο πελάτης ζητάει ακύρωση παραγγελίας.",
    "proposed_action": "Ακύρωση παραγγελίας #1234",
    "urgency": "standard",
    "callback_url": "http://localhost:8001/api/callback"
}

print(f"[AGENT] Στέλνω αίτημα στο Gateway για τον χρήστη: {payload['operator_name']}...")
response = requests.post(GATEWAY_URL, json=payload)
print("[AGENT] Απάντηση Gateway:", response.json())