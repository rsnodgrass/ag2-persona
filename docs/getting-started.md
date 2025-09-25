# Getting Started

## Installation

```bash
pip install ag2-persona
```

## Quick Overview

PersonaAgent's power comes from **separating persona definition from runtime configuration**. Domain experts define agent behavior in YAML files, while developers handle the runtime integration.

**Key Benefits:**
- **🔄 Reusable**: Share personas across projects and teams
- **👥 Collaborative**: Non-developers can edit YAML persona files
- **🛠️ Maintainable**: Update agent behavior without code changes
- **📝 Trackable**: Version control persona definitions and evolution

## YAML Persona Library Pattern (Recommended)

The most powerful approach - load expert personas from configuration files:

```python
from ag2_persona import PersonaBuilder

# Load domain expert persona from YAML library
analyst = (PersonaBuilder("data_analyst")
          .from_yaml("library/senior_data_engineer.yaml")
          .llm_config({"model": "gpt-4", "temperature": 0.7})
          .build())

# Use like any AG2 agent
response = analyst.generate_reply(messages=[{"content": "Analyze this sales data"}])
```

## Direct Construction (For Simple Cases)

For simple, one-off agents you can construct directly:

```python
from ag2_persona import PersonaAgent

# Direct construction for simple cases
expert = PersonaAgent(
    name="data_analyst",
    role="Data Analysis Expert",
    goal="Analyze the provided dataset and identify key insights",
    backstory="You specialize in statistical analysis and data visualization",
    llm_config={"model": "gpt-4", "temperature": 0.7}
)
```

## Next Steps

- Check out the [Examples](examples.md) for complete use cases
- See the [API Reference](api.md) for detailed documentation