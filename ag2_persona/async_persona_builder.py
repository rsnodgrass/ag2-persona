"""
AsyncPersonaBuilder for creating PersonaAgent instances with fluent async-safe chaining.

This module provides AsyncPersonaBuilder using a deferred execution pattern that enables
true single-chain syntax: await (builder.method1().method2().build()).

Design Decision: Methods record operations in a queue and execute them during build().
This enables perfect fluent chaining while supporting both sync and async operations.
Only build() is async, allowing natural single-await syntax.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, cast

if TYPE_CHECKING:
    from .persona_agent import PersonaAgent


class AsyncPersonaBuilder:
    """
    Fluent async-safe builder for creating PersonaAgent instances.

    Uses deferred execution pattern where all methods record operations in a queue
    and execute them during build(). This enables true single-chain syntax with
    perfect operation ordering and type safety.

    Design Pattern:
        - All methods return Self for perfect fluent chaining
        - Operations are queued and executed during build() in exact call order
        - Mix of sync (property setters) and async (file I/O) operations supported
        - Single await required only at build() - no intermediate awaits needed
        - Errors deferred until build() for clean validation and stack traces

    Examples:
        Basic usage with fluent chaining:
        >>> agent = await (AsyncPersonaBuilder("analyst")
        ...                .role("Data Scientist")
        ...                .goal("Analyze customer data")
        ...                .llm_config({"model": "gpt-4", "temperature": 0.7})
        ...                .build())

        Loading from YAML with async I/O:
        >>> agent = await (AsyncPersonaBuilder("expert")
        ...                .from_yaml("personas/data_scientist.yaml")
        ...                .llm_config({"model": "gpt-4"})
        ...                .human_input_never()
        ...                .build())

        Complex multi-step configuration:
        >>> agent = await (AsyncPersonaBuilder("researcher")
        ...                .from_yaml("personas/researcher.yaml")
        ...                .extend_goal("focus on statistical significance")
        ...                .add_constraint("Use peer-reviewed sources")
        ...                .add_constraint("Provide confidence intervals")
        ...                .temperature(0.5)
        ...                .description("Statistical research specialist")
        ...                .kwargs(max_consecutive_auto_reply=10)
        ...                .build())

        Debug mode for development:
        >>> agent = await (AsyncPersonaBuilder("debug_agent", debug=True)
        ...                .role("Test Role")
        ...                .goal("Test Goal")
        ...                .llm_config({"model": "gpt-4"})
        ...                .build())
        # Will log: "AsyncPersonaBuilder Running sync step: set_role" etc.

    Queue Execution Order:
        Operations execute in exact method call order during build():
        1. All queued operations (sync first, then async)
        2. Configuration validation
        3. PersonaAgent construction
        4. Return fully configured agent

    Type Safety:
        - Full Self typing enables perfect IDE autocomplete
        - Type-safe method chaining with return type inference
        - Async operations properly typed as Awaitable[None]
        - Build() returns PersonaAgent with all attributes guaranteed set
    """

    def __init__(self, name: str, debug: bool = False):
        """
        Initialize AsyncPersonaBuilder with agent name.

        Args:
            name: Unique identifier for the agent
            debug: Enable debug logging of execution steps
        """
        self.name = name
        self._debug = debug
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Queue of (is_async, function) tuples for deferred execution
        self._steps: list[tuple[int, Callable[[], None] | Callable[[], Awaitable[None]]]] = []

        # Instance state - set during build()
        self._role: str | None = None
        self._goal: str | None = None
        self._backstory: str = ""
        self._constraints: list[str] = []
        self._llm_config: dict[str, Any] | bool | None = None
        self._description: str | None = None
        self.additional_kwargs: dict[str, Any] = {}

    def _record_sync(self, func: Callable[[], None]) -> None:
        """Record a synchronous operation for deferred execution."""
        self._steps.append((0, func))

    def _record_async(self, func: Callable[[], Awaitable[None]]) -> None:
        """Record an asynchronous operation for deferred execution."""
        self._steps.append((1, func))

    def _log(self, label: str, func: Callable[[], None] | Callable[[], Awaitable[None]]) -> None:
        """Log debug information if debug mode is enabled."""
        if self._debug:
            fname = getattr(func, "__name__", repr(func))
            self._logger.debug("AsyncPersonaBuilder %s: %s", label, fname)

    # ---- Sync builder methods ----

    def role(self, role: str) -> Self:
        """Set the persona's role or title."""

        def set_role() -> None:
            self._role = role

        self._record_sync(set_role)
        return self

    def goal(self, goal: str) -> Self:
        """Set the persona's objective or goal."""

        def set_goal() -> None:
            self._goal = goal

        self._record_sync(set_goal)
        return self

    def backstory(self, backstory: str) -> Self:
        """Set the persona's background and expertise."""

        def set_backstory() -> None:
            self._backstory = backstory

        self._record_sync(set_backstory)
        return self

    def add_constraint(self, constraint: str) -> Self:
        """Add a single constraint or rule for the agent."""

        def add_constraint_impl() -> None:
            if constraint and constraint not in self._constraints:
                self._constraints.append(constraint)

        self._record_sync(add_constraint_impl)
        return self

    def constraints(self, constraints: list[str]) -> Self:
        """Set multiple constraints at once, replacing any existing constraints."""

        def set_constraints() -> None:
            self._constraints = constraints

        self._record_sync(set_constraints)
        return self

    def llm_config(self, config: dict[str, Any] | bool) -> Self:
        """Set the LLM configuration for the agent."""

        def set_llm_config() -> None:
            self._llm_config = config

        self._record_sync(set_llm_config)
        return self

    def temperature(self, temp: float) -> Self:
        """Convenience method to set just the temperature in LLM config."""

        def set_temperature() -> None:
            if not self._llm_config:
                self._llm_config = {}
            if isinstance(self._llm_config, dict):
                self._llm_config["temperature"] = temp

        self._record_sync(set_temperature)
        return self

    def description(self, description: str) -> Self:
        """Set description for GroupChat agent selection."""

        def set_description() -> None:
            self._description = description

        self._record_sync(set_description)
        return self

    def human_input_never(self) -> Self:
        """Set agent to never prompt for human input."""

        def set_human_input_never() -> None:
            self.additional_kwargs["human_input_mode"] = "NEVER"

        self._record_sync(set_human_input_never)
        return self

    def human_input_always(self) -> Self:
        """Set agent to always prompt for human input."""

        def set_human_input_always() -> None:
            self.additional_kwargs["human_input_mode"] = "ALWAYS"

        self._record_sync(set_human_input_always)
        return self

    def human_input_terminate(self) -> Self:
        """Set agent to prompt for human input only on termination (AG2 default)."""

        def set_human_input_terminate() -> None:
            self.additional_kwargs["human_input_mode"] = "TERMINATE"

        self._record_sync(set_human_input_terminate)
        return self

    def kwargs(self, **kwargs: Any) -> Self:
        """Add additional ConversableAgent parameters."""

        def set_kwargs() -> None:
            self.additional_kwargs.update(kwargs)

        self._record_sync(set_kwargs)
        return self

    def extend_goal(self, additional_goal: str) -> Self:
        """Extend the existing goal with additional requirements."""

        def extend_goal_impl() -> None:
            if self._goal:
                self._goal = f"{self._goal}. Additionally, {additional_goal}"
            else:
                self._goal = additional_goal

        self._record_sync(extend_goal_impl)
        return self

    # ---- Async builder methods ----

    def from_dict(self, config_dict: dict[str, Any]) -> Self:
        """
        Load persona attributes from a configuration dictionary.

        Note: This does NOT load llm_config from the dictionary - LLM configuration
        should be provided at runtime using llm_config().
        """

        def load_from_dict() -> None:
            if not isinstance(config_dict, dict):
                raise ValueError(f"Configuration must be a dictionary for persona '{self.name}'")

            # Load persona attributes (but not llm_config)
            self._role = config_dict.get("role")
            self._goal = config_dict.get("goal")
            self._backstory = config_dict.get("backstory", "")

            # Load constraints with type validation
            constraints_raw = config_dict.get("constraints", [])
            if constraints_raw and not isinstance(constraints_raw, list):
                raise ValueError(
                    f"Constraints must be a list for persona '{self.name}', got {type(constraints_raw)}"
                )
            self._constraints = constraints_raw

        self._record_sync(load_from_dict)
        return self

    def from_yaml(self, file_path: str | Path) -> Self:
        """
        Load persona definition from a YAML file asynchronously.

        This method uses deferred execution - the file I/O will happen during build()
        to avoid blocking the event loop during method chaining.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            Self for method chaining

        Raises:
            FileNotFoundError: If the YAML file doesn't exist (raised during build())
            ValueError: If the YAML file is invalid or contains bad data (raised during build())
            ImportError: If ruamel.yaml or aiofiles is not installed (raised during build())

        Example:
            >>> # File I/O happens asynchronously during build(), not here
            >>> agent = await (AsyncPersonaBuilder("analyst")
            ...                .from_yaml("configs/data_analyst.yaml")  # Queued for async execution
            ...                .llm_config({"model": "gpt-4"})         # Sync operation
            ...                .build())                               # Async file load happens here

        YAML File Format:
            role: "Data Analyst"
            goal: "Analyze datasets and provide insights"
            backstory: "Expert in statistical analysis with 10 years experience"
            constraints:
              - "Use statistical significance tests"
              - "Provide data visualizations"
        """

        async def load_from_yaml() -> None:
            try:
                from ruamel.yaml import YAML
            except ImportError as err:
                raise ImportError(
                    "ruamel.yaml is required for YAML config files. Install with: pip install ruamel.yaml"
                ) from err

            try:
                import aiofiles  # type: ignore[import-untyped]
                import aiofiles.os  # type: ignore[import-untyped]
            except ImportError as err:
                raise ImportError(
                    "aiofiles is required for async YAML loading. Install with: pip install aiofiles"
                ) from err

            file_path_obj = Path(file_path)

            # Async file existence check
            if not await aiofiles.os.path.exists(file_path_obj):
                raise FileNotFoundError(f"Persona YAML file not found: {file_path_obj}")

            yaml = YAML()
            try:
                async with aiofiles.open(file_path_obj) as f:
                    content = await f.read()
                    config = yaml.load(content)
            except Exception as e:
                raise ValueError(f"Error loading YAML from {file_path_obj}: {e}") from e

            if config is None:
                raise ValueError(f"YAML file {file_path_obj} is empty or contains no valid data")

            # Apply the loaded config using from_dict logic
            if not isinstance(config, dict):
                raise ValueError(f"Configuration must be a dictionary for persona '{self.name}'")

            # Load persona attributes (but not llm_config)
            self._role = config.get("role")
            self._goal = config.get("goal")
            self._backstory = config.get("backstory", "")

            # Load constraints with type validation
            constraints_raw = config.get("constraints", [])
            if constraints_raw and not isinstance(constraints_raw, list):
                raise ValueError(
                    f"Constraints must be a list for persona '{self.name}', got {type(constraints_raw)}"
                )
            self._constraints = constraints_raw

        self._record_async(load_from_yaml)
        return self

    # ---- Finalizer ----

    def validate(self) -> None:
        """Validate the current configuration before building."""
        errors = []

        if not self.name:
            errors.append("Persona name is required")
        if not self._role:
            errors.append(f"Role is required for persona '{self.name}'")
        if not self._goal:
            errors.append(f"Goal is required for persona '{self.name}'")

        # Validate LLM config structure if provided (skip if False - means no LLM)
        if isinstance(self._llm_config, dict):
            required_keys = ["config_list", "model"]
            if not any(key in self._llm_config for key in required_keys):
                errors.append(
                    f"LLM config must contain one of {required_keys} for persona '{self.name}'"
                )

        if errors:
            error_msg = f"Persona validation failed for '{self.name}':\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

    async def build(self) -> PersonaAgent:
        """
        Build the PersonaAgent instance by executing all deferred operations.

        Returns:
            PersonaAgent: The constructed agent instance

        Raises:
            ValueError: If validation fails
        """
        # Execute all deferred operations in order
        for is_async, func in self._steps:
            if is_async:
                self._log("Awaiting async step", func)
                await cast(Callable[[], Awaitable[None]], func)()
            else:
                self._log("Running sync step", func)
                func()

        # Validate the final configuration
        self.validate()

        # Import here to avoid circular imports
        from .persona_agent import PersonaAgent

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
        steps_count = len(self._steps)
        return f"AsyncPersonaBuilder(name='{self.name}', queued_steps={steps_count})"
