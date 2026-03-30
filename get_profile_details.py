"""
Get Profile Details
===================
Returns a summary of the profile details and JSON response for a given artist name or profile ID.
"""

import requests
import sys
from typing import Dict, Any, Optional, List, Tuple
import pprint
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("MUSO_API_KEY")
if not API_KEY:
    raise ValueError("MUSO_API_KEY not found in environment variables. Please check your .env file.")

# Import the search functionality
from search_name import search_artist
# Import request tracking
from request_tracker import record_api_request, can_make_api_request, print_api_status

def get_profile_details(muso_id: str, api_key: str) -> Dict[str, Any]:
    """
    Get detailed profile information from MUSO.ai API using a profile ID.
    
    Args:
        muso_id (str): The MUSO.ai profile ID
        api_key (str): API key for authentication
        
    Returns:
        Dict[str, Any]: Profile details from the API
    """
    # Check if we can make the request
    can_make, message = can_make_api_request(1)
    if not can_make:
        print(f"Cannot make profile details request: {message}")
        return {}
    
    # Format the URL with the ID
    url = f"https://api.developer.muso.ai/v4/profile/{muso_id}"
    
    # Set headers with API key and content type
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Fixed number of retries with exponential backoff
    max_retries = 3
    retries = 0
    
    while retries <= max_retries:
        try:
            # Make the GET request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Record successful request
            record_api_request(1, "profile_details")
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Check if it's a rate limit error (HTTP 429)
            if e.response.status_code == 429:
                retries += 1
                if retries <= max_retries:
                    # Wait with exponential backoff
                    wait_time = 2 ** retries  # 2, 4, 8 seconds...
                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                    continue
            print(f"Error occurred during API request: {e}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API request: {e}")
            sys.exit(1)
    
    print("Maximum retries exceeded")
    return {}

