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
async def test_async_from_yaml():
    """Test AsyncPersonaBuilder.from_yaml functionality."""
    yaml_content = """
role: "Software Engineer"
goal: "Write clean, maintainable code"
backstory: "Senior developer with 10 years experience"
constraints:
  - "Follow coding standards"
  - "Write comprehensive tests"
"""

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    try:
        agent = await AsyncPersonaBuilder("engineer").from_yaml(yaml_path).llm_config(False).build()

        assert agent.role == "Software Engineer"
        assert agent.goal == "Write clean, maintainable code"
        assert agent.backstory == "Senior developer with 10 years experience"
        assert agent.constraints == ["Follow coding standards", "Write comprehensive tests"]
    finally:
        Path(yaml_path).unlink()


@pytest.mark.asyncio
async def test_async_method_chaining():
    """Test true fluent async method chaining with deferred execution."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write('role: "Test Role"\ngoal: "Test Goal"')
        yaml_path = f.name

    try:
        # Test true fluent async method chaining
        agent = await (
            AsyncPersonaBuilder("chained")
            .from_yaml(yaml_path)
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
    finally:
        Path(yaml_path).unlink()


@pytest.mark.asyncio
async def test_async_validation_errors():
    """Test AsyncPersonaBuilder validation with async build."""
    builder = AsyncPersonaBuilder("incomplete")

    # Should fail validation - missing role and goal
    with pytest.raises(ValueError, match="Role is required"):
        await builder.build()


@pytest.mark.asyncio
async def test_async_file_not_found():
    """Test AsyncPersonaBuilder with non-existent YAML file."""
    with pytest.raises(FileNotFoundError):
        await AsyncPersonaBuilder("missing").from_yaml("non_existent_file.yaml").build()


@pytest.mark.asyncio
async def test_async_invalid_yaml():
    """Test AsyncPersonaBuilder with invalid YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content: [")  # Invalid YAML
        yaml_path = f.name

    try:
        with pytest.raises(ValueError, match="Error loading YAML"):
            await AsyncPersonaBuilder("invalid").from_yaml(yaml_path).build()
    finally:
        Path(yaml_path).unlink()


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
    """Test AsyncPersonaBuilder kwargs functionality."""
    agent = await (
        AsyncPersonaBuilder("kwargs_test")
        .role("Test Role")
        .goal("Test Goal")
        .kwargs(is_termination_msg=lambda x: x.get("content", "").strip() == "DONE")
        .llm_config(False)
        .build()
    )

    # Test that kwargs are passed through (termination function should be set)
    assert agent._is_termination_msg is not None
