import streamlit as st
import requests
import os

# Ρυθμίσεις σελίδας
st.set_page_config(page_title="AI Agent Control Panel", page_icon="🤖")

# --- ΚΡΙΣΙΜΗ ΑΛΛΑΓΗ ΓΙΑ ΔΟCKER ---
# Αν τρέχει στο Docker, το URL θα είναι http://gateway:8000/api/v1/hitl-request
# Αν το τρέχεις τοπικά, θα πέσει πίσω στο localhost.
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000/api/v1/hitl-request")

st.title("🤖 Dummy AI Agent Interface")
st.markdown("Χρησιμοποίησε αυτή τη φόρμα για να στείλεις ένα αίτημα στο **HITL Gateway**.")

# Κύρια Φόρμα
with st.form("agent_request_form"):
    st.subheader("📝 Στοιχεία Αιτήματος")
    
    # Επιλογή Agent
    agent_name = st.selectbox("Agent Name", ["Finance-Bot", "Refund-Bot", "Support-AI", "Legal-Analyst"])
    
    # Στοιχεία Χρήστη & Callback
    col1, col2 = st.columns(2)
    with col1:
        # Προτεινόμενα IDs από τη βάση σου: it_dept, cyber_dept, finance_dept
        operator_name = st.text_input("Target Operator Username (ID)", value="it_dept")
    with col2:
        callback_url = st.text_input("Agent Callback URL", value="https://webhook.site/your-id")
    
    # Περιγραφή Task
    task_metadata = st.text_area("Task Context / Metadata", "Ο πελάτης ζητάει ακύρωση παραγγελίας λόγω καθυστέρησης.")
    proposed_action = st.text_input("Proposed Action", "Ακύρωση παραγγελίας #1234 και επιστροφή χρημάτων.")
    
    # Κρισιμότητα
    urgency = st.select_slider("Urgency Level", options=["standard", "critical"])
    
    submit_button = st.form_submit_button(label="🚀 Αποστολή στο Gateway")

# Λογική Αποστολής
if submit_button:
    payload = {
        "agent_name": agent_name,
        "operator_name": operator_name,
        "task_metadata": task_metadata,
        "proposed_action": proposed_action,
        "urgency": urgency,
        "callback_url": callback_url
    }
    
    with st.spinner("Επικοινωνία με το Gateway..."):
        try:
            # Αποστολή στο δυναμικό GATEWAY_URL
            response = requests.post(GATEWAY_URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Το αίτημα εστάλη! Request ID: {result.get('request_id')}")
                st.info(f"🔔 Ειδοποίηση: **{'Teams' if urgency == 'standard' else 'SMS/Voice Call'}** -> **{operator_name}**")
            else:
                # Εδώ θα φανεί αν ο χρήστης δεν υπάρχει (404)
                st.error(f"❌ Σφάλμα Gateway ({response.status_code}): {response.text}")
        
        except Exception as e:
            st.error(f"❌ Αποτυχία σύνδεσης στο Gateway: {str(e)}")

st.divider()
st.caption(f"Connected to Gateway: {GATEWAY_URL}")