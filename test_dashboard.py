#!/usr/bin/env python3
"""
Test the dashboard to verify it shows real money amounts
"""

import requests
import json

def test_dashboard():
    """Test if the dashboard shows real money amounts"""
    
    print("🧪 TESTING DASHBOARD MONEY DISPLAY")
    print("=" * 40)
    
    try:
        # Get current bot status
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])
            
            if not transactions:
                print("❌ No transactions found")
                return
            
            print("📊 LATEST TRANSACTION ANALYSIS:")
            print("-" * 35)
            
            latest = transactions[-1]
            price = float(latest.get('executed_price', 0))
            size = float(latest.get('executed_size', 0))
            
            if price > 0:
                trade_value = price * size
                print(f"✅ Price: ${price:.2f}")
                print(f"✅ Size: {size:.6f} BTC")
                print(f"✅ Your Money Used: ${trade_value:.2f}")
                print(f"✅ Signal: {latest.get('signal', 'Unknown')}")
                print(f"✅ Order ID: {latest.get('order_id', 'Unknown')}")
                
                print(f"\n🎯 DASHBOARD SHOULD SHOW:")
                print(f"   • Price: ${price:.2f}")
                print(f"   • Size: {size:.6f}")
                print(f"   • Trade Value: ${trade_value:.2f}")
                print(f"   • Your Money Used: ${trade_value:.2f}")
                
                print(f"\n💡 IF YOU STILL SEE $0.00:")
                print("   1. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)")
                print("   2. Open new browser tab")
                print("   3. Clear browser cache")
                print("   4. Check if you're on http://127.0.0.1:5000")
                
            else:
                print("❌ Latest trade has no price data")
                print("   This means the bot hasn't made a trade with real prices yet")
                
        else:
            print("❌ Could not connect to bot")
            print("   Make sure the bot is running")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dashboard()
