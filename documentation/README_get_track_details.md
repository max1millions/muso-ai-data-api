# `get_track_details.py` — Track Details

## Overview

Retrieves detailed track information from the MUSO.ai API. Supports three lookup modes: by track ID, by track title (search), or by artist name combined with a title keyword. Also contains helpers for paginating through an artist's full credit list to locate specific tracks.

---

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v4/track/id/{track_id}` | Fetch details for a specific track |
| `POST /v4/search` (type: `track`) | Search tracks by title keyword |
| `GET /v4/profile/{muso_id}/credits` | Page through an artist's credits to locate tracks |

---

## Functions

### `get_track_details(track_id, api_key) -> dict`

Fetches full track data for a known MUSO track ID.

| Parameter | Type | Description |
|---|---|---|
| `track_id` | `str` | MUSO.ai track ID |
| `api_key` | `str` | MUSO.ai API key |

**Returns:** Full JSON response or `{}` on failure.

**Behaviour:**
- Quota-checked before the request
- Records request as `"track_details"`
- Retries up to 3× on HTTP 429 with exponential backoff (2s, 4s, 8s)

---

### `get_profile_credits(muso_id, api_key, limit, offset) -> dict`

Fetches one page of credits for a profile (used internally by `get_artist_tracks`).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `muso_id` | `str` | — | Profile ID |
| `api_key` | `str` | — | API key |
| `limit` | `int` | `20` | Items per page |
| `offset` | `int` | `0` | Pagination offset |

---

### `get_artist_tracks(muso_id, api_key, title_keyword, limit) -> list[dict]`

Pages through a profile's credits to find tracks matching an optional title keyword.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `muso_id` | `str` | — | Profile ID |
| `api_key` | `str` | — | API key |
| `title_keyword` | `str` | `""` | Optional substring filter on track title |
| `limit` | `int` | `30` | Maximum tracks to return |

Adds a 0.5-second delay between pages to avoid overwhelming the API.

---

### `search_tracks(keyword, api_key, limit) -> dict`

Searches MUSO.ai for tracks matching a title keyword.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `keyword` | `str` | — | Title keyword |
| `api_key` | `str` | — | API key |
| `limit` | `int` | `10` | Max results |

---

### `display_track_summary(track_data) -> None`

Prints a formatted summary of a track response.

**Output sections:**
- Track ID & Title
- Duration, Year, Popularity
- Release title, ID, and type
- Artists and their roles
- ISRCs
- Streaming URLs (Spotify, Apple Music, etc.)

---

### `extract_track_results(search_result) -> list[tuple]`

Parses a title-based search response into `(track_id, title, artist_names, additional_info)` tuples.

---

### `extract_artist_credit_tracks(credits) -> list[tuple]`

Parses credits from `get_artist_tracks` into the same `(track_id, title, artist_names, additional_info)` format, including release date, label, and credit roles.

---

### `extract_artist_profiles(search_result) -> list[tuple]`

Parses profile search results into `(muso_id, name, additional_info)` tuples (same logic as in `get_profile_details.py`).

---

## CLI Usage

```bash
python3 get_track_details.py
```

**Interactive flow:**

```
Search options:
1. Search by track ID
2. Search by track title
3. Search by artist name + track title
```

**Option 1 — Track ID:**
- Enter the MUSO track ID directly
- Details fetched and displayed immediately

**Option 2 — Track title:**
- Keyword is posted to `/v4/search`
- Matching tracks listed; user selects one
- Full details fetched for the selection

**Option 3 — Artist + title:**
- Artist name is searched → user selects a profile
- Credits are paged through with a title keyword filter
- Matching tracks listed; user selects one
- Full details fetched for the selection

After any lookup, the user is offered the full raw JSON response.

---

## Sample Output

```
=== MUSO.ai Track Summary ===
ID: track789xyz
Title: Midnight Drive

--- Basic Information ---
Duration: 213
Year: 2022
Popularity: 85

--- Release Information ---
Release Title: After Hours EP
Release ID: rel456
Release Type: EP

--- Artists ---
Artist: Dampszn (ID: abc123)
  Role: Main Artist

--- ISRCs ---
ISRC: GBAAA2200001

--- Streaming Links ---
spotify: https://open.spotify.com/track/...
```

---

## Request Cost

| Operation | Requests used |
|---|---|
| Title search | 1 |
| Artist name search (option 3) | 1 |
| Credits pages (option 3, ~20 items/page) | 1 per page |
| Track details fetch | 1 |
