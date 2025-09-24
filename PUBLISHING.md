# Publishing to PyPI

This document outlines how to publish the `ag2-persona` package to PyPI.

## Prerequisites

1. Install the package with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Or install build tools manually:
   ```bash
   pip install build twine
   ```

2. Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (for production)
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing [optional])

3. Set up API tokens (recommended over passwords):
   - Generate tokens at: https://pypi.org/manage/account/token/
   - Store in `~/.pypirc` or use `keyring`

## Publishing Process

### 1. Update Version

Update version in `pyproject.toml`:
```toml
version = "0.1.1"  # Increment as needed
```

Update `CHANGELOG.md` with new version details.

### 2. Build the Package
W
```bash
# Clean any previous builds
rm -rf dist/ build/

# Build source and wheel distributions
python -m build
```

This creates:
- `dist/ag2_persona-X.X.X.tar.gz` (source distribution)
- `dist/ag2_persona-X.X.X-py3-none-any.whl` (wheel distribution)

### 3. Verify the Build

```bash
# Check the package for common issues
twine check dist/*
```

### 4. Test Upload (Recommended)

First upload to TestPyPI to verify everything works:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ ag2-persona
```

### 5. Production Upload

Once verified, upload to production PyPI:

```bash
twine upload dist/*
```

## Using GitHub Actions (Automated)

The repository includes a GitHub Actions workflow at `.github/workflows/pypi-publish.yml`.

### Manual Trigger
1. Go to Actions tab in GitHub
2. Select "Publish Python Package to PyPI"
3. Click "Run workflow"
4. Set `dry_run: true` for TestPyPI or `dry_run: false` for production

### Automatic on Release (Future)
Uncomment the release trigger in the workflow to auto-publish on GitHub releases:

```yaml
on:
  release:
    types: [published]
```

## Troubleshooting

### Common Issues

1. **Version already exists**: Increment version number in `pyproject.toml`
2. **Authentication failed**: Check API tokens or credentials
3. **Package validation errors**: Run `twine check dist/*` for details

### Testing Locally

Manual commands:
```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run linting
ruff check .
ruff format --check .

# Run type checking
mypy ag2_persona/
```

## Security Notes

- Never commit API tokens to git
- Use PyPI's trusted publishing for GitHub Actions when possible
- Always test on TestPyPI before production uploads
- Consider using `keyring` to store credentials securely