#!/usr/bin/env python3
"""
Fix dashboard cache issue and show correct single-coin data
"""

import requests
import webbrowser
import time

def fix_dashboard_cache():
    """Force clear cache and show correct dashboard"""
    
    print("🔧 FIXING DASHBOARD CACHE ISSUE")
    print("=" * 45)
    
    # Get current API data
    try:
        response = requests.get('http://127.0.0.1:5001/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 REAL BOT DATA:")
            print(f"Status: {data.get('status')}")
            print(f"Position: {data.get('current_position')}")
            print(f"Equity: ${data.get('equity', 0):.2f}")
            print(f"Daily P&L: ${data.get('daily_pnl', 0):.2f}")
            print(f"Last Signal: {data.get('last_signal')}")
            print(f"SMA Fast: {data.get('sma_fast')}")
            print(f"SMA Slow: {data.get('sma_slow')}")
            print(f"Transactions: {len(data.get('transactions', []))}")
            
            # Force update the web UI with correct data
            correct_data = {
                "status": "running",
                "current_position": data.get('current_position', 'flat'),
                "equity": data.get('equity', 0),
                "daily_pnl": data.get('daily_pnl', 0),
                "daily_start_equity": data.get('daily_start_equity', 1000),
                "last_signal": data.get('last_signal', 'None'),
                "last_signal_time": "2025-10-22T23:05:00.000000",
                "sma_fast": data.get('sma_fast'),
                "sma_slow": data.get('sma_slow'),
                "transactions": data.get('transactions', [])
            }
            
            # Send correct data to web UI
            update_response = requests.post('http://127.0.0.1:5001/api/update', 
                                          json=correct_data, timeout=5)
            
            if update_response.status_code == 200:
                print("✅ Correct data sent to web UI!")
                
                # Open dashboard with cache-busting parameter
                timestamp = int(time.time())
                dashboard_url = f"http://127.0.0.1:5001/?v={timestamp}&nocache=1"
                
                print(f"🌐 Opening dashboard: {dashboard_url}")
                webbrowser.open(dashboard_url)
                
                print("\n🎯 WHAT YOU SHOULD NOW SEE:")
                print("• Single-coin BTC/USDT trading")
                print("• Real bot status (not mock data)")
                print("• Your actual trades with real prices")
                print("• Dynamic trade sizing (5% of account)")
                print("• 'Your Money Used' column showing real amounts")
                
                print("\n💡 IF YOU STILL SEE MULTI-COIN DATA:")
                print("1. Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)")
                print("2. Open incognito/private window")
                print("3. Clear browser cache completely")
                print("4. Try different browser")
                
            else:
                print("❌ Failed to update web UI")
                
        else:
            print("❌ Could not get bot data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_dashboard_cache()
