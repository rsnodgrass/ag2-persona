"""
AG2 PersonaAgent - Persona-based agents for AG2.

This package provides PersonaAgent, an extension of AG2's ConversableAgent that
enables agents to embody distinct personas through role, goal, and backstory components.
"""

from .async_persona_builder import AsyncPersonaBuilder
from .persona_agent import PersonaAgent
from .persona_builder import PersonaBuilder

__version__ = "0.1.1"
__all__ = ["AsyncPersonaBuilder", "PersonaAgent", "PersonaBuilder"]
