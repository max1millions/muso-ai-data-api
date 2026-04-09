import requests
import sys
import pprint
import time
import os
from dotenv import load_dotenv
from request_tracker import record_api_request, can_make_api_request

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("MUSO_API_KEY")

if not API_KEY:
    raise ValueError("MUSO_API_KEY not found in environment variables. Please check your .env file.")

def _search(keyword, api_key, search_type):
    """Core search function used by search_artist and search_company."""

    can_make, message = can_make_api_request(1)
    if not can_make:
        print(f"Cannot make API request: {message}")
        sys.exit(1)

    url = "https://api.developer.muso.ai/v4/search"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "keyword": keyword,
        "type": [search_type],
        "limit": 11,
        "offset": 0,
    }

    max_retries = 5
    retries = 0

    while retries <= max_retries:
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            record_api_request(1, "search")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retries += 1
                if retries <= max_retries:
                    wait_time = min(2 ** retries, 60)
                    print(f"Rate limit hit during search. Retrying in {wait_time} seconds... (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Rate limit exceeded maximum retries. Please try again later.")
                    sys.exit(1)
            else:
                print(f"HTTP Error occurred during API request: {e}")
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API request: {e}")
            sys.exit(1)

    print("Unexpected error in search function")
    sys.exit(1)


def search_artist(artist_name, api_key):
    """Search for an artist/performer profile using the MUSO.ai API."""
    return _search(artist_name, api_key, "profile")


def search_organization(org_name, api_key):
    """Search for an organization (label, publisher, etc.) using the MUSO.ai API."""
    return _search(org_name, api_key, "organization")

def main():
    print("MUSO.ai Artist Search")
    print("---------------------")
    
    artist_name = input("Enter artist name to search: ")
    
    if not artist_name.strip():
        print("Error: Artist name cannot be empty.")
        return
    
    print(f"\nSearching for: {artist_name}...\n")
    
    # Perform the search using the hardcoded API key
    result = search_artist(artist_name, API_KEY)
    
    # Pretty print the JSON response
    pprint.pprint(result, indent=4, width=100)

if __name__ == "__main__":
    main()

