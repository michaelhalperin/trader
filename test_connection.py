#!/usr/bin/env python3
"""
Test Bybit API connection
"""

import ccxt
import os

def test_connection():
    """Test Bybit API connection"""
    print("🔌 Testing Bybit API Connection...")
    
    try:
        # Create exchange instance
        exchange = ccxt.bybit({
            'apiKey': 'S2kUTR5K1FSp1c9ihh',
            'secret': 'IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU',
            'sandbox': True,  # Testnet
            'enableRateLimit': True,
        })
        
        # Test connection
        print("📡 Testing API connection...")
        balance = exchange.fetch_balance()
        print(f"✅ Connection successful!")
        print(f"💰 USDT Balance: {balance.get('USDT', {}).get('free', 0)}")
        
        # Test market data
        print("📊 Testing market data...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Market data OK - BTC: ${ticker['last']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
