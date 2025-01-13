# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 7000 8501

# Create a script to run both services
RUN echo '#!/bin/bash\n\
python -m uvicorn src.api.metrics_service:app --host 0.0.0.0 --port 7000 & \
python -m streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0\
' > /app/start.sh && chmod +x /app/start.sh

# Set the entry point
ENTRYPOINT ["/app/start.sh"]
