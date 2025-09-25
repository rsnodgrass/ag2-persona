# Publishing to PyPI

This document outlines how to publish the `ag2-persona` package to PyPI using the modern 2025 workflow with `uv` and `hatchling`.

## Prerequisites

1. Install `uv` for fast package management:
   ```bash
   pip install uv
   ```

2. Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (for production)
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing [optional])

3. Set up API tokens (recommended over passwords):
   - Generate tokens at: https://pypi.org/manage/account/token/
   - Store in `~/.pypirc` or use `keyring`

## Modern 2025 Workflow

This project uses:
- **uv**: Fast package/dependency manager for dev/test/CI
- **hatchling**: Modern build backend for packaging/publishing

## Publishing Process

### 1. Development Setup

```bash
uv sync

# Install with dev extras
uv sync --extra dev
```

### 2. Testing and Quality Checks

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format --check .

# Run type checking
uv run mypy ag2_persona/
```

### 3. Update Project Version

Update version in `pyproject.toml`:
```toml
version = "0.1.2"  # Increment as needed
```

Version changes will be tracked in GitHub releases instead of a separate changelog file.

### 4. Build the Package

```bash
# Clean any previous builds
rm -rf dist/

# Build using uv (which uses hatchling backend)
uv build
```

This creates:
- `dist/ag2_persona-X.X.X.tar.gz` (source distribution)
- `dist/ag2_persona-X.X.X-py3-none-any.whl` (wheel distribution)

### 5. Verify the Build

The package is automatically validated during the build process with hatchling:

```bash
# List built files
ls -la dist/

# Package validation is built into hatchling - no additional tools needed
```

### 6. Test Upload (Recommended)

First upload to TestPyPI to verify everything works:

```bash
# Upload to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Test install from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ ag2-persona
```

### 7. Production Upload

Once verified, upload to production PyPI:

```bash
# Publish to PyPI
uv publish
```

## Alternative: Using GitHub Actions (Automated)

The repository can include a GitHub Actions workflow for automated publishing.

### Manual Trigger Workflow

Create `.github/workflows/pypi-publish.yml`:

```yaml
name: Publish to PyPI

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'testpypi'
        type: choice
        options:
        - testpypi
        - pypi

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4
      with:
        version: "latest"

    - name: Set up Python
      run: uv python install

    - name: Build package
      run: uv build

    - name: Publish to TestPyPI
      if: github.event.inputs.environment == 'testpypi'
      run: uv publish --index-url https://test.pypi.org/legacy/
      env:
        UV_PUBLISH_TOKEN: ${{ secrets.TEST_PYPI_API_TOKEN }}

    - name: Publish to PyPI
      if: github.event.inputs.environment == 'pypi'
      run: uv publish
      env:
        UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

## Why This Modern Approach?

### Benefits of uv + hatchling:

1. **Speed**: uv is 10-100x faster than pip for dependency resolution
2. **Modern**: Uses latest Python packaging standards (PEP 621, PEP 668)
3. **Unified**: Single tool for development, building, and publishing
4. **Reliable**: Built-in validation and dependency locking
5. **Future-proof**: Actively developed modern tooling

### Migration from old tools:

- `python -m build && python -m twine upload dist/*` → `uv build && uv publish`
- `pip install -e .` → `uv sync`
- `pytest` → `uv run pytest`
- Validation is now built-in with hatchling

## Troubleshooting

### Common Issues

1. **Version already exists**: Increment version number in `pyproject.toml`
2. **Authentication failed**: Check API tokens in `~/.pypirc` or `UV_PUBLISH_TOKEN` env var
3. **Package validation errors**: Check build output from `uv build` for details
4. **Dependency conflicts**: Use `uv lock --upgrade` to update lockfile

### Environment Variables

Set these for automated publishing:

```bash
# For PyPI
export UV_PUBLISH_TOKEN="pypi-..."

# For TestPyPI
export UV_PUBLISH_TOKEN="pypi-..." UV_PUBLISH_URL="https://test.pypi.org/legacy/"
```

### Local Testing Commands

```bash
# Full development setup
uv sync --extra dev

# Run all checks
uv run pytest
uv run ruff check . --fix
uv run mypy ag2_persona/

# Build and validate
uv build

# Build documentation (optional)
uv run mkdocs build
```

## Documentation

The project documentation is available at: https://rsnodgrass.github.io/ag2-persona/

To build and serve documentation locally:
```bash
uv run mkdocs serve  # Serves at http://127.0.0.1:8000
```

## Summary

The modern 2025 workflow is:

```bash
# Development
uv sync --extra dev
uv run pytest

# Publishing
uv build              # build with validation
uv publish            # to PyPI
```

This replaces the old multi-tool workflow with a single, fast, modern tool.
