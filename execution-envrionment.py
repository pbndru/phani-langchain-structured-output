
import os

from langchain.agents import create_agent
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware
from langchain_openai import ChatOpenAI

# --- 1. Define your tool cleanly ---
def search(query: str) -> str:
    """Useful for searching internal network files or local data documents."""
    return f"Mock search results for: '{query}'"

LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b")

# 3. Create the local model instance
local_llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    model=LM_STUDIO_MODEL,
    temperature=0.5,
    timeout=600,
)

# --- 2. Initialize the Agent ---
agent = create_agent(
    model=local_llm,
    tools=[search],
    middleware=[FilesystemMiddleware(backend=StateBackend())],
)

# --- 3. Execute and Output the Results (FIXED INPUT FORMAT) ---
user_query = "Search the local data for quarterly financial reports and summarize them."

print(f"Sending query to agent: '{user_query}'...\n")

try:
    # FIX: Pass the input structured inside a "messages" list format
    response = agent.invoke({
        "messages": [
            {"role": "user", "content": user_query}
        ]
    })
    
    # Output the final response cleanly
    print("=== Agent Final Output ===")
    
    # deepagents state management stores history in the message track
    if "messages" in response and len(response["messages"]) > 0:
        # Print the content of the very last message returned by the assistant
        print(response["messages"][-1].content)
    else:
        print(response)
        
except Exception as e:
    print(f"An error occurred during execution: {e}")
