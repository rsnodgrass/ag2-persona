"""
PersonaBuilder for creating PersonaAgent instances with fluent interface and validation.

This module provides PersonaBuilder, which offers a more flexible and robust way
to create PersonaAgent instances compared to direct constructor calls or from_dict methods.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .persona_agent import PersonaAgent


class PersonaBuilder:
    """
    Builder pattern for creating PersonaAgent instances with validation and flexibility.

    Provides a fluent interface for constructing PersonaAgents with comprehensive
    validation, flexible loading from YAML/dict sources, and runtime LLM configuration.

    Example:
        >>> agent = (PersonaBuilder("analyst")
        ...           .from_yaml("analyst.yaml")
        ...           .llm_config({"model": "gpt-4"})
        ...           .add_constraint("Focus on statistical significance")
        ...           .build())
    """

    def __init__(self, name: str):
        """
        Initialize PersonaBuilder with agent name.

        Args:
            name: Unique identifier for the agent
        """
        self.name = name
        self._role: str | None = None
        self._goal: str | None = None
        self._backstory: str = ""
        self._constraints: list[str] = []
        self._llm_config: dict[str, Any] | None = None
        self._description: str | None = None
        self.additional_kwargs: dict[str, Any] = {}

    def role(self, role: str) -> "PersonaBuilder":
        """Set the persona's role or title."""
        self._role = role
        return self

    def goal(self, goal: str) -> "PersonaBuilder":
        """Set the persona's objective or goal."""
        self._goal = goal
        return self

    def backstory(self, backstory: str) -> "PersonaBuilder":
        """Set the persona's background and expertise."""
        self._backstory = backstory
        return self

    def add_constraint(self, constraint: str) -> "PersonaBuilder":
        """Add a single constraint or rule for the agent."""
        if constraint and constraint not in self._constraints:
            self._constraints.append(constraint)
        return self

    def constraints(self, constraints: list[str]) -> "PersonaBuilder":
        """Set multiple constraints at once, replacing any existing constraints."""
        self._constraints = constraints
        return self

    def llm_config(self, config: dict[str, Any]) -> "PersonaBuilder":
        """Set the LLM configuration for the agent."""
        self._llm_config = config
        return self

    def temperature(self, temp: float) -> "PersonaBuilder":
        """Convenience method to set just the temperature in LLM config."""
        if not self._llm_config:
            self._llm_config = {}
        self._llm_config["temperature"] = temp
        return self

    def with_human_input_never(self) -> "PersonaBuilder":
        """Set agent to never prompt for human input."""
        self.additional_kwargs["human_input_mode"] = "NEVER"
        return self

    def with_human_input_always(self) -> "PersonaBuilder":
        """Set agent to always prompt for human input."""
        self.additional_kwargs["human_input_mode"] = "ALWAYS"
        return self

    def with_human_input_terminate(self) -> "PersonaBuilder":
        """Set agent to prompt for human input only on termination (AG2 default)."""
        self.additional_kwargs["human_input_mode"] = "TERMINATE"
        return self

    def description(self, description: str) -> "PersonaBuilder":
        """Set description for GroupChat agent selection."""
        self._description = description
        return self

    def with_kwargs(self, **kwargs: Any) -> "PersonaBuilder":
        """Add additional ConversableAgent parameters."""
        self.additional_kwargs.update(kwargs)
        return self

    def from_dict(self, config_dict: dict[str, Any]) -> "PersonaBuilder":
        """
        Load persona attributes from a configuration dictionary.

        Note: This does NOT load llm_config from the dictionary - LLM configuration
        should be provided at runtime using llm_config().

        Args:
            config_dict: Dictionary containing persona configuration

        Returns:
            PersonaBuilder: Self for method chaining

        Raises:
            ValueError: If config_dict is not a valid dictionary
        """
        if not isinstance(config_dict, dict):
            raise ValueError(f"Configuration must be a dictionary for persona '{self.name}'")

        # Load persona attributes (but not llm_config)
        self._role = config_dict.get("role")
        self._goal = config_dict.get("goal")
        self._backstory = config_dict.get("backstory", "")
        self._constraints = config_dict.get("constraints", [])

        # Validate constraints format
        if self._constraints and not isinstance(self._constraints, list):
            raise ValueError(
                f"Constraints must be a list for persona '{self.name}', got {type(self._constraints)}"
            )

        return self

    def from_yaml(self, file_path: str | Path) -> "PersonaBuilder":
        """
        Load persona definition from a YAML file.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            PersonaBuilder: Self for method chaining

        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            ValueError: If the YAML file is invalid or contains bad data
            ImportError: If ruamel.yaml is not installed
        """
        try:
            from ruamel.yaml import YAML
        except ImportError as err:
            raise ImportError(
                "ruamel.yaml is required for YAML config files. Install with: pip install ruamel.yaml"
            ) from err

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Persona YAML file not found: {file_path}")

        yaml = YAML()
        try:
            with file_path.open() as f:
                config = yaml.load(f)
        except Exception as e:
            raise ValueError(f"Error loading YAML from {file_path}: {e}") from e

        if config is None:
            raise ValueError(f"YAML file {file_path} is empty or contains no valid data")

        return self.from_dict(config)

    def extend_goal(self, additional_goal: str) -> "PersonaBuilder":
        """Extend the existing goal with additional requirements."""
        if self._goal:
            self._goal = f"{self._goal}. Additionally, {additional_goal}"
        else:
            self._goal = additional_goal
        return self

    def validate(self) -> "PersonaBuilder":
        """Validate the current configuration before building.

        Raises:
            ValueError: If validation fails with detailed error messages
        """
        errors = []

        if not self.name:
            errors.append("Persona name is required")
        if not self._role:
            errors.append(f"Role is required for persona '{self.name}'")
        if not self._goal:
            errors.append(f"Goal is required for persona '{self.name}'")

        # Validate constraints format
        if self._constraints and not isinstance(self._constraints, list):
            errors.append(
                f"Constraints must be a list for persona '{self.name}', got {type(self._constraints)}"
            )

        # Validate LLM config structure if provided
        if self._llm_config is not None:
            if not isinstance(self._llm_config, dict):
                errors.append(
                    f"LLM config must be a dictionary for persona '{self.name}', got {type(self._llm_config)}"
                )
            elif not any(key in self._llm_config for key in ("config_list", "model")):
                errors.append(
                    f"LLM config must contain 'config_list' or 'model' for persona '{self.name}'"
                )

        if errors:
            error_msg = f"Persona validation failed for '{self.name}':\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

        return self

    def build(self) -> "PersonaAgent":
        """
        Build the PersonaAgent instance with validation.

        Returns:
            PersonaAgent: The constructed agent instance

        Raises:
            ValueError: If validation fails
        """
        # Import here to avoid circular imports
        from .persona_agent import PersonaAgent

        # Validate before building
        self.validate()

        # After validation, these should be guaranteed to exist
        assert self._role is not None, "Role should be set after validation"
        assert self._goal is not None, "Goal should be set after validation"

        return PersonaAgent(
            name=self.name,
            role=self._role,
            goal=self._goal,
            backstory=self._backstory,
            constraints=self._constraints,
            description=self._description,
            llm_config=self._llm_config,
            **self.additional_kwargs,
        )

    def __repr__(self) -> str:
        """String representation of the builder."""
        if self._goal is None:
            goal_display = "None"
        elif len(self._goal) > 30:  # noqa: PLR2004
            goal_display = f"'{self._goal[:30]}...'"
        else:
            goal_display = f"'{self._goal}'"

        return f"PersonaBuilder(name='{self.name}', role='{self._role}', goal={goal_display})"
