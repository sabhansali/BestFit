"""Registry-facing ranking tool."""

from rules.ranking_rules import rank_outfits


def rank_outfits_tool(outfits: list[list[dict]], required_categories: tuple[str, ...], **requirements: object):
    return rank_outfits(outfits, required_categories, **requirements)
