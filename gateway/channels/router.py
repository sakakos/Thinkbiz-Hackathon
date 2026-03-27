from gateway.channels.teams import send_teams_alert
# Αν φτιάξετε και αρχείο για SMS/Twilio, θα το κάνετε import εδώ:
# from gateway.channels.sms import send_critical_sms

def route_to_chat(request_id: str, agent_name: str, action: str):
    """
    Στέλνει ειδοποίηση σε enterprise chat (π.χ. Microsoft Teams ή Slack).
    """
    print(f"\n[ROUTER -> TEAMS] Δρομολόγηση Standard Alert...")
    print(f"| Request ID: {request_id}")
    print(f"| Agent: {agent_name} | Ενέργεια: {action}")
    
    # Πραγματική κλήση της συνάρτησης που στέλνει το Webhook
    success = send_teams_alert(request_id, agent_name, action)
    
    if success:
        print("[ROUTER] Το αίτημα παραδόθηκε επιτυχώς στο Teams. Αναμονή απάντησης...")
    else:
        print("[ROUTER ERROR] Υπήρξε πρόβλημα με την παράδοση στο Teams.")

def route_to_voice_sms(request_id: str, agent_name: str, action: str):
    """
    Στέλνει ειδοποίηση μέσω κλήσης ή SMS (π.χ. Twilio ή Azure Communication Services) για κρίσιμα escalations.
    """
    print(f"\n[ROUTER -> SMS/VOICE] ⚠️ Αποστολή CRITICAL Alert (Κλήση/SMS).")
    print(f"| Request ID: {request_id}")
    print(f"| Agent: {agent_name} | Κρίσιμη Ενέργεια: {action}")
    
    # Για το Hackathon MVP, αν δεν προλάβετε να βάλετε Twilio/Azure Communication Services,
    # είναι αποδεκτό αυτό να μείνει ως mock (απλό print) ή να το στέλνει και αυτό στο Teams 
    # με ένδειξη "URGENT". 
    #
    # Αν έχετε συνάρτηση: send_critical_sms(request_id, agent_name, action)re