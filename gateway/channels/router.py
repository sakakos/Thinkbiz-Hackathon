import os
from gateway.channels.teams import send_teams_alert
from gateway.channels.phone import trigger_escalation_call

def route_to_chat(request_id: str, agent_name: str, action: str, operator_data: dict):
    """
    Δρομολογεί το μήνυμα στο κατάλληλο κανάλι βάσει των προτιμήσεων του operator.
    """
    channel = operator_data.get("preferred_channel", "teams").lower()
    webhook_url = operator_data.get("webhook_url")
    
    print(f"\n[ROUTER -> {channel.upper()}] Δρομολόγηση Standard Alert...")
    print(f"| Request ID: {request_id}")
    print(f"| Agent: {agent_name} | Ενέργεια: {action}")
    
    if channel == "teams":
        success = send_teams_alert(request_id, agent_name, action, webhook_url)
        if success:
            print("[ROUTER] Το αίτημα παραδόθηκε επιτυχώς στο Teams. Αναμονή απάντησης...")
        else:
            print("[ROUTER ERROR] Υπήρξε πρόβλημα με την παράδοση στο Teams.")
            
    elif channel == "slack":
        # Εδώ μελλοντικά θα καλείται η send_slack_alert(..., webhook_url)
        print("[ROUTER] Προσομοίωση αποστολής στο Slack...")
        
    else:
        print(f"[ROUTER ERROR] Άγνωστο κανάλι επικοινωνίας: {channel}")

def route_to_voice_sms(request_id: str, agent_name: str, task_metadata: str, action: str, operator_data: dict):
    """
    Στέλνει ειδοποίηση μέσω κλήσης ή SMS για κρίσιμα escalations.
    """
    phone = operator_data.get("phone_number")
    
    # Διαβάζει το URL από το .env. Αν δεν το βρει, χρησιμοποιεί το Railway.
    RAILWAY_PUBLIC_URL = os.getenv("GATEWAY_BASE_URL", "https://thinkbiz-hackathon-production.up.railway.app")
    
    print(f"\n[ROUTER -> SMS/VOICE] ⚠️ Αποστολή CRITICAL Alert.")
    print(f"| Request ID: {request_id}")
    print(f"| Agent: {agent_name} | Κρίσιμη Ενέργεια: {action}")
    print(f"| Τηλέφωνο Επικοινωνίας: {phone}")

    # ΔΗΜΙΟΥΡΓΙΑ ΤΟΥ ΠΛΗΡΟΥΣ ΜΗΝΥΜΑΤΟΣ 
    voice_message = f"Warning. Notification from system {agent_name}. Message: {action}. Description: {task_metadata}."

    # Περνάμε το ID, το URL ΚΑΙ το μήνυμα στην κλήση!
    success = trigger_escalation_call(request_id, RAILWAY_PUBLIC_URL, voice_message)
    
    if success:
        print(f"| Η κλήση ξεκίνησε επιτυχώς προς {phone}.")
        return

    print("| [ROUTER ERROR] Η κλήση δεν εκτελέστηκε. Fallback σε chat κανάλι...")
    route_to_chat(request_id, agent_name, f"[CRITICAL FALLBACK] {action}", operator_data)