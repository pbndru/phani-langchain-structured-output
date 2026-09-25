import os
import json
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langsmith import traceable, tracing_context
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

# --- 1. Pure Python Data Search Function ---
def search(query: str) -> str:
    """Useful for searching the historical brewing archives."""
    print(f"\n[SUB-AGENT SEARCH LOG] Executing database lookup for query: '{query}'")
    
    if "stout" in query.lower() or "brewing" in query.lower():
        return (
            "Archive Record #882: Craft stout techniques historically rely on roasted barley "
            "(around 10% of the grain bill) to achieve the signature dark profile, distinct from traditional porters. "
            "Key development occurred in the early 18th century London markets."
        )
    return "No historical records matched that specific query layout."

# --- 2. Initialize Infrastructure ---
backend = StateBackend()

LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "qwen2.5-coder-1.5b-instruct")

local_llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    model=LM_STUDIO_MODEL,
    temperature=0.0,  # Force strict adherence to system layouts
    timeout=600,
)

# --- 3. Robust Sub-Agent Execution Subroutine ---
@traceable(run_type="chain", name="ResearcherSubAgentExecution")
def run_subagent_pipeline(research_topic: str) -> str:
    print(f"\n[MANAGER ACTION] Activating 'researcher' sub-agent pipeline.")
    
    # 1. Ask the researcher model to decide what query it wants to search
    researcher_prompt = (
        f"You are a specialized historical researcher sub-agent. You need to gather facts about: {research_topic}.\n"
        "You must output exactly this JSON format to request a search lookup:\n"
        '{"action": "search", "query": "<your search terms here>"}\n'
        "Do not include conversational preamble or explanation text."
    )
    
    # Use direct LLM calls to keep 1.5B structure stable
    sub_response_1 = local_llm.invoke(researcher_prompt)
    raw_sub_output = sub_response_1.content
    
    # Clean and parse the sub-agent's tool intent
    clean_sub_json = raw_sub_output.replace("```json", "").replace("```", "").strip()
    parsed_sub_action = json.loads(clean_sub_json)
    search_query = parsed_sub_action["query"]
    
    # 2. Execute the actual search function in real Python code
    search_facts = search(search_query)
    
    # 3. Feed the retrieved facts back to the researcher to write the final summary
    synthesis_prompt = (
        f"You are the historical researcher sub-agent. Here are the raw facts retrieved from the database:\n"
        f"'{search_facts}'\n\n"
        f"Based on these exact facts, write a concise two-sentence summary of the history and techniques."
    )
    
    final_summary_response = local_llm.invoke(synthesis_prompt)
    return final_summary_response.content

# --- 4. Build Parent Architect Agent Configuration ---
SYSTEM_PROMPT = (
    "You are the Lead Master Brewer and Architect Agent.\n\n"
    "CRITICAL RESPONSE REQUIREMENT:\n"
    "You are analyzing a complex historical task. You must respond using a raw JSON snippet "
    "to trigger the next phase. Output exactly this format, replacing the bracketed value:\n"
    '{"name": "delegate_to_researcher", "arguments": {"research_topic": "<insert topic here>"}}\n'
    "Do not include conversational conversational text or preamble."
)

parent_agent = create_agent(
    model=local_llm,
    tools=[], 
    system_prompt=SYSTEM_PROMPT,
    middleware=[
        FilesystemMiddleware(backend=backend),
        TodoListMiddleware(),
    ],
)

# --- 5. Run Execution Loop inside Tracing Context ---
complex_task = (
    "Research the history of craft stout brewing techniques. "
    "Format a clean summary layout based on the research. "
    "Use your specialized researcher sub-agent to handle the deep search phase."
)

with tracing_context(
    project_name="agent-delegation-practice",
    tags=["qwen-coder-tier", "explicit-delegation"]
):
    print("==================================================")
    print(f"Executing Multi-Agent Delegation Plan via {LM_STUDIO_MODEL}...")
    print("==================================================")
    
    try:
        # Parent processes the prompt
        response = parent_agent.invoke({
            "messages": [
                {"role": "user", "content": complex_task}
            ]
        })
        
        raw_output = response["messages"][-1].content
        print(f"\n[PARENT PROCESSOR LOG] Raw string received:\n{raw_output}")
        
        clean_json = raw_output.replace("```json", "").replace("```", "").strip()
        parsed_action = json.loads(clean_json)
        topic_target = parsed_action["arguments"]["research_topic"]
        
        # Runs the fixed sub-agent pipeline containing the native python execution steps
        subagent_summary = run_subagent_pipeline(topic_target)
        
        print("\n================ FINAL ARCHITECT SUMMARY OUTPUT ================")
        print(subagent_summary)
        print("================================================================")
        
    except Exception as e:
        print(f"Error during sandbox planning run parsing: {e}")
