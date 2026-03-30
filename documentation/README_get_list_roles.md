# `get_list_roles.py` — Roles List

## Overview

Fetches the full taxonomy of credit roles available in MUSO.ai. Each role has a **parent** category (e.g. `"Music"`, `"Video"`) and a **child** sub-role (e.g. `"Songwriter"`, `"Producer"`, `"Director"`). These parent/child pairs are the values used in the `credits` array of track and profile credit responses.

---

## API Endpoint

```
GET https://api.developer.muso.ai/v4/roles
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `limit` | `int` | Items per page |
| `offset` | `int` | Pagination offset |

---

## Functions

### `get_roles(api_key, limit, offset) -> dict`

Fetches one page of roles.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str` | — | MUSO.ai API key |
| `limit` | `int` | `20` | Items per page |
| `offset` | `int` | `0` | Pagination offset |

**Returns:** Raw JSON response or `{}` on failure.

**Behaviour:**
- Quota-checked before the request
- Recorded as `"list_roles"` on success
- Retries up to 3× on HTTP 429 with exponential backoff (2s, 4s, 8s)

---

### `fetch_all_roles(api_key, page_size) -> dict`

Automatically pages through the entire roles endpoint and returns a single combined response containing all roles.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str` | — | API key |
| `page_size` | `int` | `50` | Items per page during pagination |

**Returns:** Combined dict with the full `data.items` list and original metadata fields.

**Notes:**
- Adds a 0.3-second delay between pages to be respectful of the API
- Uses `deepcopy` on the first page's response structure to avoid mutation

---

### `display_roles_summary(roles_data) -> None`

Prints a numbered list of all roles in `parent / child` format.

```
=== MUSO.ai Roles Summary ===
Total Roles Available: 82

1. Music / Songwriter
2. Music / Producer
3. Music / Composer
...
```

---

## CLI Usage

```bash
python3 get_list_roles.py
```

**Interactive flow:**

1. API status is shown
2. Prompted: continue with CLI? (`y/n`)
3. Prompted: print full JSON for ALL roles? (`y/n`)

**If yes (all roles):**
- Fetches via `fetch_all_roles` with page size 50
- Displays summary + full JSON

**If no:**
- Prompted for `limit` (default 50) and `offset` (default 0)
- Fetches and displays that page's roles
- Optionally prints the JSON for that page

---

## Sample Output

```
=== MUSO.ai Roles Summary ===
Total Roles Available: 82

1. Music / Songwriter
2. Music / Producer
3. Music / Composer
4. Music / Arranger
5. Video / Director
6. Video / Producer
...
```

---

## Request Cost

| Operation | Requests used |
|---|---|
| Single page (limit 50) | 1 |
| Full roles fetch (~82 roles, page size 50) | 2 |

Use `fetch_all_roles` once to cache the complete taxonomy, rather than fetching repeatedly.
