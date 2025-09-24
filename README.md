# PersonaAgent for AG2: Enabling Distinct Character Embodiment

## Why This Matters

AG2 (AutoGen) agents currently mix role, purpose, and context into a single unstructured `system_message`, which is fantastic flexibility but does not propose an common pattern for agents to authentically embody distinct personas. PersonaAgent enables agents to adopt rich, well-defined characters through explicit `role`, `goal`, and `backstory` components, allowing for more authentic and consistent agent behavior while maintaining full compatibility with all that AG2 offers.

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

### Helper Functions

#### `persona_agent()`

Alternative functional interface for creating persona agents:

```python
from ag2_persona import persona_agent

agent = persona_agent(
    name="helper",
    role="Assistant",
    goal="Help users with their questions",
    llm_config={"model": "gpt-4"}
)
```

#### `persona_agent_from_config()`

Create persona agents from configuration dictionaries:

```python
from ag2_persona import persona_agent_from_config

config = {
    "name": "bioinformatics_specialist",
    "role": "Bioinformatics Specialist",
    "goal": "Analyze genomic sequences and identify patterns",
    "backstory": "PhD in computational biology with expertise in sequence analysis",
    "constraints": ["Use validated algorithms", "Ensure reproducibility"],
    "llm_config": {"model": "gpt-4", "temperature": 0.5}
}

agent = persona_agent_from_config(config)
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

### From CrewAI

**CrewAI:**
```python
from crewai import Agent

agent = Agent(
    role="Climate Scientist",
    goal="Analyze climate data and predict weather patterns",
    backstory="You are a climate scientist with expertise in atmospheric modeling",
    verbose=True
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

## Advanced Examples

### Configuration-Driven Agents

Create agents from YAML configuration:

```yaml
# agents.yaml
principal_investigator:
  role: "Principal Investigator"
  goal: "Lead research project and ensure scientific rigor"
  backstory: "20 years experience in pharmaceutical research"
  constraints:
    - "Follow FDA guidelines"
    - "Ensure statistical significance"
    - "Consider ethical implications"
  llm_config:
    model: "gpt-4"
    temperature: 0.3
```

```python
from ruamel.yaml import YAML
from ag2_persona import persona_agent_from_config

# Load configuration
yaml = YAML()
with open("agents.yaml", "r") as f:
    agents_config = yaml.load(f)

# Create agents from config
agents = {}
for name, config in agents_config.items():
    config["name"] = name
    agents[name] = persona_agent_from_config(config)
```

### Dynamic Role-Playing

```python
# Create a versatile agent
analyst = PersonaAgent(
    name="analyst",
    role="Data Analyst",
    goal="Provide data-driven insights",
    backstory="Expert in statistics and machine learning"
)

# Adapt for different research phases
for phase in ["data_collection", "analysis", "interpretation"]:
    analyst.update_goal(f"Focus on {phase} phase and identify key findings")
    results = analyst.analyze(research_data[phase])
    print(f"{phase.title()} Phase: {results}")
```

### Hierarchical Team Structure

```python
# Create research team with clear hierarchy
research_director = PersonaAgent(
    name="director",
    role="Research Director",
    goal="Set research priorities and approve major decisions",
    backstory="25 years leading interdisciplinary research teams"
)

project_manager = PersonaAgent(
    name="pm",
    role="Research Project Manager",
    goal="Coordinate research activities and ensure timeline adherence",
    backstory="12 years managing complex scientific projects"
)

researchers = [
    PersonaAgent(
        name=f"researcher_{i}",
        role="Research Scientist",
        goal="Conduct experiments and collect data according to protocols",
        backstory="PhD scientist specializing in experimental methodology"
    )
    for i in range(3)
]

# Create hierarchical group chat
all_agents = [research_director, project_manager] + researchers
groupchat = GroupChat(agents=all_agents, messages=[], max_round=15)
```

## Design Philosophy

### Why These Specific Components?

1. **Role**: Defines identity and expertise
   - Helps LLM understand the agent's perspective
   - Makes team composition clearer

2. **Goal**: Defines current objective
   - Separates "what to do" from "who you are"
   - Enables dynamic task assignment

3. **Backstory**: Provides context and expertise
   - Enriches agent responses with appropriate depth
   - Optional but valuable for complex agents

4. **Constraints**: Define boundaries
   - Explicit limitations improve safety
   - Clear rules reduce undesired behaviors

### Why Inheritance Over Functions?

We chose to extend `ConversableAgent` because:

1. **Consistency**: AG2 uses inheritance for all agent types
2. **Encapsulation**: Properties and methods stay together
3. **Discoverability**: IDEs understand the structure
4. **Future-proof**: Easy to add methods without breaking changes

### Backward Compatibility

PersonaAgent is a pure addition:
- Extends ConversableAgent without modifying it
- Works with all existing AG2 features
- Can be mixed with standard agents
- No breaking changes to any AG2 APIs

## Performance Benefits

Persona-based prompts improve LLM performance:

1. **Better Context Understanding**: Clear role separation helps models
2. **Reduced Confusion**: Explicit goals prevent task drift
3. **Consistent Outputs**: Constraints guide behavior
4. **Easier Debugging**: Know exactly what each component does

## FAQ

**Q: Does this replace ConversableAgent?**
A: No, it extends it. All ConversableAgent features still work.

**Q: Can I mix PersonaAgent with regular agents?**
A: Yes, they're fully compatible in group chats and conversations.

**Q: What if I need custom system message formatting?**
A: Pass additional `system_message` in kwargs - it gets appended.

**Q: Does this work with function calling?**
A: Yes, all ConversableAgent features including function calling work normally.

**Q: How do I contribute improvements?**
A: Submit PRs to enhance the structure while maintaining backward compatibility.

## See Also

* [AG2](https://ag2.ai/)
