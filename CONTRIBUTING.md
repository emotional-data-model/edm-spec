# Contributing to EDM

Thank you for your interest in contributing to the Emotional Data Model (EDM) specification.

## Status: Release Candidate

EDM v0.4 is a **Release Candidate** actively seeking community feedback before v1.0. Your input helps shape the standard.

## Ways to Contribute

### 1. Report Issues

Found a bug, inconsistency, or unclear documentation?

- Open an [Issue](https://github.com/deepadata/deepadata-edm-spec/issues)
- Include: what you expected, what happened, and relevant context

### 2. Suggest Improvements

Have ideas for schema improvements?

- Open a [Discussion](https://github.com/deepadata/deepadata-edm-spec/discussions) first
- Explain the use case and proposed change
- Consider backward compatibility implications

### 3. Submit Pull Requests

For schema or documentation changes:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-improvement`)
3. Make your changes
4. Run validation: `npm run validate`
5. Submit a Pull Request with clear description

### 4. Implement and Share

Build something with EDM and share your experience:

- Validators in other languages
- Integration examples
- Extraction tools
- Storage adapters

## Contribution Guidelines

### Schema Changes

- **Backward compatibility**: Breaking changes require strong justification
- **Profile completeness**: Artifacts must contain only the domains defined for the declared profile
- **Non-inferential**: No fields for psychological inference or behavioral prediction
- **Governance-first**: Changes should support compliance, not hinder it

### Documentation

- Keep language clear and concise
- Include practical examples
- Update relevant cross-references

### Code Style

- Use consistent formatting
- Include comments for complex logic
- Follow existing patterns in the codebase

## Review Process

1. All PRs require review before merging
2. Schema changes require additional scrutiny for breaking changes
3. Discussions happen in PR comments or GitHub Discussions

## Questions?

- Email: jason@deepadata.com
- GitHub Discussions: For design questions
- Issues: For bugs and specific improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make emotional AI safer and more governed.
