# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Active    |

---

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately via GitHub Security Advisories:

**[→ Report a vulnerability](https://github.com/OmDongaonkar03/micrologs-python/security/advisories/new)**

You will receive a response within 72 hours.

---

## Security Design

**Keys are private attributes.** `_host` and `_key` use Python's single-underscore private convention. They are not exposed in `__repr__` or `__dict__` output.

**The SDK never stores or logs your key.** It is only used in request headers and is never written to disk, logged, or exposed in warning messages.

**The SDK never raises.** All failures return `None` with a `warnings.warn()`. This prevents analytics failures from leaking stack traces or sensitive context into your application's error handling.

**5 second request timeout.** All HTTP calls have a hard 5 second timeout. A hung Micrologs server will not hang your application.