# PersonaAgent for AG2: Enabling Distinct Character Embodiment

[![PyPi](https://img.shields.io/pypi/v/ag2-persona.svg)](https://pypi.python.org/pypi/ag2-person)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)


## Why This Matters

[AG2 (AutoGen)](https://ag2.ai/) agents currently mix role, purpose, and context into a single unstructured `system_message`, which is fantastic flexibility but does not propose a common pattern for agents to authentically embody distinct personas. PersonaAgent enables agents to adopt rich, well-defined characters through explicit `role`, `goal`, and `backstory` components.

**The real power comes from the PersonaBuilder YAML library pattern:** Load expert personas from configuration files, enabling domain experts to define agent behavior while developers handle runtime integration. This separation provides:

- **🔄 Reusability**: Share persona definitions across projects and teams
- **🛠️ Maintainability**: Update agent behavior without touching code
- **👥 Non-developer friendly**: Subject matter experts can edit YAML files directly
- **📝 Version control**: Track persona evolution and collaborate on definitions
- **⚡ Separation of concerns**: Stable persona definition vs variable runtime config

Perfect for teams where domain experts define the "who" while developers handle the "how".

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
# or with modern uv:
uv add ag2-persona
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

### Team Composition with PersonaBuilder

Build multi-agent teams by loading expert personas from YAML files. This enables domain experts to define agent behavior while developers handle runtime integration:

```python
from ag2_persona import PersonaBuilder
from autogen import GroupChat, GroupChatManager

# Load domain expert personas from YAML library (sync version)
lead_scientist = (PersonaBuilder("lead_scientist")
                 .from_yaml("library/research_team_lead.yaml")
                 .llm_config({"model": "gpt-4", "temperature": 0.7})
                 .build())

data_analyst = (PersonaBuilder("data_analyst")
               .from_yaml("library/senior_data_engineer.yaml")
               .llm_config({"model": "gpt-4", "temperature": 0.5})
               .build())

# Manual construction when YAML doesn't exist yet
lab_technician = (PersonaBuilder("lab_tech")
                 .role("Laboratory Technician")
                 .goal("Execute experiments and ensure quality control")
                 .constraints(["Follow safety protocols", "Document all procedures"])
                 .llm_config({"model": "gpt-4", "temperature": 0.3})
                 .build())

# Use in GroupChat - personas are consistent and reusable
groupchat = GroupChat(
    agents=[lead_scientist, data_analyst, lab_technician],
    messages=[],
    max_round=10
)
manager = GroupChatManager(groupchat)
```

**Benefits:**
- Domain experts edit YAML files, developers handle runtime
- Personas are shared across projects and teams
- Updates don't require code changes
- Version control tracks persona evolution

### Async Team Composition

For async applications, use `AsyncPersonaBuilder` to avoid blocking the event loop:

```python
import asyncio
from ag2_persona import AsyncPersonaBuilder
from autogen import GroupChat, GroupChatManager

async def create_async_team():
    # Load personas asynchronously with true fluent chaining - no blocking I/O
    lead_agent = await (AsyncPersonaBuilder("lead_scientist")
                       .from_yaml("library/research_team_lead.yaml")
                       .llm_config({"model": "gpt-4", "temperature": 0.7})
                       .build())

    analyst_agent = await (AsyncPersonaBuilder("data_analyst")
                          .from_yaml("library/senior_data_engineer.yaml")
                          .llm_config({"model": "gpt-4", "temperature": 0.5})
                          .build())

    return GroupChat(agents=[lead_agent, analyst_agent], messages=[], max_round=10)

# Usage in async context
async def main():
    team = await create_async_team()
    # Use team in async AG2 workflows...

# YAML and async support now included by default
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

### PersonaBuilder Methods

PersonaBuilder supports three construction patterns for different use cases:

```python
from ag2_persona import PersonaBuilder

# Option 1 (Recommended): Load expert personas from YAML library
expert = (PersonaBuilder("bioinformatics_specialist")
          .from_yaml("library/bioinformatics_specialist.yaml")
          .llm_config({"model": "gpt-4", "temperature": 0.5})
          .build())

# Option 2: Construct from dictionary
persona_config = {
    "role": "Bioinformatics Specialist",
    "goal": "Analyze genomic sequences and identify patterns",
    "backstory": "PhD in computational biology with expertise in sequence analysis",
    "constraints": ["Use validated algorithms", "Ensure reproducibility"]
}

agent = (PersonaBuilder("bioinformatics_specialist")
         .from_dict(persona_config)
         .llm_config({"model": "gpt-4", "temperature": 0.5})
         .build())

# Option 3: Manual construction
agent = (PersonaBuilder("bioinformatics_specialist")
         .role("Bioinformatics Specialist")
         .goal("Analyze genomic sequences and identify patterns")
         .backstory("PhD in computational biology with expertise in sequence analysis")
         .constraints(["Use validated algorithms", "Ensure reproducibility"])
         .llm_config({"model": "gpt-4", "temperature": 0.5})
         .build())

# Async YAML loading (for async applications)
async def create_async_agent():
    return await (AsyncPersonaBuilder("bioinformatics_specialist")
                 .from_yaml("library/bioinformatics_specialist.yaml")
                 .llm_config({"model": "gpt-4", "temperature": 0.5})
                 .build())
```

**YAML and async support included by default.**

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
agent = (PersonaBuilder("researcher")
         .role("Marine Biology Researcher")
         .goal("Analyze oceanographic data to identify coral health patterns")
         .backstory("You have 8 years of experience studying coral reef ecosystems")
         .constraints([
             "Focus on temperature and pH correlations",
             "Always cite relevant scientific literature",
             "Follow peer review standards"
         ])
         .llm_config(config)
         .build())
```

### Compared to CrewAI

**CrewAI:**
```python
from crewai import Agent

agent = Agent(
    role="Climate Scientist",
    goal="Analyze climate data and predict weather patterns",
    backstory="You are a climate scientist with expertise in atmospheric modeling",
    llm={"model": "gpt-4"}
)
```

**AG2 PersonaAgent:**
```python
agent = (PersonaBuilder("climate_scientist")
         .role("Climate Scientist")
         .goal("Analyze climate data and predict weather patterns")
         .backstory("You are a climate scientist with expertise in atmospheric modeling")
         .llm_config({"model": "gpt-4"})
         .build())
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

## Frequently Asked Questions

<details>
<summary><strong>Does this replace ConversableAgent?</strong></summary>

No, PersonaAgent extends ConversableAgent. All existing ConversableAgent features work exactly as before, including function calling, human input modes, and group chats.
</details>

<details>
<summary><strong>Can I mix PersonaAgent with regular AG2 agents?</strong></summary>

Yes! PersonaAgents are fully compatible with regular ConversableAgents in group chats and conversations. You can gradually adopt PersonaAgent without changing your existing setup.
</details>

<details>
<summary><strong>What if I need custom system message formatting?</strong></summary>

Pass additional `system_message` content via kwargs - it gets appended to the generated persona message:

```python
agent = PersonaAgent(
    name="reviewer",
    role="Code Reviewer",
    goal="Review code quality",
    system_message="Additional custom instructions here",
    llm_config=config
)
```
</details>

<details>
<summary><strong>What's the best way to load personas from configuration?</strong></summary>

Use PersonaBuilder with YAML files for maximum flexibility:

```python
# Recommended: YAML library pattern
agent = (PersonaBuilder("expert")
         .from_yaml("library/domain_expert.yaml")
         .llm_config({"model": "gpt-4", "temperature": 0.7})
         .build())
```

This separates persona definition (stable, edited by domain experts) from runtime configuration (variable, handled by developers).
</details>

<details>
<summary><strong>How do I contribute improvements?</strong></summary>

Submit pull requests that enhance functionality while maintaining backward compatibility. Focus on:
- New persona library entries
- Additional PersonaBuilder methods
- Documentation improvements
- Bug fixes and performance enhancements
</details>
