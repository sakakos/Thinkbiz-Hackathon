import streamlit as st
import requests
import os

# Page Configuration - Wide layout to spread elements horizontally
st.set_page_config(page_title="Agent Interface", page_icon="🤖", layout="wide")

# Custom CSS to force everything into one screen
st.markdown("""
    <style>
    /* Reduce top padding of the main container */
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    /* Make text areas and inputs shorter */
    .stTextArea textarea {height: 70px !important;}
    .stTextInput input {height: 35px !important;}
    
    /* Tighten margins between elements */
    .element-container {margin-bottom: 0.2rem !important;}
    div[data-testid="stForm"] {padding: 0.8rem !important; margin-bottom: 0px;}
    
    /* Fix radio buttons alignment */
    div[role="radiogroup"] {margin-top: -10px;}
    
    /* Make headers smaller */
    h1 {font-size: 1.8rem !important; margin-bottom: 0.5rem;}
    h3 {font-size: 1.2rem !important; margin-bottom: 0.2rem;}
    </style>
    """, unsafe_allow_html=True)

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000/api/v1/hitl-request")

st.title("Agent Interface")

# Main Form
with st.form("agent_request_form"):
    st.subheader("Request Details")
    
    # Row 1: Agent Name and Callback URL
    col_a, col_b = st.columns(2)
    with col_a:
        agent_name = st.selectbox("Agent Name", ["Finance-Bot", "Refund-Bot", "Support-AI", "Legal-Analyst"])
    with col_b:
        callback_url = st.text_input("Agent Callback URL", value="https://webhook.site/your-id")
    
    # Row 2: Target Operator
    operator_name = st.text_input("Target Department ID", value="it_dept")
    
    # Row 3: Proposed Action (Back to original order)
    proposed_action = st.text_input("Proposed Action", value="Shutdown the 'Core-Finance-Service' due to suspicious activity.")
    
    # Row 4: Metadata/Context (Back to original order)
    task_metadata = st.text_area("Task Context", value="Detected unusual encryption patterns matching ransomware behavior.")
    
    # Row 5: Urgency Level
    urgency = st.radio("Urgency Level", options=["standard", "critical"], horizontal=True)
    
    submit_button = st.form_submit_button(label="Send Request to Gateway", use_container_width=True)

# Submission Logic
if submit_button:
    payload = {
        "agent_name": agent_name, "operator_name": operator_name,
        "task_metadata": task_metadata, "proposed_action": proposed_action,
        "urgency": urgency, "callback_url": callback_url
    }
    
    try:
        response = requests.post(GATEWAY_URL, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            method = "Microsoft Teams" if urgency == "standard" else "Phone Call/SMS"
            
            # Compact Success Message to avoid scrolling after submission
            st.success(f"**Sent!** ID: {result.get('request_id', 'N/A')} | **Target:** {operator_name} | **Method:** {method}")
        else:
            st.error(f"❌ Error: {response.text}")
    except Exception as e:
        st.error(f"❌ Connection Failed: {str(e)}")