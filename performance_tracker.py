#!/usr/bin/env python3
"""
Performance tracking and analysis for the trading bot
"""

import csv
import os
from datetime import datetime, timezone
import requests

def analyze_performance():
    """Analyze bot performance from trades.csv"""
    
    trades_file = "trades.csv"
    if not os.path.exists(trades_file):
        print("❌ No trades.csv file found")
        return
    
    print("📊 BOT PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Read trades
    trades = []
    with open(trades_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(row)
    
    if not trades:
        print("📈 No trades recorded yet")
        return
    
    # Calculate metrics
    total_trades = len(trades)
    profitable_trades = 0
    losing_trades = 0
    total_pnl = 0.0
    
    print(f"📈 Total Trades: {total_trades}")
    print("-" * 30)
    
    for i, trade in enumerate(trades, 1):
        pnl = float(trade.get('pnl_usdt', 0) or 0)
        total_pnl += pnl
        
        if pnl > 0:
            profitable_trades += 1
            status = "✅ PROFIT"
        elif pnl < 0:
            losing_trades += 1
            status = "❌ LOSS"
        else:
            status = "➖ BREAKEVEN"
        
        print(f"Trade #{i}: {status} ${pnl:.2f}")
    
    # Summary
    print("\n📊 PERFORMANCE SUMMARY")
    print("=" * 30)
    print(f"Total P&L: ${total_pnl:.2f}")
    print(f"Profitable Trades: {profitable_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {(profitable_trades/total_trades)*100:.1f}%")
    
    if total_pnl > 0:
        print(f"🎉 NET PROFIT: ${total_pnl:.2f}")
    elif total_pnl < 0:
        print(f"📉 NET LOSS: ${total_pnl:.2f}")
    else:
        print("➖ BREAKEVEN")

def get_current_status():
    """Get current bot status from web UI"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print("\n🤖 CURRENT BOT STATUS")
            print("=" * 30)
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Position: {data.get('current_position', 'Unknown')}")
            print(f"Equity: ${data.get('equity', 0):.2f}")
            print(f"Daily P&L: ${data.get('daily_pnl', 0):.2f}")
            print(f"Last Signal: {data.get('last_signal', 'None')}")
            
            # SMA indicators
            sma_fast = data.get('sma_fast')
            sma_slow = data.get('sma_slow')
            if sma_fast and sma_slow:
                print(f"SMA(5): ${sma_fast:.2f}")
                print(f"SMA(20): ${sma_slow:.2f}")
                
                # Signal analysis
                if sma_fast > sma_slow:
                    print("📈 Signal: BULLISH (SMA5 > SMA20)")
                elif sma_fast < sma_slow:
                    print("📉 Signal: BEARISH (SMA5 < SMA20)")
                else:
                    print("➖ Signal: NEUTRAL")
        else:
            print("❌ Could not connect to bot")
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def main():
    print("🚀 BYBIT TRADING BOT - PERFORMANCE TRACKER")
    print("=" * 50)
    
    # Analyze historical performance
    analyze_performance()
    
    # Get current status
    get_current_status()
    
    print("\n💡 PROFITABILITY TIPS:")
    print("-" * 30)
    print("1. Watch the SMA crossover signals")
    print("2. Monitor win rate (aim for >50%)")
    print("3. Check daily P&L regularly")
    print("4. Let the bot run for several days to see trends")
    print("5. The $60 loss might be from a single bad trade")

if __name__ == "__main__":
    main()
