# `manage_api_config.py` — API Configuration Manager

## Overview

CLI utility for configuring and inspecting the MUSO.ai daily request tracking system. Wraps the functions in `request_tracker.py` behind a simple command-line interface — both argument-based and interactive.

See also: [README_API_TRACKING.md](README_API_TRACKING.md) for the full tracking system reference.

---

## Commands

Run with a command argument for direct execution, or without arguments for interactive mode.

```bash
python3 manage_api_config.py <command>
```

| Command | Description |
|---|---|
| `status` | Display current config and live usage stats |
| `developer` | Enable tracking and configure a daily limit |
| `commercial` | Disable tracking (for unlimited accounts) |
| `reset` | Reset today's request counter to 0 |
| `disable` | Alias for disabling tracking |

---

## Functions

### `show_current_config()`

Prints the active configuration values and, if tracking is enabled, the current daily usage status via `print_api_status()`.

**Example output:**

```
Current API Configuration:
==============================
Enabled: True
Daily Limit: 1000
Enforce Limit: True
Warning Thresholds: [80, 90, 95]%
Tracking Files Location: /path/to/tracking_data

📊 API Request Usage Status:
   Date: 2024-12-19
   Requests made: 45
   Daily limit: 1000
   Remaining: 955
   Usage: 4.5%
   Status: ✅ GOOD
```

---

### `configure_for_commercial()`

Calls `disable_tracking()` and prints a confirmation message. No requests will be checked or blocked after this.

```bash
python3 manage_api_config.py commercial
# ✅ Commercial configuration complete!
#    - Request tracking disabled
#    - No daily limits enforced
#    - Scripts will run without request checks
```

---

### `configure_for_developer()`

Prompts for a daily limit (default: 1000) and whether to enforce it strictly, then calls `enable_tracking()` and saves the enforcement flag.

```bash
python3 manage_api_config.py developer
# Enter daily request limit (default 1000): 1000
# Enforce limit strictly? (y/n, default y): y
# ✅ Developer configuration complete!
#    - Request tracking enabled
#    - Daily limit: 1000
#    - Enforcement: Strict
```

---

### `reset_usage()`

Sets `requests_made` to 0 in the usage file without changing the config.

```bash
python3 manage_api_config.py reset
# ✅ Usage count reset to 0
```

---

## Interactive Mode

Running without arguments launches a menu:

```
MUSO.ai API Configuration Manager
===================================

Options:
1. Show current configuration
2. Configure for commercial account (disable tracking)
3. Configure for developer account (enable tracking)
4. Reset today's usage count
5. Exit
```

---

## Typical Workflow

**Initial setup (first time):**

```bash
python3 manage_api_config.py developer
# Set limit to 1000, enforce strictly
```

**Check status before a large run:**

```bash
python3 manage_api_config.py status
```

**After upgrading to a commercial MUSO.ai account:**

```bash
python3 manage_api_config.py commercial
```

**If counter gets corrupted mid-day:**

```bash
python3 manage_api_config.py reset
```
