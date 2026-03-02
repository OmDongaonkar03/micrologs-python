# Changelog

All notable changes to `micrologs` (Python SDK) will be documented here.

---

## [0.1.0] - 2026-03-02

Initial release.

### Added
- `client.error()` - track errors from any Python backend
- `client.audit()` - track audit events
- `client.create_link()` - create tracked short links
- `client.get_link()` - fetch a single link by code
- `client.edit_link()` - edit a link's destination, label, or active state
- `client.delete_link()` - delete tracked links
- `client.update_error_status()` - update error group status individually or in bulk
- `client.verify()` - verify a public or secret key
- `client.analytics()` - full analytics query surface: visitors, returning, sessions, pages, devices, locations, referrers, utm, errors, errors_trend, error_detail, audits, links, link_detail
- Silent failure by design - all methods return `None` on error, never raise
- Zero dependencies - standard library only (`urllib`, `json`, `warnings`)
- Python 3.8+ compatible