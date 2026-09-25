import os
import json
from dotenv import load_dotenv
load_dotenv()

# Native tracking imports
from langsmith import traceable, tracing_context
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

# --- 1. Custom Local PII Guardrail Middleware Simulator ---
# Small 1.5B local models can easily leak or process PII text if not filtered.
# This code bit simulates PIIMiddleware("email") directly at the orchestration tier.
@traceable(run_type="chain", name="PIIGuardrailMiddleware")
def apply_pii_guardrail(text_input: str) -> str:
    """Scans and redacts email PII patterns before data leaves the internal network tier."""
    import re
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Check if an email pattern is present in the stream block
    if re.search(email_regex, text_input):
        print("\n[GUARDRAIL ALARM] PII Middleware triggered! Email footprint detected.")
        # Redact the sensitive data to maintain compliance boundaries
        redacted_text = re.sub(email_regex, "[REDACTED_EMAIL]", text_input)
        print(f"-> [REDACTION COMPLETE] Safe text generated: '{redacted_text}'")
        return redacted_text
        
    return text_input

# --- 2. Define the Base Core Data Search Tool ---
def search(query: str) -> str:
    """Useful for searching the historical brewing archives."""
    print(f"\n[SUB-AGENT ARCHIVE] Running deep database search for: '{query}'")
    return f"Search results for: {query}. Archive admin contact is admin@brewmaster-local.internal"

# --- 3. Initialize the Infrastructure Layer ---
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "qwen2.5-coder-1.5b-instruct")

local_llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    model=LM_STUDIO_MODEL,
    temperature=0.0, 
    timeout=600,
)

# --- 4. Build Parent Instructions ---
SYSTEM_PROMPT = (
    "You are the Lead Master Brewer and Architect Agent.\n\n"
    "CRITICAL INSTUCTION:\n"
    "You must declare which tool you want to use using a raw JSON snippet format.\n"
    "Output exactly this layout, replacing the bracketed value:\n"
    '{"name": "search", "arguments": {"query": "<insert search parameters here>"}}\n'
    "Do not include conversational preamble or extra text."
)

# --- 5. Run Execution Loop inside Tracing Context ---
# Input prompt containing dangerous PII that needs to be scrubbed by the guardrail
sensitive_prompt = "Search the archive for stout techniques. If you need help, email me at test-user@example.com."

with tracing_context(
    project_name="agent-guardrails-practice",
    tags=["qwen-coder-tier", "pii-compliance-evaluation"]
):
    print("==================================================")
    print(f"Executing Guardrails Sandbox via {LM_STUDIO_MODEL}...")
    print("==================================================")
    
    try:
        # Step 1: Pass incoming query through the PII Guardrail layer first
        safe_prompt = apply_pii_guardrail(sensitive_prompt)
        
        # Step 2: Let the local model process the sanitized request string parameters
        response = local_llm.invoke(f"{SYSTEM_PROMPT}\n\nUser Question: {safe_prompt}")
        raw_output = response.content
        print(f"\n[PARENT PROCESSOR LOG] Raw string received:\n{raw_output}")
        
        # Step 3: Clean code block layout footprints and convert to variables
        clean_json = raw_output.replace("```json", "").replace("```", "").strip()
        parsed_action = json.loads(clean_json)
        target_query = parsed_action["arguments"]["query"]
        
        # Step 4: Run the underlying tool execution string logic block
        database_facts = search(target_query)
        
        # Step 5: Run the output back through the synthesis model
        synthesis_prompt = (
            f"You are the Lead Master Brewer. Here are the facts retrieved from the database:\n"
            f"'{database_facts}'\n\n"
            f"Write a concise response summary layout for the user. Do not leak internal system emails."
        )
        
        final_answer = local_llm.invoke(synthesis_prompt)
        
        # Step 6: Final check on output block text to ensure no tools leaked data out
        sanitized_final_answer = apply_pii_guardrail(final_answer.content)
        
        print("\n================ FINAL ARCHITECT SANITIZED OUTPUT ================")
        print(sanitized_final_answer)
        print("==================================================================")
        
    except Exception as e:
        print(f"Error during sandbox guardrails run execution loop: {e}")
