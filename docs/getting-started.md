# Getting Started

## Installation

```bash
pip install ag2-persona
```

## Quick Overview

PersonaAgent's power comes from **separating persona definition from runtime configuration**. Domain experts define agent behavior in Markdown files, while developers handle the runtime integration.

**Key Benefits:**
- **🔄 Reusable**: Share personas across projects and teams
- **👥 Collaborative**: Non-developers can edit Markdown persona files
- **🛠️ Maintainable**: Update agent behavior without code changes
- **📝 Trackable**: Version control persona definitions and evolution

## Markdown Persona Library Pattern (Recommended)

### Design Philosophy: Spec vs Character

PersonaAgent's Markdown format follows a clear separation of concerns:

1. **Frontmatter = Structure** (what the system needs)
2. **Markdown = Narrative** (what makes the character real)

This design ensures domain experts can write rich character stories while systems get the structured data they need for routing and validation.

**Example Structure:**
```markdown
---
# The SPEC - What the agent IS and MUST do
role: Senior Software Architect
goal: Review designs for scalability
constraints:
  - Must consider security implications
  - Focus on maintainable solutions
---

# The CHARACTER - Who the agent is
# Backstory
Twenty years building distributed systems at Netflix, Google...
Rich narrative with personality, experience, war stories...
```

### Using Persona Libraries

The most powerful approach - load expert personas from configuration files:

```python
from ag2_persona import PersonaBuilder, AsyncPersonaBuilder

# Sync version (blocks during I/O)
analyst = (PersonaBuilder.from_markdown("library/senior_data_engineer.md")
          .set_name("data_analyst")
          .llm_config({"model": "gpt-4", "temperature": 0.7})
          .build())

# Async version (non-blocking I/O)
async def create_analyst():
    return await (AsyncPersonaBuilder("data_analyst")
                 .from_markdown("library/senior_data_engineer.md")
                 .llm_config({"model": "gpt-4", "temperature": 0.7})
                 .build())

# Use like any AG2 agent
response = analyst.generate_reply(messages=[{"content": "Analyze this sales data"}])
```

### Installation Options

```bash
# Basic installation (sync Markdown only)
pip install ag2-persona[markdown]

# Async support included
pip install ag2-persona[markdown-async]

# Development setup with async
pip install ag2-persona[all]
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
