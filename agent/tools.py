"""
tools.py — Tool execution layer for the AutoStream agent.
Contains the mock_lead_capture function that simulates
saving a qualified lead to a CRM or backend system.
"""

import json
from datetime import datetime


def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Simulates capturing a qualified lead.
    In production, this would POST to a CRM API (HubSpot, Salesforce, etc.)

    Args:
        name:     Full name of the lead
        email:    Email address of the lead
        platform: Creator platform (YouTube, Instagram, TikTok, etc.)

    Returns:
        A confirmation string.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Simulate saving to a local leads log file
    lead_data = {
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": timestamp,
        "product_interest": "AutoStream Pro Plan"
    }

    # Print confirmation (as required by assignment)
    print(f"\n{'='*50}")
    print(f"✅ Lead captured successfully!")
    print(f"   Name:      {name}")
    print(f"   Email:     {email}")
    print(f"   Platform:  {platform}")
    print(f"   Timestamp: {timestamp}")
    print(f"{'='*50}\n")

    # Also append to a local leads.json log
    try:
        import os
        leads_file = os.path.join(os.path.dirname(__file__), "..", "leads.json")
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, "r") as f:
                leads = json.load(f)
        leads.append(lead_data)
        with open(leads_file, "w") as f:
            json.dump(leads, f, indent=2)
    except Exception:
        pass  # Non-critical — don't break the agent if file write fails

    return (
        f"Lead captured successfully for {name} ({email}) "
        f"on platform {platform}."
    )
