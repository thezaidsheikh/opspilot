# Security Policy

## Security Scope

OpsPilot is an evolving software project.

Security issues may include:

- Authentication and authorization weaknesses
- Tenant isolation failures
- Sensitive information exposure
- Prompt injection vulnerabilities
- Unsafe diagnostic tool behavior
- Unauthorized remediation execution
- Dependency vulnerabilities
- Secret or credential exposure

## Reporting a Vulnerability

Please report security vulnerabilities privately through GitHub Security Advisories if private vulnerability reporting is enabled for this repository.

Do not publish exploitable vulnerability details in public issues.

## Secrets Management

Never commit:

- API keys
- Passwords
- Access tokens
- Private keys
- Database credentials
- Production secrets

Use environment variables and managed secret storage as the project evolves.

## Safe Execution

Diagnostic tools must remain read-only by default.

Risky remediation actions must require explicit human approval.

## Security Development

Security tests and permission boundaries will be introduced incrementally according to the project roadmap.
