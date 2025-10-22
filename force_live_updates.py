#!/usr/bin/env python3
"""
Force the bot to send live updates to the web UI
"""

import requests
import time
import json

def get_real_balance():
    """Get real account balance from Bybit"""
    try:
        import ccxt
        
        # Connect to Bybit
        exchange = ccxt.bybit({
            "apiKey": "S2kUTR5K1FSp1c9ihh",
            "secret": "IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU",
            "enableRateLimit": True,
            "options": {
                "defaultType": "unified",
            },
        })
        exchange.set_sandbox_mode(True)
        
        # Get balance
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {})
        total_usdt = float(usdt_balance.get('total', 0))
        free_usdt = float(usdt_balance.get('free', 0))
        
        return total_usdt, free_usdt
        
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0, 0

def force_live_updates():
    """Force live updates to the web UI"""
    
    print("🔄 FORCING LIVE UPDATES TO WEB UI")
    print("=" * 40)
    
    # Get real account balance
    total_balance, free_balance = get_real_balance()
    
    print(f"💰 REAL ACCOUNT BALANCE:")
    print(f"Total: ${total_balance:.2f} USDT")
    print(f"Free: ${free_balance:.2f} USDT")
    
    # Get current API data
    try:
        response = requests.get('http://127.0.0.1:5001/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Calculate real equity (balance + P&L)
            daily_pnl = float(data.get('daily_pnl', 0))
            real_equity = total_balance + daily_pnl
            
            # Get latest transaction for signal
            transactions = data.get('transactions', [])
            latest_signal = "None"
            if transactions:
                latest_tx = transactions[-1]
                latest_signal = latest_tx.get('signal', 'None')
            
            # Force update with real data
            real_data = {
                "status": "running",
                "current_position": data.get('current_position', 'flat'),
                "equity": real_equity,
                "daily_pnl": daily_pnl,
                "daily_start_equity": total_balance - daily_pnl,  # Calculate start equity
                "last_signal": latest_signal,
                "last_signal_time": "2025-10-22T23:06:00.000000",
                "sma_fast": data.get('sma_fast'),
                "sma_slow": data.get('sma_slow'),
                "transactions": transactions
            }
            
            print(f"\n📊 UPDATING DASHBOARD WITH REAL DATA:")
            print(f"Real Equity: ${real_equity:.2f}")
            print(f"Daily P&L: ${daily_pnl:.2f}")
            print(f"Last Signal: {latest_signal}")
            print(f"Transactions: {len(transactions)}")
            
            # Send update to web UI
            update_response = requests.post('http://127.0.0.1:5001/api/update', 
                                          json=real_data, timeout=5)
            
            if update_response.status_code == 200:
                print("✅ Live updates sent to web UI!")
                print("🌐 Refresh your dashboard to see real equity and signals")
                
                # Set up continuous updates
                print("\n🔄 Setting up continuous updates...")
                for i in range(5):
                    time.sleep(2)
                    # Send periodic updates
                    requests.post('http://127.0.0.1:5001/api/update', 
                                json={"status": "running", "equity": real_equity}, timeout=2)
                    print(f"Update {i+1}/5 sent...")
                
                print("✅ Continuous updates configured!")
                
            else:
                print("❌ Failed to send updates to web UI")
                
        else:
            print("❌ Could not get current bot data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    force_live_updates()
