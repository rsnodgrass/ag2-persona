"""Tests for PersonaBuilder from_markdown functionality."""

import tempfile
from pathlib import Path

import pytest

from ag2_persona import PersonaAgent, PersonaBuilder


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


def test_extensible_metadata_frontmatter():
    """Test extensible metadata field in frontmatter."""
    markdown_content = """---
role: Data Scientist
goal: Analyze data
llm_config:
  model: gpt-3.5-turbo
  temperature: 0.7
metadata:
  audit_info:
    created_by: "user@example.com"
    project: "earnings_analysis"
  custom_field: "original_value"
  nested_data:
    key1: "value1"
    key2: 42
---

# Backstory
Experienced data scientist with expertise in machine learning.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        # Core fields should be set correctly
        assert builder._role == "Data Scientist"
        assert builder._goal == "Analyze data"
        assert isinstance(builder._llm_config, dict)
        assert builder._llm_config["model"] == "gpt-3.5-turbo"
        assert builder._llm_config["temperature"] == 0.7

        # Extensible metadata should be in _metadata
        assert "audit_info" in builder._metadata
        assert builder._metadata["audit_info"]["created_by"] == "user@example.com"
        assert builder._metadata["audit_info"]["project"] == "earnings_analysis"
        assert builder._metadata["custom_field"] == "original_value"
        assert builder._metadata["nested_data"]["key1"] == "value1"
        assert builder._metadata["nested_data"]["key2"] == 42

        # Note: Unknown frontmatter keys outside metadata are now ignored for security
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


def test_with_markdown_in_memory():
    """Test the with_markdown method for in-memory markdown content."""
    markdown_content = """---
name: memory_agent
role: Memory Test Agent
goal: Test in-memory markdown processing
llm_config:
  model: gpt-4
  temperature: 0.2
---

# Backstory
Agent loaded from in-memory markdown content for testing purposes.
"""

    builder = PersonaBuilder().with_markdown(markdown_content)

    assert builder.name == "memory_agent"
    assert builder._role == "Memory Test Agent"
    assert builder._goal == "Test in-memory markdown processing"
    assert "in-memory markdown content" in builder._backstory
    assert isinstance(builder._llm_config, dict)
    assert builder._llm_config["model"] == "gpt-4"
    expected_temperature = 0.2
    assert builder._llm_config["temperature"] == expected_temperature


def test_with_markdown_file():
    """Test the with_markdown_file method."""
    markdown_content = """---
name: file_agent
role: File Test Agent
goal: Test file-based markdown processing
constraints:
  - Test constraint one
  - Test constraint two
---

# Backstory
Agent loaded from file using with_markdown_file method.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder().with_markdown_file(temp_path)

        assert builder.name == "file_agent"
        assert builder._role == "File Test Agent"
        assert builder._goal == "Test file-based markdown processing"
        assert "with_markdown_file method" in builder._backstory
        expected_constraints_count = 2
        assert len(builder._constraints) == expected_constraints_count
        assert "Test constraint one" in builder._constraints
        assert "Test constraint two" in builder._constraints
    finally:
        temp_path.unlink()


def test_with_markdown_file_uses_filename_as_name():
    """Test that with_markdown_file uses the filename as name when name is not set."""
    markdown_content = """---
role: File Agent
goal: Test filename as name
---

# Backstory
Testing automatic name assignment from filename.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder().with_markdown_file(temp_path)
        # Name should be derived from the temp file name (without extension)
        assert builder.name == temp_path.stem
        assert builder._role == "File Agent"
        assert builder._goal == "Test filename as name"
    finally:
        temp_path.unlink()


def test_with_markdown_chaining():
    """Test that with_markdown supports method chaining."""
    markdown_content = """---
role: Chainable Agent
goal: Test method chaining
---

# Backstory
Testing method chaining capabilities.
"""

    builder = (
        PersonaBuilder("chain_test")
        .with_markdown(markdown_content)
        .temperature(0.8)
        .add_constraint("Additional constraint")
    )

    assert builder.name == "chain_test"
    assert builder._role == "Chainable Agent"
    assert builder._goal == "Test method chaining"
    assert "method chaining" in builder._backstory
    assert isinstance(builder._llm_config, dict)
    expected_temperature = 0.8
    assert builder._llm_config["temperature"] == expected_temperature
    assert "Additional constraint" in builder._constraints


def test_with_markdown_content_direct():
    """Test with_markdown with content that has the desired values directly."""
    markdown_content = """---
role: Override Agent
goal: Overridden goal
llm_config:
  model: gpt-4
  temperature: 0.1
  max_tokens: 2000
---

