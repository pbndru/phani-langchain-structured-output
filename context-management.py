import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware, MemoryMiddleware, SkillsMiddleware, SummarizationMiddleware

# Load configurations from the .env file
load_dotenv()

# --- 1. Tool Setup (Your sandbox data source) ---
def search(query: str) -> str:
    """Useful for searching the local recipe archive files."""
    print(f"\n[SYSTEM ACTION] Tool activated! Searching archive for: '{query}'")
    
    # Simple dictionary lookup simulating a local file read
    archive = {
        "ipa": "Recipe Name: Alpha Hops IPA. Volume: 20 Litres. Grains: 5kg Maris Otter, 500g Crystal Malt. Hops: Citra, Mosaic.",
        "stout": "Recipe Name: Nightfall Stout. Volume: 25 Litres. Grains: 6kg Pale Ale Malt, 1kg Roasted Barley. Hops: East Kent Goldings."
    }
    
    # Normalize query to lowercase to keep matching simple
    query_lower = query.lower()
    for key in archive:
        if key in query_lower:
            return archive[key]
            
    return "No recipe matching that style found in the local archive."

# --- 2. Middleware & Brain Initialization ---
backend = StateBackend()

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

practice_agent = create_agent(
    model=local_llm,
    tools=[search],
    middleware=[
        FilesystemMiddleware(backend=backend),
        SummarizationMiddleware(model=local_llm, backend=backend),
        MemoryMiddleware(backend=backend, sources=["./AGENTS.md"]),
        SkillsMiddleware(backend=backend, sources=["./skills/"]),
    ],
)

# --- 3. Execute the Local Practice Run ---
test_prompt = "Can you help me brew a great IPA? Show me the recipe layout."

print("==================================================")
print(f"Executing Practice Test Input: '{test_prompt}'")
print("==================================================")

try:
    response = practice_agent.invoke({
        "messages": [
            {"role": "user", "content": test_prompt}]},
            config={"configurable": {"thread_id": "great-gatsby-lc"}},
    )
    
    print("\n================ FINAL AGENT OUTPUT ================")
    print(response["messages"][-1].content)
    print("====================================================")

except Exception as e:
    print(f"Error during sandbox run: {e}")
