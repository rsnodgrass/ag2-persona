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
            # Don't set name directly as subclasses may have custom property setters
            object.__setattr__(self, "name", name)
            self.system_message = system_message
            self.llm_config = kwargs.get("llm_config", {})

            # Store all kwargs as attributes for test compatibility
            for key, value in kwargs.items():
                setattr(self, key, value)

        def update_system_message(self, new_message: str) -> None:
            """Update the system message (mock implementation)."""
            self.system_message = new_message

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
        description (str): Short description for GroupChat agent selection

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
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
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
            version: Version identifier for auditing purposes
            metadata: Optional extensible metadata dictionary for user-defined data
            **kwargs: Additional ConversableAgent parameters (llm_config, human_input_mode, etc.)
        """
        # Store structured components as properties
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.constraints = constraints if constraints is not None else []
        self.version = version
        self._metadata = metadata if metadata is not None else {}

        # Store name for immutability control (before parent init)
        self._persona_name = name
        # Track that construction is complete to enable name immutability
        self._construction_complete = False

        # Generate description for GroupChat if not provided
        if description is None:
            description = f"{self.role}: {self.goal}"

        # Store description as instance property so tests can access it
        self.description = description

        # Build the structured system message
        system_message = self._build_system_message()

        # Handle any additional system_message in kwargs
        # This maintains backward compatibility
        if "system_message" in kwargs:
            additional = kwargs.pop("system_message")
            system_message = f"{system_message}\n\nAdditional Instructions:\n{additional}"

        # Store human_input_mode for property access
        self._human_input_mode = kwargs.get("human_input_mode", "TERMINATE")

        # Initialize parent ConversableAgent (inherits AG2's defaults)
        super().__init__(
            name=name, system_message=system_message, description=description, **kwargs
        )

        # Mark construction as complete to enable name immutability
        self._construction_complete = True

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

    @property
    def human_input_mode(self) -> str:
        """Get the human input mode."""
        return getattr(self, "_human_input_mode", "TERMINATE")

    @human_input_mode.setter
    def human_input_mode(self, value: str) -> None:
        """Set the human input mode."""
        self._human_input_mode = value

    @property
    def name(self) -> str:
        """Get the agent name (immutable after construction)."""
        return self._persona_name

    @name.setter
    def name(self, value: str) -> None:
        """Prevent name modification after construction."""
        if getattr(self, "_construction_complete", False):
            raise AttributeError("PersonaAgent name is immutable after construction")
        # Allow setting during construction
        self._persona_name = value

    @property
    def metadata(self) -> dict[str, Any]:
        """
        Get the extensible metadata dictionary.

        Returns:
            dict: Copy of the metadata dictionary to prevent external modification
        """
        return self._metadata.copy()

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """
        Update the extensible metadata dictionary.

        Args:
            metadata: Dictionary containing metadata updates to merge

        Example:
            >>> agent.update_metadata({
            ...     "audit_info": {"last_used": "2024-09-26"},
            ...     "custom_field": "value"
            ... })
        """
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")

        self._metadata.update(metadata)

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

        Includes all configuration needed to recreate the agent.
        Use PersonaBuilder.from_dict(agent.to_dict()) to recreate the agent.

        Returns:
            dict: Persona configuration including llm_config and version
        """
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "constraints": self.constraints,
            "llm_config": getattr(self, "llm_config", None),
            "version": self.version,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"PersonaAgent(name='{self.name}', role='{self.role}', goal='{self.goal[:50]}...')"