# Backstory
Testing direct content functionality.
"""

    builder = PersonaBuilder().with_markdown(markdown_content)

    assert builder._role == "Override Agent"
    assert builder._goal == "Overridden goal"
    assert isinstance(builder._llm_config, dict)
    assert builder._llm_config["model"] == "gpt-4"
    expected_temperature = 0.1
    expected_max_tokens = 2000
    assert builder._llm_config["temperature"] == expected_temperature
    assert builder._llm_config["max_tokens"] == expected_max_tokens


def test_version_tracking():
    """Test that version is properly tracked from frontmatter."""
    markdown_content = """---
name: versioned_agent
role: Version Test Agent
goal: Test version tracking
version: "2024-09-26"
---

# Backstory
Agent for testing persona version tracking functionality.
"""

    builder = PersonaBuilder().with_markdown(markdown_content)

    assert builder.name == "versioned_agent"
    assert builder._version == "2024-09-26"


def test_version_from_frontmatter_only():
    """Test that version can only be set from frontmatter."""
    # Test that version can only come from frontmatter, not builder methods
    markdown_content = """---
name: version_test_agent
role: Test Role
goal: Test Goal
version: "2025-01-15"
---

# Backstory
Test backstory
"""

    builder = PersonaBuilder().with_markdown(markdown_content)
    assert builder._version == "2025-01-15"

    # Test that no builder method exists to set version
    assert not hasattr(builder, "version")


def test_version_in_agent_serialization():
    """Test that version is included in agent serialization."""
    markdown_content = """---
name: serialization_agent
role: Serialization Test Agent
goal: Test version in serialization
version: "2024-12-03"
---

# Backstory
Agent for testing persona version in serialization.
"""

    builder = PersonaBuilder().with_markdown(markdown_content)

    # Test that version is preserved in builder
    assert builder._version == "2024-12-03"

    # Test that version is passed to agent (we'll build without LLM config to avoid client issues)
    builder._llm_config = False  # Disable LLM for testing
    agent = builder.build()

    # Test that version is stored in agent
    assert agent.version == "2024-12-03"

    # Test that version is included in serialization
    agent_dict = agent.to_dict()
    assert agent_dict["version"] == "2024-12-03"


def test_version_none_handling():
    """Test that missing version defaults to today's date."""
    from datetime import date

    markdown_content = """---
name: no_version_agent
role: No Version Agent
goal: Test no version handling
---

# Backstory
Agent without version for testing default date handling.
"""

    builder = PersonaBuilder().with_markdown(markdown_content)

    # Test that version defaults to today's date when not specified
    expected_date = date.today().strftime("%Y-%m-%d")
    assert builder._version == expected_date

    # Test that default version is handled in agent
    builder._llm_config = False  # Disable LLM for testing
    agent = builder.build()
    assert agent.version == expected_date

    # Test that default version is included in serialization
    agent_dict = agent.to_dict()
    assert agent_dict["version"] == expected_date


def test_version_from_dict():
    """Test that version is loaded from dictionary configuration."""
    config_dict = {
        "name": "dict_agent",
        "role": "Dict Test Agent",
        "goal": "Test dict loading",
        "backstory": "Test backstory",
        "version": "2025-03-14",
    }

    builder = PersonaBuilder().from_dict(config_dict)

    assert builder._version == "2025-03-14"


def test_version_immutable_from_frontmatter():
    """Test that version is set from frontmatter and is immutable."""
    import tempfile
    from pathlib import Path

    markdown_content = """---
name: update_version_agent
role: Update Version Agent
goal: Test version update
version: "2024-08-15"
---

# Backstory
Agent for testing version update functionality.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        # Load file - version should come from frontmatter and be immutable
        builder = PersonaBuilder().with_markdown_file(temp_path)
        assert builder._version == "2024-08-15"  # from frontmatter, immutable

        # Metadata can track additional version info
        builder.update_metadata(
            {"version_history": ["2024-08-15", "2024-09-26"], "last_updated_by": "user@example.com"}
        )
        assert builder._metadata["version_history"] == ["2024-08-15", "2024-09-26"]
    finally:
        temp_path.unlink()


def test_version_semantic_example():
    """Test that semantic versions still work (for backwards compatibility)."""
    markdown_content = """---
name: semantic_version_agent
role: Semantic Version Agent
goal: Test semantic version compatibility
version: "1.2.3"
---

# Backstory
Agent for testing semantic version compatibility.
"""

    builder = PersonaBuilder().with_markdown(markdown_content)

    assert builder._version == "1.2.3"


def test_name_resolution_consistency():
    """Test that both with_markdown and with_markdown_file have consistent name resolution behavior."""

    # Test 1: Both methods should use frontmatter name when available
    markdown_with_name = """---
