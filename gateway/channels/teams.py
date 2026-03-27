import requests

def send_teams_alert(request_id: str, agent_name: str, action: str, webhook_url: str):
    """
    Δημιουργεί και στέλνει μια Adaptive Card στο Microsoft Teams του εκάστοτε χρήστη.
    """
    if not webhook_url:
        print(f"[TEAMS ERROR] 🔔 Δεν βρέθηκε Webhook URL για αυτόν τον χρήστη.")
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
                            "type": "Action.OpenUrl",
                            "title": "✅ Έγκριση",
                            # Θα καλεί το νέο GET endpoint που θα φτιάξουμε
                            "url": f"http://localhost:8000/api/v1/human-response-get?request_id={request_id}&decision=approve"
                        },
                        {
                            "type": "Action.OpenUrl",
                            "title": "❌ Απόρριψη",
                            "url": f"http://localhost:8000/api/v1/human-response-get?request_id={request_id}&decision=deny"
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=card_payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[TEAMS ERROR] Αποτυχία αποστολής στο Teams: {e}")
        return False