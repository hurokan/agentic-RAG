
import asyncio
import re

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    function_tool,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)


# --------------------------------------------------
# Ollama: Local LLM configuration
# --------------------------------------------------

set_tracing_disabled(True)

ollama_client = AsyncOpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",  # Ollama does not require a real API key
)

local_model = OpenAIChatCompletionsModel(
    model="qwen3:1.7b",
    openai_client=ollama_client,
)


# --------------------------------------------------
# Notes search configuration
# --------------------------------------------------

STOP_WORDS = {
    "what", "is", "the", "a", "an", "of", "my",
    "according", "to", "and", "in", "from", "about",
    "does", "do", "me", "please", "find", "tell",
    "show", "give", "can", "you", "for", "on",
    "with", "how", "much", "many", "your"
}


# --------------------------------------------------
# Tool 1: Search local notes
# --------------------------------------------------

@function_tool
def search_notes(query: str) -> str:
    """Search local developer notes for relevant information."""

    print(f"\n[TOOL CALL] search_notes(query={query!r})")

    try:
        with open("/app/notes.txt", "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        return "ERROR: notes.txt was not found."

    words = re.findall(r"[a-z0-9]+", query.lower())
    keywords = [word for word in words if word not in STOP_WORDS]

    if not keywords:
        return "Please provide a more specific search query."

    scored_lines = []

    for line in lines:
        text = line.lower()
        score = sum(keyword in text for keyword in keywords)

        if score > 0:
            scored_lines.append((score, line))

    scored_lines.sort(key=lambda item: item[0], reverse=True)

    if not scored_lines:
        result = "No matching information found in the notes."
    else:
        result = "\n".join(
            line for _, line in scored_lines[:5]
        )

    print(f"[TOOL RESULT] {result}")
    return result


# --------------------------------------------------
# Tool 2: Calculate percentage
# --------------------------------------------------

@function_tool
def calculate_percentage(part: float, whole: float) -> str:
    """Calculate what percentage the part is of the whole."""

    print(
        "\n[TOOL CALL] "
        f"calculate_percentage(part={part}, whole={whole})"
    )

    if whole == 0:
        result = "Cannot calculate a percentage when the whole is zero."
    else:
        percentage = (part / whole) * 100
        result = f"{percentage:g}%"

    print(f"[TOOL RESULT] {result}")
    return result


# --------------------------------------------------
# AI Agent
# --------------------------------------------------

agent = Agent(
    name="Developer Assistant",
    model=local_model,
    instructions="""
You are a helpful developer assistant running locally through Ollama.

Available tools:

1. search_notes(query)
   Use this tool when the answer requires information
   from the local developer notes.

2. calculate_percentage(part, whole)
   Use this tool when a percentage calculation is required.
   It calculates (part / whole) * 100.

Rules:
- Use the tools when appropriate; do not merely claim you used them.
- For questions requiring both note lookup and calculation,
  search the notes first, then calculate using the retrieved values.
- Do not invent facts missing from the notes.
- If the notes do not contain the requested information,
  clearly say so.
- Explain the result in simple, concise language.
- Never claim a tool succeeded unless its result supports the answer.
""",
    tools=[search_notes, calculate_percentage],
)


# --------------------------------------------------
# Interactive terminal
# --------------------------------------------------

async def main():
    print("\nDeveloper Assistant is ready!")
    print("Model: qwen3:1.7b (local Ollama)")
    print("Tools: search_notes, calculate_percentage")
    print("Type your question, or 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            result = await Runner.run(agent, question)

            print("\n[FINAL ANSWER]")
            print(result.final_output)
            print()

        except Exception as e:
            print(f"\n[ERROR] {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