name: frontmatter_agent
role: Test Agent
goal: Test name resolution
---

# Backstory
Testing name resolution.
"""

    builder1 = PersonaBuilder().with_markdown(markdown_with_name)
    assert builder1.name == "frontmatter_agent"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_with_name)
        temp_path = Path(f.name)

    try:
        builder2 = PersonaBuilder().with_markdown_file(temp_path)
        assert builder2.name == "frontmatter_agent"
    finally:
        temp_path.unlink()


def test_name_resolution_fallback_behavior():
    """Test fallback behavior when name is missing."""

    # Test 1: with_markdown should use default fallback when no name
    markdown_no_name = """---
role: No Name Agent
goal: Test fallback behavior
---

# Backstory
Testing fallback when no name is provided.
"""

    builder1 = PersonaBuilder().with_markdown(markdown_no_name)
    assert builder1.name == "unnamed_persona"

    # Test 2: with_markdown_file should use filename as fallback
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_no_name)
        temp_path = Path(f.name)

    try:
        builder2 = PersonaBuilder().with_markdown_file(temp_path)
        assert builder2.name == temp_path.stem  # Should use filename
    finally:
        temp_path.unlink()


def test_name_resolution_builder_name_priority():
    """Test that existing builder name has highest priority."""

    markdown_with_name = """---
name: frontmatter_agent
role: Test Agent
goal: Test name priority
---

# Backstory
Testing name priority.
"""

    # Test 1: with_markdown should use builder name over frontmatter
    builder1 = PersonaBuilder("builder_agent").with_markdown(markdown_with_name)
    assert builder1.name == "builder_agent"  # Builder name wins

    # Test 2: with_markdown_file should use builder name over frontmatter and filename
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_with_name)
        temp_path = Path(f.name)

    try:
        builder2 = PersonaBuilder("builder_agent").with_markdown_file(temp_path)
        assert builder2.name == "builder_agent"  # Builder name wins over frontmatter and filename
    finally:
        temp_path.unlink()


def test_name_resolution_update_metadata_behavior():
    """Test that update_metadata only handles extensible metadata blob, not core fields."""

    markdown_with_name = """---
name: frontmatter_agent
role: Test Agent
goal: Test goal
metadata:
  custom_field: original_value
---

# Backstory
Testing metadata behavior.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_with_name)
        temp_path = Path(f.name)

    try:
        # Test that update_metadata only updates extensible metadata, not core fields
        builder1 = (
            PersonaBuilder()
            .with_markdown_file(temp_path)
            .update_metadata(
                {
                    "name": "should_be_ignored",  # Core field should be ignored
                    "custom_field": "updated_value",  # Extensible metadata should update
                    "new_field": "new_value",  # New extensible metadata should be added
                }
            )
        )

        # Core field should remain unchanged
        assert builder1.name == "frontmatter_agent"

        # Extensible metadata should be updated
        assert builder1._metadata["custom_field"] == "updated_value"
        assert builder1._metadata["new_field"] == "new_value"

        # Test with existing builder name - same behavior
        builder2 = (
            PersonaBuilder("builder_agent")
            .with_markdown_file(temp_path)
            .update_metadata({"custom_field": "another_value"})
        )

        # Builder name should be preserved (has highest priority)
        assert builder2.name == "builder_agent"

        # Extensible metadata should be updated
        assert builder2._metadata["custom_field"] == "another_value"
    finally:
        temp_path.unlink()


def test_update_metadata_comprehensive():
    """Test comprehensive update_metadata functionality for extensible metadata only."""

    # Start with a basic builder
    builder = (
        PersonaBuilder("test_agent")
        .role("Initial Role")
        .goal("Initial Goal")
        .llm_config({"model": "gpt-3.5-turbo", "temperature": 0.5})
    )

    # Test updating extensible metadata only
    update_data = {
        "audit_info": {
            "created_by": "user@example.com",
            "last_modified": "2024-09-26",
            "version": "1.0",
        },
        "project_data": {"name": "financial_analysis", "id": 12345},
        "custom_field": "custom_value",
        "nested_config": {"level1": {"level2": "deep_value"}},
    }

    builder.update_metadata(update_data)

    # Core fields should remain unchanged
    assert builder.name == "test_agent"
    assert builder._role == "Initial Role"
    assert builder._goal == "Initial Goal"

    # Metadata should be updated
    assert builder._metadata["audit_info"]["created_by"] == "user@example.com"
    assert builder._metadata["audit_info"]["last_modified"] == "2024-09-26"
    assert builder._metadata["audit_info"]["version"] == "1.0"
    assert builder._metadata["project_data"]["name"] == "financial_analysis"
    assert builder._metadata["project_data"]["id"] == 12345
    assert builder._metadata["custom_field"] == "custom_value"
    assert builder._metadata["nested_config"]["level1"]["level2"] == "deep_value"


