# MUSO.ai Data API

A Python toolkit for interacting with the [MUSO.ai](https://muso.ai) API (v4). Provides CLI-driven modules for searching artists, retrieving track and profile data, listing credits, exploring roles, and managing daily API request quotas.

---

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Modules](#modules)
- [Quick Start](#quick-start)
- [Request Tracking](#request-tracking)
- [Documentation](#documentation)

---

## Requirements

- Python 3.9+
- A valid [MUSO.ai API key](https://developer.muso.ai)
- The following Python packages:
  - `requests`
  - `python-dotenv`

Install dependencies:

```bash
pip install requests python-dotenv
```

---

## Setup

1. Copy the environment file template and add your key:

```bash
cp .env.example .env
```

2. Edit `.env`:

```
MUSO_API_KEY=your_actual_api_key_here
```

3. (Optional) Configure request tracking for developer accounts:

```bash
python3 manage_api_config.py developer
```

---

## Project Structure

```
MUSO.AI-DATA-API/
├── .env                          # API key (gitignored)
├── .env.example                  # Template for .env
├── .gitignore
├── README.md                     # This file
│
├── search_name.py                # Search profiles by artist name
├── get_profile_details.py        # Fetch full profile data by name or ID
├── get_track_details.py          # Fetch track data by ID, title, or artist+title
├── list_profile_credits.py       # List all credits for a profile
├── get_list_roles.py             # Retrieve the full MUSO.ai roles taxonomy
├── request_tracker.py            # Daily API quota tracking (core module)
├── manage_api_config.py          # CLI for configuring request tracking
│
├── tracking_data/
│   ├── api_config.json           # Tracking configuration (limits, thresholds)
│   └── api_usage.json            # Live daily usage counters (gitignored)
│
└── documentation/
    ├── README_API_TRACKING.md
    ├── README_search_name.md
    ├── README_get_profile_details.md
    ├── README_get_track_details.md
    ├── README_list_profile_credits.md
    ├── README_get_list_roles.md
    ├── README_request_tracker.md
    └── README_manage_api_config.md
```

---

## Modules

| Module | Purpose | Run directly? |
|---|---|---|
| `search_name.py` | Search MUSO.ai for artist/performer profiles by name | Yes |
| `get_profile_details.py` | Retrieve full profile details (IPI, collaborators, bio, social links) | Yes |
| `get_track_details.py` | Retrieve track details (ISRCs, artists, release, streaming links) | Yes |
| `list_profile_credits.py` | List paginated credits for a profile | Yes |
| `get_list_roles.py` | List all parent/child credit roles in MUSO.ai taxonomy | Yes |
| `request_tracker.py` | Core tracking module — imported by all other modules | No (library) |
| `manage_api_config.py` | Configure and inspect daily quota settings | Yes |

---

## Quick Start

### Search for an artist

```bash
python3 search_name.py
# Prompts: Enter artist name to search
```

### Get full profile details

```bash
python3 get_profile_details.py "Dampszn"
# or pass profile ID directly
python3 get_profile_details.py abc123profileid
```

### Get track details

```bash
python3 get_track_details.py
# Interactive: choose search by track ID, title, or artist + title
```

### List credits for a profile

```bash
python3 list_profile_credits.py
# Interactive: enter profile ID or search by name
```

### List all MUSO.ai roles

```bash
python3 get_list_roles.py
# Fetches all parent/child credit roles with optional full JSON output
```

### Manage API quota config

```bash
python3 manage_api_config.py status       # View current quota and usage
python3 manage_api_config.py developer    # Configure for developer account (1000 req/day)
python3 manage_api_config.py commercial   # Disable tracking for unlimited accounts
python3 manage_api_config.py reset        # Reset today's request counter
```

---

## Request Tracking

All modules share a global `RequestTracker` instance from `request_tracker.py`. It:

- Tracks daily request counts across all scripts
- Automatically resets at midnight
- Emits warnings at 80%, 90%, and 95% usage
- Blocks further requests when the daily limit is reached (configurable)
- Stores state in `tracking_data/api_config.json` and `tracking_data/api_usage.json`

**Developer accounts** (1,000 requests/day default): tracking is enabled and enforced.  
**Commercial accounts** (unlimited): run `manage_api_config.py commercial` to disable all tracking.

Typical request cost per artist:

| Operation | Requests |
|---|---|
| Name search | 1 |
| Profile details | 1 |
| Credits page (20 items) | 1 |
| Track details | 1 per track |
| Roles list (full) | 1–3 |
| **Typical artist run** | **~50–200** |

---

## Documentation

Detailed documentation for each module lives in the [`documentation/`](documentation/) folder:

- [API Tracking System](documentation/README_API_TRACKING.md)
- [search_name](documentation/README_search_name.md)
- [get_profile_details](documentation/README_get_profile_details.md)
- [get_track_details](documentation/README_get_track_details.md)
- [list_profile_credits](documentation/README_list_profile_credits.md)
- [get_list_roles](documentation/README_get_list_roles.md)
- [request_tracker](documentation/README_request_tracker.md)
- [manage_api_config](documentation/README_manage_api_config.md)
