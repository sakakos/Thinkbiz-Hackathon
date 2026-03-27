import os
import requests

def send_teams_alert(request_id: str, agent_name: str, action: str):
    """
    Δημιουργεί και στέλνει μια Adaptive Card στο Microsoft Teams.
    """
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    gateway_base_url = os.getenv("GATEWAY_BASE_URL", "http://localhost:8000").rstrip("/")
    human_response_url = f"{gateway_base_url}/api/v1/human-response"
    
    if not webhook_url:
        print(f"[TEAMS MOCK] 🔔 Ειδοποίηση για {agent_name}: {action} (Δεν βρέθηκε Webhook URL)")
        return False

    # Το JSON payload (Adaptive Card) με τα κουμπιά
    card_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "⚠️ Απαιτείται Έγκριση (HITL)",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Attention"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Agent:", "value": agent_name},
                                {"title": "Request ID:", "value": request_id}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": f"**Προτεινόμενη Ενέργεια:**\n{action}",
                            "wrap": True
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.Http",
                            "title": "✅ Έγκριση",
                            "method": "POST",
                            "url": human_response_url,
                            "body": f'{{"request_id": "{request_id}", "decision": "approve", "feedback": ""}}',
                            "headers": [{"name": "Content-Type", "value": "application/json"}]
                        },
                        {
                            "type": "Action.Http",
                            "title": "❌ Απόρριψη",
                            "method": "POST",
                            "url": human_response_url,
                            "body": f'{{"request_id": "{request_id}", "decision": "deny", "feedback": ""}}',
                            "headers": [{"name": "Content-Type", "value": "application/json"}]
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=card_payload, timeout=5)
        response.raise_for_status()
        print(f"[TEAMS] Επιτυχής αποστολή ειδοποίησης για το request {request_id}")
        return True
    except Exception as e:
        print(f"[TEAMS ERROR] Αποτυχία αποστολής στο Teams: {e}")
        return False