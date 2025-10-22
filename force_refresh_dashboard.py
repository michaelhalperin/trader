#!/usr/bin/env python3
"""
Force refresh the dashboard to show real money amounts
"""

import webbrowser
import time
import requests

def force_refresh_dashboard():
    """Open dashboard with cache-busting parameters"""
    
    print("🔄 FORCING DASHBOARD REFRESH")
    print("=" * 35)
    
    # Add timestamp to bust cache
    timestamp = int(time.time())
    url = f"http://127.0.0.1:5000/?v={timestamp}"
    
    print(f"🌐 Opening dashboard: {url}")
    print("📊 This should show:")
    print("   ✅ 'Your Money Used' column")
    print("   ✅ Real prices ($108,790.60)")
    print("   ✅ Trade values ($49.93)")
    print()
    
    try:
        # Test if the server is running
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=2)
        if response.status_code == 200:
            print("✅ Bot is running - opening dashboard...")
            webbrowser.open(url)
            print("🚀 Dashboard opened in your browser!")
            print()
            print("💡 If you still see old data:")
            print("   1. Press Ctrl+F5 (or Cmd+Shift+R on Mac)")
            print("   2. Or open a new incognito/private window")
            print("   3. Or clear your browser cache")
        else:
            print("❌ Bot is not running")
            print("   Start the bot first: python3 bybit_bot.py")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the bot and web UI are running")

if __name__ == "__main__":
    force_refresh_dashboard()
