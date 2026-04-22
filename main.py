"""
main.py — Entry point for the AutoStream conversational AI agent.

Run with:
    python main.py

The agent maintains full conversation state across all turns using
LangGraph's state machine. Type 'quit' or 'exit' to stop.
"""

import os
import sys
from dotenv import load_dotenv
from agent.graph import build_graph, initial_state

load_dotenv()


def check_env():
    """Validate required environment variables before starting."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY is not set.")
        print("   Create a .env file with: GOOGLE_API_KEY=your_key_here")
        print("   Get your free key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)


def print_banner():
    print("\n" + "="*60)
    print("  🎬  AutoStream AI Assistant  |  Powered by Inflx/ServiceHive")
    print("="*60)
    print("  Hi! I'm Aria, your AutoStream assistant.")
    print("  Ask me about pricing, features, or how to get started.")
    print("  Type 'quit' to exit.\n")


def chat():
    """Main interactive chat loop."""
    check_env()
    print_banner()

    # Build the compiled LangGraph agent
    agent = build_graph()

    # Initialize persistent state
    state = initial_state()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
            print("\nAria: Thanks for chatting! Have a great day creating content! 🎬\n")
            break

        # Append the user's message to conversation history
        state["messages"].append({
            "role": "user",
            "content": user_input
        })

        # Run one turn through the LangGraph agent
        try:
            result = agent.invoke(state)
        except Exception as e:
            print(f"\n⚠️  Agent error: {e}")
            print("Please check your GOOGLE_API_KEY and try again.\n")
            continue

        # Update state with result from this turn
        state = result
        reply = state.get("response", "I'm sorry, I didn't understand that.")

        # Append assistant's response to history
        state["messages"].append({
            "role": "assistant",
            "content": reply
        })

        # Display the reply
        print(f"\nAria: {reply}\n")

        # If lead was just captured, show a summary and optionally end
        if state.get("lead_captured"):
            print("-" * 60)
            print("✅ Lead successfully captured and saved to leads.json")
            print(f"   Name:     {state.get('lead_name')}")
            print(f"   Email:    {state.get('lead_email')}")
            print(f"   Platform: {state.get('lead_platform')}")
            print("-" * 60 + "\n")


if __name__ == "__main__":
    chat()
