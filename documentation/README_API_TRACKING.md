# MUSO.ai API Request Tracking System

This system provides intelligent request tracking and management for MUSO.ai API usage, designed to work with both developer accounts (with daily limits) and commercial accounts (unlimited).

## 🚀 Quick Start

### For Developer Accounts (1000 requests/day limit):
```bash
# Check current API status
python3 manage_api_config.py status

# Run script with safe delays and monitoring
python3 run_with_delay.py "Artist Name"

# Configure tracking for your account
python3 manage_api_config.py developer
```

### For Commercial Accounts (unlimited requests):
```bash
# Disable tracking once you get commercial access
python3 manage_api_config.py commercial

# Then run scripts normally without delays
python3 print_recording_writer.py "Artist Name"
```

## 📊 Features

### ✅ Request Tracking
- **Daily Usage Monitoring**: Tracks requests across all script runs
- **Automatic Reset**: Resets count daily at midnight
- **Persistent Storage**: Maintains count across script restarts
- **Multi-Endpoint Tracking**: Monitors search, track details, and profile requests

### ⚠️ Smart Warnings
- **80% Warning**: Info notification when approaching limit
- **90% Warning**: Caution warning with remaining count
- **95% Critical**: Critical alert when near limit
- **Limit Protection**: Prevents exceeding daily quota

### 🔧 Flexible Configuration
- **Easy Enable/Disable**: Simple commands for different account types
- **Configurable Limits**: Set custom daily limits
- **Enforcement Options**: Strict blocking or warning-only mode
- **Commercial Ready**: Easily disable for unlimited accounts

## 📁 Files Overview

### Core Files:
- **`request_tracker.py`** - Main tracking module
- **`print_recording_writer.py`** - Updated main script with tracking
- **`search_name.py`** - Updated search with tracking
- **`run_with_delay.py`** - Safe runner with status checks
- **`manage_api_config.py`** - Configuration management

### Generated Files:
- **`api_config.json`** - Configuration settings
- **`api_usage.json`** - Daily usage data

## 🛠️ Configuration

### Initial Setup (Developer Account):
```bash
python3 manage_api_config.py developer
# Enter daily limit: 1000
# Enforce limit strictly? y
```

### Switch to Commercial:
```bash
python3 manage_api_config.py commercial
```

### Check Status Anytime:
```bash
python3 manage_api_config.py status
```

## 🏃‍♂️ Running Scripts

### Option 1: Safe Runner (Recommended for Developer Accounts)
```bash
# With 5-minute delay (default)
python3 run_with_delay.py "Dampszn"

# With custom delay
python3 run_with_delay.py "Dampszn" 10

# No delay
python3 run_with_delay.py "Dampszn" 0

# Just check status
python3 run_with_delay.py "Dampszn" 0
# Then type 's' when prompted
```

### Option 2: Direct Run
```bash
python3 print_recording_writer.py "Dampszn"
```

## 📈 Request Estimation

The system estimates requests needed based on:
- **Search**: 1 request
- **Credit Fetching**: ~10-50 requests (pagination)
- **Track Details**: 1 per unique track
- **Profile Details**: 1 per unique collaborator
- **Buffer**: 25% extra for retries

**Typical Usage**: 50-200 requests per artist

## 🔍 Monitoring

### Real-time Status:
```bash
📊 API Request Usage Status:
   Date: 2024-12-19
   Requests made: 156
   Daily limit: 1000
   Remaining: 844
   Usage: 15.6%
   Status: ✅ GOOD
```

### Request Analysis:
```bash
Request Analysis:
- Estimated requests needed: 125
- Current remaining: 844
✅ Sufficient requests available
```

## ⚙️ Advanced Configuration

### Custom Limits:
Edit `api_config.json`:
```json
{
  "enabled": true,
  "daily_limit": 2000,
  "warning_thresholds": [75, 85, 95],
  "enforce_limit": true
}
```

### Warning-Only Mode:
```json
{
  "enforce_limit": false
}
```

## 🚨 Troubleshooting

### Rate Limiting Issues:
1. **Check Status**: `python3 manage_api_config.py status`
2. **Reset if Needed**: `python3 manage_api_config.py reset`
3. **Use Safe Runner**: `python3 run_with_delay.py "Artist" 10`

### Script Fails Mid-Process:
- Check remaining requests before continuing
- Use longer delays between runs
- Consider splitting large artists across multiple days

### Migration to Commercial:
1. **Disable Tracking**: `python3 manage_api_config.py commercial`
2. **Verify**: Scripts should show "Request tracking disabled"
3. **Remove Delays**: Use direct script calls

## 📝 Best Practices

### For Developer Accounts:
- ✅ Always check status before large operations
- ✅ Use `run_with_delay.py` for safety
- ✅ Monitor usage throughout the day
- ✅ Plan larger artists for early morning (fresh limit)

### For Commercial Accounts:
- ✅ Disable tracking immediately after upgrade
- ✅ Remove artificial delays
- ✅ Run scripts directly as needed

### General:
- ✅ Keep scripts updated
- ✅ Monitor processing logs for errors
- ✅ Use realistic estimates for planning

## 🔄 Daily Reset

The system automatically resets at midnight (configurable). You can also manually reset:

```bash
python3 manage_api_config.py reset
```

## 📞 Support

If you encounter issues:
1. Check `api_config.json` and `api_usage.json` for corruption
2. Try resetting configuration: `python3 manage_api_config.py developer`
3. Review processing logs for API errors
4. Ensure API key is valid and active

---

**Note**: This system is designed to grow with your needs. Start with developer tracking, then easily disable when you upgrade to commercial access. 