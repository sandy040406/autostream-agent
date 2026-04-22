"""
intent.py — Rule-assisted intent classification for the AutoStream agent.
The LLM handles nuanced intent detection inside the graph,
but this module provides deterministic keyword signals as
a lightweight pre-filter to reduce hallucination risk.
"""

from enum import Enum
from typing import List


class Intent(str, Enum):
    GREETING        = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    HIGH_INTENT     = "high_intent"
    LEAD_INFO       = "lead_info"        # User is providing their name/email/platform
    OTHER           = "other"


# Keywords that strongly signal high purchase intent
HIGH_INTENT_SIGNALS: List[str] = [
    "sign up", "sign me up", "i want to try", "i'd like to try",
    "i want to subscribe", "let's do it", "how do i start",
    "get started", "purchase", "buy", "upgrade", "subscribe",
    "i'm ready", "i am ready", "let me try", "i'll take",
    "i want the pro", "i want the basic", "i want to join",
    "ready to start", "interested in signing up", "want to get",
    "can i sign up", "enroll", "onboard"
]

# Keywords for product/pricing queries
PRODUCT_INQUIRY_SIGNALS: List[str] = [
    "price", "pricing", "cost", "how much", "plan", "plans",
    "feature", "features", "what does", "tell me about",
    "refund", "support", "cancel", "4k", "resolution",
    "unlimited", "caption", "basic", "pro", "difference",
    "compare", "include", "offer", "provide", "does it"
]

# Greeting keywords
GREETING_SIGNALS: List[str] = [
    "hi", "hello", "hey", "good morning", "good afternoon",
    "good evening", "howdy", "greetings", "what's up", "sup"
]

# Email pattern helper
import re
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def keyword_intent(message: str) -> Intent:
    """
    Fast keyword-based intent pre-classification.
    Used to assist the LLM, not replace it.
    """
    msg = message.lower().strip()

    # Check for high intent first (most important to catch early)
    if any(signal in msg for signal in HIGH_INTENT_SIGNALS):
        return Intent.HIGH_INTENT

    # Check for product inquiry
    if any(signal in msg for signal in PRODUCT_INQUIRY_SIGNALS):
        return Intent.PRODUCT_INQUIRY

    # Check for greeting (only short messages to avoid false positives)
    if len(msg.split()) <= 6 and any(signal in msg for signal in GREETING_SIGNALS):
        return Intent.GREETING

    return Intent.OTHER


def contains_email(text: str) -> bool:
    """Check if a message contains an email address."""
    return bool(EMAIL_PATTERN.search(text))


def looks_like_platform(text: str) -> bool:
    """Check if text mentions a known creator platform."""
    platforms = [
        "youtube", "instagram", "tiktok", "twitter", "facebook",
        "twitch", "linkedin", "snapchat", "pinterest", "x.com"
    ]
    return any(p in text.lower() for p in platforms)
