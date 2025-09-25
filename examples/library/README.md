# PersonaAgent Library Examples

This directory contains example PersonaAgent definitions in YAML format. Each file represents a complete agent persona with role, goal, backstory, constraints, and LLM configuration.

## Construction Team Specialists (Multi-Agent Example)

These three agents work together to solve complex construction challenges:

| Agent | Role | Focus Area | Expertise |
|-------|------|------------|-----------|
| `construction_project_manager` | Senior Project Manager | Timeline & Coordination | Critical path scheduling, trade coordination, 94% on-time delivery |
| `architectural_specialist` | Architectural Specialist | Design Interpretation | Clash detection, code compliance, buildability analysis |
| `value_engineering_specialist` | Value Engineering Specialist | Cost Optimization | ROI analysis, lifecycle costs, saved $500M through VE |

**Team Collaboration**: These agents excel when used together in AG2's GroupChat, providing comprehensive analysis of construction decisions by balancing timeline, design intent, and financial optimization.

## Other Domain Specialists

| Agent | Role | Domain | Example Use Cases |
|-------|------|--------|----------|
| `technical_architect` | Senior Software Architect | Technology | System design reviews, architecture decisions, scalability assessment |
| `construction_bid_analyst` | Senior Bid Analyst | Construction | Compare contractor bids, identify hidden costs, evaluate risks |
| `pharmaceutical_researcher` | Pharmaceutical Researcher | Life Sciences | Clinical trial analysis, drug efficacy studies, FDA compliance |
| `logistics_customer_service` | Senior Customer Service Rep | Logistics | Shipping inquiries, package tracking, delivery issues |
| `research_analyst` | Senior Research Analyst | Analytics | Data synthesis, trend analysis, strategic recommendations |
| `product_strategist` | Senior Product Strategist | Product | Market analysis, feature prioritization, competitive positioning |

## Usage

### Single Agent
```python
from ag2_persona import PersonaAgent

# Load directly from YAML
agent = PersonaAgent.from_yaml("library/value_engineering_specialist.yaml")
```

### Multi-Agent Team (Construction Example)
```python
from ag2_persona import PersonaAgent
from autogen import GroupChat, GroupChatManager

# Load the construction team
pm = PersonaAgent.from_yaml("library/construction_project_manager.yaml")
arch = PersonaAgent.from_yaml("library/architectural_specialist.yaml")
ve = PersonaAgent.from_yaml("library/value_engineering_specialist.yaml")

# Create GroupChat for collaboration
groupchat = GroupChat(agents=[pm, arch, ve], messages=[], max_round=10)
manager = GroupChatManager(groupchat=groupchat)

# Start collaborative problem-solving
manager.initiate_chat(message="How do we handle this facade delay?")
```

## File Format

Each YAML file should contain:

- `name`: Unique identifier (should match filename without .yaml)
- `role`: The agent's professional title/role
- `goal`: What the agent should accomplish (can be overridden)
- `backstory`: Rich background, experience, and expertise
- `constraints`: List of rules, guidelines, and limitations
- `llm_config`: Model configuration (model, temperature, max_tokens)

## Benefits

- **Modularity**: One agent per file for easy version control
- **Reusability**: Load same agent with different goals
- **Rich Personas**: Detailed backstories for authentic behavior
- **Easy Maintenance**: Simple YAML format for non-technical editing
- **Flexibility**: Override any parameter when creating agents