"""
AsyncPersonaBuilder for creating PersonaAgent instances with async YAML loading.

This module provides AsyncPersonaBuilder, which offers async file I/O operations
for loading persona definitions from YAML files without blocking the event loop.

Design Decision: All methods are async for API consistency and readability.
While only file I/O operations truly require async, making all methods async
enables beautiful single-chain syntax and consistent API patterns. The
readability and API consistency benefits outweigh the minimal performance cost
of unnecessary async calls for simple operations like setting configuration values.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .persona_agent import PersonaAgent


class AsyncPersonaBuilder:
    """
    Async builder pattern for creating PersonaAgent instances with non-blocking I/O.

    Provides async file loading capabilities for high-concurrency applications
    while maintaining the same fluent interface as PersonaBuilder.

    Example:
        >>> agent = await (AsyncPersonaBuilder("analyst")
        ...                .from_yaml("analyst.yaml")
        ...                .llm_config({"model": "gpt-4"})
        ...                .build())
    """

    def __init__(self, name: str):
        """
        Initialize AsyncPersonaBuilder with agent name.

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

    async def from_yaml(self, file_path: str | Path) -> "AsyncPersonaBuilder":
        """
        Load persona definition from a YAML file asynchronously.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            AsyncPersonaBuilder: Self for method chaining

        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            ValueError: If the YAML file is invalid or contains bad data
            ImportError: If ruamel.yaml or aiofiles is not installed
        """
        try:
            from ruamel.yaml import YAML
        except ImportError as err:
            raise ImportError(
                "ruamel.yaml is required for YAML config files. Install with: pip install ruamel.yaml"
            ) from err

        try:
            import aiofiles
            import aiofiles.os
        except ImportError as err:
            raise ImportError(
                "aiofiles is required for async YAML loading. Install with: pip install aiofiles"
            ) from err

        file_path = Path(file_path)

        # Async file existence check
        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"Persona YAML file not found: {file_path}")

        yaml = YAML()
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                config = yaml.load(content)
        except Exception as e:
            raise ValueError(f"Error loading YAML from {file_path}: {e}") from e

        if config is None:
            raise ValueError(f"YAML file {file_path} is empty or contains no valid data")

        return self.from_dict(config)

    async def from_dict(self, config_dict: dict[str, Any]) -> "AsyncPersonaBuilder":
        """
        Load persona attributes from a configuration dictionary.

        Args:
            config_dict: Dictionary containing persona configuration

        Returns:
            AsyncPersonaBuilder: Self for method chaining

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

    async def role(self, role: str) -> "AsyncPersonaBuilder":
        """Set the persona's role or title."""
        self._role = role
        return self

    async def goal(self, goal: str) -> "AsyncPersonaBuilder":
        """Set the persona's objective or goal."""
        self._goal = goal
        return self

    async def backstory(self, backstory: str) -> "AsyncPersonaBuilder":
        """Set the persona's background and expertise."""
        self._backstory = backstory
        return self

    async def add_constraint(self, constraint: str) -> "AsyncPersonaBuilder":
        """Add a single constraint or rule for the agent."""
        if constraint and constraint not in self._constraints:
            self._constraints.append(constraint)
        return self

    async def constraints(self, constraints: list[str]) -> "AsyncPersonaBuilder":
        """Set multiple constraints at once, replacing any existing constraints."""
        self._constraints = constraints
        return self

    async def llm_config(self, config: dict[str, Any]) -> "AsyncPersonaBuilder":
        """Set the LLM configuration for the agent."""
        self._llm_config = config
        return self

    async def temperature(self, temp: float) -> "AsyncPersonaBuilder":
        """Convenience method to set just the temperature in LLM config."""
        if not self._llm_config:
            self._llm_config = {}
        self._llm_config["temperature"] = temp
        return self

    async def description(self, description: str) -> "AsyncPersonaBuilder":
        """Set description for GroupChat agent selection."""
        self._description = description
        return self

    async def human_input_never(self) -> "AsyncPersonaBuilder":
        """Set agent to never prompt for human input."""
        self.additional_kwargs["human_input_mode"] = "NEVER"
        return self

    async def human_input_always(self) -> "AsyncPersonaBuilder":
        """Set agent to always prompt for human input."""
        self.additional_kwargs["human_input_mode"] = "ALWAYS"
        return self

    async def human_input_terminate(self) -> "AsyncPersonaBuilder":
        """Set agent to prompt for human input only on termination (AG2 default)."""
        self.additional_kwargs["human_input_mode"] = "TERMINATE"
        return self

    async def kwargs(self, **kwargs: Any) -> "AsyncPersonaBuilder":
        """Add additional ConversableAgent parameters."""
        self.additional_kwargs.update(kwargs)
        return self

    async def extend_goal(self, additional_goal: str) -> "AsyncPersonaBuilder":
        """Extend the existing goal with additional requirements."""
        if self._goal:
            self._goal = f"{self._goal}. Additionally, {additional_goal}"
        else:
            self._goal = additional_goal
        return self

    async def validate(self) -> "AsyncPersonaBuilder":
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

    async def build(self) -> "PersonaAgent":
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
        elif len(self._goal) > 30:
            goal_display = f"'{self._goal[:30]}...'"
        else:
            goal_display = f"'{self._goal}'"

        return f"AsyncPersonaBuilder(name='{self.name}', role='{self._role}', goal={goal_display})"