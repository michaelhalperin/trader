#!/usr/bin/env python3
"""
Test UI connection by sending sample data
"""

import requests
import time

def test_ui_connection():
    """Test sending data to the web UI"""
    print("🧪 Testing UI Connection...")
    
    try:
        # Test sending status update
        response = requests.post('http://127.0.0.1:5000/api/update', 
                               json={
                                   "status": "running",
                                   "current_position": "flat",
                                   "equity": 9940.06,
                                   "daily_pnl": 0.0,
                                   "last_signal": "None",
                                   "sma_fast": 45000.0,
                                   "sma_slow": 44800.0
                               }, 
                               timeout=5)
        
        if response.status_code == 200:
            print("✅ UI Connection Test: SUCCESS")
            print("   Dashboard should now show updated data")
        else:
            print(f"❌ UI Connection Test: FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ UI Connection Test: ERROR - {e}")
        print("   Make sure the web UI is running at http://127.0.0.1:5000")

if __name__ == "__main__":
    test_ui_connection()
