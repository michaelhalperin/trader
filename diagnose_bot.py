#!/usr/bin/env python3
"""
Diagnostic script to check why the AI trading bot isn't making trades
"""

import os
import sys
from datetime import datetime, timezone

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_trading_bot import AITradingBot

def diagnose_bot():
    """Diagnose why the bot isn't trading"""
    print("🔍 AI Trading Bot Diagnostic")
    print("=" * 50)
    
    try:
        # Initialize bot
        bot = AITradingBot()
        
        # Check 1: Exchange connection
        print("\n1️⃣ Exchange Connection:")
        if bot.exchange:
            print("   ✅ Exchange connected")
            try:
                balance = bot.fetch_account_balance()
                if balance:
                    print(f"   💰 Account Balance: ${balance.get('equity', 0):.2f}")
                else:
                    print("   ❌ Could not fetch balance")
            except Exception as e:
                print(f"   ❌ Balance fetch error: {e}")
        else:
            print("   ❌ No exchange connection")
            return
        
        # Check 2: Daily loss limit
        print("\n2️⃣ Daily Loss Limit:")
        if bot.check_daily_loss_limit():
            print("   🛑 DAILY LOSS LIMIT EXCEEDED - Trading stopped")
            print(f"   📊 Daily start balance: ${bot.daily_start_balance:.2f}")
        else:
            print("   ✅ Daily loss limit OK")
        
        # Check 3: Portfolio exposure
        print("\n3️⃣ Portfolio Exposure:")
        exposure = bot.calculate_total_exposure()
        max_exposure = bot.config['ai_parameters']['max_total_exposure_pct']
        print(f"   📈 Current exposure: {exposure*100:.1f}%")
        print(f"   📊 Max exposure limit: {max_exposure*100:.1f}%")
        if exposure >= max_exposure:
            print("   ⏸️ MAX EXPOSURE REACHED - No new positions allowed")
        else:
            print("   ✅ Exposure limit OK")
        
        # Check 4: Current positions
        print("\n4️⃣ Current Positions:")
        if bot.positions:
            for symbol, pos in bot.positions.items():
                print(f"   📊 {symbol}: {pos['quantity']:.6f} @ ${pos['avg_price']:.2f}")
        else:
            print("   📊 No open positions")
        
        # Check 5: Position limits per coin
        print("\n5️⃣ Position Limits:")
        max_per_coin = bot.config['ai_parameters']['max_positions_per_coin']
        print(f"   📊 Max positions per coin: {max_per_coin}")
        for coin in bot.config['coins']:
            symbol = coin['symbol']
            count = sum(1 for pos_symbol in bot.positions.keys() if pos_symbol == symbol)
            print(f"   📈 {symbol}: {count}/{max_per_coin} positions")
            if count >= max_per_coin:
                print(f"   ⏸️ {symbol} at max positions")
        
        # Check 6: Confidence threshold
        print("\n6️⃣ AI Confidence Threshold:")
        threshold = bot.config['ai_parameters']['confidence_threshold']
        print(f"   🧠 Required confidence: {threshold*100:.1f}%")
        
        # Check 7: Test AI analysis on one coin
        print("\n7️⃣ AI Analysis Test:")
        try:
            test_symbol = "BTC/USDT"
            decision = bot.analyze_coin_ai(test_symbol)
            if decision:
                print(f"   📊 {test_symbol} Analysis:")
                print(f"      Action: {decision.action}")
                print(f"      Confidence: {decision.confidence*100:.1f}%")
                print(f"      Reasoning: {decision.reasoning}")
                print(f"      Position Size: ${decision.position_size_usd:.2f}")
                
                if decision.confidence > threshold:
                    print("   ✅ Confidence above threshold - Would trade")
                else:
                    print("   ⏸️ Confidence below threshold - No trade")
            else:
                print(f"   ❌ No analysis generated for {test_symbol}")
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
        
        # Check 8: Market data availability
        print("\n8️⃣ Market Data Test:")
        try:
            ticker = bot.exchange.fetch_ticker("BTC/USDT")
            print(f"   📊 BTC/USDT Price: ${ticker['last']:.2f}")
            print("   ✅ Market data available")
        except Exception as e:
            print(f"   ❌ Market data error: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 DIAGNOSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")

if __name__ == "__main__":
    diagnose_bot()
