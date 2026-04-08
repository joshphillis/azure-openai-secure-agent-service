FROM python:3.11-slim

# --- Create non-root user for security ---
USER root
RUN useradd -m appuser

# --- Set working directory ---
WORKDIR /app

# --- Install dependencies ---
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application code ---
COPY app.py /app/app.py

# --- Drop privileges ---
USER appuser

# --- Expose service port ---
EXPOSE 8000

# --- Start FastAPI with Uvicorn ---
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]