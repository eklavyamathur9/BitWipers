# Contributing to BitWipers

Thank you for your interest in contributing to BitWipers! This document provides guidelines for contributing to our secure data wiping solution for trustworthy IT asset recycling.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive in all interactions
- Focus on constructive feedback and solutions
- Respect privacy and security considerations
- Follow responsible disclosure for security issues

## How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check existing issues to avoid duplicates
2. Use the issue template when available
3. Provide detailed reproduction steps
4. Include system information (OS, Python version, etc.)

### Security Vulnerabilities

⚠️ **IMPORTANT**: Do not report security vulnerabilities through public GitHub issues.

For security issues:
1. Email the maintainers privately
2. Include detailed information about the vulnerability
3. Allow reasonable time for response before disclosure
4. Follow responsible disclosure principles

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/BitWipers.git
   cd BitWipers
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Code Standards

#### Python Style Guide
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions and classes

#### Security Guidelines
- Never log sensitive information
- Validate all user inputs
- Use secure random generation for cryptographic operations
- Follow principle of least privilege
- Implement proper error handling without information leakage

#### Testing Requirements
- Write unit tests for all new functionality
- Maintain test coverage above 80%
- Include integration tests for critical paths
- Test on multiple platforms where possible

### Commit Guidelines

Use conventional commits format:
```
type(scope): brief description

Detailed description if needed

Closes #issue-number
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(core): add SSD secure erase support

Implement ATA SECURITY ERASE UNIT command for SSDs
following NIST SP 800-88 guidelines.

Closes #123
```

### Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation as needed
3. Add or update tests for your changes
4. Ensure all tests pass
5. Update the changelog if applicable
6. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Testing instructions

### Review Process

- All submissions require code review
- Maintainers will review PRs within 48-72 hours
- Address review feedback promptly
- Squash commits before merging when requested

## Development Guidelines

### Core Principles

1. **Security First**: All code must prioritize data security and user safety
2. **Cross-Platform**: Ensure compatibility across Windows, Linux, and Android
3. **User-Friendly**: Maintain simplicity in user interface and operation
4. **Standards Compliance**: Follow NIST SP 800-88 and industry standards
5. **Verifiable**: All operations must be auditable and verifiable

### Architecture Guidelines

- Maintain clear separation between GUI and core logic
- Use dependency injection for testability
- Implement proper logging and error handling
- Follow SOLID principles
- Keep modules focused and cohesive

### Testing Strategy

#### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Focus on edge cases and error conditions

#### Integration Tests
- Test component interactions
- Validate end-to-end workflows
- Test certificate generation and verification

#### Security Tests
- Validate data erasure completeness
- Test cryptographic implementations
- Verify secure random generation
- Test privilege escalation handling

### Documentation

- Update README.md for user-facing changes
- Document API changes in docstrings
- Update technical documentation in docs/
- Include code examples where helpful

## Release Process

1. Version following semantic versioning (MAJOR.MINOR.PATCH)
2. Update version numbers in relevant files
3. Update changelog with release notes
4. Create release tag and GitHub release
5. Build and test distribution packages

## Questions and Support

- GitHub Discussions for general questions
- GitHub Issues for bugs and feature requests
- Check existing documentation first
- Be specific and provide context

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation where applicable

---

Thank you for contributing to BitWipers and supporting India's e-waste management and circular economy initiatives!
