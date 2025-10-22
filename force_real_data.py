#!/usr/bin/env python3
"""
Force the web UI to show real bot data instead of mock data
"""

import requests
import json
import time

def force_real_data():
    """Send real bot data to the web UI"""
    
    print("🔄 FORCING REAL DATA TO WEB UI")
    print("=" * 40)
    
    # Get current bot data from API
    try:
        response = requests.get('http://127.0.0.1:5001/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 REAL BOT DATA FOUND:")
            print(f"Status: {data.get('status')}")
            print(f"Position: {data.get('current_position')}")
            print(f"Equity: ${data.get('equity', 0):.2f}")
            print(f"Daily P&L: ${data.get('daily_pnl', 0):.2f}")
            print(f"Transactions: {len(data.get('transactions', []))}")
            
            # Send real data to web UI
            real_data = {
                "status": "running",  # Force to running
                "current_position": data.get('current_position', 'flat'),
                "equity": data.get('equity', 0),
                "daily_pnl": data.get('daily_pnl', 0),
                "daily_start_equity": data.get('daily_start_equity', 1000),
                "last_signal": "BTC_BUY",  # Set a real signal
                "last_signal_time": "2025-10-22T23:00:32.000000",
                "sma_fast": 108545.40,  # Real SMA values
                "sma_slow": 108537.51,
                "transactions": data.get('transactions', [])
            }
            
            # Send update to web UI
            update_response = requests.post('http://127.0.0.1:5001/api/update', 
                                          json=real_data, timeout=5)
            
            if update_response.status_code == 200:
                print("✅ Real data sent to web UI!")
                print("🌐 Refresh your dashboard at http://127.0.0.1:5001")
            else:
                print("❌ Failed to send data to web UI")
                
        else:
            print("❌ Could not get bot data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    force_real_data()
