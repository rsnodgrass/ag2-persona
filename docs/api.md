# API Reference

Welcome to the AG2 PersonaAgent API documentation. This guide provides comprehensive information about all classes and methods available in the library.

!!! tip "Quick Start"
    New to AG2 PersonaAgent? Check out our [Getting Started](getting-started.md) guide first, then return here for detailed API information.

## Overview

AG2 PersonaAgent extends AG2's `ConversableAgent` to enable agents with distinct personas. The main components are:

- **PersonaAgent**: The core agent class that embodies a persona
- **PersonaBuilder**: Synchronous builder for creating personas from structured data
- **AsyncPersonaBuilder**: Asynchronous version of the builder for file-based operations

## Core Classes

### PersonaAgent

The `PersonaAgent` class is the heart of this library, extending AG2's `ConversableAgent` with persona capabilities.

!!! example "Basic Usage"
    ```python
    from ag2_persona import PersonaAgent

    # Create a persona agent
    agent = PersonaAgent(
        name="DataScientist",
        role="Senior Data Scientist",
        goal="Analyze data to provide actionable business insights",
        backstory="Expert with 8+ years in machine learning and statistics",
        llm_config={"model": "gpt-4"}
    )
    ```

::: ag2_persona.PersonaAgent
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

---

### PersonaBuilder

The `PersonaBuilder` class provides a convenient way to create `PersonaAgent` instances from structured data formats like YAML and Markdown.

!!! info "Supported Formats"
    - **YAML**: Standard YAML with frontmatter
    - **Markdown**: Markdown files with YAML frontmatter
    - **Dict**: Python dictionaries with persona data

!!! example "Creating from YAML"
    ```python
    from ag2_persona import PersonaBuilder

    yaml_content = """
    name: "TechExpert"
    role: "Technology Consultant"
    goal: "Help businesses adopt new technologies"
    backstory: "Former CTO with deep technical expertise"
    """

    builder = PersonaBuilder()
    agent = builder.from_yaml(yaml_content, llm_config={"model": "gpt-4"})
    ```

::: ag2_persona.PersonaBuilder
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

---

### AsyncPersonaBuilder

The `AsyncPersonaBuilder` class provides asynchronous methods for building personas, particularly useful when loading from files or external sources.

!!! warning "Async Context Required"
    This class requires an async context to use. Make sure to use `await` with its methods.

!!! example "Loading from File"
    ```python
    import asyncio
    from ag2_persona import AsyncPersonaBuilder

    async def create_agent():
        builder = AsyncPersonaBuilder()
        agent = await builder.from_file(
            "personas/consultant.md",
            llm_config={"model": "gpt-4"}
        )
        return agent

    agent = asyncio.run(create_agent())
    ```

::: ag2_persona.AsyncPersonaBuilder
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

## Data Structures

### Persona Format

Personas can be defined using the following structure:

```yaml
name: "AgentName"           # Required: Agent identifier
role: "Agent Role"          # Required: What the agent does
goal: "Agent Objective"     # Required: Agent's primary goal
backstory: "Agent History"  # Required: Agent's background/expertise
system_message: "Custom system message"  # Optional: Override default
description: "Brief description"         # Optional: Agent description
```

!!! note "Required Fields"
    The `name`, `role`, `goal`, and `backstory` fields are required for all personas. The library will raise a validation error if any are missing.

### LLM Configuration

When creating agents, you'll need to provide an `llm_config` parameter. This follows AG2's standard configuration format:

=== "OpenAI"
    ```python
    llm_config = {
        "model": "gpt-4",
        "api_key": "your-api-key",  # or set OPENAI_API_KEY env var
        "temperature": 0.7
    }
    ```

=== "Azure OpenAI"
    ```python
    llm_config = {
        "model": "gpt-4",
        "api_type": "azure",
        "api_base": "https://your-endpoint.openai.azure.com/",
        "api_key": "your-api-key",
        "api_version": "2023-05-15"
    }
    ```

=== "Local Models"
    ```python
    llm_config = {
        "model": "llama2",
        "api_base": "http://localhost:11434/v1",
        "api_key": "ollama"  # placeholder for local models
    }
    ```

## Error Handling

The library provides specific exceptions for different error conditions:

```python
from ag2_persona import PersonaBuilder

try:
    builder = PersonaBuilder()
    agent = builder.from_yaml(invalid_yaml, llm_config=config)
except ValueError as e:
    print(f"Invalid persona data: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

!!! tip "Best Practices"
    - Always validate your persona data before creating agents
    - Use try/except blocks when loading from external sources
    - Check the logs for detailed error information

## Integration with AG2

`PersonaAgent` is fully compatible with AG2's ecosystem:

```python
from ag2_persona import PersonaAgent
from autogen import GroupChat, GroupChatManager

# Create persona agents
analyst = PersonaAgent(
    name="DataAnalyst",
    role="Data Analyst",
    goal="Extract insights from data",
    backstory="Statistics expert with business acumen",
    llm_config=llm_config
)

consultant = PersonaAgent(
    name="BusinessConsultant",
    role="Business Consultant",
    goal="Provide strategic business advice",
    backstory="Former McKinsey partner with 15 years experience",
    llm_config=llm_config
)

# Use in AG2 GroupChat
groupchat = GroupChat(
    agents=[analyst, consultant],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
```

!!! success "Full AG2 Compatibility"
    PersonaAgent inherits from `ConversableAgent`, so it works seamlessly with all AG2 features including GroupChat, function calling, and custom workflows.
