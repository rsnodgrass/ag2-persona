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
    validation, flexible loading from Markdown sources, and runtime LLM configuration.

    Example:
        >>> # Recommended: Load from Markdown files
        >>> agent = PersonaBuilder.from_markdown("analyst.md").build()

        >>> # With name override and chaining
        >>> agent = (PersonaBuilder.from_markdown("base.md")
        ...           .set_name("custom_analyst")
        ...           .extend_goal("Focus on real-time data")
        ...           .build())

        >>> # Manual construction (for programmatic use)
        >>> agent = (PersonaBuilder("analyst")
        ...           .role("Data Analyst")
        ...           .goal("Analyze data")
        ...           .build())
    """

    def __init__(self, name: str | None = None):
        """
        Initialize PersonaBuilder with optional agent name.

        Args:
            name: Optional unique identifier for the agent. If None, must be set via from_* methods or set_name() method.
        """
        self.name = name
        self._role: str | None = None
        self._goal: str | None = None
        self._backstory: str = ""
        self._constraints: list[str] = []
        self._llm_config: dict[str, Any] | bool | None = None
        self._description: str | None = None
        self.additional_kwargs: dict[str, Any] = {}

    def set_name(self, name: str) -> "PersonaBuilder":
        """Set the agent name."""
        self.name = name
        return self

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
        if isinstance(self._llm_config, dict):
            self._llm_config["temperature"] = temp
        return self

    def human_input_mode(self, mode: str) -> "PersonaBuilder":
        """Set agent's human input mode.

        Args:
            mode: One of "NEVER", "ALWAYS", or "TERMINATE"

        Raises:
            ValueError: If mode is not valid
        """
        valid_modes = ["NEVER", "ALWAYS", "TERMINATE"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid human_input_mode: {mode}. Must be one of {valid_modes}")
        self.additional_kwargs["human_input_mode"] = mode
        return self

    def human_input_never(self) -> "PersonaBuilder":
        """Set agent to never prompt for human input."""
        return self.human_input_mode("NEVER")

    def human_input_always(self) -> "PersonaBuilder":
        """Set agent to always prompt for human input."""
        return self.human_input_mode("ALWAYS")

    def human_input_terminate(self) -> "PersonaBuilder":
        """Set agent to prompt for human input only on termination (AG2 default)."""
        return self.human_input_mode("TERMINATE")

    def description(self, description: str) -> "PersonaBuilder":
        """Set description for GroupChat agent selection."""
        self._description = description
        return self

    def add_kwargs(self, **kwargs: Any) -> "PersonaBuilder":
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

        # Load persona attributes (but not llm_config for instance method backward compatibility)
        self._role = config_dict.get("role")
        self._goal = config_dict.get("goal")
        self._backstory = config_dict.get("backstory", "")
        self._constraints = config_dict.get("constraints", [])

        # Load name only if not already set (preserves instance name)
        if not self.name and "name" in config_dict:
            self.name = config_dict["name"]

        # Load LLM config from 'llm_config' key (matches AG2 API)
        if "llm_config" in config_dict:
            self._llm_config = config_dict["llm_config"]

        # Validate constraints format
        if self._constraints and not isinstance(self._constraints, list):
            raise ValueError(
                f"Constraints must be a list for persona '{self.name}', got {type(self._constraints)}"
            )

        return self

    @classmethod
    def from_markdown(
        cls,
        file_path: str | Path,
        override_metadata: dict[str, Any] | None = None,
    ) -> "PersonaBuilder":
        """
        Create PersonaBuilder from a Markdown file with YAML frontmatter metadata.

        The Markdown format supports:
        - YAML frontmatter (between --- delimiters) containing metadata
        - Main content sections that map to persona attributes

        Example Markdown format:
        ```markdown
        ---
        name: technical_architect
        llm_config:
          model: gpt-4
          temperature: 0.3
        custom_field: value
        ---

        # Role
        Senior Software Architect

        # Goal
        Review system designs and provide expert guidance

        # Backstory
        15+ years building distributed systems...

        # Constraints
        - Focus on maintainable solutions
        - Evaluate scalability
        ```

        Args:
            file_path: Path to Markdown file with persona definition
            override_metadata: Optional dictionary to override/extend frontmatter metadata

        Returns:
            PersonaBuilder: New instance with data loaded from file

        Raises:
            FileNotFoundError: If the Markdown file doesn't exist
            ValueError: If the Markdown format is invalid or name is missing
        """
        return cls()._load_from_markdown(file_path, None, override_metadata)

    def _load_from_markdown(
        self,
        file_path: str | Path,
        name_override: str | None = None,
        override_metadata: dict[str, Any] | None = None,
    ) -> "PersonaBuilder":
        """Internal method to load from markdown (supports both class method and instance method usage)."""
        from .parsers import PersonaMarkdownParser

        file_path = Path(file_path)

        # Sync file I/O
        if not file_path.exists():
            raise FileNotFoundError(f"Persona Markdown file not found: {file_path}")

        with file_path.open() as f:
            content = f.read()

        # Parse content using simplified parser
        config = PersonaMarkdownParser.parse_persona_markdown(content)

        # Apply metadata overrides (business logic)
        if override_metadata:
            # Handle nested dictionary merging for llm_config
            if "llm_config" in override_metadata and isinstance(config.get("llm_config"), dict):
                merged_llm_config = config["llm_config"].copy()
                merged_llm_config.update(override_metadata["llm_config"])
                override_metadata = override_metadata.copy()
                override_metadata["llm_config"] = merged_llm_config

            # Apply other overrides
            for key, value in override_metadata.items():
                if key == "llm_config":
                    config[key] = value  # Already handled above
                elif key in config:
                    config[key] = value
                else:
                    config["additional_kwargs"][key] = value

        # Handle name resolution (business logic)
        config["name"] = name_override or self.name or config.get("name") or file_path.stem

        # Apply the configuration to this builder instance
        self.name = config["name"]
        self._role = config["role"]
        self._goal = config["goal"]
        self._backstory = config["backstory"]
        self._constraints = config["constraints"]
        self._llm_config = config["llm_config"]
        self._description = config["description"]
        self.additional_kwargs.update(config["additional_kwargs"])

        return self

    def extend_goal(self, additional_goal: str) -> "PersonaBuilder":
        """Extend the existing goal with additional requirements."""
        if self._goal:
            self._goal = f"{self._goal}. Additionally, {additional_goal}"
        else:
            self._goal = additional_goal
        return self

    @classmethod
    def from_persona_dict(
        cls, config_dict: dict[str, Any], name: str | None = None
    ) -> "PersonaBuilder":
        """
        Create PersonaBuilder from a persona configuration dictionary.

        This is the factory method equivalent of PersonaAgent.from_dict() for creating
        agents from serialized persona data.

        Args:
            config_dict: Dictionary containing persona configuration (from PersonaAgent.to_dict())
            name: Optional name override. If None, uses name from config_dict

        Returns:
            PersonaBuilder: New instance with data loaded from dictionary

        Raises:
            ValueError: If config_dict is not a valid dictionary
        """
        builder_name = name or config_dict.get("name")
        return cls(builder_name).from_dict(config_dict)

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

        # Validate LLM config structure if provided (skip validation if False - means no LLM)
        if self._llm_config is not None and self._llm_config is not False:
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
        assert self.name is not None, "Name should be set after validation"
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
