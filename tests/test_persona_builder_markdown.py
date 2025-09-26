"""Tests for PersonaBuilder from_markdown functionality."""

import tempfile
from pathlib import Path

import pytest

from ag2_persona import PersonaBuilder


def test_from_markdown_basic():
    """Test loading a basic markdown persona file."""
    markdown_content = """---
name: test_agent
llm_config:
  model: gpt-4
  temperature: 0.5
role: Test Agent Role
goal: Test agent goal
constraints:
  - First constraint
  - Second constraint
---

# Backstory
Test agent backstory with comprehensive knowledge and experience.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        # verify builder properties without building agent (to avoid OpenAI client creation)
        assert builder.name == "test_agent"
        assert builder._role == "Test Agent Role"
        assert builder._goal == "Test agent goal"
        assert "Test agent backstory" in builder._backstory
        expected_constraints_count = 2
        expected_temperature = 0.5
        assert len(builder._constraints) == expected_constraints_count
        assert "First constraint" in builder._constraints
        assert "Second constraint" in builder._constraints
        assert isinstance(builder._llm_config, dict)
        assert builder._llm_config["model"] == "gpt-4"
        assert builder._llm_config["temperature"] == expected_temperature
    finally:
        temp_path.unlink()


def test_from_markdown_no_frontmatter():
    """Test loading markdown without frontmatter (should fail validation)."""
    markdown_content = """# Backstory
Experienced developer with 10 years experience

Some additional narrative content.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Required fields missing"):
            PersonaBuilder.from_markdown(temp_path)
    finally:
        temp_path.unlink()


def test_markdown_required_fields_validation():
    """Test that required fields (role, goal, backstory) are validated when loading from markdown."""

    # Test missing role - should fail
    markdown_content = """---
goal: Test goal
---

# Backstory
Some backstory
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'role' is required in frontmatter"):
            PersonaBuilder.from_markdown(temp_path)
    finally:
        temp_path.unlink()

    # Test missing backstory - should fail
    markdown_content = """---
role: Test Role
goal: Test goal
---

# Some Other Section
Not a backstory
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        with pytest.raises(
            ValueError, match="'# Backstory' section is required in markdown content"
        ):
            PersonaBuilder.from_markdown(temp_path)
    finally:
        temp_path.unlink()

    # Test missing constraints - should pass (defaults to empty list)
    markdown_content = """---
role: Test Role
goal: Test goal
---

# Backstory
Valid backstory
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)
        assert not builder._constraints  # Missing constraints default to empty list
    finally:
        temp_path.unlink()


def test_from_markdown_metadata_override():
    """Test overriding metadata from frontmatter."""
    markdown_content = """---
role: Data Scientist
goal: Analyze data
llm_config:
  model: gpt-3.5-turbo
  temperature: 0.7
custom_field: original_value
---

# Backstory
Experienced data scientist with expertise in machine learning.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        override = {
            "llm_config": {"model": "gpt-4", "temperature": 0.3, "max_tokens": 1000},
            "custom_field": "overridden_value",
        }

        builder = PersonaBuilder.from_markdown(temp_path, override_metadata=override)

        expected_temperature = 0.3
        expected_max_tokens = 1000
        assert isinstance(builder._llm_config, dict)
        assert builder._llm_config["model"] == "gpt-4"
        assert builder._llm_config["temperature"] == expected_temperature
        assert builder._llm_config["max_tokens"] == expected_max_tokens
        assert builder.additional_kwargs["custom_field"] == "overridden_value"
    finally:
        temp_path.unlink()


def test_from_markdown_mixed_source():
    """Test Spec vs Character separation: spec in frontmatter, character in content."""
    markdown_content = """---
role: Architect from metadata
goal: Design scalable systems
constraints:
  - Performance first
  - Security always
---

# Backstory
Senior architect with deep experience in distributed systems.
Built platforms serving millions of users.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        assert builder._role == "Architect from metadata"  # SPEC: from frontmatter
        assert builder._goal == "Design scalable systems"  # SPEC: from frontmatter
        assert (
            "Senior architect with deep experience" in builder._backstory
        )  # CHARACTER: from markdown
        expected_constraints_count = 2
        assert len(builder._constraints) == expected_constraints_count  # SPEC: from frontmatter
        assert "Performance first" in builder._constraints
        assert "Security always" in builder._constraints
    finally:
        temp_path.unlink()


def test_from_markdown_additional_kwargs():
    """Test that additional metadata fields are stored as kwargs."""
    markdown_content = """---
role: Assistant
goal: Help users
human_input_mode: NEVER
max_consecutive_auto_reply: 10
---

# Backstory
Helpful assistant with extensive experience in user support.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        assert builder.additional_kwargs["human_input_mode"] == "NEVER"
        expected_max_replies = 10
        assert builder.additional_kwargs["max_consecutive_auto_reply"] == expected_max_replies
    finally:
        temp_path.unlink()


def test_from_markdown_description_section():
    """Test parsing description from markdown sections."""
    markdown_content = """---
name: expert
role: Domain Expert
goal: Provide expert advice
---

# Backstory
Experienced domain expert with comprehensive knowledge.

# Description
Expert in multiple domains with deep knowledge
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        assert builder._description == "Expert in multiple domains with deep knowledge"
    finally:
        temp_path.unlink()


def test_from_markdown_file_not_found():
    """Test error handling for missing file."""
    builder = PersonaBuilder("test")

    with pytest.raises(FileNotFoundError, match="Persona Markdown file not found"):
        builder.from_markdown("non_existent_file.md")


def test_from_markdown_invalid_yaml():
    """Test error handling for invalid YAML frontmatter."""
    markdown_content = """---
invalid yaml: [unclosed
---

# Role
Test
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Error parsing frontmatter"):
            PersonaBuilder.from_markdown(temp_path)
    finally:
        temp_path.unlink()


def test_from_markdown_empty_file():
    """Test handling of empty markdown file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("")
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Required fields missing"):
            PersonaBuilder.from_markdown(temp_path)
    finally:
        temp_path.unlink()


def test_from_markdown_multiline_sections():
    """Test parsing multiline backstory content."""
    markdown_content = """---
role: Senior Software Engineer with Full Stack Expertise
goal: Build robust applications that scale to millions of users and maintain high availability
constraints:
  - Follow best practices
  - Write comprehensive tests
---

# Backstory
Started as a junior developer in 2010.
Worked at several startups and big tech companies.

Has experience with:
- Python and Django
- JavaScript and React
- Cloud infrastructure

Published multiple open source projects.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        assert builder._role and "Full Stack Expertise" in builder._role  # SPEC: from frontmatter
        assert builder._goal and "millions of users" in builder._goal  # SPEC: from frontmatter
        assert "open source projects" in builder._backstory  # CHARACTER: from markdown
    finally:
        temp_path.unlink()


def test_from_markdown_constraints_formats():
    """Test constraint formatting in frontmatter (SPEC fields only)."""
    markdown_content = """---
role: Tester
goal: Test software
constraints:
  - Constraint with dash format
  - Another valid constraint
  - Third constraint for testing
---

# Backstory
Experienced tester with deep knowledge of quality assurance.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        expected_constraints_count = 3
        assert len(builder._constraints) == expected_constraints_count  # SPEC: from frontmatter
        assert "Constraint with dash format" in builder._constraints
        assert "Another valid constraint" in builder._constraints
        assert "Third constraint for testing" in builder._constraints
    finally:
        temp_path.unlink()
