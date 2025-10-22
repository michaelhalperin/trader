#!/usr/bin/env python3
"""
Calculate the actual money used in the latest trade
"""

import requests

def calculate_latest_trade():
    """Calculate the money used in the latest trade"""
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])
            
            if not transactions:
                print("No transactions found")
                return
            
            latest = transactions[-1]
            price = float(latest.get('executed_price', 0))
            size = float(latest.get('executed_size', 0))
            
            if price > 0:
                trade_value = price * size
                print("🎯 LATEST TRADE CALCULATION:")
                print(f"Price: ${price:.2f}")
                print(f"Size: {size:.6f} BTC")
                print(f"Your Money Used: ${trade_value:.2f}")
                print(f"Signal: {latest.get('signal', 'Unknown')}")
                print(f"Order ID: {latest.get('order_id', 'Unknown')}")
            else:
                print("❌ Latest trade has no price data")
                
        else:
            print("❌ Could not connect to bot")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    calculate_latest_trade()
