FROM python:3.11-slim AS base
# Prevent Python from writing pyc files to disc and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY ./requirements.txt /code/requirements.txt

# Install the dependencies
# --no-cache-dir keeps the image size down by not storing the pip cache
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the gateway application code into the container
# Αλλάξαμε το ./app σε ./gateway για να ταιριάζει με τη νέα δομή
COPY ./gateway /code/gateway

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# Αλλάξαμε το app.main:app σε gateway.main:app
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- STAGE 2: Agent UI (Streamlit) ---
FROM base AS agent-ui
# Αντιγράφουμε το αρχείο του UI (πρέπει να είναι στον κεντρικό φάκελο)
COPY agent_ui.py .
EXPOSE 8501
CMD ["streamlit", "run", "agent_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]