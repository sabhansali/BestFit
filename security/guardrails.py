"""Input guardrails that reject common prompt-injection attempts."""

import re
import unicodedata


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"(override|disregard|bypass|forget)\s+(your|the|all)?\s*(system\s+)?instructions",
    r"(listen|obey)\s+to\s+me\s+now",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"override\s+(the\s+)?budget",
    r"ignore\s+(the\s+)?budget",
    r"show\s+(me\s+)?expensive\s+outfits",
    r"disregard\s+(the\s+)?security",
    r"(reveal|show|print|dump)\s+(all\s+)?(hidden|secret|internal|developer)\s+(instructions|prompt|data|rules)",
    r"(system|developer|admin)\s*(message|mode|role)\s*[:=]",
    r"(do\s*not|don't)\s+(follow|apply)\s+(the\s+)?(rules|constraints|budget|safety)",
    r"(make|treat)\s+.*(ignore|bypass|override).*(constraint|budget|security|validation)",
    r"(grant|give)\s+me\s+(admin|developer|tool)\s+access",
    r"(call|execute|use)\s+the\s+(shell|filesystem|database|admin)\s+tool",
)


def _normalize_for_detection(query: str) -> str:
    """Normalize harmless formatting tricks before pattern matching."""

    normalized = unicodedata.normalize("NFKC", query).casefold()
    normalized = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def validate_user_query(query: str) -> tuple[bool, list[str]]:
    normalized = _normalize_for_detection(query)
    if not normalized:
        return False, ["Query cannot be empty"]
    findings = [
        pattern
        for pattern in INJECTION_PATTERNS
        if re.search(pattern, normalized, flags=re.IGNORECASE)
    ]
    if len(normalized) > 2_000:
        findings.append("query_length_limit")
    return not findings, [
        "Blocked input pattern: query_length_limit"
        if pattern == "query_length_limit"
        else f"Blocked input pattern: {pattern}"
        for pattern in findings
    ]
