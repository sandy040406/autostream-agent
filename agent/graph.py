import os
from typing import TypedDict, List, Optional, Literal
from dotenv import load_dotenv

from google import genai
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from agent.rag import retrieve_relevant_chunks
from agent.intent import keyword_intent, Intent
from agent.tools import mock_lead_capture


# Load .env properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

class AgentState(TypedDict):
    messages: List[dict]
    intent: str
    collecting_lead: bool
    lead_name: Optional[str]
    lead_email: Optional[str]
    lead_platform: Optional[str]
    lead_captured: bool
    last_asked: Optional[str]
    response: str

# ─────────────────────────────────────────────
# LLM SETUP
# ─────────────────────────────────────────────

def get_llm():
    import os
    from google import genai

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return client

import time

def llm_invoke(client, prompt: str):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e):
                time.sleep(2)  # wait and retry
            else:
                raise e
    return "Sorry, I'm having trouble right now. Please try again."
# ─────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are Aria, a friendly and knowledgeable sales assistant for AutoStream.

Goals:
- Help users with pricing and features
- Detect high intent
- Collect Name, Email, Platform
- Be friendly and concise
"""

def build_prompt(state: AgentState, extra: str = ""):
    history = "\n".join([f"{m['role']}: {m['content']}" for m in state["messages"]])
    return SYSTEM_PROMPT + "\n" + extra + "\n" + history

# ─────────────────────────────────────────────
# CLASSIFY
# ─────────────────────────────────────────────

def classify_node(state: AgentState) -> AgentState:
    if not state["messages"]:
        return {**state, "intent": Intent.GREETING}

    if state["collecting_lead"] and not state["lead_captured"]:
        return {**state, "intent": Intent.LEAD_INFO}

    latest = state["messages"][-1]["content"]
    kw = keyword_intent(latest)

    if kw in [Intent.HIGH_INTENT, Intent.GREETING, Intent.PRODUCT_INQUIRY]:
        return {**state, "intent": kw}

    llm = get_llm()
    prompt = f"""Classify intent:
greeting / product_inquiry / high_intent / other

Message: {latest}
Answer only one word."""
    
    raw = llm_invoke(llm, prompt).lower().strip()

    return {**state, "intent": raw}

# ─────────────────────────────────────────────
# GREETING
# ─────────────────────────────────────────────

def greeting_node(state: AgentState) -> AgentState:
    llm = get_llm()
    prompt = build_prompt(state)
    reply = llm_invoke(llm, prompt)
    return {**state, "response": reply}

# ─────────────────────────────────────────────
# RAG
# ─────────────────────────────────────────────

def rag_respond_node(state: AgentState) -> AgentState:
    llm = get_llm()
    query = state["messages"][-1]["content"]

    context = retrieve_relevant_chunks(query)

    # 🔥 Fallback if no useful context
    if not context.strip():
        return {
            **state,
            "response": "I don’t have that specific info right now, but I can connect you with our team or help you get started."
        }

    # 🔥 Improved prompt
    prompt = build_prompt(state, f"""
You are a helpful SaaS sales assistant for AutoStream.

Instructions:
- ALWAYS present pricing in a structured format when pricing is mentioned
- ALWAYS include ALL available plans (Basic and Pro)
- Use clean bullet formatting
- Highlight key differences clearly
- If user mentions YouTube/creator/content, recommend Pro plan
- Be concise and professional (like a real SaaS product page)
- Do NOT make up information

Format pricing like this:

**AutoStream Pricing Plans**

**Basic – $29/month**
• 10 videos/month  
• 720p resolution  
• Basic auto-editing  
• Email support  

**Pro – $79/month**
• Unlimited videos  
• 4K resolution  
• AI captions  
• Advanced editing  
• Priority support  

Context:
{context}
""")

    reply = llm_invoke(llm, prompt)

    return {**state, "response": reply.strip()}

# ─────────────────────────────────────────────
# START LEAD
# ─────────────────────────────────────────────

def start_lead_collection_node(state: AgentState) -> AgentState:
    llm = get_llm()

    if not state.get("lead_name"):
        ask = "What's your name?"
        field = "name"
    elif not state.get("lead_email"):
        ask = "What's your email?"
        field = "email"
    else:
        ask = "Which platform do you use?"
        field = "platform"

    return {
        **state,
        "collecting_lead": True,
        "last_asked": field,
        "response": ask
    }

# ─────────────────────────────────────────────
# COLLECT
# ─────────────────────────────────────────────

def collect_lead_node(state: AgentState) -> AgentState:
    latest = state["messages"][-1]["content"]
    field = state["last_asked"]

    new_state = dict(state)

    if field == "name":
        new_state["lead_name"] = latest
    elif field == "email":
        new_state["lead_email"] = latest
    elif field == "platform":
        new_state["lead_platform"] = latest

    if not new_state.get("lead_name"):
        return {**new_state, "last_asked": "name", "response": "Your name?"}
    elif not new_state.get("lead_email"):
        return {**new_state, "last_asked": "email", "response": "Your email?"}
    elif not new_state.get("lead_platform"):
        return {**new_state, "last_asked": "platform", "response": "Your platform?"}
    else:
        return capture_lead_node(new_state)

# ─────────────────────────────────────────────
# CAPTURE
# ─────────────────────────────────────────────

def capture_lead_node(state: AgentState) -> AgentState:
    name = state["lead_name"]
    email = state["lead_email"]
    platform = state["lead_platform"]

    mock_lead_capture(name, email, platform)

    return {
        **state,
        "lead_captured": True,
        "collecting_lead": False,
        "response": f"You're all set {name}! We'll reach you at {email} 🚀"
    }

# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────

def route_after_classify(state: AgentState):
    if state["collecting_lead"] and not state["lead_captured"]:
        return "collect_lead"

    if state["intent"] == Intent.GREETING:
        return "greeting"
    elif state["intent"] == Intent.HIGH_INTENT:
        return "start_lead_collection"
    else:
        return "rag_respond"

# ─────────────────────────────────────────────
# GRAPH
# ─────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_node)
    graph.add_node("greeting", greeting_node)
    graph.add_node("rag_respond", rag_respond_node)
    graph.add_node("start_lead_collection", start_lead_collection_node)
    graph.add_node("collect_lead", collect_lead_node)
    graph.add_node("capture_lead", capture_lead_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "greeting": "greeting",
            "rag_respond": "rag_respond",
            "start_lead_collection": "start_lead_collection",
            "collect_lead": "collect_lead",
        }
    )

    graph.add_edge("greeting", END)
    graph.add_edge("rag_respond", END)
    graph.add_edge("start_lead_collection", END)
    graph.add_edge("collect_lead", END)

    return graph.compile()

# ─────────────────────────────────────────────

def initial_state() -> AgentState:
    return {
        "messages": [],
        "intent": Intent.OTHER,
        "collecting_lead": False,
        "lead_name": None,
        "lead_email": None,
        "lead_platform": None,
        "lead_captured": False,
        "last_asked": None,
        "response": "",
    }