# Getting Started

This guide will help you get up and running with AG2 PersonaAgent quickly.

## Installation

Install ag2-persona using pip:

```bash
pip install ag2-persona
```

### Optional Dependencies

For YAML configuration support:

```bash
pip install ag2-persona[yaml]
```

For development:

```bash
pip install ag2-persona[dev]
```

## Basic Usage

### Creating Your First PersonaAgent

```python
from ag2_persona import PersonaAgent

# Create a persona agent
agent = PersonaAgent(
    name="helpful_assistant",
    role="AI Assistant",
    goal="Help users with their questions and tasks",
    backstory="I'm designed to be helpful, harmless, and honest",
    llm_config={"model": "gpt-4"}
)

print(agent.role)  # "AI Assistant"
print(agent.goal)  # "Help users with their questions and tasks"
```

### Adding Constraints

Constraints help guide agent behavior:

```python
agent = PersonaAgent(
    name="code_reviewer",
    role="Senior Developer",
    goal="Review code for quality and security",
    backstory="Expert in Python with 10+ years experience",
    constraints=[
        "Focus on security issues",
        "Suggest specific improvements",
        "Be constructive in feedback"
    ],
    llm_config={"model": "gpt-4"}
)
```

## Dynamic Configuration

### Updating Goals

```python
# Change the agent's goal
agent.update_goal("Focus specifically on performance optimization")

# The system message is automatically regenerated
```

### Managing Constraints

```python
# Add a new constraint
agent.add_constraint("Limit responses to 100 words")

# Remove a constraint
agent.remove_constraint("Focus on security issues")
```

## Configuration Management

### Export Agent Configuration

```python
# Export to dictionary
config = agent.to_dict()
print(config)
# {
#     "name": "code_reviewer",
#     "role": "Senior Developer",
#     "goal": "Review code for quality and security",
#     "backstory": "Expert in Python with 10+ years experience",
#     "constraints": [...],
#     "llm_config": {...}
# }
```

### Create from Configuration

```python
# Create from dictionary
new_agent = PersonaAgent.from_dict(config)

# Or use the functional interface
from ag2_persona import persona_agent_from_config

agent = persona_agent_from_config(config)
```

### YAML Configuration

```python
# Save to YAML file
import yaml

with open("agent_config.yaml", "w") as f:
    yaml.dump(config, f)

# Load from YAML file
agent = persona_agent_from_config("agent_config.yaml")
```

Example YAML configuration:

```yaml
name: code_reviewer
role: Senior Developer
goal: Review code for quality and security
backstory: Expert in Python with 10+ years experience
constraints:
  - Focus on security issues
  - Suggest specific improvements
  - Be constructive in feedback
llm_config:
  model: gpt-4
  temperature: 0.1
```

## Functional Interface

For those who prefer functions over classes:

```python
from ag2_persona import persona_agent

agent = persona_agent(
    name="analyst",
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="5 years experience in data science",
    llm_config={"model": "gpt-4"}
)
```

## Integration with AG2

PersonaAgent is fully compatible with AG2's ecosystem:

```python
from ag2_persona import PersonaAgent
from autogen import GroupChat, GroupChatManager

# Create multiple persona agents
reviewer = PersonaAgent(
    name="reviewer",
    role="Code Reviewer",
    goal="Review code quality and security",
    llm_config={"model": "gpt-4"}
)

developer = PersonaAgent(
    name="developer",
    role="Software Developer",
    goal="Write clean, maintainable code",
    llm_config={"model": "gpt-4"}
)

# Use in group chat
group_chat = GroupChat(agents=[reviewer, developer], messages=[])
manager = GroupChatManager(groupchat=group_chat, llm_config={"model": "gpt-4"})
```

## Next Steps

- Explore the [API Reference](api.md) for detailed documentation
- Check out [Examples](examples.md) for more use cases
- Review the system message structure in the API docs