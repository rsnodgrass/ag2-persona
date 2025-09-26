"""
Shared parsing utilities for PersonaBuilder classes.

This module provides shared parsing logic to avoid code duplication between
sync and async PersonaBuilder implementations.
"""

import re
from typing import Any


class PersonaMarkdownParser:
    """Shared Markdown parsing utility for both sync and async PersonaBuilder."""

    @staticmethod
    def parse_persona_markdown(content: str) -> dict[str, Any]:
        """
        Parse Markdown content into persona configuration.

        Args:
            content: Markdown content string to parse

        Returns:
            dict: Persona configuration with standard fields populated from
                  frontmatter and markdown sections

        Raises:
            ValueError: If the Markdown format is invalid
            ImportError: If required dependencies are not installed
        """
        try:
            import frontmatter
            from ruamel.yaml import YAML
        except ImportError as err:
            missing_lib = "python-frontmatter" if "frontmatter" in str(err) else "ruamel.yaml"
            raise ImportError(
                f"{missing_lib} is required for Markdown persona files. Install with: pip install {missing_lib}"
            ) from err

        # Use python-frontmatter with ruamel.yaml as the engine
        try:
            # Create custom handler that uses ruamel.yaml
            class RuamelYAMLHandler(frontmatter.YAMLHandler):  # type: ignore[misc]
                def load(self, fm: str) -> Any:
                    return YAML().load(fm)

            post = frontmatter.loads(content, handler=RuamelYAMLHandler())
            metadata = post.metadata
            main_content = post.content
        except Exception as e:
            raise ValueError(f"Error parsing frontmatter: {e}") from e

        # Parse markdown sections
        sections = PersonaMarkdownParser._parse_markdown_sections(main_content)

        # Build persona configuration following Spec vs Character philosophy
        # SPEC fields (role, goal, constraints) come ONLY from frontmatter
        # CHARACTER fields (backstory) come from markdown sections
        config = {
            "name": metadata.get("name"),  # None if not in frontmatter
            "role": metadata.get("role"),  # SPEC: frontmatter only
            "goal": metadata.get("goal"),  # SPEC: frontmatter only
            "backstory": sections.get("backstory", "").strip(),  # CHARACTER: markdown only
            "constraints": [],  # SPEC: frontmatter only (handled below)
            "llm_config": metadata.get("llm_config"),  # SPEC: frontmatter only
            "description": sections.get("description", "").strip()
            or metadata.get("description"),  # Can be in either
            "additional_kwargs": {},
        }

        # Handle constraints from sections or metadata
        PersonaMarkdownParser._apply_constraints(sections, metadata, config)

        # Store any additional metadata as kwargs
        reserved_keys = {
            "name",
            "role",
            "goal",
            "backstory",
            "constraints",
            "llm_config",
            "description",
        }
        for key, value in metadata.items():
            if key not in reserved_keys:
                config["additional_kwargs"][key] = value

        # Validate required fields for markdown loading
        PersonaMarkdownParser._validate_required_fields(config)

        return config

    @staticmethod
    def _apply_constraints(
        sections: dict[str, str], metadata: dict[str, Any], config: dict[str, Any]
    ) -> None:
        """Apply constraints from frontmatter only (following Spec vs Character philosophy)."""
        # SPEC fields like constraints should ONLY come from frontmatter
        # This ensures structured data and prevents constraints from being buried in prose
        if "constraints" in metadata:
            constraints = metadata.get("constraints", [])
            if isinstance(constraints, list):
                config["constraints"] = constraints
            else:
                raise ValueError(f"Constraints in metadata must be a list, got {type(constraints)}")
        # Note: We intentionally ignore any # Constraints sections in the markdown body
        # to maintain the Spec vs Character separation

    @staticmethod
    def _validate_required_fields(config: dict[str, Any]) -> None:
        """Validate that all required fields are present for markdown personas."""
        errors = []

        # SPEC fields (must be in frontmatter)
        if not config.get("role"):
            errors.append("'role' is required in frontmatter")
        if not config.get("goal"):
            errors.append("'goal' is required in frontmatter")
        # Note: constraints can be missing (defaults to empty list)

        # CHARACTER fields (must be in markdown content)
        if not config.get("backstory", "").strip():
            errors.append("'# Backstory' section is required in markdown content")

        if errors:
            persona_name = config.get("name", "unknown")
            error_msg = f"Required fields missing for persona '{persona_name}':\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

    @staticmethod
    def _parse_markdown_sections(content: str) -> dict[str, str]:
        """
        Parse Markdown content into sections based on headers.

        Supports both # and ## level headers.

        Args:
            content: Markdown content to parse

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        current_section = None
        current_content: list[str] = []

        # Compile regex once for better performance
        header_pattern = re.compile(r"^#{1,2}\s+(.+)$")

        # Single pass through lines for better performance
        for line in content.splitlines():
            header_match = header_pattern.match(line.strip())

            if header_match:
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = header_match.group(1).lower().replace(" ", "_")
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections
