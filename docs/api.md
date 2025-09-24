# API Reference

Complete API documentation for AG2 PersonaAgent.

## PersonaAgent

::: ag2_persona.PersonaAgent
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Functional Interface

::: ag2_persona.persona_agent
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

::: ag2_persona.persona_agent_from_config
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## System Message Structure

PersonaAgent generates structured system messages from persona components:

```
# Role: [role]

## Goal
[goal]

## Background
[backstory]

## Constraints
- [constraint 1]
- [constraint 2]
- ...
```

### Example

For a PersonaAgent with:
- **Role**: "Code Reviewer"
- **Goal**: "Review code for quality and security"
- **Backstory**: "10+ years Python development experience"
- **Constraints**: ["Focus on security", "Be constructive"]

The generated system message would be:

```
# Role: Code Reviewer

## Goal
Review code for quality and security

## Background
10+ years Python development experience

## Constraints
- Focus on security
- Be constructive
```

This structured approach ensures consistent persona representation while maintaining AG2 compatibility.