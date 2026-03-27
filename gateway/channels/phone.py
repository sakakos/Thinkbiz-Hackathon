import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = 'AC34c4ffd4da2cf53fddeeb041a8229319'
TWILIO_AUTH_TOKEN = '421d43e916bffe4d837fa726ae4002cb'
TWILIO_PHONE_NUMBER = '+14788886661'
DESTINATION_PHONE_NUMBER = '+306997891734'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def trigger_escalation_call(request_id: str, gateway_url: str, message: str):
    """
    Προσομοιώνει το Gateway που καλεί το κινητό, διαβάζοντας δυναμικό μήνυμα.
    """
    print(f"Initiating HITL escalation to {DESTINATION_PHONE_NUMBER}...")
    
    # Φτιάχνουμε δυναμικά τις οδηγίες TwiML. 
    # Προσθέσαμε language="el-GR" για να διαβάζει σωστά τα Ελληνικά!
    twiml_instructions = f"""
    <Response>
        <Gather action="{gateway_url}/api/voice-response?request_id={request_id}" numDigits="1">
            <Say voice="alice" language="el-GR">{message}</Say>
        </Gather>
    </Response>
    """
    
    try:
        call = client.calls.create(
            to=DESTINATION_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml_instructions  # Στέλνουμε τις δυναμικές οδηγίες
        )
        print(f"✅ Επιτυχία! Η κλήση ξεκίνησε. Call SID: {call.sid}")
        print("Περιμένω τον άνθρωπο να απαντήσει...")
        return True
        
    except Exception as e:
        print(f"❌ Σφάλμα κατά την κλήση: {e}")
        return False