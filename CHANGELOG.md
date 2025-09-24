# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-09-24

### Added
- Initial release of PersonaAgent for AG2
- Core PersonaAgent class extending AG2's ConversableAgent
- Support for persona-based agent creation with role, goal, backstory, and constraints
- Dynamic persona updates without full prompt rewrites
- Functional interface via `persona_agent()` function
- Configuration-based agent creation via `persona_agent_from_config()`
- Full type annotations and comprehensive test suite
- PyPI-ready package structure following 2025 best practices
- GitHub Actions workflow for automated PyPI publishing
- Pre-commit hooks for code quality with ruff and mypy
- Minimum Python 3.11 requirement

### Features
- Authentic character embodiment through structured persona components
- Seamless integration with existing AG2 workflows
- Support for YAML and JSON configuration files
- Comprehensive documentation with examples
- MIT license for open source usage

[Unreleased]: https://github.com/rsnodgrass/ag2-persona-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rsnodgrass/ag2-persona-agent/releases/tag/v0.1.0