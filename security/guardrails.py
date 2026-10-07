"""Input guardrails that reject common prompt-injection attempts."""

import re


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"(override|disregard|bypass|forget)\s+(your|the|all)?\s*(system\s+)?instructions",
    r"(listen|obey)\s+to\s+me\s+now",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"override\s+(the\s+)?budget",
    r"disregard\s+(the\s+)?security",
)


def validate_user_query(query: str) -> tuple[bool, list[str]]:
    if not query.strip():
        return False, ["Query cannot be empty"]
    findings = [
        pattern
        for pattern in INJECTION_PATTERNS
        if re.search(pattern, query, flags=re.IGNORECASE)
    ]
    return not findings, [f"Blocked input pattern: {pattern}" for pattern in findings]
