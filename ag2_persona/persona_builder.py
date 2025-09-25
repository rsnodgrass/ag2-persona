"""
PersonaBuilder for creating PersonaAgent instances with fluent interface and validation.

This module provides PersonaBuilder, which offers a more flexible and robust way
to create PersonaAgent instances compared to direct constructor calls or from_dict methods.
"""

from typing import Any, Optional
from pathlib import Path


class PersonaBuilder:
    """
    Builder pattern for creating PersonaAgent instances with validation and flexibility.

    Provides a fluent interface for constructing PersonaAgents with comprehensive
    validation, flexible loading from YAML/dict sources, and runtime LLM configuration.

    Example:
        >>> agent = (PersonaBuilder("analyst")
        ...           .from_yaml("analyst.yaml")
        ...           .with_llm_config({"model": "gpt-4"})
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
        self.role: Optional[str] = None
        self.goal: Optional[str] = None
        self.backstory: str = ""
        self.constraints: list[str] = []
        self.llm_config: Optional[dict[str, Any]] = None
        self.description: Optional[str] = None
        self.additional_kwargs: dict[str, Any] = {}

    def with_role(self, role: str) -> "PersonaBuilder":
        """
        Set the persona's role or title.

        Args:
            role: The agent's professional role (e.g., "Senior Software Engineer")

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.role = role
        return self

    def with_goal(self, goal: str) -> "PersonaBuilder":
        """
        Set the persona's objective or goal.

        Args:
            goal: What the agent should accomplish

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.goal = goal
        return self

    def with_backstory(self, backstory: str) -> "PersonaBuilder":
        """
        Set the persona's background and expertise.

        Args:
            backstory: Background context, experience, and expertise

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.backstory = backstory
        return self

    def add_constraint(self, constraint: str) -> "PersonaBuilder":
        """
        Add a single constraint or rule for the agent.

        Args:
            constraint: A rule or limitation for the agent to follow

        Returns:
            PersonaBuilder: Self for method chaining
        """
        if constraint and constraint not in self.constraints:
            self.constraints.append(constraint)
        return self

    def with_constraints(self, constraints: list[str]) -> "PersonaBuilder":
        """
        Set multiple constraints at once, replacing any existing constraints.

        Args:
            constraints: List of rules or limitations

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.constraints = constraints if constraints else []
        return self

    def with_llm_config(self, config: dict[str, Any]) -> "PersonaBuilder":
        """
        Set the LLM configuration for the agent.

        Args:
            config: LLM configuration dictionary (model, temperature, etc.)

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.llm_config = config
        return self

    def with_temperature(self, temp: float) -> "PersonaBuilder":
        """
        Convenience method to set just the temperature in LLM config.

        Args:
            temp: Temperature value for the LLM

        Returns:
            PersonaBuilder: Self for method chaining
        """
        if not self.llm_config:
            self.llm_config = {}
        self.llm_config["temperature"] = temp
        return self

    def with_human_input_never(self) -> "PersonaBuilder":
        """
        Set agent to never prompt for human input.

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.additional_kwargs["human_input_mode"] = "NEVER"
        return self

    def with_human_input_always(self) -> "PersonaBuilder":
        """
        Set agent to always prompt for human input.

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.additional_kwargs["human_input_mode"] = "ALWAYS"
        return self

    def with_human_input_terminate(self) -> "PersonaBuilder":
        """
        Set agent to prompt for human input only on termination.

        This is the default AG2 ConversableAgent behavior.

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.additional_kwargs["human_input_mode"] = "TERMINATE"
        return self

    def with_description(self, description: str) -> "PersonaBuilder":
        """
        Set description for GroupChat agent selection.

        Args:
            description: Concise description for GroupChatManager to use for agent selection

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.description = description
        return self

    def with_kwargs(self, **kwargs: Any) -> "PersonaBuilder":
        """
        Add additional ConversableAgent parameters.

        Args:
            **kwargs: Additional parameters to pass to PersonaAgent constructor

        Returns:
            PersonaBuilder: Self for method chaining
        """
        self.additional_kwargs.update(kwargs)
        return self

    def from_dict(self, config_dict: dict[str, Any]) -> "PersonaBuilder":
        """
        Load persona attributes from a configuration dictionary.

        Note: This does NOT load llm_config from the dictionary - LLM configuration
        should be provided at runtime using with_llm_config().

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
        self.role = config_dict.get("role")
        self.goal = config_dict.get("goal")
        self.backstory = config_dict.get("backstory", "")
        self.constraints = config_dict.get("constraints", [])

        # Validate constraints format
        if self.constraints and not isinstance(self.constraints, list):
            raise ValueError(f"Constraints must be a list for persona '{self.name}', got {type(self.constraints)}")

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
            with open(file_path) as f:
                config = yaml.load(f)
        except Exception as e:
            raise ValueError(f"Error loading YAML from {file_path}: {e}") from e

        if config is None:
            raise ValueError(f"YAML file {file_path} is empty or contains no valid data")

        return self.from_dict(config)

    def extend_goal(self, additional_goal: str) -> "PersonaBuilder":
        """
        Extend the existing goal with additional requirements.

        Args:
            additional_goal: Additional goal text to append

        Returns:
            PersonaBuilder: Self for method chaining
        """
        if self.goal:
            self.goal = f"{self.goal}. Additionally, {additional_goal}"
        else:
            self.goal = additional_goal
        return self

    def validate(self) -> "PersonaBuilder":
        """
        Validate the current configuration before building.

        Returns:
            PersonaBuilder: Self for method chaining

        Raises:
            ValueError: If validation fails with detailed error messages
        """
        errors = []

        if not self.name:
            errors.append("Persona name is required")
        if not self.role:
            errors.append(f"Role is required for persona '{self.name}'")
        if not self.goal:
            errors.append(f"Goal is required for persona '{self.name}'")

        # Validate constraints format
        if self.constraints and not isinstance(self.constraints, list):
            errors.append(f"Constraints must be a list for persona '{self.name}', got {type(self.constraints)}")

        # Validate LLM config structure if provided
        if self.llm_config is not None:
            if not isinstance(self.llm_config, dict):
                errors.append(f"LLM config must be a dictionary for persona '{self.name}', got {type(self.llm_config)}")
            elif not any(key in self.llm_config for key in ["config_list", "model"]):
                errors.append(f"LLM config must contain 'config_list' or 'model' for persona '{self.name}'")

        if errors:
            error_msg = f"Persona validation failed for '{self.name}':\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)

        return self

    def build(self):
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

        return PersonaAgent(
            name=self.name,
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            constraints=self.constraints,
            description=self.description,
            llm_config=self.llm_config,
            **self.additional_kwargs
        )

    def __repr__(self) -> str:
        """String representation of the builder."""
        return (f"PersonaBuilder(name='{self.name}', role='{self.role}', "
                f"goal='{self.goal[:30]}...' if self.goal else None)")