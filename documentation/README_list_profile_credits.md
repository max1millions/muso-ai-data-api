# `list_profile_credits.py` — Profile Credits

## Overview

Lists the credits associated with a MUSO.ai profile — i.e., all tracks where the artist has a recorded production, writing, or performance credit. Supports direct lookup by profile ID or an interactive artist name search. Results are paginated and displayed in a readable summary format.

---

## API Endpoint

```
GET https://api.developer.muso.ai/v4/profile/{muso_id}/credits
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `limit` | `int` | Number of credits per page (default: 20) |
| `offset` | `int` | Pagination offset (default: 0) |

**Headers:**

```
x-api-key: <MUSO_API_KEY>
Content-Type: application/json
```

---

## Functions

### `get_profile_credits(muso_id, api_key, limit, offset) -> dict`

Fetches one page of credits for a profile.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `muso_id` | `str` | — | MUSO.ai profile ID |
| `api_key` | `str` | — | API key |
| `limit` | `int` | `20` | Items per page |
| `offset` | `int` | `0` | Pagination offset |

**Returns:** Raw JSON response or `{}` if the quota check fails.

**Behaviour:**
- Checks quota via `can_make_api_request` before sending
- Records the request as `"profile_credits"` on success
- Retries up to 3× on HTTP 429 with exponential backoff (2s, 4s, 8s)

---

### `extract_artist_profiles(search_result) -> list[tuple]`

Parses a profile search response into `(profile_id, name, additional_info)` tuples — used when an artist name is provided instead of a direct ID.

---

### `format_credit_item(item) -> str`

Formats a single credit entry as a multi-line string for display.

**Output fields:**
- Track title and MUSO track ID
- Album/release title and release date
- Label
- Credit roles (parent/child, e.g. `"Music"/"Songwriter"`)

---

### `display_credits_summary(credits_data, max_items) -> None`

Prints a numbered summary of credits, capped at `max_items`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `credits_data` | `dict` | — | Raw API response |
| `max_items` | `int` | `20` | Maximum items to display |

---

## CLI Usage

```bash
python3 list_profile_credits.py
```

**Interactive flow:**

```
Search options:
1. Enter profile ID
2. Search by artist/performer name
```

- **Option 1:** Enter the MUSO profile ID directly
- **Option 2:** Type an artist name → results listed → select a profile

After selecting a profile, you are prompted for:
- **Limit** — how many credits to retrieve (default: 20)
- **Offset** — pagination starting point (default: 0)

Credits are then displayed. The full raw JSON can optionally be printed.

---

## Sample Output

```
=== MUSO.ai Profile Credits Summary ===
Total Credits: 340

1. Track: Midnight Drive (ID: track789xyz)
   Release: After Hours EP | Date: 2022-06-10
   Label: Atlantic Records
   Roles: Music/Songwriter, Music/Producer

2. Track: So High (ID: track012abc)
   Release: Vibe Season | Date: 2021-11-01
   Label: Independent
   Roles: Music/Songwriter
```

---

## Request Cost

| Operation | Requests used |
|---|---|
| Name search (if used) | 1 |
| Credits page fetch | 1 per page |
| **Typical (20 credits)** | **1–2** |

To retrieve large credit lists, increase the `limit` or page through with increasing `offset` values across multiple runs.
