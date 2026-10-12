FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create isolated Python environment
RUN python3 -m venv /opt/agent-venv

ENV PATH="/opt/agent-venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=127.0.0.1:11434

# Install Agent SDK
RUN pip install --no-cache-dir openai-agents

# Copy application files
COPY agent.py .
COPY notes.txt .
COPY start.sh .

# Start application instead of the Ollama CLI
ENTRYPOINT ["/bin/sh", "/app/start.sh"]
