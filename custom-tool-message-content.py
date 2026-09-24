from pydantic import BaseModel, Field
from typing import Literal
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.structured_output import ToolStrategy

# The tool_message_content parameter allows you to customize the message that appears in the conversation history 
# when structured output is generated:

class MeetingAction(BaseModel):
    """Action items extracted from a meeting transcript."""
    task: str = Field(description="The specific task to be completed")
    assignee: str = Field(description="Person responsible for the task")
    priority: Literal["low", "medium", "high"] = Field(description="Priority level")

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
    response_format=ToolStrategy(
        schema=MeetingAction,
        tool_message_content="Action item captured and added to meeting notes!"
    )
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "From our meeting: Sarah needs to update the project timeline as soon as possible"}]
})

# Print your custom ToolMessage content specifically
print("--- Tool Message Content ---")
print(result["messages"][-1].content)
# Output: Action item captured and added to meeting notes!

# Print the final structured Pydantic object
print("\n--- Structured Response ---")
print(result["structured_response"])
# Output: MeetingAction(task='Update the project timeline', assignee='Sarah', priority='high')

# Access specific fields inside the structured response
print(f"\nTask Assigned: {result['structured_response'].task}")
# Output: Task Assigned: Update the project timeline
print(f"Assignee: {result['structured_response'].assignee}")
# Output: Assignee: Sarah
print(f"Priority: {result['structured_response'].priority}")
# Output: Priority: high