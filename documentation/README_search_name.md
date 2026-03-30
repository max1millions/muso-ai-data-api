# `search_name.py` — Artist/Profile Search

## Overview

Searches the MUSO.ai API for artist or performer profiles by name. Returns a paginated list of matching profiles with popularity, credit count, and common roles.

This module is also used as a **library** by `get_profile_details.py`, `get_track_details.py`, and `list_profile_credits.py`, which all import `search_artist` to resolve a name into a MUSO profile ID before making downstream requests.

---

## API Endpoint

```
POST https://api.developer.muso.ai/v4/search
```

**Payload:**

```json
{
  "keyword": "<artist name>",
  "type": ["profile"],
  "limit": 11,
  "offset": 0
}
```

**Headers:**

```
x-api-key: <MUSO_API_KEY>
Content-Type: application/json
```

---

## Functions

### `search_artist(artist_name, api_key) -> dict`

Core search function used by all other modules.

| Parameter | Type | Description |
|---|---|---|
| `artist_name` | `str` | Name of the artist/performer to search for |
| `api_key` | `str` | MUSO.ai API key |

**Returns:** Raw JSON response from the MUSO.ai search API.

**Behaviour:**
- Checks quota via `can_make_api_request` before sending
- Records the request via `record_api_request` on success
- Retries up to 5 times on HTTP 429 (rate limit) with exponential backoff, capped at 60 seconds
- Exits with an error on non-rate-limit HTTP errors or network failures

**Example response shape:**

```json
{
  "data": {
    "profiles": {
      "items": [
        {
          "id": "abc123",
          "name": "Dampszn",
          "popularity": 72,
          "creditCount": 340,
          "commonCredits": ["Songwriter", "Producer"]
        }
      ],
      "totalCount": 3
    }
  }
}
```

---

## CLI Usage

Run directly to search interactively:

```bash
python3 search_name.py
```

```
MUSO.ai Artist Search
---------------------
Enter artist name to search: Dampszn

Searching for: Dampszn...

{'data': {'profiles': {'items': [...], 'totalCount': 3}}}
```

Output is printed via `pprint` — useful for inspecting raw API responses.

---

## Request Cost

| Operation | Requests used |
|---|---|
| One name search | 1 |

---

## Notes

- The search returns up to **11 profiles** per call (hardcoded `limit: 11`).
- Commented-out payload fields (`childCredits`, `releaseDateEnd`, `releaseDateStart`) can be uncommented to filter results by role or date range.
- When imported as a library, only `search_artist` is used — `main()` is not called.
