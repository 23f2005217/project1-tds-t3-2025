from typing import Dict, Any
from .config import SECRET


def verify_secret(provided_secret: str) -> bool:
    return provided_secret == SECRET


def validate_request(data: Dict[str, Any]) -> tuple[bool, str]:
    required_fields = [
        "email",
        "secret",
        "task",
        "round",
        "nonce",
        "brief",
        "checks",
        "evaluation_url",
    ]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if not verify_secret(data["secret"]):
        return False, "Invalid secret"

    if not isinstance(data.get("round"), int) or data["round"] < 1:
        return False, "Invalid round number"

    if not isinstance(data.get("checks"), list):
        return False, "Checks must be a list"

    if "attachments" in data and not isinstance(data["attachments"], list):
        return False, "Attachments must be a list"

    return True, "Valid"
