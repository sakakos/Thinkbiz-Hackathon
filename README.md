# HITL (Human-in-the-loop) Middleware 
> *"A cloud-native layer that enables AI agents to 'reach' the right person, at the right time, on the right channel."*

**1st Place Winner - TechBiz Hackathon 2026** 🥇

## 📖 Overview
As AI agents increasingly execute complex tasks, such as system security checks, full AI autonomy remains a major risk. Human supervision is no longer optional, it is a non-negotiable requirement. 

This project provides a **Human-in-the-Loop (HITL) Gateway Layer** that pauses autonomous execution when an AI agent reaches a critical point and ensures the right human operator is notified at the right time, on the optimal platform, to approve or reject the AI decisions.


## ✨ Key Features
* **Agent-Agnostic:** Designed to integrate with any AI agent, regardless of the underlying architecture.
* **Channel Modularity:** Routes the approval request to the most suitable communication channel for the human operator.
* **Asynchronous Feedback:** Ensures that the system isn't blocked while waiting for human input.


## 🛠️ Tech Stack
* **Backend:** FastAPI / Python
* **Integrations (Channels):** Microsoft Teams (Adaptive Cards), Twilio API for Phone Calls
* **Deployment:** Localhost / Docker

## ⚙️ System Workflow

The middleware handles requests in a non-blocking, asynchronous manner to prevent agent timeout:

1. **AI Payload:** The AI agent hits a confidence or risk threshold, pauses its execution, and fires an approval request to our system.
2. **Gateway Routing:** The system parses the payload and determines the optimal human channel (Teams or Phone Call) based on urgency and operator availability.
3. **Human Channel Delivery:** The request is delivered to the operator through specific interfaces.
   * **Teams:** Dispatches an Adaptive Card to a specified MS Teams webhook.
   * **Phone Call:** Triggers an automated call prompting keypad input.
5. **Decision Capture:** The human operator easily inputs their decision (e.g. clicks a button on Teams or presses a keypad digit on the phone).
6. **Async Return:** A background task captures the human feedback and asynchronously notifies the paused AI agent to resume its workflow based on the decision.

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* Microsoft Teams Webhook URL
* Twilio Account (for voice calls)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sakakos/Thinkbiz-Hackathon.git
cd Thinkbiz-Hackathon
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the root directory and configure your environment variables:
```env
TEAMS_WEBHOOK_URL=https://your.webhook.url
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
APP_PORT=8000
```

### Running the Application
Start the development server:
```bash
uvicorn main:app --reload --port 8000
```

## 👥 Team
Built by team **Agents Zero** for the TechBiz 2026 Hackathon.
