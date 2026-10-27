FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt requirements.lock* ./
RUN pip install --no-cache-dir -r requirements.lock

# Copy source code
COPY . .

# Environment setup
# Secrets will be mounted at /run/secrets/ at runtime via docker-compose
ENV PYTHONUNBUFFERED=1

# Command to run the agent
CMD ["python", "agent.py", "start"]
