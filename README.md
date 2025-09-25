# PersonaAgent for AG2: Enabling Distinct Character Embodiment

[![PyPi](https://img.shields.io/pypi/v/ag2-persona.svg)](https://pypi.python.org/pypi/ag2-person)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Build Status](https://github.com/rsnodgrass/ag2-persona/actions/workflows/ci.yml/badge.svg)](https://github.com/rsnodgrass/ag2-persona/actions/workflows/ci.yml)


## Why This Matters

[AG2 (AutoGen)](https://ag2.ai/) agents currently mix role, purpose, and context into a single unstructured `system_message`, which is fantastic flexibility but does not propose an common pattern for agents to authentically embody distinct personas. PersonaAgent enables agents to adopt rich, well-defined characters through explicit `role`, `goal`, and `backstory` components, allowing for more authentic and consistent agent behavior while maintaining full compatibility with all that AG2 offers.

### The Problem

Current AG2 agent creation:
```python
agent = ConversableAgent(
    name="reviewer",
    system_message="You are a senior software engineer with 10 years of experience. Your task is to review code for quality issues, security vulnerabilities, and suggest improvements. Focus on Python best practices and ensure the code follows PEP-8 standards. You should be constructive in your feedback."
)
```

Issues:
- 🎭 **Weak Persona Embodiment** - Agents lack distinct character identity
- 🔄 **Limited Reuse** - Changing or sharing personas requires rewriting entire prompts
- 📚 **Maintainability** - Difficult to update character aspects
- 🎯 **Inconsistent Behavior** - Unstructured prompts lead to character drift

### The Solution

PersonaAgent enables authentic character embodiment (inspired by CrewAI's backstory/goal structure):
```python
agent = PersonaAgent(
    name="reviewer",
    role="Senior Software Engineer",
    goal="Review code for quality issues and suggest improvements",
    backstory="You have 10 years of experience in Python development",
    constraints=["Focus on Python best practices", "Follow PEP-8 standards"],
    llm_config={"model": "gpt-4"}
)
```

Benefits:
- 🎭 **Authentic Personas** - Agents embody distinct, consistent characters
- 🔄 **Dynamic Character Updates** - Modify and share persona aspects without full rewrites
- 📚 **Better Persona Maintenance** - Update character traits independently
- 🎯 **Consistent Behavior** - Well-defined personas reduce character drift

## Quick Start

### Installation

```bash
pip install ag2-persona
```

### Basic Usage

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

### Dynamic Goal Updates

```python
# Create agent with initial goal
agent = PersonaAgent(
    name="assistant",
    role="AI Assistant",
    goal="Help with general questions"
)

# Update goal for specific task
agent.update_goal("Focus on technical documentation writing")
# The system message is automatically regenerated
```

### Team Composition

```python
from ag2_persona import PersonaAgent
from autogen import GroupChat, GroupChatManager

# Create a research team with persona agents
lead_scientist = PersonaAgent(
    name="lead_scientist",
    role="Research Lead",
    goal="Design experiments and coordinate research objectives",
    backstory="PhD in biology with 15 years of research experience"
)

data_analyst = PersonaAgent(
    name="data_analyst",
    role="Data Scientist",
    goal="Analyze experimental data and generate statistical insights",
    backstory="Expert in statistical modeling and machine learning"
)

lab_technician = PersonaAgent(
    name="lab_tech",
    role="Laboratory Technician",
    goal="Execute experiments and ensure quality control",
    constraints=["Follow safety protocols", "Document all procedures"]
)

# Use in GroupChat as normal
groupchat = GroupChat(
    agents=[lead_scientist, data_analyst, lab_technician],
    messages=[],
    max_round=10
)
manager = GroupChatManager(groupchat)
```

## API Reference

### PersonaAgent

Extends `ConversableAgent` with persona-based prompt components.

#### Constructor

```python
PersonaAgent(
    name: str,
    role: str,
    goal: str,
    backstory: str = "",
    constraints: Optional[List[str]] = None,
    **kwargs  # All standard ConversableAgent parameters
)
```

**Parameters:**
- `name` (str): Agent identifier
- `role` (str): The agent's role or title (e.g., "Code Reviewer", "Data Scientist")
- `goal` (str): What the agent should accomplish
- `backstory` (str, optional): Background, expertise, or context
- `constraints` (List[str], optional): Limitations or rules to follow
- `**kwargs`: Any additional `ConversableAgent` parameters

#### Methods

##### `update_goal(new_goal: str) -> None`
Dynamically update the agent's goal and regenerate the system message.

```python
agent.update_goal("Review only the security aspects of the code")
```

#### Properties

- `role` (str): The agent's role
- `goal` (str): The agent's current goal
- `backstory` (str): The agent's backstory
- `constraints` (List[str]): The agent's constraints
- `system_message` (str): The composed system message (inherited)

### Creating Agents from Configuration

#### `PersonaBuilder` (Recommended)

Create persona agents with validation and flexible configuration:

```python
from ag2_persona import PersonaBuilder

# From dictionary
config = {
    "name": "bioinformatics_specialist",
    "role": "Bioinformatics Specialist",
    "goal": "Analyze genomic sequences and identify patterns",
    "backstory": "PhD in computational biology with expertise in sequence analysis",
    "constraints": ["Use validated algorithms", "Ensure reproducibility"]
}

agent = (PersonaBuilder("bioinformatics_specialist")
         .from_dict(config)
         .with_llm_config({"model": "gpt-4", "temperature": 0.5})
         .build())

# Or from YAML file
agent = (PersonaBuilder("bioinformatics_specialist")
         .from_yaml("specialists/bioinformatics.yaml")
         .with_llm_config({"model": "gpt-4", "temperature": 0.5})
         .build())
```


## Migration Guide

### From Standard ConversableAgent

**Before:**
```python
agent = ConversableAgent(
    name="researcher",
    system_message="""You are a marine biology researcher with 8 years
    of experience studying coral reef ecosystems. Analyze oceanographic
    data to identify patterns in coral health. Focus on temperature and
    pH correlations. Always cite relevant scientific literature and
    follow peer review standards.""",
    llm_config=config
)
```

**After:**
```python
agent = PersonaAgent(
    name="researcher",
    role="Marine Biology Researcher",
    goal="Analyze oceanographic data to identify coral health patterns",
    backstory="You have 8 years of experience studying coral reef ecosystems",
    constraints=[
        "Focus on temperature and pH correlations",
        "Always cite relevant scientific literature",
        "Follow peer review standards"
    ],
    llm_config=config
)
```

### Compared to CrewAI

**CrewAI:**
```python
from crewai import Agent

agent = Agent(
    role="Climate Scientist",
    goal="Analyze climate data and predict weather patterns",
    backstory="You are a climate scientist with expertise in atmospheric modeling"
)
```

**AG2 PersonaAgent:**
```python
agent = PersonaAgent(
    name="climate_scientist",
    role="Climate Scientist",
    goal="Analyze climate data and predict weather patterns",
    backstory="You are a climate scientist with expertise in atmospheric modeling",
    llm_config={"model": "gpt-4"}
)
```

## Examples

### Persona Library

A comprehensive collection of pre-built persona agents across various domains is available in [`examples/library/`](examples/). These YAML files provide ready-to-use personas that you can load with PersonaBuilder:

- **Construction Team**: Project managers, architects, engineers for collaborative construction analysis
- **Software Development**: Architects, data engineers, product managers for technical decision-making
- **Life Sciences**: Pharmaceutical researchers, analysts for scientific research
- **Business Operations**: Customer service, logistics, strategic analysis

See [`examples/README.md`](examples/README.md) for complete documentation.

### Multi-Agent Construction Team Example

The [`examples/construction_team.py`](examples/construction_team.py) demonstrates a complete multi-agent system where:
- **UserProxyAgent** acts as human client proxy presenting real construction challenges
- **Three AI specialists** collaborate autonomously using GroupChat
- **PersonaBuilder** loads agents from YAML configurations with runtime LLM setup

This example showcases the hybrid conversation pattern: human problems → expert AI collaboration.

```bash
# Run the construction team example
cd examples/
python construction_team.py
```

## FAQ

**Q: Does this replace ConversableAgent?**
A: No, it extends it. All ConversableAgent features still work.

**Q: Can I mix PersonaAgent with regular agents?**
A: Yes, they're fully compatible in group chats and conversations.

**Q: What if I need custom system message formatting?**
A: Pass additional `system_message` in kwargs - it gets appended.

**Q: Does this work with function calling?**
A: Yes, all ConversableAgent features including function calling work normally.

**Q: What is the best way to load PersonaAgents from config instead of hardcoded?**
A: Use `PersonaBuilder` with `.from_yaml()` or `.from_dict()`. This provides validation, flexible configuration, and separates persona definition from runtime LLM config. Example: `PersonaBuilder("agent").from_yaml("config.yaml").with_llm_config(llm_config).build()`

**Q: How do I contribute improvements?**
A: Submit PRs to enhance the structure while maintaining backward compatibility.
