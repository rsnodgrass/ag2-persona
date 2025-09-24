# AG2 PersonaAgent

Persona-based agents for AG2 (AutoGen) - enabling distinct character embodiment.

## Overview

PersonaAgent extends AG2's ConversableAgent to enable agents to embody distinct personas through role, goal, and backstory components. This allows for more authentic character representation and consistent behavior patterns.

## Key Features

- **🎭 Persona-Based Design**: Agents embody distinct roles with clear goals and backstories
- **🔧 Full AG2 Compatibility**: Drop-in replacement for ConversableAgent
- **⚡ Dynamic Configuration**: Update goals and constraints at runtime
- **📦 Type Safety**: Full type annotations and mypy compatibility
- **💾 Serializable**: Export/import agent configurations as dictionaries or YAML

## Quick Start

### Installation

```bash
pip install ag2-persona
```

### Basic Usage

```python
from ag2_persona import PersonaAgent

# Create a persona-based agent
agent = PersonaAgent(
    name="code_reviewer",
    role="Senior Software Engineer",
    goal="Review code for quality, security, and best practices",
    backstory="10+ years experience in Python development with expertise in secure coding practices",
    constraints=[
        "Focus on security vulnerabilities",
        "Suggest specific improvements",
        "Be constructive and educational"
    ],
    llm_config={"model": "gpt-4"}
)

# Use like any AG2 agent
response = agent.generate_reply([{"role": "user", "content": "Please review this code..."}])
```

## Why PersonaAgent?

Traditional AI agents often lack consistent character and behavior patterns. PersonaAgent addresses this by:

1. **Structured Identity**: Clear separation of role, goal, backstory, and constraints
2. **Consistent Behavior**: Agents maintain character throughout conversations
3. **Easy Customization**: Modify behavior by updating persona components
4. **Reusable Configurations**: Save and load agent personalities

## Architecture

PersonaAgent builds on AG2's proven architecture while adding structured persona management:

```
PersonaAgent → ConversableAgent → Agent
     ↓              ↓              ↓
  Persona      Conversation    Core AI
Components     Management      Features
```

## Getting Started

Ready to create your first persona agent? Check out our [Getting Started Guide](getting-started.md) or explore the [API Reference](api.md).