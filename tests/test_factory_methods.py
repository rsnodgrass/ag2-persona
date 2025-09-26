"""Tests for PersonaBuilder factory methods."""

import tempfile
from pathlib import Path

from ag2_persona import PersonaBuilder


def test_from_markdown_factory_basic():
    """Test the factory method loads from markdown correctly."""
    markdown_content = """---
name: test_agent
role: Test Agent Role
goal: Test agent goal
llm_config:
  model: gpt-4
  temperature: 0.5
---

# Backstory
Experienced test agent with comprehensive testing knowledge.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        assert builder.name == "test_agent"
        assert builder._role == "Test Agent Role"
        assert builder._goal == "Test agent goal"
        assert isinstance(builder._llm_config, dict)
        assert builder._llm_config["model"] == "gpt-4"
    finally:
        temp_path.unlink()


def test_from_markdown_filename_fallback():
    """Test that filename is used when no name in metadata."""
    markdown_content = """---
role: Senior Developer
goal: Write clean code
---

# Backstory
Senior Developer with extensive experience building applications.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path)

        # should use filename without extension
        assert builder.name == temp_path.stem
        assert builder._role == "Senior Developer"
    finally:
        temp_path.unlink()


def test_from_markdown_name_override():
    """Test name parameter overrides file name."""
    markdown_content = """---
name: file_name
role: Developer
goal: Code
---

# Backstory
Experienced developer with coding expertise.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        # Name override via set_name method
        builder = PersonaBuilder.from_markdown(temp_path).set_name("override_name")

        assert builder.name == "override_name"  # override wins
        assert builder._role == "Developer"
    finally:
        temp_path.unlink()


def test_name_method_chaining():
    """Test .name() method works with factory methods."""
    markdown_content = """---
name: original
role: Developer
goal: Original goal
---

# Backstory
Experienced developer with extensive knowledge.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = PersonaBuilder.from_markdown(temp_path).set_name("chained_name").goal("New goal")

        assert builder.name == "chained_name"
        assert builder._role == "Developer"
        assert builder._goal == "New goal"
    finally:
        temp_path.unlink()


def test_complex_chaining_example():
    """Test complex chaining with factory method."""
    markdown_content = """---
role: Assistant
goal: Help users
llm_config:
  model: gpt-3.5-turbo
---

# Backstory
Helpful assistant with extensive experience in user support.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        builder = (
            PersonaBuilder.from_markdown(temp_path)
            .set_name("enhanced_assistant")
            .extend_goal("with detailed explanations")
            .add_constraint("Always be helpful")
            .temperature(0.2)
        )

        assert builder.name == "enhanced_assistant"
        assert builder._goal and "with detailed explanations" in builder._goal
        assert "Always be helpful" in builder._constraints
        expected_temperature = 0.2
        assert isinstance(builder._llm_config, dict)
        assert builder._llm_config["temperature"] == expected_temperature
        assert builder._llm_config["model"] == "gpt-3.5-turbo"  # from file
    finally:
        temp_path.unlink()


def test_name_priority_order():
    """Test the exact priority order for name resolution."""
    markdown_content = """---
name: metadata_name
role: Test Role
goal: Test goal
---

# Backstory
Test persona with comprehensive experience.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, prefix="filename_") as f:
        f.write(markdown_content)
        temp_path = Path(f.name)

    try:
        # 1. Parameter override beats everything
        # 1. Factory method with override not supported in current simple API
        # builder1 = PersonaBuilder.from_markdown(temp_path, name="param_override")
        # assert builder1.name == "param_override"

        # 2. Metadata name beats filename
        builder2 = PersonaBuilder.from_markdown(temp_path)
        assert builder2.name == "metadata_name"

        # 3. Test filename fallback (no metadata name) - this will fail validation now
        markdown_no_name = """---
role: Test Role
goal: Test goal
---

# Backstory
Fallback test persona.
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, prefix="fallback_"
        ) as f2:
            f2.write(markdown_no_name)
            temp_path2 = Path(f2.name)

        builder3 = PersonaBuilder.from_markdown(temp_path2)
        assert builder3.name and builder3.name.startswith("fallback_")  # filename without extension

        temp_path2.unlink()

    finally:
        temp_path.unlink()
