# Persona Library Examples

The 'examples/library/' directory contains example PersonaAgent definitions in Markdown format. Each file represents a complete agent persona with role, goal, backstory, constraints, and LLM configuration.

## Construction Team Specialists (Multi-Agent Example)

These three agents work together to solve complex construction challenges:

| Agent | Role | Focus Area | Expertise |
|-------|------|------------|-----------|
| `construction_project_manager` | Senior Project Manager | Timeline & Coordination | Critical path scheduling, trade coordination, 94% on-time delivery |
| `architectural_specialist` | Architectural Specialist | Design Interpretation | Clash detection, code compliance, buildability analysis |
| `value_engineering_specialist` | Value Engineering Specialist | Cost Optimization | ROI analysis, lifecycle costs, saved $500M through VE |

**Team Collaboration**: These agents excel when used together in AG2's GroupChat, providing comprehensive analysis of construction decisions by balancing timeline, design intent, and financial optimization.

## Other Domain Specialist Examples in Library

| Agent | Role | Domain | Example Use Cases |
|-------|------|--------|----------|
| `senior_software_architect` | Senior Software Architect | Technology | System design reviews, architecture decisions, scalability assessment |
| `senior_data_engineer` | Senior Data Engineer | Data & Analytics | Pipeline design, data platform architecture, ETL optimization |
| `senior_product_manager` | Senior Product Manager | Business & Management | Product strategy, roadmap planning, feature prioritization |
| `technical_architect` | Senior Software Architect | Technology | System design reviews, architecture decisions, scalability assessment |
| `construction_bid_analyst` | Senior Bid Analyst | Construction | Compare contractor bids, identify hidden costs, evaluate risks |
| `pharmaceutical_researcher` | Pharmaceutical Researcher | Life Sciences | Clinical trial analysis, drug efficacy studies, FDA compliance |
| `logistics_customer_service` | Senior Customer Service Rep | Logistics | Shipping inquiries, package tracking, delivery issues |
| `research_analyst` | Senior Research Analyst | Analytics | Data synthesis, trend analysis, strategic recommendations |
| `product_strategist` | Senior Product Strategist | Product | Market analysis, feature prioritization, competitive positioning |

## Usage

### Single Agent
```python
from ag2_persona import PersonaBuilder

# Load a persona from Markdown using PersonaBuilder
agent = (PersonaBuilder.from_markdown("library/value_engineering_specialist.md")
         .set_name("value_engineer")
         .llm_config({"model": "gpt-4", "temperature": 0.7})
         .build())
```

### Multi-Agent Team (Construction Example)

See [examples/construction_team.py](examples/construction_team.py) for a more complete example of the following multi-agent construction team.

```python
from ag2_persona import PersonaBuilder
from autogen import GroupChat, GroupChatManager

llm_config = {"model": "gpt-4", "temperature": 0.7}

# Load the construction team using PersonaBuilder
pm = (PersonaBuilder.from_markdown("library/construction_project_manager.md")
      .set_name("project_manager")
      .llm_config(llm_config)
      .build())

arch = (PersonaBuilder.from_markdown("library/architectural_specialist.md")
        .set_name("architect_specialist")
        .llm_config(llm_config)
        .build())

ve = (PersonaBuilder.from_markdown("library/value_engineering_specialist.md")
      .set_name("value_engineer")
      .llm_config(llm_config)
      .build())

# Create GroupChat for collaboration
group = GroupChat(agents=[pm, arch, ve], messages=[], max_round=10)
manager = GroupChatManager(groupchat=group)

# Start collaborative problem-solving
manager.initiate_chat(message="How do we handle this facade delay?")
```

## Design Philosophy: Spec vs Character

The Markdown persona format follows a clear separation of concerns:

1. **Frontmatter = Structure** (what the system needs)
2. **Markdown = Narrative** (what makes the character real)

This separation makes the format both **human-friendly** (domain experts write stories) and **machine-friendly** (systems get structured data). It's the right balance between flexibility and consistency.

### The SPEC (YAML Frontmatter)
The frontmatter defines the **contract** - structured, concise statements of what the agent IS and MUST do:

- `name`: Unique identifier (should match filename without .md)
- `role`: The agent's professional title/role (one-line identity)
- `goal`: What the agent should accomplish (clear objective, can be overridden)
- `constraints`: List of rules, guidelines, and limitations (enforced as YAML list)
- `llm_config`: Model configuration (model, temperature, max_tokens)

### The CHARACTER (Markdown Content)
The markdown body provides the **narrative** - rich, flexible storytelling that brings the agent to life:

- `# Backstory`: Rich background, experience, expertise, and personality

This structure ensures that:
- **Role/Goal** stay concise (not buried in prose)
- **Constraints** remain structured (guaranteed bullet points)
- **Backstory** can be richly formatted (paragraphs, emphasis, personality)

## Markdown File Benefits

- **Modularity**: One agent per file for easy version control
- **Reusability**: Load same agent with different goals
- **Rich Personas**: Detailed backstories in readable Markdown format
- **Easy Maintenance**: Simple Markdown format for non-technical editing
- **Flexibility**: Override any parameter when creating agents
