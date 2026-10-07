"""Factory for the standard Phase 3 tool registry."""

from tools.comparison_tool import compare_outfits
from tools.filter_tool import filter_products
from tools.outfit_tool import build_outfits
from tools.ranking_tool import rank_outfits_tool
from tools.registry import ToolMetadata, ToolRegistry
from tools.search_tool import search_products
from tools.validation_tool import validate_recommendation


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    definitions = (
        ("search_products", "Search the fashion catalog", "search_agent", search_products),
        ("filter_products", "Apply hard product constraints", "filter_agent", filter_products),
        ("build_outfits", "Construct compatible outfits", "outfit_builder_agent", build_outfits),
        ("compare_outfits", "Compare candidate outfits", "comparison_agent", compare_outfits),
        ("rank_outfits", "Rank outfits deterministically", "ranking_agent", rank_outfits_tool),
        ("validate_recommendation", "Validate a recommendation", "validator_agent", validate_recommendation),
    )
    for name, description, agent, handler in definitions:
        registry.register(ToolMetadata(name, description, frozenset({agent})), handler)
    return registry