def test_update_metadata_validation():
    """Test update_metadata validation and error handling."""
    builder = PersonaBuilder("test")

    # Test invalid metadata type
    with pytest.raises(ValueError, match="Metadata must be a dictionary"):
        builder.update_metadata("not a dict")  # type: ignore[arg-type]

    # Test that metadata accepts any structure
    builder.update_metadata(
        {
            "any_field": "any_value",
            "nested": {"deeply": {"nested": "value"}},
            "list_data": [1, 2, 3],
            "none_value": None,
            "complex_structure": {"mixed": ["types", 42, True, None]},
        }
    )

    # All metadata should be accepted as-is
    assert builder._metadata["any_field"] == "any_value"
    assert builder._metadata["nested"]["deeply"]["nested"] == "value"
    assert builder._metadata["list_data"] == [1, 2, 3]
    assert builder._metadata["none_value"] is None
    assert builder._metadata["complex_structure"]["mixed"] == ["types", 42, True, None]


def test_persona_agent_metadata_api():
    """Test PersonaAgent metadata API methods."""

    # Create agent with initial metadata
    initial_metadata = {"created_at": "2024-09-26", "project": "test_project"}

    # Build agent with metadata
    builder = (
        PersonaBuilder("test_agent")
        .role("Test Role")
        .goal("Test Goal")
        .backstory("Test backstory")
        .update_metadata(initial_metadata)
    )

    # Disable LLM for testing
    builder._llm_config = False
    agent = builder.build()

    # Test metadata property returns copy
    metadata = agent.metadata
    assert metadata["created_at"] == "2024-09-26"
    assert metadata["project"] == "test_project"

    # Verify it's a copy (modifying returned dict doesn't affect agent)
    metadata["modified"] = True
    assert "modified" not in agent.metadata

    # Test update_metadata
    agent.update_metadata({"last_used": "2024-09-27", "usage_count": 5})

    # Verify updates were applied
    updated_metadata = agent.metadata
    assert updated_metadata["created_at"] == "2024-09-26"  # Original preserved
    assert updated_metadata["project"] == "test_project"  # Original preserved
    assert updated_metadata["last_used"] == "2024-09-27"  # New field
    assert updated_metadata["usage_count"] == 5  # New field

    # Test serialization includes metadata
    agent_dict = agent.to_dict()
    assert agent_dict["metadata"] == updated_metadata


def test_persona_agent_name_immutability():
    """Test that PersonaAgent names are immutable after construction."""

    # Create a PersonaAgent
    agent = PersonaAgent(
        name="test_agent", role="Test Role", goal="Test Goal", backstory="Test backstory"
    )

    # Verify name is accessible
    assert agent.name == "test_agent"

    # Verify that attempting to modify name raises AttributeError
    with pytest.raises(AttributeError, match="PersonaAgent name is immutable after construction"):
        agent.name = "modified_name"

    # Verify name remains unchanged after failed assignment attempt
    assert agent.name == "test_agent"

    # Test with PersonaBuilder as well
    builder_agent = (
        PersonaBuilder("builder_test")
        .role("Builder Role")
        .goal("Builder Goal")
        .backstory("Builder backstory")
        .build()
    )

    assert builder_agent.name == "builder_test"

    # Verify immutability on builder-created agent as well
    with pytest.raises(AttributeError, match="PersonaAgent name is immutable after construction"):
        builder_agent.name = "changed_name"

    assert builder_agent.name == "builder_test"


def test_version_missing_warning_and_default():
    """Test that missing version logs warning and defaults to today's date."""
    from datetime import date
    from unittest.mock import patch

    markdown_content = """---
name: no_version_agent
role: Test Role
goal: Test Goal
---

# Backstory
Test backstory without version
"""

    # Capture log messages
    with patch("ag2_persona.parsers.logging.warning") as mock_warning:
        builder = PersonaBuilder().with_markdown(markdown_content)

        # Verify warning was logged
        mock_warning.assert_called_once()
        warning_call = mock_warning.call_args[0][0]
        assert "Version key missing for persona 'no_version_agent'" in warning_call
        assert "Defaulting to today's date:" in warning_call

        # Verify version was set to today's date
        expected_date = date.today().strftime("%Y-%m-%d")
        assert builder._version == expected_date

        # Verify agent has the default version
        builder._llm_config = False  # Disable LLM for testing
        agent = builder.build()
        assert agent.version == expected_date
