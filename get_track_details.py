import requests
import sys
from typing import Dict, Any, Optional, List, Tuple
import pprint
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("MUSO_API_KEY")
if not API_KEY:
    raise ValueError("MUSO_API_KEY not found in environment variables. Please check your .env file.")

#
#
#
#
##RETURNS A SUMMARY OF THE TRACK DETAILS & JSON RESPONSE FOR A GIVEN TRACK ID, TITLE, OR ARTIST+TITLE
#
#
#
#

# Import the artist search functionality
from search_name import search_artist
# Import request tracking
from request_tracker import record_api_request, can_make_api_request, print_api_status



def get_track_details(track_id: str, api_key: str) -> Dict[str, Any]:
    """
    Get detailed track information from MUSO.ai API using a track ID.
    
    Args:
        track_id (str): The MUSO.ai track ID
        api_key (str): API key for authentication
        
    Returns:
        Dict[str, Any]: Track details from the API
    """
    # Check if we can make the request
    can_make, message = can_make_api_request(1)
    if not can_make:
        print(f"Cannot make track details request: {message}")
        return {}
    
    # Format the URL with the ID
    url = f"https://api.developer.muso.ai/v4/track/id/{track_id}"
    
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
            record_api_request(1, "track_details")
            
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

def get_profile_credits(muso_id: str, api_key: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Get credits information for a profile from MUSO.ai API using a profile ID.
    
    Args:
        muso_id (str): The MUSO.ai profile ID
        api_key (str): API key for authentication
        limit (int): Number of results to return (default: 20)
        offset (int): Offset for pagination (default: 0)
        
    Returns:
        Dict[str, Any]: Profile credits from the API
    """
    # Format the URL with the ID
    url = f"https://api.developer.muso.ai/v4/profile/{muso_id}/credits"
    
    # Set headers with API key and content type
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Add query parameters for pagination
    params = {
        "limit": limit,
        "offset": offset
    }
    
    # Fixed number of retries
    max_retries = 3
    retries = 0
    while retries <= max_retries:
        try:
            # Make the GET request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Check if it's a rate limit error (HTTP 429)
            if e.response.status_code == 429:
                retries += 1
                if retries <= max_retries:
                    # Wait with exponential backoff
                    wait_time = 2 ** retries  # 2, 4, 8 seconds...
                    print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
            print(f"Error occurred during API request: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API request: {e}")
            raise

def get_artist_tracks(muso_id: str, api_key: str, title_keyword: str = "", limit: int = 30) -> List[Dict[str, Any]]:
    """
    Get tracks by an artist with optional title filter by using the profile credits API.
    
    Args:
        muso_id (str): The artist's MUSO ID
        api_key (str): API key for authentication
        title_keyword (str): Optional track title to filter by
        limit (int): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of tracks by the artist
    """
    # Use a reasonable page size to avoid API limits
    page_size = 20
    offset = 0
    all_items = []
    total_count = None
    
    print(f"Fetching tracks by artist (this might take a moment)...")
    
    try:
        while len(all_items) < limit:
            # Get a page of results
            result = get_profile_credits(muso_id, api_key, limit=page_size, offset=offset)
            
            # Extract data
            if 'data' in result and 'items' in result['data']:
                items = result['data']['items']
                
                # Get total count if not already known
                if total_count is None:
                    total_count = result['data'].get('totalCount', 0)
                
                # Filter by title if a keyword was provided
                if title_keyword:
                    title_keyword_lower = title_keyword.lower()
                    filtered_items = [
                        item for item in items 
                        if 'track' in item 
                        and 'title' in item['track'] 
                        and title_keyword_lower in item['track']['title'].lower()
                    ]
                    all_items.extend(filtered_items)
                else:
                    all_items.extend(items)
                
                # If we got fewer items than requested or reached the total count, we're done
                if len(items) < page_size or (total_count and (offset + len(items)) >= total_count):
                    break
                
                # Move to the next page
                offset += page_size
                
                # Add a small delay to avoid overloading the API
                time.sleep(0.5)
            else:
                break
            
            # Break if we've reached the limit
            if len(all_items) >= limit:
                all_items = all_items[:limit]
                break
            
    except Exception as e:
        print(f"Error while fetching credits: {e}")
    
    return all_items

def search_tracks(keyword: str, api_key: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for tracks using the MUSO.ai API.
    
    Args:
        keyword (str): Search keyword (title)
        api_key (str): API key for authentication
        limit (int): Maximum number of results to return
        
    Returns:
        Dict[str, Any]: Search results from the API
    """
    url = "https://api.developer.muso.ai/v4/search"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Creating payload according to API documentation
    payload = {
        "keyword": keyword,
        "type": ["track"],
        "limit": limit,
        "offset": 0
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API request: {e}")
        sys.exit(1)

def display_track_summary(track_data: Dict[str, Any]) -> None:
    """
    Display a summary of the track information.
    
    Args:
        track_data (Dict[str, Any]): Track data from the API
    """
    if 'data' not in track_data:
        print("No track data found in the response.")
        return
    
    data = track_data['data']
    
    print("\n=== MUSO.ai Track Summary ===")
    print(f"ID: {data.get('id', 'N/A')}")
    print(f"Title: {data.get('title', 'N/A')}")
    
    # Basic information
    print("\n--- Basic Information ---")
    print(f"Duration: {data.get('duration', 'N/A')}")
    print(f"Year: {data.get('year', 'N/A')}")
    print(f"Popularity: {data.get('popularity', 'N/A')}")
    
    # Release information
    release = data.get('release', {})
    if release:
        print("\n--- Release Information ---")
        print(f"Release Title: {release.get('title', 'N/A')}")
        print(f"Release ID: {release.get('id', 'N/A')}")
        print(f"Release Type: {release.get('type', 'N/A')}")
    
    # Artists
    artists = data.get('artists', [])
    if artists:
        print("\n--- Artists ---")
        for artist in artists:
            print(f"Artist: {artist.get('name', 'N/A')} (ID: {artist.get('id', 'N/A')})")
            print(f"  Role: {artist.get('role', 'N/A')}")
    
    # ISRCs
    isrcs = data.get('isrcs', [])
    if isrcs:
        print("\n--- ISRCs ---")
        for isrc in isrcs:
            print(f"ISRC: {isrc}")
    
    # Stream links
    streaming = data.get('streamingUrls', {})
    if streaming:
        print("\n--- Streaming Links ---")
        for platform, url in streaming.items():
            print(f"{platform}: {url}")

def extract_track_results(search_result: Dict[str, Any]) -> List[Tuple[str, str, str, str]]:
    """
    Extract track information from search results.
    
    Args:
        search_result (Dict[str, Any]): Response from the MUSO.ai API
        
    Returns:
        List[Tuple[str, str, str, str]]: List of (track_id, title, artist_names, additional_info) tuples
    """
    results = []
    
    if 'data' not in search_result or 'tracks' not in search_result['data'] or 'items' not in search_result['data']['tracks']:
        return results
    
    for item in search_result['data']['tracks']['items']:
        if 'id' in item and 'title' in item:
            track_id = item['id']
            title = item['title']
            
            # Get artist names
            artists = item.get('artists', [])
            artist_names = ', '.join([artist.get('name', 'Unknown') for artist in artists]) if artists else 'Unknown'
            
            # Get additional info to help verify the track
            release_title = item.get('releaseTitle', 'Unknown')
            year = item.get('year', 'Unknown')
            
            additional_info = f"Release: {release_title}, Year: {year}"
            results.append((track_id, title, artist_names, additional_info))
    
    return results

def extract_artist_credit_tracks(credits: List[Dict[str, Any]]) -> List[Tuple[str, str, str, str]]:
    """
    Extract track information from artist credits.
    
    Args:
        credits (List[Dict[str, Any]]): Credits for an artist
        
    Returns:
        List[Tuple[str, str, str, str]]: List of (track_id, title, artist_names, additional_info) tuples
    """
    results = []
    
    for item in credits:
        track = item.get('track', {})
        if 'id' in track and 'title' in track:
            track_id = track['id']
            title = track['title']
            
            # Get artist names - this should include the artist we searched for
            artists = item.get('artists', [])
            artist_names = ', '.join([artist.get('name', 'Unknown') for artist in artists]) if artists else 'Unknown'
            
            # Additional info
            release_date = item.get('releaseDate', 'Unknown')
            label = item.get('label', 'Unknown')
            roles = []
            
            # Extract credit roles
            credits_list = item.get('credits', [])
            if credits_list:
                for credit in credits_list:
                    role = f"{credit.get('parent', '')}"
                    if credit.get('child'):
                        role += f"/{credit.get('child')}"
                    roles.append(role)
            
            roles_str = ', '.join(roles) if roles else 'Unknown'
            additional_info = f"Released: {release_date}, Label: {label}, Roles: {roles_str}"
            
            results.append((track_id, title, artist_names, additional_info))
    
    return results

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

def main():
    print("MUSO.ai Track Details")
    print("--------------------")
    
    # Show initial API status
    print("\nCurrent API Status:")
    print_api_status()
    print()
    
    # Determine the search method
    print("Search options:")
    print("1. Search by track ID")
    print("2. Search by track title")
    print("3. Search by artist name + track title")
    
    while True:
        try:
            option = int(input("\nSelect search method (1-3): "))
            if 1 <= option <= 3:
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")
    
    if option == 1:
        # Search by track ID
        track_id = input("Enter track ID: ")
        if not track_id:
            print("Error: Track ID is required.")
            sys.exit(1)
        
        print(f"\nFetching track details for ID: {track_id}")
        track_data = get_track_details(track_id, API_KEY)
        
        # Display track summary
        display_track_summary(track_data)
        
        # Ask if user wants to see the full JSON response
        see_full = input("\nWould you like to see the full JSON response? (y/n): ")
        if see_full.lower() == 'y':
            print("\nFull JSON Response:")
            pprint.pprint(track_data, indent=2)
    
    elif option == 2:
        # Search by track title
        track_title = input("Enter track title: ")
        if not track_title:
            print("Error: Track title is required.")
            sys.exit(1)
        
        print(f"\nSearching for tracks with title: {track_title}")
        search_result = search_tracks(track_title, API_KEY)
        
        # Extract track results
        tracks = extract_track_results(search_result)
        
        if not tracks:
            print("No tracks found. Try a different search term.")
            sys.exit(1)
        
        # Display tracks
        print("\nTracks found:")
        for i, (track_id, title, artists, year) in enumerate(tracks, 1):
            print(f"{i}. {title} ({year})")
            print(f"   ID: {track_id}")
            print(f"   Artists: {artists}")
            print()
        
        # Ask user to select a track
        while True:
            try:
                selection = int(input("Select a track (number), or 0 to cancel: "))
                if 0 <= selection <= len(tracks):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        if selection == 0:
            print("Operation cancelled.")
            sys.exit(0)
        
        # Get the selected track
        selected_track = tracks[selection - 1]
        track_id = selected_track[0]
        
        print(f"\nFetching track details for: {selected_track[1]} (ID: {track_id})")
        
        # Get track details
        track_data = get_track_details(track_id, API_KEY)
        
        # Display track summary
        display_track_summary(track_data)
        
        # Ask if user wants to see the full JSON response
        see_full = input("\nWould you like to see the full JSON response? (y/n): ")
        if see_full.lower() == 'y':
            print("\nFull JSON Response:")
            pprint.pprint(track_data, indent=2)
    
    else:  # option == 3
        # Search by artist name + track title
        artist_name = input("Enter artist name: ")
        if not artist_name:
            print("Error: Artist name is required.")
            sys.exit(1)
        
        # Search for the artist
        search_result = search_artist(artist_name, API_KEY)
        
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
        
        # Now get track title filter
        track_title = input("Enter track title (or partial title) to search for: ")
        
        print(f"\nFetching tracks by {selected_profile[1]} matching '{track_title}'...")
        
        # Get tracks by this artist with the title filter
        tracks = get_artist_tracks(muso_id, API_KEY, track_title)
        
        # Extract track information in a consistent format
        formatted_tracks = extract_artist_credit_tracks(tracks)
        
        if not formatted_tracks:
            print(f"No tracks found for {selected_profile[1]} with title containing '{track_title}'.")
            sys.exit(1)
        
        # Display tracks
        print("\nTracks found:")
        for i, (track_id, title, artists, year) in enumerate(formatted_tracks, 1):
            print(f"{i}. {title} ({year})")
            print(f"   ID: {track_id}")
            print(f"   Artists: {artists}")
            print()
        
        # Ask user to select a track
        while True:
            try:
                selection = int(input("Select a track (number), or 0 to cancel: "))
                if 0 <= selection <= len(formatted_tracks):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        if selection == 0:
            print("Operation cancelled.")
            sys.exit(0)
        
        # Get the selected track
        selected_track = formatted_tracks[selection - 1]
        track_id = selected_track[0]
        
        print(f"\nFetching track details for: {selected_track[1]} (ID: {track_id})")
        
        # Get track details
        track_data = get_track_details(track_id, API_KEY)
        
        # Display track summary
        display_track_summary(track_data)
        
        # Ask if user wants to see the full JSON response
        see_full = input("\nWould you like to see the full JSON response? (y/n): ")
        if see_full.lower() == 'y':
            print("\nFull JSON Response:")
            pprint.pprint(track_data, indent=2)
    
    # Show final API status
    print("\n" + "="*50)
    print("FINAL API STATUS:")
    print_api_status()

if __name__ == "__main__":
    main()
