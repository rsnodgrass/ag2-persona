"""
Test cases for AsyncPersonaBuilder async functionality.
"""

import tempfile
from pathlib import Path

import pytest

from ag2_persona import AsyncPersonaBuilder


@pytest.mark.asyncio
async def test_async_basic_builder():
    """Test basic AsyncPersonaBuilder functionality with fluent syntax."""
    agent = await (
        AsyncPersonaBuilder("test_agent")
        .role("Test Role")
        .goal("Test Goal")
        .llm_config(False)  # Disable LLM for testing
        .build()
    )

    assert agent.name == "test_agent"
    assert agent.role == "Test Role"
    assert agent.goal == "Test Goal"


@pytest.mark.asyncio
async def test_async_from_dict():
    """Test AsyncPersonaBuilder.from_dict functionality."""
    config = {
        "role": "Data Analyst",
        "goal": "Analyze data efficiently",
        "backstory": "Expert in data analysis",
        "constraints": ["Focus on accuracy", "Provide visualizations"],
    }

    agent = await AsyncPersonaBuilder("analyst").from_dict(config).llm_config(False).build()

    assert agent.role == "Data Analyst"
    assert agent.goal == "Analyze data efficiently"
    assert agent.backstory == "Expert in data analysis"
    assert agent.constraints == ["Focus on accuracy", "Provide visualizations"]


@pytest.mark.asyncio
async def test_async_from_markdown():
    """Test AsyncPersonaBuilder.from_markdown functionality."""
    # Create temporary Markdown file following Spec vs Character philosophy
    markdown_content = """---
name: software_engineer
role: Senior Software Engineer
goal: Write clean, maintainable code
constraints:
  - Follow coding standards
  - Write comprehensive tests
llm_config:
  model: gpt-4
  temperature: 0.3
---

# Backstory
Senior developer with 10 years experience in building scalable applications.
Strong advocate for clean code and test-driven development.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        md_path = f.name

    try:
        agent = await AsyncPersonaBuilder("test").from_markdown(md_path).llm_config(False).build()

        assert agent.name == "test"  # Builder name takes precedence
        assert agent.role == "Senior Software Engineer"
        assert agent.goal == "Write clean, maintainable code"
        assert "Senior developer with 10 years experience" in agent.backstory
        assert agent.constraints == ["Follow coding standards", "Write comprehensive tests"]
    finally:
        Path(md_path).unlink()


@pytest.mark.asyncio
async def test_async_from_markdown_with_name_resolution():
    """Test AsyncPersonaBuilder name resolution with from_markdown."""
    # Create temporary Markdown file with SPEC in frontmatter
    markdown_content = """---
name: engineer_from_file
role: Engineer
goal: Build software
constraints: []
---

# Backstory
Experienced engineer who loves building software solutions.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown_content)
        md_path = f.name

    try:
        # Test: Builder with temp name, should use name from file
        agent = await AsyncPersonaBuilder("temp").from_markdown(md_path).llm_config(False).build()
        assert agent.name == "temp"  # Builder name takes precedence

        # Test: Using filename stem when no name in frontmatter
        md_no_name = """---
role: Engineer
goal: Build software
---

# Backstory
Experienced engineer with strong technical skills."""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f2:
            f2.write(md_no_name)
            md_path2 = f2.name

        try:
            agent3 = (
                await AsyncPersonaBuilder("test").from_markdown(md_path2).llm_config(False).build()
            )
            assert agent3.name == "test"  # Builder name still takes precedence
        finally:
            Path(md_path2).unlink()
    finally:
        Path(md_path).unlink()


@pytest.mark.asyncio
async def test_async_method_chaining():
    """Test true fluent async method chaining with basic configuration."""
    # Test true fluent async method chaining
    agent = await (
        AsyncPersonaBuilder("chained")
        .role("Test Role")
        .goal("Test Goal")
        .backstory("Test backstory")
        .add_constraint("Test constraint")
        .llm_config(False)  # Disable LLM for testing
        .description("Test description")
        .human_input_never()
        .build()
    )

    assert agent.name == "chained"
    assert agent.role == "Test Role"
    assert agent.goal == "Test Goal"
    assert agent.backstory == "Test backstory"
    assert agent.constraints == ["Test constraint"]
    # LLM is disabled, no need to test temperature and model
    assert agent.description == "Test description"
    assert agent.human_input_mode == "NEVER"


@pytest.mark.asyncio
async def test_async_validation_errors():
    """Test AsyncPersonaBuilder validation with async build."""
    builder = AsyncPersonaBuilder("incomplete")

    # Should fail validation - missing role and goal
    with pytest.raises(ValueError, match="Role is required"):
        await builder.build()


@pytest.mark.asyncio
async def test_async_invalid_constraints():
    """Test AsyncPersonaBuilder with invalid constraints type."""
    config = {
        "role": "Test Role",
        "goal": "Test Goal",
        "constraints": "should be a list",  # Invalid - string instead of list
    }

    with pytest.raises(ValueError, match="Constraints must be a list"):
        await AsyncPersonaBuilder("test").from_dict(config).build()


@pytest.mark.asyncio
async def test_async_extend_goal():
    """Test AsyncPersonaBuilder extend_goal functionality."""
    agent = await (
        AsyncPersonaBuilder("extender")
        .role("Test Role")
        .goal("Original goal")
        .extend_goal("additional requirements")
        .llm_config(False)
        .build()
    )

    assert "Original goal. Additionally, additional requirements" in agent.goal


@pytest.mark.asyncio
async def test_async_human_input_modes():
    """Test all human input mode methods."""
    builder = AsyncPersonaBuilder("human_input_test")

    # Test ALWAYS mode
    agent = await (
        builder.role("Test Role").goal("Test Goal").human_input_always().llm_config(False).build()
    )
    assert agent.human_input_mode == "ALWAYS"

    # Test TERMINATE mode
    agent = await (
        AsyncPersonaBuilder("human_input_test2")
        .role("Test Role")
        .goal("Test Goal")
        .human_input_terminate()
        .llm_config(False)
        .build()
    )
    assert agent.human_input_mode == "TERMINATE"


@pytest.mark.asyncio
async def test_async_with_kwargs():
    """Test AsyncPersonaBuilder add_kwargs functionality."""
    agent = await (
        AsyncPersonaBuilder("kwargs_test")
        .role("Test Role")
        .goal("Test Goal")
        .add_kwargs(is_termination_msg=lambda x: x.get("content", "").strip() == "DONE")
        .llm_config(False)
        .build()
    )

    # Test that kwargs are passed through (termination function should be set)
    from ag2_persona.persona_agent import AG2_AVAILABLE

    # Check for termination message attribute based on AG2 availability
    if AG2_AVAILABLE:
        # Real AG2 ConversableAgent stores it as _is_termination_msg
        assert hasattr(agent, "_is_termination_msg")
        assert agent._is_termination_msg is not None
    else:
        # Mock ConversableAgent stores kwargs directly
        assert hasattr(agent, "is_termination_msg")
        assert agent.is_termination_msg is not None
