import os
from twilio.rest import Client

# === 1. ΤΑ ΚΛΕΙΔΙΑ ΣΟΥ ΑΠΟ ΤΟ TWILIO CONSOLE ===
# ΠΡΟΣΟΧΗ: Στο τελικό project καλό είναι να τα βάζετε σε αρχείο .env, 
# αλλά για το hackathon test μπορείτε να τα βάλετε κατευθείαν εδώ.
TWILIO_ACCOUNT_SID = 'AC34c4ffd4da2cf53fddeeb041a8229319' # Βάλε το δικό σου Account SID
TWILIO_AUTH_TOKEN = '421d43e916bffe4d837fa726ae4002cb'              # Βάλε το δικό σου Auth Token

# === 2. ΟΙ ΤΗΛΕΦΩΝΙΚΟΙ ΑΡΙΘΜΟΙ ===
# Πρέπει να έχουν τον κωδικό χώρας μπροστά, π.χ., +30 για Ελλάδα ή +1 για ΗΠΑ
TWILIO_PHONE_NUMBER = '+14788886661'    # Ο αριθμός που σου έδωσε το Twilio
DESTINATION_PHONE_NUMBER = '+306997891734' # Το ΔΙΚΟ ΣΟΥ verified κινητό

# Αρχικοποίηση του Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def trigger_escalation_call():
    """
    Αυτή η συνάρτηση προσομοιώνει το Gateway που καλεί το κατάλληλο κανάλι
    όταν ο agent ζητήσει human input.
    """
    print(f"Initiating HITL escalation to {DESTINATION_PHONE_NUMBER}...")
    
    try:
        call = client.calls.create(
            to=DESTINATION_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            # Εδώ βάζουμε το URL που μόλις έφτιαξες! 
            # Λέει στο Twilio να διαβάσει το μήνυμα και να περιμένει το πλήκτρο.
            url='https://handler.twilio.com/twiml/EHbf2731a614fd7bdc0026e6750eb4c048'
        )
        print(f"Επιτυχία! Η κλήση ξεκίνησε. Call SID: {call.sid}")
        print("Περιμένω τον άνθρωπο να απαντήσει...")
        return True
        
    except Exception as e:
        print(f"❌ Σφάλμα κατά την κλήση: {e}")
        return False

# Εκτέλεση της συνάρτησης για δοκιμή
if __name__ == "__main__":
    trigger_escalation_call()