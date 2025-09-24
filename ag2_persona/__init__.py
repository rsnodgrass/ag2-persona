"""
AG2 PersonaAgent - Persona-based agents for AG2.

This package provides PersonaAgent, an extension of AG2's ConversableAgent that
enables agents to embody distinct personas through role, goal, and backstory components.
"""

from .persona_agent import (
    PersonaAgent,
    persona_agent,
    persona_agent_from_config,
)

__version__ = "0.1.0"
__author__ = "Ryan Snodgrass"
__email__ = "ryan@snodgrass.dev"

__all__ = [
    "PersonaAgent",
    "persona_agent",
    "persona_agent_from_config",
]
