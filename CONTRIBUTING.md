# Contributing to OrchX

Thank you for your interest in contributing to OrchX! We welcome bug reports, feature requests, documentation improvements, and code contributions.

---

## Code of Conduct

Please ensure all interactions in issues, pull requests, and discussions remain respectful, constructive, and inclusive.

---

## How to Contribute

### 1. Reporting Bugs
- Search existing issues to ensure the bug hasn't already been reported.
- Open a new issue with a clear title, reproduction steps, expected vs. actual behavior, and relevant logs (ensure no secrets or API keys are included).

### 2. Suggesting Enhancements
- Open a feature request issue explaining the motivation, proposed API or contract changes, and practical use cases.

### 3. Pull Requests
- Fork the repository and create a feature branch off `main`.
- Follow Python PEP 8 formatting standards.
- Ensure all existing tests pass and add unit/integration tests for any new provider adapters or core features.
- Keep PRs focused on a single logical change.

---

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/orchx.git
   cd orchx
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e packages/orchx-core
   pip install -e packages/orchx-runtime
   pip install pytest pytest-asyncio
   ```

3. Run unit tests:
   ```bash
   pytest
   ```

---

## Security

Do **NOT** submit security vulnerabilities via public GitHub issues. Please refer to [SECURITY.md](SECURITY.md) for responsible disclosure instructions.
