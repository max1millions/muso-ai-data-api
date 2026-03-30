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

def search_artist(artist_name, api_key):
    """Search for an artist using the MUSO.ai API with retry logic for rate limiting."""
    
    # Check if we can make the request
    can_make, message = can_make_api_request(1)
    if not can_make:
        print(f"Cannot make API request: {message}")
        sys.exit(1)
    
    url = "https://api.developer.muso.ai/v4/search"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Creating a complete payload according to the API documentation
    payload = {
        "keyword": artist_name,
        "type": ["profile"],
        # "childCredits": ["Composer"],
        "limit": 11,
        "offset": 0,
        # "releaseDateEnd": "2025-05-21",
        # "releaseDateStart": "2000-01-01"
    }
    
    # Fixed number of retries with exponential backoff
    max_retries = 5
    retries = 0
    
    while retries <= max_retries:
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Record successful request
            record_api_request(1, "search")
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Check if it's a rate limit error (HTTP 429)
            if e.response.status_code == 429:
                retries += 1
                if retries <= max_retries:
                    # Wait with exponential backoff
                    wait_time = min(2 ** retries, 60)  # Cap at 60 seconds
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
    
    # This should not be reached
    print("Unexpected error in search function")
    sys.exit(1)

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

