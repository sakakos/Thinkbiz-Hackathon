import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Αυτό είναι το endpoint που περιμένει το χτύπημα από το Twilio (το callback)
@app.route("/api/voice-response", methods=['POST'])
def voice_response():
    # Το Twilio στέλνει τα δεδομένα της κλήσης. Το πλήκτρο έρχεται στο 'Digits'
    digits = request.form.get('Digits')
    request_id = request.args.get("request_id")
    gateway_base_url = os.getenv("GATEWAY_BASE_URL", "http://localhost:8000").rstrip("/")
    
    print("\n" + "="*50)
    print("📞 ΕΙΣΕΡΧΟΜΕΝΟ CALLBACK ΑΠΟ ΤΟΝ ΑΝΘΡΩΠΟ (HITL Gateway)")
    print("="*50)
    
    # Εδώ υλοποιούμε τη λογική του routing (1 = Approve, 2 = Deny)
    if digits == '1':
        print("✅ ΑΠΟΦΑΣΗ: APPROVE (Έγκριση κλιμάκωσης)")
        decision = "approve"
        response_message = "Action approved. The A.I. agent will proceed. Goodbye."
        
    elif digits == '2':
        print("❌ ΑΠΟΦΑΣΗ: REJECT (Απόρριψη κλιμάκωσης)")
        decision = "deny"
        response_message = "Action rejected. The A.I. agent has been stopped. Goodbye."
        
    else:
        print(f"⚠️ ΑΓΝΩΣΤΟ ΠΛΗΚΤΡΟ: {digits}")
        decision = "deny"
        response_message = "Invalid input. The A.I. agent will be notified. Goodbye."

    if request_id:
        try:
            callback_payload = {
                "request_id": request_id,
                "decision": decision,
                "feedback": "voice_input",
            }
            response = requests.post(
                f"{gateway_base_url}/api/v1/human-response",
                json=callback_payload,
                timeout=5,
            )
            print(f"[VOICE CALLBACK] Gateway ενημέρωση: {response.status_code}")
        except Exception as e:
            print(f"[VOICE CALLBACK ERROR] Αποτυχία ενημέρωσης gateway: {e}")
    else:
        print("[VOICE CALLBACK WARN] Δεν βρέθηκε request_id στο callback query params.")
        
    print("="*50 + "\n")
    
    # Χτίζουμε την απάντηση σε μορφή XML (TwiML) για να την ακούσει ο άνθρωπος στο κινητό
    twiml_response = f"""
    <Response>
        <Say voice="alice" language="en-US">{response_message}</Say>
    </Response>
    """
    
    # Επιστρέφουμε την XML απάντηση πίσω στο Twilio με κωδικό 200 (Επιτυχία)
    return twiml_response, 200, {'Content-Type': 'text/xml'}


if __name__ == "__main__":
    # Για να δουλέψει σωστά μέσα σε Docker Container, το host πρέπει να είναι 0.0.0.0
    # Χρησιμοποιούμε τη θύρα 8080 (ή όποια οριστεί από τα environment variables του Azure)
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Ο HITL Gateway Server ξεκίνησε στο port {port}...")
    app.run(host="0.0.0.0", port=port)