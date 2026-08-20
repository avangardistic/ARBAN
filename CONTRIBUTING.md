# Contributing to ARBAN

Thank you for your interest in contributing to ARBAN! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers and help them learn

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Open an issue describing the feature
2. Explain the use case
3. Discuss implementation approach

### Pull Requests

1. Fork the repository
2. Create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Write/update tests
5. Ensure all tests pass:
   ```bash
   pytest
   ruff check .
   black --check .
   mypy backend/app
   ```
6. Commit with clear messages
7. Push and open a PR

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions small and focused
- Prefer clarity over cleverness

### Testing Requirements

- New features must include tests
- Maintain or improve coverage
- Test edge cases and error conditions

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/arban.git
cd arban

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend
npm install

# Start services
docker compose up -d postgres redis
```

## Questions?

Open an issue for discussion.
