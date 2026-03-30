"""
Management script for MUSO.ai API request tracking configuration.
Use this to easily enable/disable tracking and adjust limits.
"""

import sys
from request_tracker import get_tracker, disable_tracking, enable_tracking, print_api_status

def show_current_config():
    """Display current configuration."""
    tracker = get_tracker()
    config = tracker.config
    tracking_info = tracker.get_tracking_info()
    
    print("Current API Configuration:")
    print("=" * 30)
    print(f"Enabled: {config.get('enabled', 'Unknown')}")
    print(f"Daily Limit: {config.get('daily_limit', 'Unknown')}")
    print(f"Enforce Limit: {config.get('enforce_limit', 'Unknown')}")
    print(f"Warning Thresholds: {config.get('warning_thresholds', 'Unknown')}%")
    print(f"Tracking Files Location: {tracking_info['tracking_directory']}")
    print()
    
    if config.get('enabled'):
        print_api_status()

def configure_for_commercial():
    """Configure for commercial account (disable tracking)."""
    print("Configuring for commercial account...")
    disable_tracking()
    print("\n✅ Commercial configuration complete!")
    print("   - Request tracking disabled")
    print("   - No daily limits enforced")
    print("   - Scripts will run without request checks")

def configure_for_developer():
    """Configure for developer account (enable tracking)."""
    print("Configuring for developer account...")
    
    # Ask for daily limit
    while True:
        try:
            limit = input("Enter daily request limit (default 1000): ").strip()
            if not limit:
                limit = 1000
            else:
                limit = int(limit)
            break
        except ValueError:
            print("Please enter a valid number.")
    
    enable_tracking(limit)
    
    # Configure enforcement
    tracker = get_tracker()
    enforce = input("Enforce limit strictly? (y/n, default y): ").lower()
    tracker.config['enforce_limit'] = enforce not in ['n', 'no']
    
    # Save configuration
    tracker._save_config(tracker.config)
    
    print(f"\n✅ Developer configuration complete!")
    print(f"   - Request tracking enabled")
    print(f"   - Daily limit: {limit}")
    print(f"   - Enforcement: {'Strict' if tracker.config['enforce_limit'] else 'Warning only'}")

def reset_usage():
    """Reset current day's usage count."""
    tracker = get_tracker()
    tracker.usage_data['requests_made'] = 0
    tracker._save_usage_data(tracker.usage_data)
    print("✅ Usage count reset to 0")

def main():
    print("MUSO.ai API Configuration Manager")
    print("=" * 35)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            show_current_config()
        elif command == "commercial":
            configure_for_commercial()
        elif command == "developer":
            configure_for_developer()
        elif command == "reset":
            reset_usage()
        elif command == "disable":
            disable_tracking()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: status, commercial, developer, reset, disable")
        return
    
    # Interactive mode
    while True:
        print("\nOptions:")
        print("1. Show current configuration")
        print("2. Configure for commercial account (disable tracking)")
        print("3. Configure for developer account (enable tracking)")
        print("4. Reset today's usage count")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            show_current_config()
        elif choice == "2":
            configure_for_commercial()
        elif choice == "3":
            configure_for_developer()
        elif choice == "4":
            reset_usage()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main() 