# Security Policy

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Do NOT create a public issue.**

Instead:
1. Email: security@arban.dev (placeholder)
2. Or create a private vulnerability report on GitHub
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- We will acknowledge your report within 48 hours
- We aim to resolve critical issues within 7 days
- We will keep you informed of our progress

## Security Best Practices Followed

### Code Security

- No secrets committed to Git
- Input validation on all API endpoints
- Rate limiting enabled
- CORS properly configured
- Dependencies pinned and audited

### Data Security

- No user funds handled
- No private keys stored
- No wallet credentials managed
- Read-only data access

### Infrastructure Security

- Docker containerization
- Database isolation
- Network segmentation
- Health checks and monitoring

## Known Limitations

### MVP Scope

ARBAN MVP is **read-only** by design:

- ❌ No trade execution
- ❌ No order placement
- ❌ No wallet connections
- ❌ No fund management
- ❌ No user authentication required

This significantly reduces the attack surface.

### External Dependencies

ARBAN relies on external prediction market APIs:

- Provider API changes may break functionality
- Rate limits are respected
- Failures are handled gracefully

## Security Checklist for Contributors

When contributing code, ensure:

- [ ] No hardcoded secrets or API keys
- [ ] Input validation on user-provided data
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are up-to-date
- [ ] No unnecessary permissions requested
- [ ] Logging doesn't include sensitive data

## Third-Party Libraries

ARBAN uses these key dependencies:

| Library | Purpose | Security Considerations |
|---------|---------|------------------------|
| FastAPI | Web framework | Keep updated for security patches |
| SQLAlchemy | ORM | Use parameterized queries (default) |
| httpx | HTTP client | Validate SSL certificates |
| Pydantic | Validation | Leverage for input sanitization |

Regularly audit dependencies:

```bash
pip-audit
npm audit
```

## Incident Response

In case of a security incident:

1. **Containment**: Isolate affected systems
2. **Assessment**: Determine scope and impact
3. **Notification**: Inform affected users if necessary
4. **Resolution**: Fix the vulnerability
5. **Review**: Document lessons learned

## Contact

For security-related questions:
- GitHub Issues (for non-sensitive topics)
- Email: security@arban.dev (for vulnerabilities)

---

**Last Updated**: 2024
