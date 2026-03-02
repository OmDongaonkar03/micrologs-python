# Contributing to micrologs (Python SDK)

Thanks for your interest. Before starting any work, open an issue first - PRs without prior discussion may be declined if they conflict with planned direction.

---

## Reporting a bug

Open an issue and include:
- What you called
- What you expected back
- What actually happened
- Python version
- Micrologs engine version you're running against

---

## Submitting a PR

1. Open an issue and discuss the change first
2. Fork the repo and create a branch from `main`
3. Make your changes
4. Test against a real running Micrologs server
5. Open a PR with a clear description of what changed and why

---

## Code style

- No dependencies - the SDK must stay zero-dependency (standard library only)
- All methods must return `None` on failure, never raise
- Use `warnings.warn()` for failure messages - never `print()`
- Keep Python 3.8+ as the minimum - no f-strings with `=` specifier, no `match` statements
- snake_case for all method and parameter names
- Private attributes stay private - `_host` and `_key` must never be exposed publicly

---

## What we won't merge

- Any external dependency
- Breaking changes to existing method signatures without a major version bump
- Methods that don't exist as endpoints in the Micrologs engine
- Async support - by design this SDK is sync only. Async may come in a future major version.
- Anything that logs sensitive data (keys, IPs, payloads)

---

## Versioning

This SDK follows the Micrologs engine versioning loosely:
- New engine endpoint added → minor bump (0.1.0 → 0.2.0)
- Bug fix in SDK code → patch bump (0.1.0 → 0.1.1)
- Breaking change → major bump (0.1.0 → 1.0.0)