# `get_profile_details.py` — Profile Details

## Overview

Retrieves full profile information from the MUSO.ai API for a given artist name or profile ID. Displays a formatted summary including identity fields, IPI numbers, social links, group memberships, and biography.

---

## API Endpoint

```
GET https://api.developer.muso.ai/v4/profile/{muso_id}
```

**Headers:**

```
x-api-key: <MUSO_API_KEY>
Content-Type: application/json
```

---

## Functions

### `get_profile_details(muso_id, api_key) -> dict`

Fetches raw profile data for a given MUSO profile ID.

| Parameter | Type | Description |
|---|---|---|
| `muso_id` | `str` | MUSO.ai profile ID |
| `api_key` | `str` | MUSO.ai API key |

**Returns:** Full JSON response from the profile endpoint, or `{}` if the request cannot be made.

**Behaviour:**
- Checks quota before requesting
- Records a successful request as `"profile_details"`
- Retries up to 3 times on HTTP 429 with exponential backoff (2s, 4s, 8s)

---

### `display_profile_summary(profile_data) -> None`

Prints a human-readable summary of a profile response.

**Output sections:**
- ID & Name
- City, Country, Popularity, Credit Count, Collaborators Count
- Common Credits (roles)
- Website, Spotify ID, Facebook, Instagram, Twitter
- IPI numbers
- Group memberships (with role and date range)
- Group members (if the profile is a group)
- Biography (truncated at 200 characters)

---

### `search_muso_artist(artist_name) -> dict`

Thin wrapper around `search_name.search_artist` that prints a status message.

---

### `extract_artist_profiles(search_result) -> list[tuple]`

Parses search results into a list of `(muso_id, name, additional_info)` tuples.

| Field | Description |
|---|---|
| `muso_id` | Profile ID |
| `name` | Artist name |
| `additional_info` | Popularity, credit count, and common roles as a formatted string |

---

### `is_profile_id(input_str) -> bool`

Heuristic to distinguish a typed profile ID from a name string.

A string is treated as a profile ID if it:
- Has no spaces
- Is longer than 10 characters
- Contains at least one digit

---

## CLI Usage

Pass an artist name or profile ID as a command-line argument:

```bash
python3 get_profile_details.py "Dampszn"
python3 get_profile_details.py abc123profileid456
```

Or run interactively:

```bash
python3 get_profile_details.py
# Prompts: Enter artist/performer name or Profile ID
```

**Interactive flow (name input):**
1. API status is displayed
2. MUSO.ai is searched for the name
3. Matching profiles are listed with IDs and metadata
4. User selects a profile by number
5. Full profile details are fetched and displayed
6. User is offered the full raw JSON output

---

## Sample Output

```
=== MUSO.ai Profile Summary ===
ID: abc123profileid456
Name: Dampszn

--- Basic Information ---
City: London
Country: GB
Popularity: 72
Credit Count: 340
Collaborators Count: 120
Common Credits: Songwriter, Producer

--- Social Media & Links ---
Website: N/A
Spotify ID: 2abc...

--- IPI Numbers ---
IPI: 01234567890

--- Biography ---
Dampszn is a UK-based songwriter and producer known for...
```

---

## Request Cost

| Operation | Requests used |
|---|---|
| Name search (if used) | 1 |
| Profile details fetch | 1 |
| **Total** | **1–2** |
