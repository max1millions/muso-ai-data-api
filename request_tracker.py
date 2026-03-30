#!/usr/bin/env python3
"""
Request tracking module for MUSO.ai API usage.
Tracks daily request counts and enforces limits.
"""

import json
import os
from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple

class RequestTracker:
    def __init__(self, config_file: str = "api_config.json"):
        """
        Initialize the request tracker.
        
        Args:
            config_file (str): Path to configuration file
        """
        # Get the directory where this script is located (MUSO API directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create a dedicated tracking data folder
        self.tracking_dir = os.path.join(script_dir, "tracking_data")
        os.makedirs(self.tracking_dir, exist_ok=True)
        
        # Set file paths within the tracking directory
        self.config_file = os.path.join(self.tracking_dir, config_file)
        self.data_file = os.path.join(self.tracking_dir, "api_usage.json")
        
        self.config = self._load_config()
        self.usage_data = self._load_usage_data()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration settings."""
        default_config = {
            "enabled": True,
            "daily_limit": 1000,
            "warning_thresholds": [80, 90, 95],  # Percentage thresholds for warnings
            "enforce_limit": True,  # Set to False to just warn but not block
            "reset_hour": 0  # Hour of day when limit resets (0 = midnight)
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                print("Using default configuration.")
        else:
            # Create default config file
            self._save_config(default_config)
            print(f"Created new API tracking configuration at: {self.config_file}")
            
        return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def _load_usage_data(self) -> Dict[str, Any]:
        """Load usage data from file."""
        default_data = {
            "date": str(date.today()),
            "requests_made": 0,
            "last_reset": str(datetime.now())
        }
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # Check if we need to reset for a new day
                    if data.get("date") != str(date.today()):
                        print(f"New day detected. Resetting request count.")
                        data = default_data
                        self._save_usage_data(data)
                    
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load usage data: {e}")
        
        self._save_usage_data(default_data)
        print(f"Created new API usage tracking file at: {self.data_file}")
        return default_data
    
    def _save_usage_data(self, data: Dict[str, Any]) -> None:
        """Save usage data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save usage data: {e}")
    
    def is_enabled(self) -> bool:
        """Check if request tracking is enabled."""
        return self.config.get("enabled", True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current usage status."""
        if not self.is_enabled():
            return {
                "enabled": False,
                "message": "Request tracking is disabled"
            }
        
        requests_made = self.usage_data.get("requests_made", 0)
        daily_limit = self.config.get("daily_limit", 1000)
        remaining = max(0, daily_limit - requests_made)
        percentage_used = (requests_made / daily_limit) * 100 if daily_limit > 0 else 0
        
        return {
            "enabled": True,
            "requests_made": requests_made,
            "daily_limit": daily_limit,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "date": self.usage_data.get("date"),
            "last_reset": self.usage_data.get("last_reset")
        }
    
    def can_make_request(self, count: int = 1) -> Tuple[bool, str]:
        """
        Check if we can make the specified number of requests.
        
        Args:
            count (int): Number of requests to check for
            
        Returns:
            Tuple[bool, str]: (can_make_request, message)
        """
        if not self.is_enabled():
            return True, "Request tracking disabled"
        
        status = self.get_status()
        
        if status["remaining"] >= count:
            return True, f"OK - {status['remaining']} requests remaining"
        else:
            if self.config.get("enforce_limit", True):
                return False, f"LIMIT EXCEEDED - Only {status['remaining']} requests remaining of {status['daily_limit']}"
            else:
                return True, f"WARNING - Only {status['remaining']} requests remaining (limit enforcement disabled)"
    
    def record_request(self, count: int = 1, endpoint: str = "unknown") -> bool:
        """
        Record that requests have been made.
        
        Args:
            count (int): Number of requests made
            endpoint (str): API endpoint for logging purposes
            
        Returns:
            bool: True if recorded successfully
        """
        if not self.is_enabled():
            return True
        
        # Check if we can make these requests
        can_make, message = self.can_make_request(count)
        
        if not can_make and self.config.get("enforce_limit", True):
            raise Exception(f"Request limit exceeded: {message}")
        
        # Record the requests
        self.usage_data["requests_made"] = self.usage_data.get("requests_made", 0) + count
        self.usage_data["last_request"] = str(datetime.now())
        self.usage_data["last_endpoint"] = endpoint
        
        # Save updated data
        self._save_usage_data(self.usage_data)
        
        # Check for warnings
        self._check_warnings()
        
        return True
    
    def _check_warnings(self) -> None:
        """Check if we should issue warnings about usage."""
        status = self.get_status()
        percentage = status["percentage_used"]
        
        for threshold in self.config.get("warning_thresholds", []):
            if percentage >= threshold:
                remaining = status["remaining"]
                if threshold == max(self.config.get("warning_thresholds", [])):
                    print(f"🚨 CRITICAL: {percentage:.1f}% of daily API limit used! Only {remaining} requests remaining!")
                elif percentage >= 90:
                    print(f"⚠️  WARNING: {percentage:.1f}% of daily API limit used. {remaining} requests remaining.")
                elif percentage >= 80:
                    print(f"ℹ️  INFO: {percentage:.1f}% of daily API limit used. {remaining} requests remaining.")
                break
    
    def print_status(self) -> None:
        """Print current usage status."""
        status = self.get_status()
        
        if not status["enabled"]:
            print("📊 API Request Tracking: DISABLED")
            print(f"   Tracking files location: {self.tracking_dir}")
            return
        
        print("📊 API Request Usage Status:")
        print(f"   Date: {status['date']}")
        print(f"   Requests made: {status['requests_made']}")
        print(f"   Daily limit: {status['daily_limit']}")
        print(f"   Remaining: {status['remaining']}")
        print(f"   Usage: {status['percentage_used']:.1f}%")
        print(f"   Tracking files: {self.tracking_dir}")
        
        if status['remaining'] <= 0:
            print("   Status: 🚨 LIMIT REACHED")
        elif status['percentage_used'] >= 95:
            print("   Status: 🚨 CRITICAL")
        elif status['percentage_used'] >= 90:
            print("   Status: ⚠️  WARNING")
        elif status['percentage_used'] >= 80:
            print("   Status: ℹ️  CAUTION")
        else:
            print("   Status: ✅ GOOD")
    
    def get_tracking_info(self) -> Dict[str, str]:
        """Get information about tracking file locations."""
        return {
            "tracking_directory": self.tracking_dir,
            "config_file": self.config_file,
            "usage_file": self.data_file
        }

# Global instance for easy use
_tracker = None

def get_tracker() -> RequestTracker:
    """Get the global request tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = RequestTracker()
    return _tracker

def record_api_request(count: int = 1, endpoint: str = "unknown") -> bool:
    """
    Convenience function to record API requests.
    
    Args:
        count (int): Number of requests made
        endpoint (str): API endpoint name
        
    Returns:
        bool: True if recorded successfully
    """
    return get_tracker().record_request(count, endpoint)

def can_make_api_request(count: int = 1) -> Tuple[bool, str]:
    """
    Convenience function to check if requests can be made.
    
    Args:
        count (int): Number of requests to check for
        
    Returns:
        Tuple[bool, str]: (can_make_request, message)
    """
    return get_tracker().can_make_request(count)

def print_api_status() -> None:
    """Convenience function to print API usage status."""
    get_tracker().print_status()

def disable_tracking() -> None:
    """Disable request tracking (for commercial accounts)."""
    tracker = get_tracker()
    tracker.config["enabled"] = False
    tracker._save_config(tracker.config)
    print("✅ Request tracking disabled")

def enable_tracking(daily_limit: int = 1000) -> None:
    """Enable request tracking with specified limit."""
    tracker = get_tracker()
    tracker.config["enabled"] = True
    tracker.config["daily_limit"] = daily_limit
    tracker._save_config(tracker.config)
    print(f"✅ Request tracking enabled with {daily_limit} daily limit") 