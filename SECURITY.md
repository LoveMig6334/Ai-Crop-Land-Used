# Security Policy

## Supported Versions

| Version          | Supported |
| ---------------- | --------- |
| Latest on `main` | ✅        |
| Older commits    | ❌        |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. **Email** the maintainers directly or use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
3. Include a clear description, reproduction steps, and potential impact

We will acknowledge your report within **48 hours** and provide a resolution timeline.

## Scope

This project processes local agricultural data files (CSV/Excel). Key security considerations:

- **No user authentication** — the Flask web app is intended for local/development use only
- **File paths** — all paths are managed via `src/util/data_path.py`; avoid user-controlled path inputs
- **Dependencies** — keep `requirements.txt` packages up-to-date to avoid known CVEs
