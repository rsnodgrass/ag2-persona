# Examples

## The Power of Markdown Persona Libraries

PersonaAgent's strength lies in **separating expertise definition from runtime configuration**. Domain experts can define agent personas in Markdown files, while developers handle the technical integration.

### Design Philosophy: Spec vs Character

The Markdown format follows a clear separation of concerns:
1. **Frontmatter = Structure** (what the system needs)
2. **Markdown = Narrative** (what makes the character real)

This ensures both human-friendly storytelling and machine-friendly structured data.

**Key Benefits:**

- **🔄 Reusability**: Share persona definitions across projects and teams
- **🛠️ Maintainability**: Update agent behavior without touching code
- **👥 Non-developer friendly**: Subject matter experts can edit Markdown files directly
- **📝 Version control**: Track persona evolution and collaborate on definitions
- **⚡ Separation of concerns**: Stable persona definition vs variable runtime config

## Persona Library

Pre-built expert personas are available in the [examples/library/](https://github.com/rsnodgrass/ag2-persona/tree/main/examples/library) directory. These represent real domain expertise that can be loaded and customized:

### Construction Team
- `construction_project_manager.md` - Timeline and coordination expertise
- `architectural_specialist.md` - Design buildability and code compliance
- `value_engineering_specialist.md` - Cost optimization and ROI analysis

### Software Development
- `senior_software_architect.md` - System design and architecture
- `senior_data_engineer.md` - Data pipeline and platform expertise
- `senior_product_manager.md` - Product strategy and roadmap planning

### Loading Expert Personas

The power of PersonaBuilder shines when loading domain expert personas from the library:

```python
from ag2_persona import PersonaBuilder, AsyncPersonaBuilder

# Sync version - blocks during file I/O
architect = (PersonaBuilder.from_markdown("examples/library/senior_software_architect.md")
            .set_name("architect")
            .llm_config({"model": "gpt-4", "temperature": 0.7})
            .build())

# Async version - non-blocking I/O for high-performance apps
async def load_architect():
    return await (AsyncPersonaBuilder("architect")
                 .from_markdown("examples/library/senior_software_architect.md")
                 .llm_config({"model": "gpt-4", "temperature": 0.7})
                 .build())

# Domain experts can edit the Markdown files
# Developers handle runtime LLM configuration
# Perfect separation of concerns!
```

**When to use async:**
- High-concurrency applications
- Web servers handling multiple requests
- Applications with many personas to load
- When file I/O blocking is a concern

**Why this pattern works so well:**
- **Domain experts** define the persona knowledge and behavior in Markdown
- **Developers** handle LLM configuration and integration
- **Teams** share and reuse personas across projects
- **Updates** happen in Markdown files without code changes

For complete documentation of available personas, see [examples/README.md](https://github.com/rsnodgrass/ag2-persona/blob/main/examples/README.md).

## Multi-Agent Construction Team

See the complete example in [examples/construction_team.py](https://github.com/rsnodgrass/ag2-persona/blob/main/examples/construction_team.py).

This example demonstrates the Markdown library pattern in action:
- UserProxyAgent as human client proxy
- Three AI specialists loaded from Markdown configurations
- PersonaBuilder separating persona definition from runtime config
- GroupChat orchestration with consistent agent descriptions
