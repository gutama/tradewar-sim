"""Prompt templates for LLM interactions in the trade war simulation."""

from tradewar.llm.prompts.base_prompt import (create_country_context, 
                                             create_economic_context,
                                             create_simulation_context)

__all__ = [
    "create_simulation_context",
    "create_economic_context",
    "create_country_context",
]
