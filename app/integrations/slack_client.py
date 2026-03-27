import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_approval_request(thread_id: str, proposed_action: str):
    """Sends a mock or real message to a messaging platform."""
    
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    # If no real webhook is set up yet, just print to terminal
    if not webhook_url or webhook_url == "https://hooks.slack.com/services/YOUR/WEBHOOK/URL":
        print("\n" + "="*50)
        print(f"--> [MOCK SLACK MESSAGE SENT]")
        print(f"--> Thread ID: {thread_id}")
        print(f"--> Review Required: {proposed_action}")
        print(f"--> Action: [Approve] or [Deny]")
        print("="*50 + "\n")
        return True

    # Real Slack Block Kit payload
    payload = {
        "text": f"Review required for thread {thread_id}",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*AI Action Review Required*\n{proposed_action}"}
            }
            # Add interactive buttons here for a full Slack implementation
        ]
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200