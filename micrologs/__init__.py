"""
Micrologs Python SDK
https://github.com/OmDongaonkar03/micrologs-python

Requires Python 3.8+. Zero dependencies — uses only the standard library.
"""

import json
import urllib.parse
import urllib.request
import warnings
from typing import Any, Dict, List, Optional, Union


class Micrologs:
    """
    Python SDK for Micrologs — self-hosted analytics and error tracking.

    Usage:
        from micrologs import Micrologs

        client = Micrologs(
            host="https://analytics.yourdomain.com",
            key="your_secret_key"
        )
    """

    def __init__(self, host: str, key: str):
        """
        :param host: Your Micrologs server URL (e.g. https://analytics.yourdomain.com)
        :param key:  Your project secret key
        """
        if not host or not isinstance(host, str):
            raise ValueError("[Micrologs] host is required (your server URL)")
        if not key or not isinstance(key, str):
            raise ValueError("[Micrologs] key is required (your secret key)")

        self._host = host.rstrip("/")
        self._key = key

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict]:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self._host}{endpoint}",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self._key,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            warnings.warn(f"[Micrologs] {e}")
            return None

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        try:
            clean = {k: v for k, v in (params or {}).items() if v is not None}
            query = urllib.parse.urlencode(clean)
            url = f"{self._host}{endpoint}{'?' + query if query else ''}"
            req = urllib.request.Request(
                url,
                headers={"X-API-Key": self._key},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            warnings.warn(f"[Micrologs] {e}")
            return None

    # ── Tracking ──────────────────────────────────────────────────────────────

    def error(
        self,
        message: str,
        *,
        type: str = "ManualError",
        severity: str = "error",
        file: str = "",
        line: Optional[int] = None,
        stack: Optional[str] = None,
        url: str = "",
        environment: str = "production",
        context: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Track an error from any Python backend.

        :param message:     Error message (required)
        :param type:        Error type — used for grouping (default: "ManualError")
        :param severity:    "info" | "warning" | "error" | "critical" (default: "error")
        :param file:        File where the error occurred
        :param line:        Line number
        :param stack:       Stack trace string
        :param url:         URL or endpoint where the error occurred
        :param environment: "production" | "staging" | "development" (default: "production")
        :param context:     Any extra data — dict, capped at 8KB on the server

        :returns: Response dict or None on failure

        Example:
            try:
                process_payment(order)
            except Exception as e:
                import traceback
                client.error(
                    str(e),
                    type="CheckoutError",
                    severity="critical",
                    file="checkout.py",
                    line=42,
                    stack=traceback.format_exc(),
                    url="/api/checkout",
                    context={"order_id": 123, "amount": 2999}
                )
        """
        return self._post("/api/track/error.php", {
            "message":      str(message)[:1024],
            "error_type":   type,
            "severity":     severity,
            "file":         file,
            "line":         line,
            "stack":        stack,
            "url":          url,
            "environment":  environment,
            "context":      context,
        })

    def audit(
        self,
        action: str,
        actor: str = "",
        context: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Track an audit event.

        :param action:  Action string — use dot notation e.g. "user.login", "order.placed"
        :param actor:   Who triggered the action e.g. "user@email.com"
        :param context: Any extra data as a dict

        :returns: Response dict or None on failure

        Example:
            client.audit("user.login", "user@email.com", {"role": "admin"})
            client.audit("order.placed", "user@email.com", {"order_id": 123})
        """
        if not action or not isinstance(action, str):
            warnings.warn("[Micrologs] audit() requires an action string")
            return None
        return self._post("/api/track/audit.php", {
            "action":  action,
            "actor":   actor,
            "context": context,
        })

    # ── Link management ───────────────────────────────────────────────────────

    def create_link(
        self,
        destination_url: str,
        label: str = "",
    ) -> Optional[Dict]:
        """
        Create a tracked short link.

        :param destination_url: The URL to redirect to
        :param label:           Optional label for the link

        :returns: Response dict with code, short_url, destination_url, label — or None on failure
        """
        if not destination_url:
            warnings.warn("[Micrologs] create_link() requires a destination_url")
            return None
        return self._post("/api/links/create.php", {
            "destination_url": destination_url,
            "label":           label,
        })

    def get_link(self, code: str) -> Optional[Dict]:
        """
        Fetch a single tracked link by code.

        :param code: The short link code (e.g. "aB3xYz12")

        :returns: Response dict with link details and total_clicks — or None on failure
        """
        if not code:
            warnings.warn("[Micrologs] get_link() requires a code")
            return None
        return self._get("/api/links/detail.php", {"code": code})

    def edit_link(
        self,
        code: str,
        *,
        destination_url: Optional[str] = None,
        label: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict]:
        """
        Edit a tracked link's destination URL, label, or active state.

        :param code:            The short link code to edit (required)
        :param destination_url: New destination URL
        :param label:           New label
        :param is_active:       Enable or disable the link

        :returns: Response dict with updated link — or None on failure
        """
        if not code:
            warnings.warn("[Micrologs] edit_link() requires a code")
            return None
        payload: Dict[str, Any] = {"code": code}
        if destination_url is not None:
            payload["destination_url"] = destination_url
        if label is not None:
            payload["label"] = label
        if is_active is not None:
            payload["is_active"] = is_active
        return self._post("/api/links/edit.php", payload)

    def delete_link(self, code: str) -> Optional[Dict]:
        """
        Delete a tracked link by code.

        :param code: The short link code (e.g. "aB3xYz12")

        :returns: Response dict or None on failure
        """
        if not code:
            warnings.warn("[Micrologs] delete_link() requires a code")
            return None
        return self._post("/api/links/delete.php", {"code": code})

    def update_error_status(
        self,
        ids: Union[int, List[int]],
        status: str,
    ) -> Optional[Dict]:
        """
        Update the status of one or more error groups.

        :param ids:    Single error group ID or a list of IDs (max 100)
        :param status: "open" | "investigating" | "resolved" | "ignored"

        :returns: Response dict or None on failure

        Example:
            client.update_error_status(42, "investigating")
            client.update_error_status([12, 15, 22], "resolved")
        """
        if not ids:
            warnings.warn("[Micrologs] update_error_status() requires ids")
            return None
        valid_statuses = ["open", "investigating", "resolved", "ignored"]
        if status not in valid_statuses:
            warnings.warn(f"[Micrologs] update_error_status() status must be one of: {', '.join(valid_statuses)}")
            return None
        payload = (
            {"ids": ids, "status": status}
            if isinstance(ids, list)
            else {"id": ids, "status": status}
        )
        return self._post("/api/track/errors-update-status.php", payload)

    def verify(self, key: str) -> Optional[Dict]:
        """
        Verify a public or secret key.

        :param key: The key to verify

        :returns: Response dict indicating whether the key is valid — or None on failure
        """
        return self._post("/api/projects/verify.php", {"key": key})

    # ── Analytics ─────────────────────────────────────────────────────────────

    def analytics(self) -> "_Analytics":
        """
        Access analytics endpoints.

        Example:
            client.analytics().visitors(range="30d")
            client.analytics().errors(range="7d", status="open")
        """
        return _Analytics(self)


class _Analytics:
    """
    Analytics query surface. Access via client.analytics().

    All methods accept keyword params:
        range  str  "7d" | "30d" | "90d" | "custom"  (default: "30d")
        from_  str  "YYYY-MM-DD" — required when range="custom" (maps to "from")
        to     str  "YYYY-MM-DD" — required when range="custom"
    """

    def __init__(self, client: Micrologs):
        self._client = client

    def _params(self, kwargs: dict) -> dict:
        # map from_ → from so callers avoid the Python reserved keyword
        if "from_" in kwargs:
            kwargs["from"] = kwargs.pop("from_")
        return kwargs

    def visitors(self, **kwargs) -> Optional[Dict]:
        """Unique visitors, pageviews, sessions, bounce rate, over time."""
        return self._client._get("/api/analytics/visitors.php", self._params(kwargs))

    def returning(self, **kwargs) -> Optional[Dict]:
        """New vs returning visitors, percentage split, over time."""
        return self._client._get("/api/analytics/visitors-returning.php", self._params(kwargs))

    def sessions(self, **kwargs) -> Optional[Dict]:
        """Avg session duration, avg pages per session, over time."""
        return self._client._get("/api/analytics/sessions.php", self._params(kwargs))

    def pages(self, **kwargs) -> Optional[Dict]:
        """Top pages by pageviews."""
        return self._client._get("/api/analytics/pages.php", self._params(kwargs))

    def devices(self, **kwargs) -> Optional[Dict]:
        """Breakdown by device type, OS, browser."""
        return self._client._get("/api/analytics/devices.php", self._params(kwargs))

    def locations(self, **kwargs) -> Optional[Dict]:
        """Breakdown by country, region, city."""
        return self._client._get("/api/analytics/locations.php", self._params(kwargs))

    def referrers(self, **kwargs) -> Optional[Dict]:
        """Traffic sources."""
        return self._client._get("/api/analytics/referrers.php", self._params(kwargs))

    def utm(self, **kwargs) -> Optional[Dict]:
        """UTM campaign data."""
        return self._client._get("/api/analytics/utm.php", self._params(kwargs))

    def errors(self, **kwargs) -> Optional[Dict]:
        """Error groups with occurrence counts. Supports status, severity, environment filters."""
        return self._client._get("/api/analytics/errors.php", self._params(kwargs))

    def errors_trend(self, **kwargs) -> Optional[Dict]:
        """Daily error trend, top groups. Pass group_id= to scope to one group."""
        return self._client._get("/api/analytics/errors-trend.php", self._params(kwargs))

    def error_detail(self, **kwargs) -> Optional[Dict]:
        """Single error group with all events. Requires id= param."""
        return self._client._get("/api/analytics/error-detail.php", self._params(kwargs))

    def audits(self, **kwargs) -> Optional[Dict]:
        """Audit log events. Supports action= and actor= filters."""
        return self._client._get("/api/analytics/audits.php", self._params(kwargs))

    def links(self, **kwargs) -> Optional[Dict]:
        """All tracked links with click counts."""
        return self._client._get("/api/analytics/links.php", self._params(kwargs))

    def link_detail(self, **kwargs) -> Optional[Dict]:
        """Single link with clicks over time. Requires code= param."""
        return self._client._get("/api/analytics/link-detail.php", self._params(kwargs))