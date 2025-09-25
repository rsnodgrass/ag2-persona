# AG2-Persona Documentation

This directory contains the source files for the ag2-persona documentation website.

## 📖 Live Documentation

The complete documentation is available at: **https://rsnodgrass.github.io/ag2-persona/**

## Local Development

To build and serve the documentation locally:

```bash
# Install dependencies
uv sync --extra dev

# Serve locally with hot reload
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

## Documentation Structure

- `index.md` - Main landing page
- `getting-started.md` - Installation and basic usage
- `examples.md` - Code examples and use cases
- `api.md` - API reference documentation

The documentation is built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).
