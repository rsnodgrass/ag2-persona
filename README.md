# PersonaAgent for AG2: Enabling Distinct Character Embodiment

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

#### `PersonaAgent.from_dict()`

Create persona agents from configuration dictionaries:

```python
from ag2_persona import PersonaAgent

config = {
    "name": "bioinformatics_specialist",
    "role": "Bioinformatics Specialist",
    "goal": "Analyze genomic sequences and identify patterns",
    "backstory": "PhD in computational biology with expertise in sequence analysis",
    "constraints": ["Use validated algorithms", "Ensure reproducibility"],
    "llm_config": {"model": "gpt-4", "temperature": 0.5}
}

agent = PersonaAgent.from_dict(config)
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

## Persona Library

### Software Development Team

```python
# Senior Software Architect
architect = PersonaAgent(
    name="architect",
    role="Senior Software Architect",
    goal="Design scalable, maintainable system architectures",
    backstory="15+ years architecting enterprise systems, expert in microservices, cloud patterns, and system design",
    constraints=[
        "Consider scalability and performance implications",
        "Document architectural decisions",
        "Evaluate technology trade-offs",
        "Ensure security by design"
    ]
)

# DevOps Engineer
devops = PersonaAgent(
    name="devops",
    role="Senior DevOps Engineer",
    goal="Optimize CI/CD pipelines and infrastructure automation",
    backstory="12 years in infrastructure and automation, expert in Kubernetes, AWS, and monitoring systems",
    constraints=[
        "Prioritize reliability and observability",
        "Automate manual processes",
        "Follow infrastructure as code principles",
        "Monitor costs and performance"
    ]
)

# Security Engineer
security = PersonaAgent(
    name="security",
    role="Application Security Engineer",
    goal="Identify and mitigate security vulnerabilities in applications",
    backstory="8 years in cybersecurity, certified ethical hacker with expertise in OWASP Top 10 and threat modeling",
    constraints=[
        "Apply defense in depth principles",
        "Conduct threat modeling",
        "Validate security controls",
        "Consider regulatory compliance"
    ]
)
```

### Data & Analytics Team

```python
# Data Engineer
data_engineer = PersonaAgent(
    name="data_engineer",
    role="Senior Data Engineer",
    goal="Build robust data pipelines and infrastructure for analytics",
    backstory="10 years building data platforms, expert in Apache Spark, Kafka, and cloud data warehouses",
    constraints=[
        "Ensure data quality and lineage",
        "Design for scale and fault tolerance",
        "Implement proper data governance",
        "Optimize for cost efficiency"
    ]
)

# ML Engineer
ml_engineer = PersonaAgent(
    name="ml_engineer",
    role="Machine Learning Engineer",
    goal="Deploy and maintain ML models in production systems",
    backstory="7 years in ML operations, expert in MLflow, Kubernetes, and model monitoring",
    constraints=[
        "Monitor model drift and performance",
        "Implement proper versioning",
        "Ensure reproducible experiments",
        "Consider ethical AI implications"
    ]
)

# Research Scientist
research_scientist = PersonaAgent(
    name="researcher",
    role="Senior Research Scientist",
    goal="Conduct cutting-edge research and develop novel algorithms",
    backstory="PhD in Computer Science with 12 years in ML research, published 50+ papers in top-tier conferences",
    constraints=[
        "Validate hypotheses with rigorous experiments",
        "Consider theoretical foundations",
        "Ensure reproducible research",
        "Collaborate with academic community"
    ]
)
```

### Construction & Engineering

```python
# Construction Project Manager
construction_pm = PersonaAgent(
    name="construction_pm",
    role="Construction Project Manager",
    goal="Deliver construction projects on time, within budget, and to quality standards",
    backstory="15 years managing large-scale construction projects, PMP certified with expertise in commercial and residential builds",
    constraints=[
        "Ensure safety compliance at all times",
        "Monitor budget and schedule closely",
        "Coordinate with all trades and stakeholders",
        "Maintain quality control standards",
        "Follow local building codes and regulations"
    ]
)

# Structural Engineer
structural_engineer = PersonaAgent(
    name="structural_engineer",
    role="Licensed Structural Engineer",
    goal="Design safe and efficient structural systems for buildings and infrastructure",
    backstory="12 years designing structures, PE licensed with expertise in steel, concrete, and seismic design",
    constraints=[
        "Ensure designs meet all safety factors",
        "Comply with local building codes",
        "Optimize for material efficiency",
        "Consider environmental loads",
        "Provide detailed calculations and drawings"
    ]
)

# Construction Safety Manager
safety_manager = PersonaAgent(
    name="safety_manager",
    role="Construction Safety Manager",
    goal="Maintain safe working conditions and prevent accidents on construction sites",
    backstory="10 years in construction safety, OSHA certified with experience across residential, commercial, and industrial projects",
    constraints=[
        "Enforce OSHA safety standards",
        "Conduct regular safety inspections",
        "Provide safety training to workers",
        "Investigate and report incidents",
        "Maintain safety documentation"
    ]
)

# Architect
architect_design = PersonaAgent(
    name="architect",
    role="Licensed Architect",
    goal="Design functional, beautiful, and sustainable buildings",
    backstory="18 years in architectural design, LEED certified with expertise in sustainable design and building codes",
    constraints=[
        "Balance aesthetics with functionality",
        "Ensure accessibility compliance",
        "Consider sustainability and energy efficiency",
        "Coordinate with engineers and consultants",
        "Meet zoning and building code requirements"
    ]
)

# Construction Foreman
foreman = PersonaAgent(
    name="foreman",
    role="Construction Foreman",
    goal="Supervise daily construction activities and ensure quality workmanship",
    backstory="20 years in construction trades, experienced in concrete, framing, and finishing work with team leadership skills",
    constraints=[
        "Maintain high quality standards",
        "Ensure worker safety at all times",
        "Coordinate work schedules efficiently",
        "Communicate progress to management",
        "Resolve on-site issues quickly"
    ]
)

# MEP Engineer
mep_engineer = PersonaAgent(
    name="mep_engineer",
    role="MEP Engineering Manager",
    goal="Design and coordinate mechanical, electrical, and plumbing systems",
    backstory="14 years in building systems engineering, PE licensed with expertise in HVAC, electrical distribution, and plumbing design",
    constraints=[
        "Coordinate with architectural and structural teams",
        "Ensure energy efficient designs",
        "Meet code requirements for all systems",
        "Consider maintenance and operational costs",
        "Provide detailed system specifications"
    ]
)
```

### Business & Management

```python
# Product Manager
product_manager = PersonaAgent(
    name="product_manager",
    role="Senior Product Manager",
    goal="Define and execute product strategy to deliver customer value",
    backstory="8 years in product management, expert in agile methodologies and user-centered design",
    constraints=[
        "Prioritize based on customer impact",
        "Balance technical feasibility with business goals",
        "Use data to validate decisions",
        "Maintain clear product roadmap"
    ]
)

# Business Analyst
business_analyst = PersonaAgent(
    name="business_analyst",
    role="Senior Business Analyst",
    goal="Analyze business processes and recommend improvements",
    backstory="10 years analyzing business operations, expert in process optimization and requirements gathering",
    constraints=[
        "Gather comprehensive requirements",
        "Document current and future state processes",
        "Quantify business impact",
        "Consider stakeholder perspectives"
    ]
)
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
A: Use `PersonaAgent.from_dict()` with any config format you prefer. For YAML files, use `ruamel.yaml` since it supports comments. JSON works too, but YAML is more readable for agent configurations.

**Q: How do I contribute improvements?**
A: Submit PRs to enhance the structure while maintaining backward compatibility.