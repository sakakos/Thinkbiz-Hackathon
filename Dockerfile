# --- BASE STAGE: Κοινές ρυθμίσεις και βιβλιοθήκες ---
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# --- STAGE 1: Gateway (FastAPI) ---
FROM base AS gateway
COPY ./gateway ./gateway
EXPOSE 8000
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- STAGE 2: Agent UI (Streamlit) ---
FROM base AS agent-ui
# Αντιγράφουμε το αρχείο του UI (πρέπει να είναι στον κεντρικό φάκελο)
COPY agent_ui.py .
EXPOSE 8501
CMD ["streamlit", "run", "agent_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]