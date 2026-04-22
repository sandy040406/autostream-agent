"""
rag.py — RAG pipeline for AutoStream knowledge base.
Loads the local JSON knowledge base and retrieves relevant
chunks based on the user's query using keyword similarity.
"""

import json
import os
from typing import List, Dict

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "autostream_kb.json")


def load_knowledge_base() -> Dict:
    """Load the AutoStream knowledge base from JSON."""
    with open(KB_PATH, "r") as f:
        return json.load(f)


def flatten_kb_to_chunks(kb: Dict) -> List[Dict]:
    """
    Convert the nested knowledge base into a flat list of
    searchable text chunks, each with a 'text' and 'source' field.
    """
    chunks = []

    # Product description
    chunks.append({
        "source": "product_description",
        "text": f"AutoStream: {kb['description']}"
    })

    # Pricing plans
    for plan in kb["pricing"]:
        features_str = ", ".join(plan["features"])
        chunks.append({
            "source": f"pricing_{plan['plan'].replace(' ', '_').lower()}",
            "text": (
                f"{plan['plan']} costs {plan['price']}. "
                f"Features include: {features_str}."
            )
        })

    # Policies
    for policy in kb["policies"]:
        chunks.append({
            "source": f"policy_{policy['topic'].replace(' ', '_').lower()}",
            "text": f"{policy['topic']}: {policy['details']}"
        })

    # FAQs
    for faq in kb["faqs"]:
        chunks.append({
            "source": "faq",
            "text": f"Q: {faq['question']} A: {faq['answer']}"
        })

    return chunks


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> str:
    """
    Simple keyword-based retrieval from the knowledge base.
    Returns the top_k most relevant chunks as a single string
    to be injected into the LLM prompt as context.

    For a production system this would use vector embeddings,
    but keyword overlap is sufficient for this scoped KB.
    """
    kb = load_knowledge_base()
    chunks = flatten_kb_to_chunks(kb)

    query_lower = query.lower()
    query_words = set(query_lower.split())

    # Score each chunk by word overlap with the query
    scored = []
    for chunk in chunks:
        chunk_words = set(chunk["text"].lower().split())
        overlap = len(query_words & chunk_words)

        # Boost score for key topic matches
        boost = 0
        if any(w in query_lower for w in ["price", "cost", "plan", "pricing", "how much", "pay"]):
            if "pricing" in chunk["source"] or "plan" in chunk["text"].lower():
                boost += 5
        if any(w in query_lower for w in ["refund", "cancel", "policy", "support"]):
            if "policy" in chunk["source"]:
                boost += 5
        if any(w in query_lower for w in ["pro", "unlimited", "4k", "caption"]):
            if "pro" in chunk["text"].lower():
                boost += 3
        if any(w in query_lower for w in ["basic", "29", "720"]):
            if "basic" in chunk["text"].lower():
                boost += 3

        scored.append((overlap + boost, chunk["text"]))

    # Sort by score descending and pick top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    top_chunks = [text for _, text in scored[:top_k] if _ > 0]

    if not top_chunks:
    # fallback: return pricing + description
        top_chunks = [
        c["text"] for c in chunks
        if "pricing" in c["source"] or "product_description" in c["source"]
        ]

    return "\n\n".join(top_chunks)
