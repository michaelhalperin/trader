#!/usr/bin/env python3
"""
Check Bybit testnet account balance
"""

import os
import ccxt
from dotenv import load_dotenv

# Load API keys
load_dotenv('api_keys.env')

def check_balance():
    """Check account balance on Bybit testnet"""
    
    # Get API keys
    api_key = os.getenv("BYBIT_API_KEY", "S2kUTR5K1FSp1c9ihh")
    api_secret = os.getenv("BYBIT_API_SECRET", "IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU")
    
    print("🔍 Checking Bybit Testnet Account Balance...")
    print("=" * 50)
    
    try:
        # Connect to Bybit testnet
        exchange = ccxt.bybit({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {
                "defaultType": "unified",  # Check unified trading balance
            },
        })
        exchange.set_sandbox_mode(True)
        
        # Fetch balance
        balance = exchange.fetch_balance()
        
        print("📊 ACCOUNT BALANCE:")
        print("-" * 30)
        
        # Show USDT balance (main trading currency)
        usdt_balance = balance.get('USDT', {})
        usdt_total = usdt_balance.get('total', 0)
        usdt_free = usdt_balance.get('free', 0)
        usdt_used = usdt_balance.get('used', 0)
        
        print(f"💰 USDT Balance:")
        print(f"   Total: {usdt_total:.2f} USDT")
        print(f"   Free:  {usdt_free:.2f} USDT")
        print(f"   Used:  {usdt_used:.2f} USDT")
        
        # Show BTC balance
        btc_balance = balance.get('BTC', {})
        btc_total = btc_balance.get('total', 0)
        btc_free = btc_balance.get('free', 0)
        
        print(f"\n₿ BTC Balance:")
        print(f"   Total: {btc_total:.6f} BTC")
        print(f"   Free:  {btc_free:.6f} BTC")
        
        # Check if enough funds for trading
        min_trade_usd = 50  # From config
        if usdt_free >= min_trade_usd:
            print(f"\n✅ SUFFICIENT FUNDS")
            print(f"   You have {usdt_free:.2f} USDT available")
            print(f"   Bot can trade with max ${min_trade_usd} per trade")
        else:
            print(f"\n❌ INSUFFICIENT FUNDS")
            print(f"   You have {usdt_free:.2f} USDT available")
            print(f"   Bot needs at least ${min_trade_usd} to trade")
            print(f"\n💡 SOLUTION:")
            print(f"   1. Go to https://testnet.bybit.com")
            print(f"   2. Login to your testnet account")
            print(f"   3. Go to 'Assets' → 'Derivatives'")
            print(f"   4. Look for 'Get Testnet Funds' or 'Faucet'")
            print(f"   5. Request USDT for derivatives trading")
        
        # Show other balances
        print(f"\n📋 ALL BALANCES:")
        print("-" * 30)
        for currency, amounts in balance.items():
            if isinstance(amounts, dict) and amounts.get('total', 0) > 0:
                total = amounts.get('total', 0)
                free = amounts.get('free', 0)
                used = amounts.get('used', 0)
                print(f"{currency}: {total:.6f} (Free: {free:.6f}, Used: {used:.6f})")
        
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Check your API keys in api_keys.env")
        print("   2. Ensure you're using testnet API keys")
        print("   3. Make sure your testnet account is active")

if __name__ == "__main__":
    check_balance()
