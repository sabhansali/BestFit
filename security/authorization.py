"""Least-privilege authorization for registry tool calls."""

from dataclasses import dataclass
@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason: str


ROLE_TOOL_ALLOWLIST: dict[str, frozenset[str]] = {
    "planner_agent": frozenset(),
    "search_agent": frozenset({"search_products"}),
    "filter_agent": frozenset({"filter_products"}),
    "outfit_builder_agent": frozenset({"build_outfits"}),
    "comparison_agent": frozenset({"compare_outfits"}),
    "ranking_agent": frozenset({"rank_outfits"}),
    "validator_agent": frozenset({"validate_recommendation"}),
    "supervisor_agent": frozenset(),
}


def authorize(agent_role: str, tool_name: str) -> AuthorizationDecision:
    if tool_name in ROLE_TOOL_ALLOWLIST.get(agent_role, frozenset()):
        return AuthorizationDecision(True, "authorized")
    return AuthorizationDecision(False, f"ACCESS DENIED: {agent_role} cannot use {tool_name}")
