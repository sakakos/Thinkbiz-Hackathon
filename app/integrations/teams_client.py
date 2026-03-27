import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_teams_approval(thread_id: str, proposed_action: str, urgency: str = "Normal"):
    """Στέλνει μια διαδραστική Adaptive Card στο Microsoft Teams."""
    
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    
    if not webhook_url or webhook_url == "YOUR_TEAMS_WEBHOOK_URL_HERE":
        print(f"\n[MOCK TEAMS] Urgency: {urgency} | Thread: {thread_id} | Action: {proposed_action}\n")
        return True

    # Το JSON payload για το Adaptive Card του Teams
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
                            "text": "⚠️ Απαιτείται Έγκριση από Άνθρωπο (HITL)",
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Thread ID:", "value": thread_id},
                                {"title": "Urgency:", "value": urgency}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": f"**Προτεινόμενη Ενέργεια:**\n{proposed_action}",
                            "wrap": True
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "✅ Έγκριση",
                            "data": {
                                "thread_id": thread_id,
                                "decision": "approve"
                            }
                        },
                        {
                            "type": "Action.Submit",
                            "title": "❌ Απόρριψη",
                            "data": {
                                "thread_id": thread_id,
                                "decision": "deny"
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, json=card_payload, headers=headers)
    
    if response.status_code == 200 or response.status_code == 202:
        print(f"[TEAMS] Επιτυχής αποστολή αιτήματος για thread {thread_id}")
        return True
    else:
        print(f"[TEAMS] Σφάλμα: {response.status_code} - {response.text}")
        return False