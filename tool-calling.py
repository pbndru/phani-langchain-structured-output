import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# 1. Configuration for LM Studio
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b")

# 2. Define the tool using the @tool decorator
# The docstring is critical: the local model reads it to understand when to use the tool.
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a specific city or location."""
    return f"It's sunny and 22°C in {location}."

def main():
    print(f"Connecting to LM Studio at: {LM_STUDIO_BASE_URL}")
    print(f"Using model: {LM_STUDIO_MODEL}\n")

    # 3. Create the local model instance
    local_llm = ChatOpenAI(
        base_url=LM_STUDIO_BASE_URL,
        api_key=LM_STUDIO_API_KEY,
        model=LM_STUDIO_MODEL,
        temperature=0.0,  # Lower temperature is highly recommended for stable tool calling
        timeout=600,
    )

    # 4. Bind the tool to the model
    model_with_tools = local_llm.bind_tools([get_weather])

    # 5. Invoke the model with a prompt that triggers the tool
    user_prompt = "What's the weather like in Boston?"
    print(f"User Prompt: '{user_prompt}'")
    print("Sending request to local LLM...")
    
    response = model_with_tools.invoke(user_prompt)

    # 6. Inspect the model's decision
    print("\n--- Execution Results ---")
    if response.tool_calls:
        print(f"Success! The model decided to call {len(response.tool_calls)} tool(s).\n")
        for tool_call in response.tool_calls:
            print(f"Tool Name: {tool_call['name']}")
            print(f"Arguments: {tool_call['args']}")
            print(f"Tool Call ID: {tool_call['id']}")
    else:
        print("The model did not trigger any tools. It returned a plain text response instead:")
        print(response.content)

if __name__ == "__main__":
    main()
