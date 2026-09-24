import os
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 1. Define the Pydantic schema for structured output
class ContactInfo(BaseModel):
    """Contact information for a person."""
    name: str = Field(description="The name of the person")
    email: str = Field(description="The email address of the person")
    phone: str = Field(description="The phone number of the person")

# 2. Configure LM Studio base parameters
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

# 4. Initialize the agent using your local LM Studio instance
agent = create_agent(
    model=local_llm,             # Replaced "gpt-5.5" with your local setup
    response_format=ContactInfo   # Auto-selects ProviderStrategy
)

# 5. Invoke the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
})

print(result["structured_response"])
# Expected output: ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
