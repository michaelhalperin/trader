#!/usr/bin/env python3
"""
Coin selector and configuration tool
"""

import json
import os

def show_available_coins():
    """Show available coins for trading"""
    
    print("🪙 AVAILABLE CRYPTOCURRENCIES FOR TRADING")
    print("=" * 50)
    
    coins = [
        {"symbol": "BTC/USDT", "name": "Bitcoin", "risk": "Low", "recommended": True},
        {"symbol": "ETH/USDT", "name": "Ethereum", "risk": "Medium", "recommended": True},
        {"symbol": "SOL/USDT", "name": "Solana", "risk": "High", "recommended": True},
        {"symbol": "ADA/USDT", "name": "Cardano", "risk": "Medium", "recommended": True},
        {"symbol": "DOT/USDT", "name": "Polkadot", "risk": "High", "recommended": False},
        {"symbol": "MATIC/USDT", "name": "Polygon", "risk": "High", "recommended": False},
        {"symbol": "AVAX/USDT", "name": "Avalanche", "risk": "High", "recommended": False},
        {"symbol": "LINK/USDT", "name": "Chainlink", "risk": "Medium", "recommended": False},
        {"symbol": "UNI/USDT", "name": "Uniswap", "risk": "High", "recommended": False},
        {"symbol": "ATOM/USDT", "name": "Cosmos", "risk": "High", "recommended": False}
    ]
    
    for i, coin in enumerate(coins, 1):
        status = "✅ RECOMMENDED" if coin["recommended"] else "⚠️  HIGH RISK"
        print(f"{i:2d}. {coin['symbol']:<12} {coin['name']:<15} Risk: {coin['risk']:<8} {status}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 30)
    print("• Start with BTC/USDT (most stable)")
    print("• Add ETH/USDT (good volume)")
    print("• Include SOL/USDT (high volatility)")
    print("• Limit to 3-4 coins initially")
    print("• Adjust trade sizes based on volatility")

def create_custom_config():
    """Create custom multi-coin configuration"""
    
    print("\n⚙️  CUSTOM MULTI-COIN CONFIGURATION")
    print("=" * 40)
    
    # Default configuration
    config = {
        "coins": [
            {"symbol": "BTC/USDT", "max_trade_usd": 50, "enabled": True},
            {"symbol": "ETH/USDT", "max_trade_usd": 30, "enabled": True},
            {"symbol": "SOL/USDT", "max_trade_usd": 20, "enabled": True}
        ],
        "strategy": {
            "fast_period": 5,
            "slow_period": 20,
            "timeframe": "1m"
        },
        "risk": {
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.03,
            "daily_loss_limit_pct": 0.05,
            "max_total_exposure_usd": 200
        }
    }
    
    print("📋 DEFAULT CONFIGURATION:")
    print("-" * 25)
    for coin in config["coins"]:
        print(f"• {coin['symbol']}: ${coin['max_trade_usd']} per trade")
    
    print(f"\n🛡️  RISK SETTINGS:")
    print(f"• Stop Loss: {config['risk']['stop_loss_pct']*100}%")
    print(f"• Take Profit: {config['risk']['take_profit_pct']*100}%")
    print(f"• Daily Loss Limit: {config['risk']['daily_loss_limit_pct']*100}%")
    print(f"• Max Total Exposure: ${config['risk']['max_total_exposure_usd']}")
    
    return config

def show_trading_benefits():
    """Show benefits of multi-coin trading"""
    
    print("\n🚀 BENEFITS OF MULTI-COIN TRADING")
    print("=" * 35)
    print("✅ DIVERSIFICATION:")
    print("   • Spread risk across multiple assets")
    print("   • Reduce impact of single coin crashes")
    print("   • Capture opportunities in different markets")
    
    print("\n✅ INCREASED OPPORTUNITIES:")
    print("   • More trading signals per day")
    print("   • Different coins have different cycles")
    print("   • Some coins trend while others consolidate")
    
    print("\n✅ FLEXIBLE POSITION SIZING:")
    print("   • BTC: $50 per trade (stable)")
    print("   • ETH: $30 per trade (medium risk)")
    print("   • SOL: $20 per trade (high volatility)")
    print("   • ADA: $15 per trade (emerging)")
    
    print("\n⚠️  RISKS TO CONSIDER:")
    print("   • More complex to monitor")
    print("   • Higher total exposure")
    print("   • Need more capital")
    print("   • Correlation between coins")

def main():
    print("🤖 MULTI-COIN TRADING BOT SETUP")
    print("=" * 35)
    
    show_available_coins()
    show_trading_benefits()
    
    config = create_custom_config()
    
    print("\n🎯 NEXT STEPS:")
    print("-" * 15)
    print("1. Choose your coins (3-4 recommended)")
    print("2. Set appropriate trade sizes")
    print("3. Run: python3 multi_coin_bot.py")
    print("4. Monitor dashboard for all coins")
    print("5. Adjust settings based on performance")

if __name__ == "__main__":
    main()