def display_profile_summary(profile_data: Dict[str, Any]) -> None:
    """
    Display a summary of the profile information.
    
    Args:
        profile_data (Dict[str, Any]): Profile data from the API
    """
    if 'data' not in profile_data:
        print("No profile data found in the response.")
        return
    
    data = profile_data['data']
    
    print("\n=== MUSO.ai Profile Summary ===")
    print(f"ID: {data.get('id', 'N/A')}")
    print(f"Name: {data.get('name', 'N/A')}")
    
    # Basic information
    print("\n--- Basic Information ---")
    print(f"City: {data.get('city', 'N/A')}")
    print(f"Country: {data.get('country', 'N/A')}")
    print(f"Popularity: {data.get('popularity', 'N/A')}")
    print(f"Credit Count: {data.get('creditCount', 'N/A')}")
    print(f"Collaborators Count: {data.get('collaboratorsCount', 'N/A')}")
    
    # Common credits
    common_credits = data.get('commonCredits', [])
    if common_credits:
        print(f"Common Credits: {', '.join(common_credits)}")
    
    # Social media and links
    print("\n--- Social Media & Links ---")
    print(f"Website: {data.get('website', 'N/A')}")
    print(f"Spotify ID: {data.get('spotifyId', 'N/A')}")
    print(f"Facebook: {data.get('facebook', 'N/A')}")
    print(f"Instagram: {data.get('instagram', 'N/A')}")
    print(f"Twitter: {data.get('twitter', 'N/A')}")
    
    # IPI numbers
    ipis = data.get('ipis', [])
    if ipis:
        print("\n--- IPI Numbers ---")
        for ipi in ipis:
            print(f"IPI: {ipi}")
    
    # Group memberships
    members_of = data.get('memberOfs', [])
    if members_of:
        print("\n--- Group Memberships ---")
        for group in members_of:
            print(f"Group: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
            periods = group.get('periods', [])
            for period in periods:
                print(f"  Role: {period.get('role', 'N/A')}, Period: {period.get('startDate', 'N/A')} to {period.get('endDate', 'N/A')}")
    
    # Members (if a group)
    members = data.get('members', [])
    if members:
        print("\n--- Group Members ---")
        for member in members:
            print(f"Member: {member.get('name', 'N/A')} (ID: {member.get('id', 'N/A')})")
            periods = member.get('periods', [])
            for period in periods:
                print(f"  Role: {period.get('role', 'N/A')}, Period: {period.get('startDate', 'N/A')} to {period.get('endDate', 'N/A')}")
    
    # Bio (truncated if too long)
    bio = data.get('bio', '')
    if bio:
        print("\n--- Biography ---")
        if len(bio) > 200:
            print(f"{bio[:200]}...")
        else:
            print(bio)

def search_muso_artist(artist_name: str) -> Dict[str, Any]:
    """
    Search for an artist using the MUSO.ai API.
    
    Args:
        artist_name (str): Name of the artist to search for
        
    Returns:
        Dict[str, Any]: Response from the MUSO.ai API
    """
    print(f"Searching MUSO.ai for: {artist_name}")
    return search_artist(artist_name, API_KEY)

def extract_artist_profiles(search_result: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """
    Extract artist profiles from search results.
    
    Args:
        search_result (Dict[str, Any]): Response from the MUSO.ai API
        
    Returns:
        List[Tuple[str, str, str]]: List of (muso_id, name, additional_info) tuples
    """
    results = []
    
    if 'data' not in search_result or 'profiles' not in search_result['data'] or 'items' not in search_result['data']['profiles']:
        return results
    
    for item in search_result['data']['profiles']['items']:
        if 'id' in item and 'name' in item:
            muso_id = item['id']
            name = item['name']
            
            # Get additional info to help verify the artist
            popularity = item.get('popularity', 'Unknown')
            credit_count = item.get('creditCount', 'Unknown')
            
            # Get common credits/roles if available
            common_credits = item.get('commonCredits', [])
            credits_str = ', '.join(common_credits) if common_credits else 'Unknown'
            
            additional_info = f"Popularity: {popularity}, Credits: {credit_count}, Roles: {credits_str}"
            results.append((muso_id, name, additional_info))
    
    return results

def is_profile_id(input_str: str) -> bool:
    """
    Check if the input string looks like a MUSO.ai Profile ID.
    Profile IDs are typically alphanumeric strings without spaces.
    
    Args:
        input_str (str): The input string to check
        
    Returns:
        bool: True if it looks like a Profile ID, False otherwise
    """
    # Profile IDs are typically alphanumeric and don't contain spaces
    # If the string has no spaces and is alphanumeric (allowing hyphens/underscores), treat it as a potential ID
    return bool(input_str and not ' ' in input_str and len(input_str) > 10 and any(c.isdigit() for c in input_str))

def main():
    print("MUSO.ai Profile Details")
    print("----------------------")
    
    # Show initial API status
    print("\nCurrent API Status:")
    print_api_status()
    print()
    
    # Get the artist name or profile ID from command line args or input
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = input("Enter artist/performer name or Profile ID: ")
    
    if not user_input:
        print("Error: Artist name or Profile ID is required.")
        sys.exit(1)
    
    # Check if input looks like a Profile ID
    if is_profile_id(user_input):
        print(f"Detected Profile ID: {user_input}")
        muso_id = user_input
        profile_name = "Unknown"
    else:
        # Search for the artist by name
        search_result = search_muso_artist(user_input)
        
        # Extract artist profiles
        profiles = extract_artist_profiles(search_result)
        
        if not profiles:
            print("No profiles found for this artist. Try a different search term.")
            sys.exit(1)
        
        # Display profiles
        print("\nProfiles found:")
        for i, (muso_id, name, additional_info) in enumerate(profiles, 1):
            print(f"{i}. {name}")
            print(f"   ID: {muso_id}")
            print(f"   Info: {additional_info}")
            print()
        
        # Ask user to select a profile
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
        
        # Get the selected profile
        selected_profile = profiles[selection - 1]
        muso_id = selected_profile[0]
        profile_name = selected_profile[1]
    
    print(f"\nFetching profile details for: {profile_name} (ID: {muso_id})")
    
    # Get profile details
    profile_data = get_profile_details(muso_id, API_KEY)
    
    # Display a summary of the profile
    display_profile_summary(profile_data)
    
    # Ask if user wants to see the full JSON response
    see_full = input("\nWould you like to see the full JSON response? (y/n): ")
    if see_full.lower() == 'y':
        print("\nFull JSON Response:")
        pprint.pprint(profile_data, indent=2)
    
    # Show final API status
    print("\n" + "="*50)
    print("FINAL API STATUS:")
    print_api_status()

if __name__ == "__main__":
    main() 