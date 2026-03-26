"""
Mock Vapi integration client for HeroCall.

All functions return mock/placeholder data. When Vapi API keys are available,
replace the mock implementations with real API calls.

# TODO: Replace with real Vapi API calls when keys are available
"""

import uuid
import random
from datetime import datetime, timedelta, timezone


# TODO: Replace with real Vapi API calls when keys are available
VAPI_API_KEY = None  # Set via environment variable when ready


def create_assistant(name: str, system_prompt: str, voice: str = "jennifer-playht") -> dict:
    """
    Create a Vapi voice assistant.

    # TODO: Replace with real Vapi API calls when keys are available
    Real implementation would POST to https://api.vapi.ai/assistant

    Args:
        name: Display name for the assistant
        system_prompt: The system prompt / instructions for the AI
        voice: Voice ID to use (default: jennifer-playht)

    Returns:
        dict with assistant_id and metadata
    """
    mock_assistant_id = f"asst_{uuid.uuid4().hex[:24]}"

    return {
        "id": mock_assistant_id,
        "name": name,
        "voice": voice,
        "model": "gpt-4",
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "_mock": True,  # Flag to indicate this is mock data
    }


def update_assistant(assistant_id: str, system_prompt: str = None, voice: str = None) -> dict:
    """
    Update an existing Vapi assistant's configuration.

    # TODO: Replace with real Vapi API calls when keys are available
    Real implementation would PATCH to https://api.vapi.ai/assistant/{assistant_id}

    Args:
        assistant_id: The Vapi assistant ID
        system_prompt: Updated system prompt (optional)
        voice: Updated voice ID (optional)

    Returns:
        dict with updated assistant data
    """
    return {
        "id": assistant_id,
        "updated": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "_mock": True,
    }


def delete_assistant(assistant_id: str) -> dict:
    """
    Delete a Vapi assistant.

    # TODO: Replace with real Vapi API calls when keys are available
    Real implementation would DELETE to https://api.vapi.ai/assistant/{assistant_id}

    Args:
        assistant_id: The Vapi assistant ID to delete

    Returns:
        dict confirming deletion
    """
    return {
        "id": assistant_id,
        "deleted": True,
        "_mock": True,
    }


def assign_phone_number(assistant_id: str) -> dict:
    """
    Assign a phone number to a Vapi assistant (via Twilio integration).

    # TODO: Replace with real Vapi API calls when keys are available
    Real implementation would:
    1. Purchase/provision a Twilio number via Vapi
    2. Link it to the assistant

    Args:
        assistant_id: The Vapi assistant ID to assign a number to

    Returns:
        dict with phone number details
    """
    area_code = random.choice(["212", "415", "312", "305", "702", "469", "678"])
    mock_number = f"+1{area_code}{random.randint(1000000, 9999999)}"

    return {
        "phone_number": mock_number,
        "assistant_id": assistant_id,
        "provider": "twilio",
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "_mock": True,
    }


def release_phone_number(phone_number: str) -> dict:
    """
    Release/delete a phone number.

    # TODO: Replace with real Vapi API calls when keys are available

    Args:
        phone_number: The phone number to release

    Returns:
        dict confirming release
    """
    return {
        "phone_number": phone_number,
        "released": True,
        "_mock": True,
    }


def get_call_logs(assistant_id: str, limit: int = 50) -> list:
    """
    Get call logs for a Vapi assistant.

    # TODO: Replace with real Vapi API calls when keys are available
    Real implementation would GET from https://api.vapi.ai/call?assistantId={assistant_id}

    Args:
        assistant_id: The Vapi assistant ID
        limit: Max number of call logs to return

    Returns:
        list of call log dicts
    """
    outcomes = ["appointment_booked", "message_taken", "transferred", "spam", "info_provided"]
    names = [
        "Sarah Johnson", "Mike Chen", "Lisa Rodriguez", "James Wilson",
        "Emily Davis", "Robert Brown", "Maria Garcia", "David Lee",
        "Jennifer Martinez", "Chris Taylor",
    ]

    now = datetime.now(timezone.utc)
    mock_calls = []

    num_calls = min(limit, random.randint(3, 15))
    for i in range(num_calls):
        call_time = now - timedelta(hours=random.randint(1, 168))  # up to 7 days ago
        duration = random.randint(30, 600)  # 30 seconds to 10 minutes
        caller_name = random.choice(names)
        outcome = random.choice(outcomes)

        mock_calls.append({
            "id": f"call_{uuid.uuid4().hex[:16]}",
            "assistant_id": assistant_id,
            "caller_phone": f"+1{random.randint(2000000000, 9999999999)}",
            "caller_name": caller_name,
            "duration_seconds": duration,
            "outcome": outcome,
            "summary": _generate_call_summary(caller_name, outcome),
            "transcript": f"[Mock transcript for {caller_name}'s call - {duration}s]",
            "created_at": call_time.isoformat(),
            "_mock": True,
        })

    # Sort by most recent first
    mock_calls.sort(key=lambda c: c["created_at"], reverse=True)
    return mock_calls


def _generate_call_summary(caller_name: str, outcome: str) -> str:
    """Generate a realistic call summary based on outcome."""
    summaries = {
        "appointment_booked": f"{caller_name} called to schedule a service appointment. Booked for next available slot.",
        "message_taken": f"{caller_name} called and left a message requesting a callback about their service needs.",
        "transferred": f"{caller_name} called with a complex issue and was transferred to a live representative.",
        "spam": f"Automated/spam call detected. No action needed.",
        "info_provided": f"{caller_name} called asking about services and pricing. Information provided.",
    }
    return summaries.get(outcome, f"{caller_name} called. Outcome: {outcome}")
