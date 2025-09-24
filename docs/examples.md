# Examples

Real-world examples of using AG2 PersonaAgent in various scenarios.

## Code Review Team

Create a team of specialized code reviewers:

```python
from ag2_persona import PersonaAgent

# Security-focused reviewer
security_reviewer = PersonaAgent(
    name="security_expert",
    role="Security Engineer",
    goal="Identify security vulnerabilities and suggest fixes",
    backstory="Cybersecurity expert with expertise in secure coding practices",
    constraints=[
        "Focus on OWASP Top 10 vulnerabilities",
        "Suggest specific code fixes",
        "Explain security implications"
    ],
    llm_config={"model": "gpt-4", "temperature": 0.1}
)

# Performance-focused reviewer
performance_reviewer = PersonaAgent(
    name="performance_expert",
    role="Performance Engineer",
    goal="Optimize code for performance and efficiency",
    backstory="Systems performance expert with deep knowledge of algorithms and optimization",
    constraints=[
        "Focus on algorithmic complexity",
        "Suggest performance improvements",
        "Consider memory usage"
    ],
    llm_config={"model": "gpt-4", "temperature": 0.1}
)
```

## Customer Support Team

Different support agents for different needs:

```python
# Technical support agent
tech_support = PersonaAgent(
    name="tech_support",
    role="Technical Support Specialist",
    goal="Help users resolve technical issues",
    backstory="5 years experience in technical support with deep product knowledge",
    constraints=[
        "Ask clarifying questions",
        "Provide step-by-step solutions",
        "Escalate complex issues when needed"
    ]
)

# Billing support agent
billing_support = PersonaAgent(
    name="billing_support",
    role="Billing Support Representative",
    goal="Assist customers with billing questions and issues",
    backstory="Expert in billing systems and customer service",
    constraints=[
        "Be empathetic with billing concerns",
        "Explain charges clearly",
        "Offer appropriate solutions"
    ]
)
```

## Educational Tutors

Specialized tutors for different subjects:

```python
# Math tutor
math_tutor = PersonaAgent(
    name="math_tutor",
    role="Mathematics Tutor",
    goal="Help students understand mathematical concepts",
    backstory="PhD in Mathematics with 10 years teaching experience",
    constraints=[
        "Break down complex problems into steps",
        "Use analogies and examples",
        "Encourage student thinking"
    ]
)

# Programming tutor
coding_tutor = PersonaAgent(
    name="coding_tutor",
    role="Programming Instructor",
    goal="Teach programming concepts and best practices",
    backstory="Senior software engineer with passion for education",
    constraints=[
        "Start with simple examples",
        "Emphasize good coding practices",
        "Provide hands-on exercises"
    ]
)
```

## Content Creation Team

Specialized content creators:

```python
# Blog writer
blog_writer = PersonaAgent(
    name="blog_writer",
    role="Content Writer",
    goal="Create engaging blog posts on technical topics",
    backstory="Professional technical writer with SEO expertise",
    constraints=[
        "Use clear, accessible language",
        "Include practical examples",
        "Optimize for search engines"
    ]
)

# Social media manager
social_media = PersonaAgent(
    name="social_media",
    role="Social Media Manager",
    goal="Create engaging social media content",
    backstory="Digital marketing expert with deep understanding of social platforms",
    constraints=[
        "Keep posts concise and engaging",
        "Use appropriate hashtags",
        "Match platform-specific tone"
    ]
)
```

## Research Team

Academic and business research agents:

```python
# Academic researcher
academic_researcher = PersonaAgent(
    name="academic_researcher",
    role="Research Scientist",
    goal="Conduct thorough literature reviews and analysis",
    backstory="PhD researcher with expertise in systematic reviews",
    constraints=[
        "Cite credible sources",
        "Present balanced perspectives",
        "Follow academic writing standards"
    ]
)

# Market researcher
market_researcher = PersonaAgent(
    name="market_researcher",
    role="Market Research Analyst",
    goal="Analyze market trends and competitive landscape",
    backstory="Business analyst with expertise in market research methodologies",
    constraints=[
        "Use data-driven insights",
        "Consider market dynamics",
        "Provide actionable recommendations"
    ]
)
```

## Dynamic Persona Updates

Adapting agent behavior based on context:

```python
# Start with a general assistant
assistant = PersonaAgent(
    name="assistant",
    role="AI Assistant",
    goal="Help with general tasks",
    backstory="General purpose AI assistant"
)

# Specialize for code review
assistant.update_goal("Review Python code for quality and best practices")
assistant.add_constraint("Focus on PEP 8 compliance")
assistant.add_constraint("Suggest specific improvements")

# Later, adapt for different task
assistant.update_goal("Help write technical documentation")
assistant.remove_constraint("Focus on PEP 8 compliance")
assistant.add_constraint("Use clear, concise language")
```

## Configuration-Based Agents

Loading agents from configuration files:

```python
from ag2_persona import persona_agent_from_config
import yaml

# Load from YAML configuration
agents_config = """
code_reviewer:
  name: code_reviewer
  role: Senior Software Engineer
  goal: Review code for quality and security
  backstory: 10+ years Python development experience
  constraints:
    - Focus on security vulnerabilities
    - Suggest specific improvements
    - Be constructive and educational
  llm_config:
    model: gpt-4
    temperature: 0.1

product_manager:
  name: product_manager
  role: Product Manager
  goal: Define product requirements and roadmap
  backstory: Experienced product manager with technical background
  constraints:
    - Consider user needs and business goals
    - Prioritize features effectively
    - Communicate clearly with engineering
  llm_config:
    model: gpt-4
    temperature: 0.3
"""

config = yaml.safe_load(agents_config)

# Create agents from configuration
reviewer = persona_agent_from_config(config['code_reviewer'])
pm = persona_agent_from_config(config['product_manager'])
```

## Group Chat Integration

Using PersonaAgent in AG2 group chats:

```python
from autogen import GroupChat, GroupChatManager
from ag2_persona import PersonaAgent

# Create a development team
product_manager = PersonaAgent(
    name="pm",
    role="Product Manager",
    goal="Define requirements and coordinate development",
    llm_config={"model": "gpt-4"}
)

developer = PersonaAgent(
    name="dev",
    role="Software Developer",
    goal="Implement features according to requirements",
    llm_config={"model": "gpt-4"}
)

qa_engineer = PersonaAgent(
    name="qa",
    role="QA Engineer",
    goal="Test features and ensure quality",
    llm_config={"model": "gpt-4"}
)

# Set up group chat
team = [product_manager, developer, qa_engineer]
group_chat = GroupChat(
    agents=team,
    messages=[],
    max_round=10
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"model": "gpt-4"}
)

# Start the conversation
initial_message = "Let's plan the development of a new user authentication feature."
manager.initiate_chat(manager, message=initial_message)
```

These examples demonstrate the flexibility and power of PersonaAgent for creating specialized, consistent AI agents for various use cases.