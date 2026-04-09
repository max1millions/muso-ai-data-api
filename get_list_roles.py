"""
Get List Roles
==============
Gets and displays all credit roles available in the MUSO.ai API.

Fetches all roles or a specific page, shows parent/child role pairs,
and offers an optional full JSON dump.

Usage:
    python get_list_roles.py

Dependencies:
    - MUSO_API_KEY in .env
    - request_tracker.py
"""

import requests
import sys
import time
import pprint
import os
from typing import Dict, Any, List, Tuple
from copy import deepcopy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("MUSO_API_KEY")
if not API_KEY:
    raise ValueError("MUSO_API_KEY not found in environment variables. Please check your .env file.")

from request_tracker import record_api_request, can_make_api_request, print_api_status


def get_roles(api_key: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """Fetch list of roles from MUSO.ai API with optional pagination."""
    # Check request allowance
    can_make, message = can_make_api_request(1)
    if not can_make:
        print(f"Cannot make roles request: {message}")
        return {}

    url = "https://api.developer.muso.ai/v4/roles"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    params = {
        "limit": limit,
        "offset": offset
    }

    max_retries = 3
    retries = 0
    while retries <= max_retries:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            # Record successful request
            record_api_request(1, "list_roles")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retries += 1
                if retries <= max_retries:
                    wait_time = 2 ** retries
                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                    continue
            print(f"HTTP Error occurred during API request: {e}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API request: {e}")
            sys.exit(1)

    print("Maximum retries exceeded.")
    return {}


def display_roles_summary(roles_data: Dict[str, Any]) -> None:
    """Display roles in a readable format."""
    if "data" not in roles_data or "items" not in roles_data["data"]:
        print("No role data found in the response.")
        return

    items = roles_data["data"]["items"]
    total_count = roles_data["data"].get("totalCount", len(items))

    print("\n=== MUSO.ai Roles Summary ===")
    print(f"Total Roles Available: {total_count}\n")

    for idx, role in enumerate(items, 1):
        parent = role.get("parent", "N/A")
        child = role.get("child", "N/A")
        print(f"{idx}. {parent} / {child}")


def fetch_all_roles(api_key: str, page_size: int = 50) -> Dict[str, Any]:
    """Fetch ALL roles by paging through the endpoint with the given page size."""
    first_page = get_roles(api_key, limit=page_size, offset=0)
    if not first_page:
        return {}

    # Defensive copy so we don't mutate original
    combined_data = deepcopy(first_page)
    items_accum: List[Dict[str, Any]] = combined_data["data"].get("items", [])

    total_count = combined_data["data"].get("totalCount", len(items_accum))
    offset = page_size

    while offset < total_count:
        page = get_roles(api_key, limit=page_size, offset=offset)
        if not page or "data" not in page or "items" not in page["data"]:
            break
        items_accum.extend(page["data"]["items"])
        offset += page_size
        # Respectful delay to avoid spamming API (even though page_size small)
        time.sleep(0.3)

    # Replace items list with full list
    combined_data["data"]["items"] = items_accum
    return combined_data


def main():
    print("MUSO.ai Roles List")
    print("-------------------")

    # Initial API status
    print("\nCurrent API Status:")
    print_api_status()
    print()

    # 1. Ask user if they want to proceed
    proceed = input("Would you like to continue with the CLI? (y/n): ").strip().lower()
    if proceed != "y":
        print("Exiting...")
        sys.exit(0)

    # 2. Ask if they want the full JSON for ALL roles
    want_full = input("Would you like to print the FULL JSON response for ALL roles? (y/n): ").strip().lower()

    if want_full == "y":
        print("\nFetching ALL roles from MUSO.ai (page size = 50)...")
        roles_data = fetch_all_roles(API_KEY, page_size=50)
        if not roles_data:
            print("Failed to fetch roles.")
            sys.exit(1)

        # Display summary
        display_roles_summary(roles_data)

        # Print full JSON
        print("\nFull JSON Response (ALL roles):")
        pprint.pprint(roles_data, indent=2)
    else:
        # Prompt for pagination values
        try:
            limit_input = input("How many roles would you like to retrieve? (default 50): ").strip()
            limit = int(limit_input) if limit_input else 50
        except ValueError:
            print("Invalid number. Using default limit of 50.")
            limit = 50

        try:
            offset_input = input("Enter offset for pagination (default 0): ").strip()
            offset = int(offset_input) if offset_input else 0
        except ValueError:
            print("Invalid number. Using default offset of 0.")
            offset = 0

        print(f"\nFetching roles (limit={limit}, offset={offset})...")
        roles_data = get_roles(API_KEY, limit=limit, offset=offset)

        # Display summary
        display_roles_summary(roles_data)

        # Ask to view current JSON page
        see_json = input("\nWould you like to see the JSON for this page? (y/n): ").strip().lower()
        if see_json == "y":
            print("\nJSON Response:")
            pprint.pprint(roles_data, indent=2)

    # Final API status
    print("\n" + "=" * 50)
    print("FINAL API STATUS:")
    print_api_status()


if __name__ == "__main__":
    main()
