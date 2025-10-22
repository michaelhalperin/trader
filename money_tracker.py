#!/usr/bin/env python3
"""
Track how much money the bot is using from your account
"""

import requests
import json
from datetime import datetime

def track_money_usage():
    """Track how much money the bot has used from your account"""
    
    print("💰 BOT MONEY USAGE TRACKER")
    print("=" * 40)
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 CURRENT ACCOUNT STATUS:")
            print(f"Total Equity: ${data.get('equity', 0):.2f}")
            print(f"Daily Start Equity: ${data.get('daily_start_equity', 0):.2f}")
            print(f"Daily P&L: ${data.get('daily_pnl', 0):.2f}")
            print()
            
            # Analyze transactions
            transactions = data.get('transactions', [])
            if not transactions:
                print("📈 No trades yet - Bot hasn't used any money")
                return
            
            print(f"📈 MONEY USAGE ANALYSIS ({len(transactions)} trades):")
            print("-" * 50)
            
            total_money_used = 0.0
            buy_trades = 0
            sell_trades = 0
            
            for i, tx in enumerate(transactions, 1):
                price = float(tx.get('executed_price', 0))
                size = float(tx.get('executed_size', 0))
                trade_value = float(tx.get('trade_value_usd', 0))
                signal = tx.get('signal', 'Unknown')
                side = tx.get('side', 'Unknown')
                
                if trade_value > 0:
                    total_money_used += trade_value
                    
                    if signal == 'buy':
                        buy_trades += 1
                    elif signal == 'sell':
                        sell_trades += 1
                
                print(f"Trade #{i}: {signal.upper()} - ${trade_value:.2f} used")
            
            print("\n💰 SUMMARY:")
            print("-" * 20)
            print(f"Total Money Used: ${total_money_used:.2f}")
            print(f"Buy Trades: {buy_trades}")
            print(f"Sell Trades: {sell_trades}")
            print(f"Average per Trade: ${total_money_used/max(1, len(transactions)):.2f}")
            
            # Show recent trade details
            if transactions:
                latest = transactions[-1]
                latest_value = float(latest.get('trade_value_usd', 0))
                latest_price = float(latest.get('executed_price', 0))
                latest_size = float(latest.get('executed_size', 0))
                
                print(f"\n🎯 LATEST TRADE:")
                print(f"Signal: {latest.get('signal', 'Unknown')}")
                print(f"Price: ${latest_price:.2f}")
                print(f"Size: {latest_size:.6f} BTC")
                print(f"Your Money Used: ${latest_value:.2f}")
                print(f"Time: {latest.get('timestamp', 'Unknown')}")
            
            # Calculate remaining balance
            current_equity = float(data.get('equity', 0))
            money_available = current_equity - total_money_used
            
            print(f"\n💳 ACCOUNT BREAKDOWN:")
            print(f"Current Equity: ${current_equity:.2f}")
            print(f"Money Used in Trades: ${total_money_used:.2f}")
            print(f"Available Balance: ${money_available:.2f}")
            
        else:
            print("❌ Could not connect to bot")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_trade_breakdown():
    """Show detailed breakdown of each trade"""
    
    print("\n📋 DETAILED TRADE BREAKDOWN")
    print("=" * 35)
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/transactions', timeout=5)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])
            
            if not transactions:
                print("No transactions found")
                return
            
            print(f"Found {len(transactions)} transactions:")
            print()
            
            for i, tx in enumerate(transactions, 1):
                price = float(tx.get('executed_price', 0))
                size = float(tx.get('executed_size', 0))
                trade_value = float(tx.get('trade_value_usd', 0))
                
                print(f"Trade #{i}:")
                print(f"  Signal: {tx.get('signal', 'Unknown')}")
                print(f"  Side: {tx.get('side', 'Unknown')}")
                print(f"  Price: ${price:.2f}")
                print(f"  Size: {size:.6f} BTC")
                print(f"  Your Money Used: ${trade_value:.2f}")
                print(f"  Order ID: {tx.get('order_id', 'Unknown')}")
                print(f"  Time: {tx.get('timestamp', 'Unknown')}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    track_money_usage()
    show_trade_breakdown()
    
    print("\n💡 UNDERSTANDING YOUR MONEY USAGE:")
    print("-" * 40)
    print("• Each trade uses a portion of your account balance")
    print("• The bot is configured to use $50 per trade (max)")
    print("• Your money is 'locked' in the position until trade closes")
    print("• Profits/losses are added/subtracted from your balance")
    print("• Monitor the dashboard to see real-time usage")
