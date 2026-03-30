# `request_tracker.py` — Request Tracking Module

## Overview

Core module responsible for tracking daily MUSO.ai API usage. Every other module imports from this file to check quota availability before making requests and to record each successful call. State is persisted to disk so counts survive script restarts.

This module is a **library** — it is not run directly.

---

## Storage

All tracking state is stored in the `tracking_data/` subfolder (created automatically):

| File | Purpose |
|---|---|
| `tracking_data/api_config.json` | Configuration (limits, thresholds, enforcement) |
| `tracking_data/api_usage.json` | Live daily usage counters (gitignored) |

---

## `RequestTracker` Class

### `__init__(config_file="api_config.json")`

Initialises the tracker. Loads or creates config and usage files.

---

### `is_enabled() -> bool`

Returns `True` if tracking is active.

---

### `get_status() -> dict`

Returns the current quota snapshot:

```python
{
    "enabled": True,
    "requests_made": 156,
    "daily_limit": 1000,
    "remaining": 844,
    "percentage_used": 15.6,
    "date": "2024-12-19",
    "last_reset": "2024-12-19 00:00:00"
}
```

Returns `{"enabled": False, "message": "..."}` when tracking is disabled.

---

### `can_make_request(count=1) -> tuple[bool, str]`

Checks whether `count` additional requests can be made within the current day's limit.

| Return value | Meaning |
|---|---|
| `(True, "OK - ...")` | Request(s) can proceed |
| `(False, "LIMIT EXCEEDED - ...")` | Enforcement is on and limit reached |
| `(True, "WARNING - ...")` | Limit reached but enforcement is off |

---

### `record_request(count=1, endpoint="unknown") -> bool`

Records that `count` requests have been made against `endpoint`.

- Increments `requests_made` in the usage file
- Saves `last_request` timestamp and `last_endpoint`
- Triggers `_check_warnings()` to emit usage alerts
- Raises `Exception` if limit is exceeded and enforcement is on

---

### `_check_warnings() -> None`

Compares current usage percentage against configured thresholds and prints the appropriate alert:

| Threshold | Output |
|---|---|
| ≥ 80% | `ℹ️  INFO: ...% used` |
| ≥ 90% | `⚠️  WARNING: ...% used` |
| ≥ 95% (max threshold) | `🚨 CRITICAL: ...% used` |

---

### `print_status() -> None`

Prints a human-readable status block:

```
📊 API Request Usage Status:
   Date: 2024-12-19
   Requests made: 156
   Daily limit: 1000
   Remaining: 844
   Usage: 15.6%
   Tracking files: /path/to/tracking_data
   Status: ✅ GOOD
```

Status labels: `✅ GOOD`, `ℹ️  CAUTION`, `⚠️  WARNING`, `🚨 CRITICAL`, `🚨 LIMIT REACHED`.

---

### `get_tracking_info() -> dict`

Returns file path info:

```python
{
    "tracking_directory": "/path/to/tracking_data",
    "config_file": "/path/to/tracking_data/api_config.json",
    "usage_file": "/path/to/tracking_data/api_usage.json"
}
```

---

## Module-level Convenience Functions

These are what other modules import:

```python
from request_tracker import record_api_request, can_make_api_request, print_api_status
```

| Function | Signature | Description |
|---|---|---|
| `get_tracker()` | `-> RequestTracker` | Returns the shared global tracker instance (created once) |
| `record_api_request(count, endpoint)` | `-> bool` | Records requests against the global tracker |
| `can_make_api_request(count)` | `-> tuple[bool, str]` | Checks quota against the global tracker |
| `print_api_status()` | `-> None` | Prints status from the global tracker |
| `disable_tracking()` | `-> None` | Sets `enabled: false` in config |
| `enable_tracking(daily_limit)` | `-> None` | Sets `enabled: true` and updates `daily_limit` in config |

---

## Default Configuration

When `api_config.json` does not exist it is created with:

```json
{
  "enabled": true,
  "daily_limit": 1000,
  "warning_thresholds": [80, 90, 95],
  "enforce_limit": true,
  "reset_hour": 0
}
```

---

## Daily Reset

On each script startup, `_load_usage_data()` compares the stored `date` to `date.today()`. If they differ, the usage counter is reset to 0 and the file is saved.

---

## Usage Pattern

```python
from request_tracker import record_api_request, can_make_api_request

# Before any API call
can_make, message = can_make_api_request(1)
if not can_make:
    print(f"Quota exceeded: {message}")
    return {}

# ... make the HTTP request ...

# After a successful call
record_api_request(1, "my_endpoint")
```
