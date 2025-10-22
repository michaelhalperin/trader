#!/usr/bin/env python3
"""
Market analysis and trading signal explanation
"""

import requests
import json

def analyze_market():
    """Analyze current market conditions and trading signals"""
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 CURRENT MARKET ANALYSIS")
            print("=" * 40)
            
            sma_fast = data.get('sma_fast', 0)
            sma_slow = data.get('sma_slow', 0)
            
            print(f"SMA(5):  ${sma_fast:.2f}")
            print(f"SMA(20): ${sma_slow:.2f}")
            print(f"Difference: ${sma_fast - sma_slow:.2f}")
            
            # Determine signal
            if sma_fast > sma_slow:
                print("\n📈 SIGNAL: BULLISH")
                print("   SMA(5) is ABOVE SMA(20)")
                print("   🎯 NEXT TRADE: BUY when crossover occurs")
                print("   💡 Market is trending UP")
            elif sma_fast < sma_slow:
                print("\n📉 SIGNAL: BEARISH") 
                print("   SMA(5) is BELOW SMA(20)")
                print("   🎯 NEXT TRADE: SELL when crossover occurs")
                print("   💡 Market is trending DOWN")
            else:
                print("\n➖ SIGNAL: NEUTRAL")
                print("   SMA(5) equals SMA(20)")
                print("   🎯 NEXT TRADE: Wait for crossover")
            
            # Trading conditions
            print("\n🤖 BOT TRADING CONDITIONS:")
            print("-" * 30)
            print("✅ Bot Status:", data.get('status', 'Unknown'))
            print("✅ Position:", data.get('current_position', 'Unknown'))
            print("✅ Equity: ${:.2f}".format(data.get('equity', 0)))
            print("✅ Last Signal:", data.get('last_signal', 'None'))
            
            # Risk management
            print("\n🛡️ RISK MANAGEMENT:")
            print("-" * 20)
            print("• Max Trade Size: $50")
            print("• Stop Loss: 2%")
            print("• Take Profit: 3%")
            print("• Daily Loss Limit: 5%")
            
        else:
            print("❌ Could not connect to bot")
    except Exception as e:
        print(f"❌ Error: {e}")

def explain_strategy():
    """Explain the SMA crossover strategy"""
    
    print("\n📚 SMA CROSSOVER STRATEGY EXPLAINED")
    print("=" * 40)
    print("🎯 HOW IT WORKS:")
    print("1. Bot calculates SMA(5) and SMA(20) every minute")
    print("2. When SMA(5) crosses ABOVE SMA(20) → BUY signal")
    print("3. When SMA(5) crosses BELOW SMA(20) → SELL signal")
    print("4. Bot waits for clear crossovers to avoid false signals")
    
    print("\n📈 BUY CONDITIONS:")
    print("• SMA(5) > SMA(20) = Bullish trend")
    print("• Bot buys BTC with USDT")
    print("• Sets stop-loss at -2%")
    print("• Sets take-profit at +3%")
    
    print("\n📉 SELL CONDITIONS:")
    print("• SMA(5) < SMA(20) = Bearish trend") 
    print("• Bot shorts BTC (sells without owning)")
    print("• Sets stop-loss at +2% (for short)")
    print("• Sets take-profit at -3% (for short)")
    
    print("\n⏰ TIMING:")
    print("• Bot checks every minute")
    print("• Only trades on clear crossovers")
    print("• Avoids duplicate signals")
    print("• Waits for market confirmation")

if __name__ == "__main__":
    analyze_market()
    explain_strategy()
