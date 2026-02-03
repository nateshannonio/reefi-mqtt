# Contributing to ReeFi MQTT Bridge

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful and constructive. We're all here to make aquarium automation better!

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/reefi-mqtt.git
   cd reefi-mqtt
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.9+
- MQTT broker (for testing)
- ReeFi Uno Pro device (or access to one)

### Install Development Dependencies

```bash
pip3 install -r requirements.txt
pip3 install flake8 pylint pytest black
```

### Install Git Hooks

```bash
git config core.hooksPath .githooks
```

This enables pre-commit checks to prevent accidentally committing secrets.

## Making Changes

### Code Style

- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use descriptive variable names

#### Format Your Code

```bash
# Auto-format with black
black reefi_mqtt.py

# Check with flake8
flake8 reefi_mqtt.py --max-line-length=120

# Lint with pylint
pylint reefi_mqtt.py
```

### Configuration Files

- **Never commit `config.py`** - It contains secrets!
- Update `config.example.py` if you add new configuration options
- Document all configuration options with comments

### Documentation

- Update README.md if you change functionality
- Update CHANGELOG.md with your changes
- Add inline comments for complex logic
- Update docs/ if needed

## Testing

### Manual Testing

1. Copy your changes to `/opt/reefi-mqtt/`
2. Restart the service: `sudo systemctl restart reefi-mqtt`
3. Check logs: `sudo journalctl -u reefi-mqtt -f`
4. Verify MQTT messages: `mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_#" -v`
5. Check Home Assistant discovery

### Test Checklist

- [ ] Bridge starts without errors
- [ ] Connects to MQTT broker
- [ ] Polls ReeFi device successfully
- [ ] Publishes correct MQTT messages
- [ ] Discovery config is valid JSON
- [ ] Temperature conversion works (F→C)
- [ ] Graceful shutdown on Ctrl+C
- [ ] Service restarts automatically on failure

## Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for SSL/TLS MQTT connections"
git commit -m "Fix temperature conversion rounding error"
git commit -m "Update documentation for multi-device setup"

# Bad
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

### Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add support for ReeFi Duo models

Add configuration option for dual-head ReeFi lights.
Update discovery to publish separate sensors for each head.

Closes #42
```

## Pull Request Process

1. **Update documentation** - README, CHANGELOG, etc.
2. **Test thoroughly** - Ensure everything works
3. **Check for secrets** - Run pre-commit hook
4. **Create PR** - Use the PR template
5. **Respond to reviews** - Address feedback promptly

### PR Checklist

- [ ] Code follows project style
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] No secrets in commits
- [ ] Tested with real ReeFi device
- [ ] CI/CD passes
- [ ] PR description is complete

## What to Contribute

### Good First Issues

- Documentation improvements
- Bug fixes
- Error message improvements
- Configuration validation
- Unit tests

### Feature Ideas

- Support for additional ReeFi models
- MQTT control (not just monitoring)
- Web interface for configuration
- Statistics tracking
- Alert notifications
- Docker container
- Home Assistant add-on

### Areas Needing Help

- Testing on different Python versions
- Testing on different Linux distributions
- Documentation in other languages
- Performance optimization
- Error handling improvements

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml).

Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Logs (`journalctl -u reefi-mqtt -n 50`)
- Configuration (redact secrets!)
- Environment (Python version, OS, HA version)

## Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml).

Include:
- Problem statement
- Proposed solution
- Use cases
- Examples

## Code Review Process

1. Maintainer reviews PR
2. CI/CD checks must pass
3. At least one approval required
4. Maintainer merges when ready

### Review Criteria

- Code quality and style
- Functionality works as described
- Documentation is clear
- No security issues
- No performance regressions

## Release Process

1. Update version in CHANGELOG.md
2. Commit: `git commit -m "Bump version to v1.0.1"`
3. Tag: `git tag v1.0.1`
4. Push: `git push --tags`
5. GitHub Actions creates release automatically

## Security

### Reporting Security Issues

**Do NOT open public issues for security vulnerabilities.**

Email: security@example.com (or use GitHub Security Advisories)

### Security Best Practices

- Never commit passwords, API keys, or IP addresses
- Use `config.example.py` as template only
- Validate user input
- Use environment variables for secrets
- Enable git hooks to prevent secret commits

## Questions?

- Open a [Discussion](https://github.com/yourusername/reefi-mqtt/discussions)
- Check existing [Issues](https://github.com/yourusername/reefi-mqtt/issues)
- Read the [Documentation](docs/)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ReeFi MQTT Bridge!** 🐠💡
