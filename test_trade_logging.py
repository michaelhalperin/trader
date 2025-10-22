#!/usr/bin/env python3
"""
Test trade logging to verify real prices are captured
"""

import requests
import time

def test_trade_logging():
    """Test if the bot is now capturing real trade prices"""
    
    print("🔍 TESTING TRADE LOGGING IMPROVEMENTS")
    print("=" * 45)
    
    try:
        # Get current status
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 CURRENT BOT STATUS:")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Equity: ${data.get('equity', 0):.2f}")
            print(f"Position: {data.get('current_position', 'Unknown')}")
            print(f"Last Signal: {data.get('last_signal', 'None')}")
            
            # Check transactions
            transactions = data.get('transactions', [])
            print(f"\n📈 RECENT TRANSACTIONS ({len(transactions)} total):")
            print("-" * 50)
            
            for i, tx in enumerate(transactions[-3:], 1):  # Show last 3 trades
                price = float(tx.get('executed_price', 0))
                size = float(tx.get('executed_size', 0))
                trade_value = float(tx.get('trade_value_usd', 0))
                
                print(f"Trade #{i}:")
                print(f"  Signal: {tx.get('signal', 'Unknown')}")
                print(f"  Side: {tx.get('side', 'Unknown')}")
                print(f"  Price: ${price:.2f}")
                print(f"  Size: {size:.6f} BTC")
                print(f"  Value: ${trade_value:.2f}")
                print(f"  Order ID: {tx.get('order_id', 'Unknown')}")
                print()
            
            # Check if prices are now showing
            recent_tx = transactions[-1] if transactions else {}
            recent_price = float(recent_tx.get('executed_price', 0))
            
            if recent_price > 0:
                print("✅ SUCCESS: Real prices are now being captured!")
                print(f"   Latest trade price: ${recent_price:.2f}")
            else:
                print("⚠️  WARNING: Prices still showing as $0.00")
                print("   This might be because no new trades have occurred yet")
                
        else:
            print("❌ Could not connect to bot")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def monitor_for_trades():
    """Monitor for new trades with real prices"""
    
    print("\n👀 MONITORING FOR NEW TRADES...")
    print("Watch for SMA crossover signals that will trigger trades")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', [])
                
                if transactions:
                    latest_tx = transactions[-1]
                    price = float(latest_tx.get('executed_price', 0))
                    trade_value = float(latest_tx.get('trade_value_usd', 0))
                    
                    if price > 0:
                        print(f"🎉 NEW TRADE DETECTED!")
                        print(f"   Signal: {latest_tx.get('signal', 'Unknown')}")
                        print(f"   Price: ${price:.2f}")
                        print(f"   Value: ${trade_value:.2f}")
                        print(f"   Time: {latest_tx.get('timestamp', 'Unknown')}")
                        break
                    else:
                        print(f"⏳ Waiting for trades... (Latest price: ${price:.2f})")
                else:
                    print("⏳ No transactions yet...")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    test_trade_logging()
    
    print("\n" + "="*50)
    print("💡 NEXT STEPS:")
    print("1. The bot is now improved to capture real prices")
    print("2. When SMA crossover occurs, you'll see real trade amounts")
    print("3. Dashboard will show actual USD values for each trade")
    print("4. Monitor the dashboard at http://127.0.0.1:5000")
    
    # Ask if user wants to monitor
    try:
        monitor_choice = input("\nWould you like to monitor for new trades? (y/n): ").lower()
        if monitor_choice == 'y':
            monitor_for_trades()
    except:
        pass
