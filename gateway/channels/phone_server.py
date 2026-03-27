import os
from flask import Flask, request

app = Flask(__name__)

# Αυτό είναι το endpoint που περιμένει το χτύπημα από το Twilio (το callback)
@app.route("/api/voice-response", methods=['POST'])
def voice_response():
    # Το Twilio στέλνει τα δεδομένα της κλήσης. Το πλήκτρο έρχεται στο 'Digits'
    digits = request.form.get('Digits')
    
    print("\n" + "="*50)
    print("📞 ΕΙΣΕΡΧΟΜΕΝΟ CALLBACK ΑΠΟ ΤΟΝ ΑΝΘΡΩΠΟ (HITL Gateway)")
    print("="*50)
    
    # Εδώ υλοποιούμε τη λογική του routing (1 = Approve, 2 = Deny)
    if digits == '1':
        print("✅ ΑΠΟΦΑΣΗ: APPROVE (Έγκριση κλιμάκωσης)")
        # Εδώ κανονικά το σύστημά σας θα έστελνε σήμα πίσω στον AI Agent
        response_message = "Action approved. The A.I. agent will proceed. Goodbye."
        
    elif digits == '2':
        print("❌ ΑΠΟΦΑΣΗ: REJECT (Απόρριψη κλιμάκωσης)")
        # Εδώ το σύστημά σας θα έλεγε στον AI Agent να σταματήσει
        response_message = "Action rejected. The A.I. agent has been stopped. Goodbye."
        
    else:
        print(f"⚠️ ΑΓΝΩΣΤΟ ΠΛΗΚΤΡΟ: {digits}")
        response_message = "Invalid input. The A.I. agent will be notified. Goodbye."
        
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