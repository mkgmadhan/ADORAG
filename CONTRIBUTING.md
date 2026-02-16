# Contributing to ADO RAG

Thank you for your interest in contributing to ADO RAG! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, OS, Azure services)

**Note**: When you open an issue, our automated triage workflow will automatically label it based on the content. See [Issue Triage Documentation](.github/ISSUE_TRIAGE.md) for details.

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Any implementation ideas you may have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines below
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Commit your changes** with clear, descriptive commit messages
6. **Push to your fork** and submit a pull request

### Code Style Guidelines

- **Python**: Follow PEP 8 style guide
- **Imports**: Group standard library, third-party, and local imports
- **Docstrings**: Use clear docstrings for classes and functions
- **Type Hints**: Use type hints where appropriate
- **Comments**: Add comments for complex logic

### Testing

Before submitting a PR:
- Test your changes locally
- Run `python test_config.py` to validate configuration
- Ensure the app runs without errors: `streamlit run app.py`
- Test with real Azure DevOps data if possible

### Commit Messages

Use clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when applicable

Examples:
```
Add bug triage feature for duplicate detection
Fix sync progress indicator calculation
Update README with deployment instructions
```

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ADORAG.git
   cd ADORAG
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your test credentials

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

Key files to understand:
- `app.py` - Streamlit UI entry point
- `src/rag_service.py` - RAG query processing and LLM integration
- `src/sync_service.py` - Sync orchestration
- `src/search_service.py` - Azure AI Search operations
- `src/ado_service.py` - Azure DevOps API integration
- `src/embedding_service.py` - Embedding generation

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Reach out via GitHub discussions

Thank you for contributing to ADO RAG! 🎉
