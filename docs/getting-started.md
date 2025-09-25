# Getting Started

## Installation

```bash
pip install ag2-persona
```

## Basic Usage

### Creating a PersonaAgent

```python
from ag2_persona import PersonaAgent

# Create an agent with a distinct persona
expert = PersonaAgent(
    name="data_analyst",
    role="Data Analysis Expert",
    goal="Analyze the provided dataset and identify key insights",
    backstory="You specialize in statistical analysis and data visualization",
    llm_config={"model": "gpt-4", "temperature": 0.7}
)

# Use like any AG2 agent
response = expert.generate_reply(messages=[{"content": "Analyze this sales data"}])
```

### Using PersonaBuilder (Recommended)

```python
from ag2_persona import PersonaBuilder

# Create agent from YAML configuration
agent = (PersonaBuilder("analyst")
         .from_yaml("analysts/data_analyst.yaml")
         .with_llm_config({"model": "gpt-4", "temperature": 0.7})
         .build())
```

## Next Steps

- Check out the [Examples](examples.md) for complete use cases
- See the [API Reference](api.md) for detailed documentation