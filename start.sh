#!/bin/sh
set -eu

echo "Starting Ollama..."
ollama serve >/tmp/ollama.log 2>&1 &

echo "Waiting for Ollama..."
ready=0

for i in $(seq 1 60); do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null; then
        ready=1
        break
    fi
    sleep 2
done

if [ "$ready" -ne 1 ]; then
    cat /tmp/ollama.log
    echo "ERROR: Ollama failed to start."
    exit 1
fi

echo "Pulling local model..."
ollama pull qwen3:1.7b

echo "Starting Python AI Agent..."
exec /opt/agent-venv/bin/python /app/agent.py