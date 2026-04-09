"""
List Profile Credits
====================
Gets and displays credit history for a MUSO.ai artist profile.

Enter a profile ID directly or search by artist name only. Supports pagination
and shows each credit's track title, release, label, and role(s), with an
optional full JSON dump.

Usage:
    python list_profile_credits.py

Dependencies:
    - MUSO_API_KEY in .env
    - search_name.py
    - request_tracker.py
"""

import requests
import sys
import time
import pprint
import os
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("MUSO_API_KEY")
if not API_KEY:
    raise ValueError("MUSO_API_KEY not found in environment variables. Please check your .env file.")

# Import artist search functionality
from search_name import search_artist
# Import request tracking utilities
from request_tracker import record_api_request, can_make_api_request, print_api_status


def get_profile_credits(muso_id: str, api_key: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Retrieve profile credits from MUSO.ai API.

    Args:
        muso_id (str): MUSO.ai profile ID.
        api_key (str): API key for authentication.
        limit (int, optional): Number of results to return. Defaults to 20.
        offset (int, optional): Pagination offset. Defaults to 0.

    Returns:
        Dict[str, Any]: JSON response from the API.
    """
    # Check request allowance
    can_make, message = can_make_api_request(1)
    if not can_make:
        print(f"Cannot make profile credits request: {message}")
        return {}

    url = f"https://api.developer.muso.ai/v4/profile/{muso_id}/credits"

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
            record_api_request(1, "profile_credits")
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Handle rate limiting
            if e.response.status_code == 429:
                retries += 1
                if retries <= max_retries:
                    wait_time = 2 ** retries  # 2, 4, 8 seconds
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


def extract_artist_profiles(search_result: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Extract (profile_id, name, additional_info) tuples from search results."""
    results: List[Tuple[str, str, str]] = []

    if (
        "data" not in search_result
        or "profiles" not in search_result["data"]
        or "items" not in search_result["data"]["profiles"]
    ):
        return results

    for item in search_result["data"]["profiles"]["items"]:
        if "id" in item and "name" in item:
            muso_id = item["id"]
            name = item["name"]
            popularity = item.get("popularity", "Unknown")
            credit_count = item.get("creditCount", "Unknown")
            common_credits = item.get("commonCredits", [])
            credits_str = ", ".join(common_credits) if common_credits else "Unknown"
            additional_info = f"Popularity: {popularity}, Credits: {credit_count}, Roles: {credits_str}"
            results.append((muso_id, name, additional_info))
    return results


def format_credit_item(item: Dict[str, Any]) -> str:
    """Return a formatted string summarising a single credit item."""
    track = item.get("track", {})
    album = item.get("album", {})
    track_id = track.get("id", "N/A")
    title = track.get("title", "N/A")
    release_title = album.get("title", "N/A")
    release_date = item.get("releaseDate", "N/A")
    label = item.get("label", "N/A")

    # Roles
    roles: List[str] = []
    for credit in item.get("credits", []):
        parent = credit.get("parent", "")
        child = credit.get("child")
        role_str = parent
        if child:
            role_str += f"/{child}"
        roles.append(role_str)
    roles_str = ", ".join(roles) if roles else "N/A"

    return (
        f"Track: {title} (ID: {track_id})\n"
        f"  Release: {release_title} | Date: {release_date}\n"
        f"  Label: {label}\n"
        f"  Roles: {roles_str}"
    )


def display_credits_summary(credits_data: Dict[str, Any], max_items: int = 20) -> None:
    """Display a human-readable summary of profile credits."""
    if "data" not in credits_data or "items" not in credits_data["data"]:
        print("No credits data found in the response.")
        return

    items = credits_data["data"]["items"]
    total_count = credits_data["data"].get("totalCount", len(items))

    print("\n=== MUSO.ai Profile Credits Summary ===")
    print(f"Total Credits: {total_count}\n")

    for idx, item in enumerate(items[:max_items], 1):
        print(f"{idx}. {format_credit_item(item)}\n")

    if len(items) > max_items:
        print(f"Showing first {max_items} of {len(items)} items.\n")


def main():
    print("MUSO.ai Profile Credits")
    print("-----------------------")

    # Initial API status
    print("\nCurrent API Status:")
    print_api_status()
    print()

    print("Search options:")
    print("1. Enter profile ID")
    print("2. Search by artist/performer name")

    while True:
        try:
            option = int(input("\nSelect an option (1-2): "))
            if option in (1, 2):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

    if option == 1:
        # Option 1: Direct profile ID
        profile_id = input("Enter MUSO.ai Profile ID: ").strip()
        if not profile_id:
            print("Error: Profile ID is required.")
            sys.exit(1)
    else:
        # Option 2: Search by name
        artist_name = input("Enter artist/performer name: ").strip()
        if not artist_name:
            print("Error: Name is required.")
            sys.exit(1)

        print(f"\nSearching MUSO.ai for: {artist_name}...")
        search_result = search_artist(artist_name, API_KEY)
        profiles = extract_artist_profiles(search_result)

        if not profiles:
            print("No profiles found. Try a different search term.")
            sys.exit(1)

        # Display profile options
        print("\nProfiles found:")
        for i, (pid, name, info) in enumerate(profiles, 1):
            print(f"{i}. {name}\n   ID: {pid}\n   Info: {info}\n")

        # User selects
        while True:
            try:
                selection = int(input("Select a profile (number), or 0 to cancel: "))
                if 0 <= selection <= len(profiles):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")

        if selection == 0:
            print("Operation cancelled.")
            sys.exit(0)

        profile_id = profiles[selection - 1][0]
        print(f"\nFetching credits for: {profiles[selection - 1][1]} (ID: {profile_id})")

    # Ask limit
    try:
        limit_input = input("How many credits would you like to retrieve? (default 20): ").strip()
        limit = int(limit_input) if limit_input else 20
    except ValueError:
        print("Invalid number. Using default limit of 20.")
        limit = 20

    # Ask offset
    try:
        offset_input = input("Enter offset for pagination (default 0): ").strip()
        offset = int(offset_input) if offset_input else 0
    except ValueError:
        print("Invalid number. Using default offset of 0.")
        offset = 0

    credits_data = get_profile_credits(profile_id, API_KEY, limit=limit, offset=offset)

    # Display summary
    display_credits_summary(credits_data, max_items=min(20, limit))

    # Ask to view full JSON
    see_full = input("\nWould you like to see the full JSON response? (y/n): ").strip().lower()
    if see_full == "y":
        print("\nFull JSON Response:")
        pprint.pprint(credits_data, indent=2)

    # Final API status
    print("\n" + "=" * 50)
    print("FINAL API STATUS:")
    print_api_status()


if __name__ == "__main__":
    main()
