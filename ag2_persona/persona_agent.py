"""
PersonaAgent for AG2: Persona-based agents with distinct character embodiment.

This module provides PersonaAgent, an extension of ConversableAgent that
enables agents to embody distinct personas through role, goal, and backstory components.
"""

from typing import Any

try:
    from autogen import ConversableAgent

    AG2_AVAILABLE = True
except ImportError:
    # Fallback for development/testing without AG2
    class ConversableAgent:  # type: ignore[no-redef]
        def __init__(self, name: str, system_message: str, **kwargs: Any) -> None:
            self.name = name
            self.system_message = system_message
            self.llm_config = kwargs.get("llm_config", {})

    AG2_AVAILABLE = False


class PersonaAgent(ConversableAgent):
    """
    An AG2 agent that embodies a distinct persona.

    Extends ConversableAgent to enable agents to adopt specific personas through
    explicit role, goal, backstory, and constraints that define their character
    and behavioral identity.

    This design allows agents to authentically embody different roles and personalities
    while maintaining full compatibility with AG2's architecture and patterns.

    Attributes:
        role (str): The agent's role or title
        goal (str): What the agent should accomplish
        backstory (str): Background context and expertise
        constraints (List[str]): Rules and limitations

    Example:
        >>> agent = PersonaAgent(
        ...     name="reviewer",
        ...     role="Code Reviewer",
        ...     goal="Review code for quality and security issues",
        ...     backstory="Senior engineer with 10 years of experience",
        ...     constraints=["Focus on Python", "Check for SQL injection"]
        ... )
    """

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str = "",
        constraints: list[str] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a PersonaAgent.

        Args:
            name: Unique agent identifier
            role: The agent's role or title (e.g., "Data Scientist")
            goal: What the agent should accomplish
            backstory: Optional background, expertise, or context
            constraints: Optional list of rules or limitations
            description: Short description for GroupChat agent selection (defaults to role + goal)
            **kwargs: Additional ConversableAgent parameters (llm_config, human_input_mode, etc.)
        """
        # Store structured components as properties
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.constraints = constraints if constraints is not None else []

        # Build the structured system message
        system_message = self._build_system_message()

        # Generate description for GroupChat if not provided
        if description is None:
            description = f"{self.role}: {self.goal}"

        # Handle any additional system_message in kwargs
        # This maintains backward compatibility
        if "system_message" in kwargs:
            additional = kwargs.pop("system_message")
            system_message = f"{system_message}\n\nAdditional Instructions:\n{additional}"

        # Initialize parent ConversableAgent (inherits AG2's defaults)
        super().__init__(
            name=name, system_message=system_message, description=description, **kwargs
        )

    def _build_system_message(self) -> str:
        """
        Compose system message from structured components.

        Returns:
            str: The complete system message
        """
        # Start with role - who the agent is
        parts = [f"# Role: {self.role}"]

        # Add goal - what the agent should do
        parts.append(f"\n## Goal\n{self.goal}")

        # Add backstory if provided - context and expertise
        if self.backstory:
            parts.append(f"\n## Background\n{self.backstory}")

        # Add constraints if provided - rules and limitations
        if self.constraints:
            parts.append("\n## Constraints")
            parts.extend(f"- {constraint}" for constraint in self.constraints)

        return "\n".join(parts)

    def update_goal(self, new_goal: str) -> None:
        """
        Dynamically update the agent's goal.

        This regenerates the system message with the new goal while preserving
        other components (role, backstory, constraints).

        Args:
            new_goal: The new goal for the agent

        Example:
            >>> agent.update_goal("Focus on performance optimization")
        """
        self.goal = new_goal
        self.update_system_message(self._build_system_message())

    def add_constraint(self, constraint: str) -> None:
        """
        Add a new constraint to the agent.

        Args:
            constraint: New rule or limitation to add

        Example:
            >>> agent.add_constraint("Respond only with JSON")
        """
        if constraint not in self.constraints:
            self.constraints.append(constraint)
            self.update_system_message(self._build_system_message())

    def remove_constraint(self, constraint: str) -> None:
        """
        Remove a constraint from the agent.

        Args:
            constraint: Constraint to remove
        """
        if constraint in self.constraints:
            self.constraints.remove(constraint)
            self.update_system_message(self._build_system_message())

    def to_dict(self) -> dict[str, Any]:
        """
        Export the agent's persona configuration as a dictionary.

        Note: This excludes llm_config as it should be provided at runtime.
        Use PersonaBuilder.from_dict(agent.to_dict()) to recreate the agent.

        Returns:
            dict: Persona configuration (role, goal, backstory, constraints)
        """
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "constraints": self.constraints,
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"PersonaAgent(name='{self.name}', role='{self.role}', goal='{self.goal[:50]}...')"
