# 🎬 AutoStream AI Agent — GenAI Social-to-Lead Conversational Workflow

> Built as part of the ServiceHive ML Intern assignment.
> A LangGraph-powered conversational AI agent that answers product queries using RAG, detects high-intent users, and captures leads through a structured multi-turn flow.

---

## ✨ Features

* 🧠 **Intent Detection** — Hybrid keyword + LLM classification (greeting, product inquiry, high-intent)
* 📚 **RAG Pipeline** — Answers grounded in a structured JSON knowledge base
* 💬 **Conversational Memory** — Maintains multi-turn state using LangGraph
* 🎯 **Lead Capture Flow** — Automatically triggers for high-intent users
* 🛠️ **Tool Execution** — Captures leads via `mock_lead_capture()` and stores in `leads.json`
* 📈 **Smart Recommendations** — Suggests Pro plan for creators (e.g., YouTube users)
* 🔁 **Robustness** — Handles API retries and fallback responses

---

## 📁 Project Structure

```
autostream-agent/
├── knowledge_base/
│   └── autostream_kb.json        # RAG knowledge base (pricing, policies, FAQs)
├── agent/
│   ├── __init__.py
│   ├── graph.py                  # LangGraph state machine (core logic)
│   ├── rag.py                    # RAG retrieval pipeline
│   ├── intent.py                 # Intent detection
│   └── tools.py                  # Lead capture tool
├── main.py                       # CLI chat interface
├── leads.json                    # Auto-created when leads are captured
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API key

```bash
copy .env.example .env
```

Add your key:

```
GOOGLE_API_KEY=your_key_here
```

Get a free key: https://aistudio.google.com/app/apikey

### 5. Run the agent

```bash
python main.py
```

---

## 💬 Example Conversation

```
You: What are your pricing plans?

Aria: Here's a quick breakdown of AutoStream plans:

**Basic – $29/month**
• 10 videos/month  
• 720p resolution  
• Basic auto-editing  
• Email support  

**Pro – $79/month**
• Unlimited videos  
• 4K resolution  
• AI-powered captions  
• Advanced editing  
• Priority support  

👉 Recommended: Pro plan is ideal for YouTube creators.
```

---

## 🔄 Agent Workflow

1. User sends a message
2. Intent is classified (keyword + LLM fallback)
3. Based on intent:

   * Greeting → friendly response
   * Product query → RAG retrieval + structured answer
   * High intent → lead collection flow
4. Lead collection:

   * Name → Email → Platform
5. Tool execution:

   * Lead stored in `leads.json`
6. Confirmation response returned

---

## 🏗️ Architecture Explanation

### Why LangGraph?

LangGraph enables **stateful, multi-step workflows**. This agent needs to:

* Remember user inputs across turns
* Track which lead fields are collected
* Route between intent → RAG → lead capture

This is handled using a centralized `AgentState`.

---

### State Management

The agent maintains:

* `messages` → conversation history
* `collecting_lead` → whether lead flow is active
* `lead_name`, `lead_email`, `lead_platform` → captured fields
* `last_asked` → prevents duplicate prompts

---

### RAG Pipeline

* Knowledge base stored in JSON
* Flattened into searchable chunks
* Keyword overlap + boosting retrieves relevant context
* Injected into LLM prompt → grounded answers

---

## 📱 WhatsApp Deployment (Design)

```
User → WhatsApp API → Webhook → Agent → Response → WhatsApp
```

* FastAPI backend receives messages
* Redis stores session state per user
* LangGraph processes each message
* Response sent via Meta API

---

## 🛠️ Tech Stack

| Component        | Technology                     |
| ---------------- | ------------------------------ |
| Language         | Python 3.9+                    |
| Agent Framework  | LangGraph                      |
| LLM              | Gemini 2.5 Flash               |
| LLM SDK          | google-genai (official SDK)    |
| Knowledge Base   | JSON + keyword-based RAG       |
| State Management | LangGraph StateGraph           |
| Tool Execution   | Python function (lead capture) |

---

### ⚠️ Note on LLM Integration

This project uses the official **`google-genai` SDK** instead of LangChain’s Gemini wrapper due to compatibility issues with deprecated API versions.
LangGraph is still used for orchestration and state management.

---

## 📊 Evaluation Mapping

| Criterion                | Implementation                            |
| ------------------------ | ----------------------------------------- |
| Agent reasoning & intent | Hybrid keyword + LLM classification       |
| Correct use of RAG       | JSON → chunk retrieval → prompt injection |
| State management         | LangGraph TypedDict                       |
| Tool execution           | Triggered after collecting all fields     |
| Code clarity             | Modular, well-documented                  |
| Real-world deployability | WhatsApp webhook design                   |

---

## 🚧 Limitations & Future Work

* Replace keyword RAG with vector embeddings
* Add stricter input validation (email, platform)
* Persistent memory using Redis
* Web UI / dashboard for leads
* Multi-agent support for sales + support

---

## 🎥 Demo

👉 (Add your 2–3 min demo video link here)

Demo includes:

* Product Q&A via RAG
* Pricing explanation
* Lead capture flow
* JSON storage of leads

---

## 📄 License

MIT — built for ServiceHive ML Intern assignment.
