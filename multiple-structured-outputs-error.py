import os

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Union
from langchain.agents import create_agent
from langchain.agents.structured_output import StructuredOutputValidationError, ToolStrategy


class ContactInfo(BaseModel):
    name: str = Field(description="Person's name")
    email: str = Field(description="Email address")

class EventDetails(BaseModel):
    event_name: str = Field(description="Name of the event")
    date: str = Field(description="Event date")

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

agent = create_agent(
    model=local_llm,
    tools=[],
    response_format=ToolStrategy(Union[ContactInfo, EventDetails])  # Default: handle_errors=True
)

# 4. Invoke and intercept validation errors
try:
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Extract info: John Doe (john@email.com) is organizing Tech Conference on March 15th"}]
    })
    
    # Print data outcome if it succeeded choosing one schema
    print("--- Structured Outcome ---")
    print(result.get("structured_response"))
    
except StructuredOutputValidationError as err:
    # --- PRINT THE ERROR OBJECTS NEEDED ---
    print("--- Caught Validation Failure Object ---")
    print(f"Error Type: {type(err)}")
    print(f"Failed Tool Choice: {err.tool_name}")
    print(f"Raw Underlying Cause: {err.source}")
    print(f"Original LLM Response Message: {err.ai_message}")