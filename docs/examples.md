# Examples

## Multi-Agent Construction Team

See the complete example in [examples/construction_team.py](https://github.com/rsnodgrass/ag2-persona/blob/main/examples/construction_team.py).

This example demonstrates:
- UserProxyAgent as human client proxy
- Three AI specialists collaborating autonomously
- PersonaBuilder loading agents from YAML configurations
- GroupChat orchestration with agent descriptions

## Persona Library

Pre-built persona agents are available in the [examples/library/](https://github.com/rsnodgrass/ag2-persona/tree/main/examples/library) directory:

### Construction Team
- `construction_project_manager.yaml` - Timeline and coordination expertise
- `architectural_specialist.yaml` - Design buildability and code compliance
- `value_engineering_specialist.yaml` - Cost optimization and ROI analysis

### Software Development
- `senior_software_architect.yaml` - System design and architecture
- `senior_data_engineer.yaml` - Data pipeline and platform expertise
- `senior_product_manager.yaml` - Product strategy and roadmap planning

### Usage

```python
from ag2_persona import PersonaBuilder

# Load any persona from the library
agent = (PersonaBuilder("specialist")
         .from_yaml("examples/library/senior_software_architect.yaml")
         .with_llm_config({"model": "gpt-4", "temperature": 0.7})
         .build())
```

For complete documentation of available personas, see [examples/README.md](https://github.com/rsnodgrass/ag2-persona/blob/main/examples/README.md).