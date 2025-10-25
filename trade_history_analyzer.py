#!/usr/bin/env python3
"""
Trade History Analyzer - Check account trades and analyze performance
Usage: python3 trade_history_analyzer.py
"""

import os
import sys
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_trading_bot import AITradingBot

class TradeHistoryAnalyzer:
    def __init__(self):
        """Initialize the trade history analyzer"""
        self.bot = AITradingBot()
        self.bot.connect_api()
        print("🔌 Connected to Bybit API")
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get current account balance"""
        try:
            balance = self.bot.fetch_account_balance()
            if balance:
                return {
                    'equity': balance.get('equity', 0),
                    'free_balance': balance.get('free_balance', 0),
                    'total_balance': balance.get('total_balance', 0),
                    'timestamp': datetime.now(timezone.utc)
                }
        except Exception as e:
            print(f"❌ Error fetching balance: {e}")
        return None
    
    def get_trading_history(self, symbol: str = None, days: int = 7) -> List[Dict]:
        """Get trading history from Bybit"""
        try:
            print(f"📊 Fetching trading history for last {days} days...")
            
            # Get orders history
            orders = self.bot.exchange.fetch_orders(symbol, limit=100)
            
            # Filter recent orders
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            recent_orders = []
            
            for order in orders:
                order_time = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                if order_time >= cutoff_date:
                    recent_orders.append({
                        'id': order['id'],
                        'symbol': order['symbol'],
                        'side': order['side'],
                        'amount': order['amount'],
                        'price': order['price'],
                        'cost': order['cost'],
                        'status': order['status'],
                        'filled': order['filled'],
                        'timestamp': order_time,
                        'type': order['type']
                    })
            
            return recent_orders
            
        except Exception as e:
            print(f"❌ Error fetching trading history: {e}")
            return []
    
    def get_positions(self) -> List[Dict]:
        """Get current open positions"""
        try:
            positions = self.bot.exchange.fetch_positions()
            active_positions = []
            
            for pos in positions:
                if pos['contracts'] > 0:  # Only active positions
                    active_positions.append({
                        'symbol': pos['symbol'],
                        'side': pos['side'],
                        'size': pos['contracts'],
                        'entry_price': pos['entryPrice'],
                        'mark_price': pos['markPrice'],
                        'unrealized_pnl': pos['unrealizedPnl'],
                        'percentage': pos['percentage'],
                        'timestamp': datetime.now(timezone.utc)
                    })
            
            return active_positions
            
        except Exception as e:
            print(f"❌ Error fetching positions: {e}")
            return []
    
    def analyze_trading_activity(self, orders: List[Dict]) -> Dict[str, Any]:
        """Analyze trading activity patterns"""
        if not orders:
            return {'total_trades': 0, 'message': 'No trades found'}
        
        # Group by date
        trades_by_date = {}
        for order in orders:
            date = order['timestamp'].date()
            if date not in trades_by_date:
                trades_by_date[date] = []
            trades_by_date[date].append(order)
        
        # Calculate statistics
        total_trades = len(orders)
        buy_orders = len([o for o in orders if o['side'] == 'buy'])
        sell_orders = len([o for o in orders if o['side'] == 'sell'])
        
        # Calculate total volume
        total_volume = sum(order['cost'] for order in orders if order['cost'])
        
        # Find most active symbols
        symbol_counts = {}
        for order in orders:
            symbol = order['symbol']
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        most_active = max(symbol_counts.items(), key=lambda x: x[1]) if symbol_counts else ('None', 0)
        
        return {
            'total_trades': total_trades,
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'total_volume': total_volume,
            'trades_by_date': trades_by_date,
            'most_active_symbol': most_active[0],
            'most_active_count': most_active[1],
            'date_range': {
                'start': min(order['timestamp'] for order in orders) if orders else None,
                'end': max(order['timestamp'] for order in orders) if orders else None
            }
        }
    
    def check_bot_status(self) -> Dict[str, Any]:
        """Check if the bot is actually running and trading"""
        try:
            # Check if bot is connected
            balance = self.get_account_balance()
            
            # Check recent orders
            recent_orders = self.get_trading_history(days=1)
            
            # Check positions
            positions = self.get_positions()
            
            return {
                'api_connected': balance is not None,
                'current_balance': balance,
                'recent_orders_24h': len(recent_orders),
                'active_positions': len(positions),
                'last_order_time': max(order['timestamp'] for order in recent_orders) if recent_orders else None,
                'positions': positions
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def display_analysis(self, analysis: Dict[str, Any]):
        """Display the analysis results"""
        print(f"\n{'='*70}")
        print(f"🔍 TRADE HISTORY ANALYSIS")
        print(f"{'='*70}")
        
        # Account Status
        print(f"\n💰 ACCOUNT STATUS:")
        if analysis.get('current_balance'):
            balance = analysis['current_balance']
            print(f"   Equity: ${balance['equity']:.2f}")
            print(f"   Free Balance: ${balance['free_balance']:.2f}")
            print(f"   Total Balance: ${balance['total_balance']:.2f}")
        else:
            print("   ❌ Could not fetch balance")
        
        # Trading Activity
        print(f"\n📊 TRADING ACTIVITY (Last 7 Days):")
        activity = analysis.get('trading_activity', {})
        print(f"   Total Trades: {activity.get('total_trades', 0)}")
        print(f"   Buy Orders: {activity.get('buy_orders', 0)}")
        print(f"   Sell Orders: {activity.get('sell_orders', 0)}")
        print(f"   Total Volume: ${activity.get('total_volume', 0):.2f}")
        print(f"   Most Active: {activity.get('most_active_symbol', 'None')} ({activity.get('most_active_count', 0)} trades)")
        
        # Recent Activity
        print(f"\n⏰ RECENT ACTIVITY (Last 24h):")
        status = analysis.get('bot_status', {})
        print(f"   Orders in 24h: {status.get('recent_orders_24h', 0)}")
        print(f"   Active Positions: {status.get('active_positions', 0)}")
        if status.get('last_order_time'):
            print(f"   Last Order: {status['last_order_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            print(f"   Last Order: None")
        
        # Positions
        if status.get('positions'):
            print(f"\n📈 ACTIVE POSITIONS:")
            for pos in status['positions']:
                pnl_color = "🟢" if pos['unrealized_pnl'] > 0 else "🔴" if pos['unrealized_pnl'] < 0 else "⚪"
                print(f"   {pos['symbol']}: {pos['side']} {pos['size']} @ ${pos['entry_price']:.2f} {pnl_color} ${pos['unrealized_pnl']:.2f}")
        
        # Analysis Summary
        print(f"\n🎯 ANALYSIS SUMMARY:")
        if activity.get('total_trades', 0) == 0:
            print("   ❌ NO TRADES FOUND - Bot may not be trading")
            print("   💡 Possible reasons:")
            print("      - Bot not running")
            print("      - Confidence threshold too high")
            print("      - Daily loss limit exceeded")
            print("      - No market opportunities")
        elif status.get('recent_orders_24h', 0) == 0:
            print("   ⚠️ NO TRADES IN 24H - Bot may be inactive")
            print("   💡 Check bot logs for issues")
        else:
            print("   ✅ Bot is actively trading")
        
        print(f"\n{'='*70}")

def main():
    """Main function to run the trade history analyzer"""
    print("🔍 TRADE HISTORY ANALYZER")
    print("=" * 50)
    print("Analyze your trading history and account status")
    print("=" * 50)
    
    try:
        analyzer = TradeHistoryAnalyzer()
        
        # Get trading history
        print("\n📊 Fetching trading data...")
        orders = analyzer.get_trading_history(days=7)
        
        # Analyze trading activity
        trading_activity = analyzer.analyze_trading_activity(orders)
        
        # Check bot status
        bot_status = analyzer.check_bot_status()
        
        # Combine analysis
        analysis = {
            'trading_activity': trading_activity,
            'bot_status': bot_status,
            'current_balance': bot_status.get('current_balance')
        }
        
        # Display results
        analyzer.display_analysis(analysis)
        
        # Additional checks
        print(f"\n🔧 ADDITIONAL CHECKS:")
        
        # Check if bot is running
        if bot_status.get('api_connected'):
            print("   ✅ API Connection: Working")
        else:
            print("   ❌ API Connection: Failed")
        
        # Check for recent activity
        if bot_status.get('recent_orders_24h', 0) > 0:
            print("   ✅ Recent Activity: Found")
        else:
            print("   ❌ Recent Activity: None")
        
        # Check balance changes
        if bot_status.get('current_balance'):
            balance = bot_status['current_balance']
            if balance['equity'] > 0:
                print(f"   ✅ Account Balance: ${balance['equity']:.2f}")
            else:
                print("   ❌ Account Balance: $0.00")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if trading_activity.get('total_trades', 0) == 0:
            print("   1. Check if bot is running on Render")
            print("   2. Verify confidence threshold (currently 49%)")
            print("   3. Check daily loss limits")
            print("   4. Monitor bot logs for errors")
        else:
            print("   1. Bot is trading - check individual trade performance")
            print("   2. Monitor profit/loss on positions")
            print("   3. Review trading frequency and size")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
