# Provider Strategy

Some model providers support structured output natively through their APIs (e.g. OpenAI, xAI (Grok), Gemini, Anthropic (Claude)). This is the most reliable method when available.
To use this strategy, configure a ProviderStrategy

# Run -> uv run .\provider-strategy.py 
# Output: name='John Doe' email='john@example.com' phone='(555) 123-4567'


# Tool calling strategy

For models that don’t support native structured output, LangChain uses tool calling to achieve the same result. This works with all models that support tool calling (most modern models).

# Run -> uv run .\tool-calling-strategy.py 
# Output: rating=5 sentiment='positive' key_points=['great product', 'fast shipping', 'expensive']

# Custom tool message content

The tool_message_content parameter allows you to customize the message that appears in the conversation history 
when structured output is generated:

# Run -> uv run .\custom-tool-message-content.py 
# Output: Action item captured and added to meeting notes!

# Multiple structured outputs error
When a model incorrectly calls multiple structured output tools, the agent provides error feedback in a ToolMessage and prompts the model to retry:
# Run -> uv run .\multiple-structured-outputs-error.py 
# Output: 
--- Structured Outcome ---
name='John Doe' email='john@email.com'

# Execution environment
Agents are especially useful when they can take action rather than just generate text. The execution environment gives the agent a workspace: tools it can call, a filesystem for reading and writing files across turns, and code execution for running scripts or shell commands.
# Run -> uv run .\execution-envrionment.py 
# Output: 
Sending query to agent: 'Search the local data for quarterly financial reports and summarize them.'...

=== Agent Final Output ===
I searched the local data for "quarterly financial reports," but the search result did not return any accessible files or content that I can read and summarize.

Could you please provide:
1. **The directory path** where these reports are located?
2. **Specific file names** (e.g., `Q3_2024_Report.pdf`)?
3. Any other details about the format or location of the data?

Once I have access to the documents, I will be happy to summarize them for you.