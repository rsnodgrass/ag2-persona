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
    class ConversableAgent:
        def __init__(self, name: str, system_message: str, **kwargs):
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
            **kwargs: Additional ConversableAgent parameters (llm_config, etc.)
        """
        # Store structured components as properties
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.constraints = constraints if constraints is not None else []

        # Build the structured system message
        system_message = self._build_system_message()

        # Handle any additional system_message in kwargs
        # This maintains backward compatibility
        if "system_message" in kwargs:
            additional = kwargs.pop("system_message")
            system_message = f"{system_message}\n\nAdditional Instructions:\n{additional}"

        # Initialize parent ConversableAgent
        super().__init__(name=name, system_message=system_message, **kwargs)

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
            for constraint in self.constraints:
                parts.append(f"- {constraint}")

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
        self.system_message = self._build_system_message()

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
            self.system_message = self._build_system_message()

    def remove_constraint(self, constraint: str) -> None:
        """
        Remove a constraint from the agent.

        Args:
            constraint: Constraint to remove
        """
        if constraint in self.constraints:
            self.constraints.remove(constraint)
            self.system_message = self._build_system_message()

    def to_dict(self) -> dict[str, Any]:
        """
        Export the agent's configuration as a dictionary.

        Useful for serialization, saving, or creating similar agents.

        Returns:
            dict: Agent configuration including all structured components
        """
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "constraints": self.constraints,
            "llm_config": self.llm_config,
            "system_message": self.system_message,
        }

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "PersonaAgent":
        """
        Create a PersonaAgent from a configuration dictionary.

        Args:
            config: Dictionary containing agent configuration

        Returns:
            PersonaAgent: New agent instance

        Example:
            >>> config = {"name": "analyst", "role": "Data Analyst", ...}
            >>> agent = PersonaAgent.from_dict(config)
        """
        # Extract structured components
        name = config.pop("name")
        role = config.pop("role")
        goal = config.pop("goal")
        backstory = config.pop("backstory", "")
        constraints = config.pop("constraints", None)

        # Remove system_message as we'll regenerate it
        config.pop("system_message", None)

        # Create agent with remaining config as kwargs
        return cls(
            name=name, role=role, goal=goal, backstory=backstory, constraints=constraints, **config
        )

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"PersonaAgent(name='{self.name}', role='{self.role}', goal='{self.goal[:50]}...')"


# Functional interface for those who prefer functions over classes
def persona_agent(
    name: str,
    role: str,
    goal: str,
    backstory: str = "",
    constraints: list[str] | None = None,
    **kwargs: Any,
) -> PersonaAgent:
    """
    Create a PersonaAgent using a functional interface.

    This is a convenience function for those who prefer functional style.

    Args:
        name: Agent identifier
        role: The agent's role
        goal: What the agent should accomplish
        backstory: Optional background context
        constraints: Optional list of limitations
        **kwargs: Additional ConversableAgent parameters

    Returns:
        PersonaAgent: Configured agent instance

    Example:
        >>> agent = persona_agent(
        ...     name="helper",
        ...     role="Assistant",
        ...     goal="Help users with questions"
        ... )
    """
    return PersonaAgent(
        name=name, role=role, goal=goal, backstory=backstory, constraints=constraints, **kwargs
    )


def persona_agent_from_config(config: dict[str, Any] | str) -> PersonaAgent:
    """
    Create a PersonaAgent from configuration.

    Args:
        config: Dictionary config or path to YAML/JSON file

    Returns:
        PersonaAgent: Configured agent instance

    Example:
        >>> # From dict
        >>> agent = persona_agent_from_config({
        ...     "name": "analyst",
        ...     "role": "Data Analyst",
        ...     "goal": "Analyze data"
        ... })

        >>> # From file
        >>> agent = persona_agent_from_config("agent_config.yaml")
    """
    if isinstance(config, str):
        # Load from file
        import json

        with open(config) as f:
            if config.endswith(".json"):
                config = json.load(f)
            elif config.endswith((".yaml", ".yml")):
                try:
                    from ruamel.yaml import YAML

                    yaml = YAML()
                    config = yaml.load(f)
                except ImportError as err:
                    raise ImportError(
                        "ruamel.yaml is required for YAML config files. Install with: pip install ruamel.yaml"
                    ) from err
            else:
                raise ValueError(f"Unsupported file format: {config}")

    return PersonaAgent.from_dict(config)
