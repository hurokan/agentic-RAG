# AI Agent from Zero: Build It, Run It, Understand It
#Run it
podman build -t agentic-rag -f Containerfile . &&
podman run --cgroups=disabled --rm -it \
  -v ollama-models:/root/.ollama \
  agentic-rag