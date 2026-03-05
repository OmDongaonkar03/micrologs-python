# micrologs

[![PyPI](https://img.shields.io/pypi/v/micrologs)](https://pypi.org/project/micrologs/)

Python SDK for [Micrologs](https://github.com/OmDongaonkar03/Micrologs) - self-hosted analytics and error tracking.

**Requires Python 3.8+. Zero dependencies.**

---

## How it works

Micrologs is an engine you install on your own server. You own the database, you own the data. This SDK is a thin wrapper around its REST API - it makes HTTP calls to your server, not to any third-party service.

```
Your Python app  →  SDK  →  your Micrologs server  →  your database
```

Nothing goes anywhere you don't control.

---

## Install

```bash
pip install micrologs
```

---

## Initialize

```python
from micrologs import Micrologs

client = Micrologs(
    host="https://analytics.yourdomain.com",  # your server - where Micrologs is installed
    key="your_secret_key"                     # your project secret key
)
```

Both `host` and `key` are required. The constructor raises `ValueError` immediately if either is missing.

`host` is the URL of the server where you installed Micrologs. `key` is the secret key for your project. Never use the public key here - that's for the JS snippet only.

---

## Tracking

### Track an error

Use this to send errors from your Python backend to Micrologs. Works alongside the JS snippet - the snippet catches frontend errors, this catches backend errors.

```python
import traceback

try:
    process_payment(order)
except Exception as e:
    client.error(
        str(e),
        type="CheckoutError",        # groups errors of the same type together
        severity="critical",         # info | warning | error | critical
        file="checkout.py",
        line=42,
        stack=traceback.format_exc(),
        url="/api/checkout",
        environment="production",    # default: "production"
        context={"order_id": 123, "amount": 2999}  # any extra data, capped at 8KB
    )
```

All fields except `message` are optional. Uses keyword-only arguments after `message`.

**How grouping works:** Micrologs hashes `error_type + message + file + line` into a fingerprint. The same error firing 1000 times creates 1 group with 1000 occurrences. If you mark a group as resolved and it fires again, it automatically reopens.

**Response:**
```python
{
    "success": True,
    "message": "OK",
    "data": {
        "queued": True
    }
}
```

The error is queued for async processing — the worker handles the DB write in the background.

---

### Track an audit event

```python
client.audit("user.login",       "user@email.com", {"role": "admin"})
client.audit("order.placed",     "user@email.com", {"order_id": 123, "amount": 2999})
client.audit("settings.updated", "admin@email.com")
```

`action` is required. Use dot notation by convention (`resource.action`) for easy filtering.

---

## Link management

### Create a tracked short link

```python
result = client.create_link(
    "https://yourdomain.com/pricing",  # destination URL
    "Pricing CTA"                      # optional label
)

print(result["data"])
# {
#     "code":            "aB3xYz12",
#     "short_url":       "https://analytics.yourdomain.com/api/redirect.php?c=aB3xYz12",
#     "destination_url": "https://yourdomain.com/pricing",
#     "label":           "Pricing CTA"
# }
```

### Get a single link

```python
result = client.get_link("aB3xYz12")
# Returns link details including total_clicks
```

### Edit a link

```python
# Any combination of fields - all optional except code
client.edit_link(
    "aB3xYz12",
    destination_url="https://yourdomain.com/new-page",
    label="Updated CTA",
    is_active=False
)
```

### Delete a link

```python
client.delete_link("aB3xYz12")
```

---

## Analytics

All analytics methods return data from your Micrologs server as a dict. Access your data via `result["data"]`.

Access analytics via `client.analytics()`:

```python
analytics = client.analytics()
```

### Common params

All analytics methods accept keyword params:

| Param   | Default  | Description |
|---------|----------|-------------|
| `range` | `"30d"`  | `"7d"` / `"30d"` / `"90d"` / `"custom"` |
| `from_` | -        | `"YYYY-MM-DD"` - required when `range="custom"` (note the underscore - `from` is a Python keyword) |
| `to`    | -        | `"YYYY-MM-DD"` - required when `range="custom"` |

---

### Visitors

```python
result = analytics.visitors(range="30d")

print(result["data"])
# {
#     "unique_visitors": 1842,
#     "total_pageviews": 5631,
#     "total_sessions":  2109,
#     "bounce_rate":     43.2,
#     "over_time": [...]
# }
```

---

### New vs returning visitors

```python
result = analytics.returning(range="30d")
```

---

### Sessions

```python
result = analytics.sessions(range="7d")
# avg_duration_seconds, avg_duration_engaged, avg_pages_per_session, over_time
```

---

### Pages

```python
result = analytics.pages(range="30d")
```

---

### Locations, devices, referrers, UTM

```python
analytics.locations(range="30d")
analytics.devices(range="30d")
analytics.referrers(range="30d")
analytics.utm(range="30d")
```

---

### Errors

```python
# All error groups
analytics.errors(range="30d")

# Filter by status, severity, environment
analytics.errors(range="30d", status="open", severity="critical", environment="production")

# Daily error trend
analytics.errors_trend(range="30d")

# Trend for a single group
analytics.errors_trend(range="30d", group_id=12)

# Full detail for one group
analytics.error_detail(id=12)
```

### Update error status

```python
# Single group
client.update_error_status(42, "investigating")
client.update_error_status(42, "resolved")

# Bulk
client.update_error_status([12, 15, 22], "ignored")
```

Valid statuses: `open` → `investigating` → `resolved` or `ignored`.

---

### Audit log

```python
analytics.audits(range="7d")
analytics.audits(range="30d", action="user.login", actor="user@email.com")
```

---

### Tracked links

```python
analytics.links(range="30d")
analytics.link_detail(code="aB3xYz12", range="30d")
```

---

### Custom date range

```python
analytics.visitors(range="custom", from_="2026-01-01", to="2026-01-31")
```

Note: use `from_` (with underscore) - `from` is a reserved keyword in Python.

---

## Verify a key

```python
result = client.verify("some_key")
```

---

## Error handling

The SDK never raises exceptions. If a network error occurs, the server is unreachable, or the server returns an error - the method returns `None` and emits a `warnings.warn()`. This is intentional.

```python
result = client.error("Payment failed")

if result is None:
    # SDK call failed - your server may be unreachable
    # Your application continues normally regardless
```

**Async environments (FastAPI, Starlette, aiohttp):** This SDK is synchronous. Calling it directly inside an `async def` route will block the event loop. Wrap calls in a thread executor instead:

```python
import asyncio

result = await asyncio.to_thread(client.error, "Payment failed")
```

---

## Full method reference

| Method | Description |
|--------|-------------|
| `client.error(message, **options)` | Track a backend error |
| `client.audit(action, actor?, context?)` | Track an audit event |
| `client.create_link(destination_url, label?)` | Create a tracked short link |
| `client.get_link(code)` | Fetch a single tracked link by code |
| `client.edit_link(code, **options)` | Edit a link's destination, label, or active state |
| `client.delete_link(code)` | Delete a tracked link by code |
| `client.update_error_status(ids, status)` | Update error group status - single ID or list |
| `client.verify(key)` | Verify a public or secret key |
| `client.analytics().visitors(**params)` | Unique visitors, pageviews, sessions, bounce rate |
| `client.analytics().returning(**params)` | New vs returning visitors |
| `client.analytics().sessions(**params)` | Session duration, pages per session |
| `client.analytics().pages(**params)` | Top pages by pageviews |
| `client.analytics().devices(**params)` | Device, OS, browser breakdown |
| `client.analytics().locations(**params)` | Country, region, city breakdown |
| `client.analytics().referrers(**params)` | Traffic sources |
| `client.analytics().utm(**params)` | UTM campaign data |
| `client.analytics().errors(**params)` | Error groups with occurrence counts |
| `client.analytics().errors_trend(**params)` | Daily error trend, top groups |
| `client.analytics().error_detail(**params)` | Single error group - all occurrences and detail |
| `client.analytics().audits(**params)` | Audit log events |
| `client.analytics().links(**params)` | Tracked links with click counts |
| `client.analytics().link_detail(**params)` | Single link - clicks over time |

---

## Requirements

- Python 3.8+
- Zero dependencies - uses only the standard library (`urllib`, `json`, `warnings`)
- A running [Micrologs](https://github.com/OmDongaonkar03/Micrologs) server (v1.3.0+)

---

## License

MIT - [Om Dongaonkar](https://github.com/OmDongaonkar03)