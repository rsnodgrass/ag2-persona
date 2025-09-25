# PersonaAgent for AG2

Welcome to the PersonaAgent documentation!

PersonaAgent enables AG2 (AutoGen) agents to embody distinct personas through explicit `role`, `goal`, and `backstory` components, allowing for more authentic and consistent agent behavior.

## Quick Links

- [Getting Started](getting-started.md) - Installation and basic usage
- [API Reference](api.md) - Complete API documentation
- [Examples](examples.md) - Code examples and tutorials

## Key Features

- 🎭 **Authentic Personas** - Agents embody distinct, consistent characters
- 🔄 **Dynamic Character Updates** - Modify persona aspects without full rewrites
- 📚 **Better Maintenance** - Update character traits independently
- 🎯 **Consistent Behavior** - Well-defined personas reduce character drift
- 🔧 **PersonaBuilder Pattern** - Fluent interface with validation and flexible configuration

## Installation

```bash
pip install ag2-persona
```

## Quick Example

```python
from ag2_persona import PersonaBuilder

# Create an expert agent using PersonaBuilder
expert = (PersonaBuilder("data_analyst")
          .from_yaml("library/data_analyst.yaml")
          .llm_config({"model": "gpt-4", "temperature": 0.7})
          .build())

# Use like any AG2 agent
response = expert.generate_reply(messages=[{"content": "Analyze this data"}])
```
