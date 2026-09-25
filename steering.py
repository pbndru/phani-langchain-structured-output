import os
import json
from dotenv import load_dotenv
load_dotenv()

# Native tracking imports
from langsmith import traceable, tracing_context
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool

# --- 1. Human-In-The-Loop Steering Simulation Layer ---
@traceable(run_type="chain", name="HumanInTheLoopMiddleware")
def human_steering_gate(tool_name: str, arguments: dict) -> tuple[bool, dict]:
    """Intercepts tool executions and prompts a human user to approve or steer the action."""
    print(f"\n[INTERRUPT DETECTED] Human-in-the-loop steering gate triggered!")
    print(f"-> Agent wants to execute tool: '{tool_name}'")
    print(f"-> Proposed Arguments: {json.dumps(arguments, indent=2)}")
    
    # Simple console input loop allowing a human operator to override the plan
    choice = input("\n[STEERING CONSOLE] Approve action? (y = Yes, n = Abort, c = Change parameters): ").strip().lower()
    
    if choice == 'y':
        print("-> [APPROVED] Executing step normally.")
        return True, arguments
    elif choice == 'c':
        print("\n--- Enter New Parameter Overrides ---")
        new_query = input("Modify search query parameter: ").strip()
        modified_arguments = {"query": new_query}
        print(f"-> [STEERED] Changing tool execution variables to: {modified_arguments}")
        return True, modified_arguments
    else:
        print("-> [ABORTED] Operation stopped by operator.")
        return False, arguments

# --- 2. Define the Base Core Data Search Tool ---
def search(query: str) -> str:
    """Useful for searching the historical brewing archives."""
    print(f"\n[SUB-AGENT ARCHIVE] Running deep database search for: '{query}'")
    if "stout" in query.lower():
        return "Archive Record #882: Craft stout techniques historically rely on roasted barley (10% of grain bill)."
    return f"Search results for: '{query}'. (No specific stout records found)."

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
test_prompt = "Search the archive for stout techniques and summarize the results."

with tracing_context(
    project_name="agent-steering-practice",
    tags=["qwen-coder-tier", "human-in-the-loop-evaluation"]
):
    print("==================================================")
    print(f"Executing Steering Sandbox via {LM_STUDIO_MODEL}...")
    print("==================================================")
    
    try:
        # Step 1: Let the model evaluate the prompt guidelines and emit its JSON intent string
        response = local_llm.invoke(f"{SYSTEM_PROMPT}\n\nUser Question: {test_prompt}")
        raw_output = response.content
        print(f"\n[PARENT PROCESSOR LOG] Raw string received:\n{raw_output}")
        
        # Step 2: Clean code block layout footprints and convert to variables
        clean_json = raw_output.replace("```json", "").replace("```", "").strip()
        parsed_action = json.loads(clean_json)
        
        target_tool = parsed_action["name"]
        target_arguments = parsed_action["arguments"]
        
        # Step 3: ROUTE TO STEERING GATE BEFORE RUNNING THE TOOL
        is_approved, runtime_arguments = human_steering_gate(target_tool, target_arguments)
        
        if is_approved:
            # Step 4: Run the underlying tool execution string logic block with approved arguments
            database_facts = search(runtime_arguments["query"])
            
            # Step 5: Run the output back through the synthesis model
            synthesis_prompt = (
                f"You are the Lead Master Brewer. Here are the facts retrieved from the database:\n"
                f"'{database_facts}'\n\n"
                f"Write a concise response summary layout for the user based strictly on these facts."
            )
            final_answer = local_llm.invoke(synthesis_prompt)
            
            print("\n================ FINAL ARCHITECT OUTPUT ================")
            print(final_answer.content)
            print("==================================================================")
        else:
            print("\n================ SYSTEM HALTED ================")
            print("Execution terminated by the user during the steering phase.")
            print("================================================================")
        
    except Exception as e:
        print(f"Error during sandbox steering run execution loop: {e}")
