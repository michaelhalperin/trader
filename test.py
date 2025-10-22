import os
import ccxt

# Load API credentials from environment
api_key = "S2kUTR5K1FSp1c9ihh"
api_secret = "IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU"

exchange = ccxt.bybit({
    "apiKey": api_key,
    "secret": api_secret,
    "enableRateLimit": True,
    "options": {
        "defaultType": "unified",  # ✅ Use Unified Trading (derivatives)
    },
})
exchange.set_sandbox_mode(True)  # ✅ Use Bybit Testnet

symbol = "BTC/USDT"  # This will be BTCUSDT perpetual on unified
amount_usdt = 10  # trade 10 USDT worth of BTC

# Fetch current price
ticker = exchange.fetch_ticker(symbol)
price = ticker['last']
amount_btc = round(amount_usdt / price, 6)

print(f"Placing market BUY for {amount_btc} BTC (~{amount_usdt} USDT) on {symbol} (Unified Trading)")

try:
    order = exchange.create_market_buy_order(symbol, amount_btc)
    print("✅ Order placed successfully!")
    print(order)
except Exception as e:
    print("❌ Error placing order:", e)