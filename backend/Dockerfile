FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment setup
# Secrets will be mounted at /run/secrets/ at runtime via docker-compose
ENV PYTHONUNBUFFERED=1

# Command to run the agent
CMD ["python", "agent.py", "start"]
