import requests

# Όσο δουλεύεις τοπικά. Όταν ανέβει στο Azure το Gateway, θα βάλεις το public URL.
GATEWAY_URL = "http://localhost:8000/api/v1/hitl-request"
AGENT_NAME = "Azure-Finance-Agent"

def escalate_to_human(task_metadata: str, proposed_action: str, urgency: str = "standard") -> str:
    """
    ΠΕΡΙΓΡΑΦΗ ΓΙΑ ΤΟ LLM (Αυτό θα διαβάζει το μοντέλο του Azure για να ξέρει πότε να το καλέσει):
    Κάλεσε αυτό το εργαλείο όταν πρόκειται να εκτελέσεις μια κρίσιμη ενέργεια ή όταν δεν είσαι σίγουρος. 
    Στέλνει τα δεδομένα σε έναν άνθρωπο για τελική έγκριση. Το urgency μπορεί να είναι "standard" ή "critical".
    """
    
    payload = {
        "agent_name": AGENT_NAME,
        "task_metadata": task_metadata,
        "proposed_action": proposed_action,
        "urgency": urgency,
        "callback_url": "http://localhost:8001/api/agent-callback" # Το δικό του URL για να λάβει την απάντηση
    }
    
    print(f"\n[AGENT TOOL] Κλήση Gateway για έγκριση: {proposed_action}...")
    
    try:
        response = requests.post(GATEWAY_URL, json=payload, timeout=5)
        response.raise_for_status()
        return "Το αίτημα στάλθηκε στον άνθρωπο επιτυχώς. Παρακαλώ μπες σε κατάσταση αναμονής (standby) μέχρι να λάβεις την απάντηση μέσω του callback."
    except Exception as e:
        return f"Αποτυχία επικοινωνίας με το HITL Gateway: {str(e)}"