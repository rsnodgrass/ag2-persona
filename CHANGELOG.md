# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-09-25

- **PersonaBuilder Pattern**: New fluent interface for creating PersonaAgent instances with validation
  - `PersonaBuilder.from_yaml()` and `PersonaBuilder.from_dict()` for flexible configuration loading
  - Runtime LLM configuration separation from persona definition
  - Explicit human input mode methods: `human_input_never()`, `human_input_always()`, `human_input_terminate()`
  - Comprehensive persona library with YAML configuration
- **AG2 Best Practices Support**: Full compatibility with AG2's ConversableAgent patterns
  - Automatic `description` generation for GroupChat agent selection
  - Support for `human_input_mode` configuration
  - Seamless integration with GroupChat and GroupChatManager
- **Enhanced Documentation**:
  - Multi-agent construction team example with hybrid conversation pattern
  - MkDocs documentation site with Material Design
  - Documentation restructured to emphasize YAML library benefits
  - FAQ format modernized with collapsible sections
- **Asynchronous Support (Optional)**:
  - AsyncPersonaBuilder that uses deferred execution queue enabling true single-chain syntax: `await
  (builder.method1().method2().build())`
  - Optional `aiofiles` dependency for non-blocking I/O
  - New dependency extras: `async`, `yaml-async`
- **Code Cleanup**:
  - Type annotations and linting issues
  - Error handling improvements

## [0.1.0] - 2025-09-23

### Features
- Initial release of PersonaAgent for AG2
- Core PersonaAgent class extending AG2's ConversableAgent
- Authentic character embodiment through structured persona components
- Seamless integration with existing AG2 workflows
- Comprehensive documentation with examples
- Support for persona-based agent creation with role, goal, backstory, and constraints
- Dynamic persona updates without full prompt rewrites
- Full type annotations and comprehensive test suite
- PyPI-ready package structure following 2025 best practices

[Unreleased]: https://github.com/rsnodgrass/ag2-persona-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rsnodgrass/ag2-persona-agent/releases/tag/v0.1.0
