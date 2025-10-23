#!/usr/bin/env python3
"""
AI Trading Bot Profitability Analyzer
Analyzes trading performance and determines if the bot is profitable
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
import statistics

class ProfitabilityAnalyzer:
    def __init__(self, dashboard_url="http://127.0.0.1:5001"):
        self.dashboard_url = dashboard_url
        self.analysis_data = []
        self.start_balance = None
        self.current_balance = None
        self.trades_log = []
        
    def fetch_bot_status(self):
        """Fetch current bot status from dashboard"""
        try:
            response = requests.get(f"{self.dashboard_url}/api/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error fetching bot status: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error connecting to bot: {e}")
            return None
    
    def log_analysis_point(self):
        """Log current analysis point"""
        status = self.fetch_bot_status()
        if status:
            timestamp = datetime.now()
            analysis_point = {
                'timestamp': timestamp,
                'equity': status.get('equity', 0),
                'daily_pnl': status.get('daily_pnl', 0),
                'active_trades': status.get('active_trades', 0),
                'confidence_level': status.get('confidence_level', 0),
                'ai_analysis_count': len(status.get('ai_analysis', [])),
                'market_regime': status.get('market_regime', 'unknown'),
                'status': status.get('status', 'unknown')
            }
            
            # Set initial balance
            if self.start_balance is None:
                self.start_balance = analysis_point['equity']
                print(f"💰 Starting Balance: ${self.start_balance:.2f}")
            
            self.current_balance = analysis_point['equity']
            self.analysis_data.append(analysis_point)
            
            # Log trades if any
            for trade in status.get('ai_analysis', []):
                if trade.get('action') in ['BUY', 'SELL']:
                    trade_log = {
                        'timestamp': timestamp,
                        'symbol': trade.get('symbol'),
                        'action': trade.get('action'),
                        'confidence': trade.get('confidence', 0),
                        'position_size': trade.get('position_size_usd', 0),
                        'reasoning': trade.get('reasoning', ''),
                        'risk_reward': trade.get('risk_reward_ratio', 0)
                    }
                    self.trades_log.append(trade_log)
            
            return analysis_point
        return None
    
    def calculate_profitability_metrics(self):
        """Calculate key profitability metrics"""
        if len(self.analysis_data) < 2:
            return None
        
        # Basic metrics
        start_balance = self.analysis_data[0]['equity']
        current_balance = self.analysis_data[-1]['equity']
        total_return = current_balance - start_balance
        return_percentage = (total_return / start_balance) * 100 if start_balance > 0 else 0
        
        # Trade analysis
        total_trades = len(self.trades_log)
        buy_trades = len([t for t in self.trades_log if t['action'] == 'BUY'])
        sell_trades = len([t for t in self.trades_log if t['action'] == 'SELL'])
        
        # Confidence analysis
        confidences = [t['confidence'] for t in self.trades_log]
        avg_confidence = statistics.mean(confidences) if confidences else 0
        high_confidence_trades = len([c for c in confidences if c > 0.7])
        
        # Position sizing analysis
        position_sizes = [t['position_size'] for t in self.trades_log]
        avg_position_size = statistics.mean(position_sizes) if position_sizes else 0
        max_position_size = max(position_sizes) if position_sizes else 0
        
        # Risk/Reward analysis
        risk_rewards = [t['risk_reward'] for t in self.trades_log if t['risk_reward'] > 0]
        avg_risk_reward = statistics.mean(risk_rewards) if risk_rewards else 0
        
        # Time analysis
        if len(self.analysis_data) > 1:
            time_span = (self.analysis_data[-1]['timestamp'] - self.analysis_data[0]['timestamp']).total_seconds() / 3600  # hours
        else:
            time_span = 0
        
        return {
            'start_balance': start_balance,
            'current_balance': current_balance,
            'total_return': total_return,
            'return_percentage': return_percentage,
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'avg_confidence': avg_confidence,
            'high_confidence_trades': high_confidence_trades,
            'avg_position_size': avg_position_size,
            'max_position_size': max_position_size,
            'avg_risk_reward': avg_risk_reward,
            'time_span_hours': time_span,
            'trades_per_hour': total_trades / time_span if time_span > 0 else 0
        }
    
    def determine_profitability(self, metrics):
        """Determine if bot is profitable based on metrics"""
        if not metrics:
            return "INSUFFICIENT_DATA", "Not enough data to analyze"
        
        # Profitability criteria
        is_profitable = metrics['return_percentage'] > 0
        is_significantly_profitable = metrics['return_percentage'] > 5
        is_highly_profitable = metrics['return_percentage'] > 15
        
        # Risk assessment
        is_risky = metrics['max_position_size'] > (metrics['current_balance'] * 0.1)  # >10% of balance
        is_over_trading = metrics['trades_per_hour'] > 2  # More than 2 trades per hour
        
        # Quality assessment
        has_good_confidence = metrics['avg_confidence'] > 0.6
        has_good_risk_reward = metrics['avg_risk_reward'] > 1.5
        has_diversified_trading = metrics['total_trades'] > 5
        
        # Determine overall status
        if is_highly_profitable and has_good_confidence and has_good_risk_reward:
            status = "HIGHLY_PROFITABLE"
            message = f"🚀 Bot is HIGHLY PROFITABLE! {metrics['return_percentage']:.2f}% return"
        elif is_significantly_profitable and has_good_confidence:
            status = "PROFITABLE"
            message = f"✅ Bot is PROFITABLE! {metrics['return_percentage']:.2f}% return"
        elif is_profitable:
            status = "SLIGHTLY_PROFITABLE"
            message = f"📈 Bot is slightly profitable: {metrics['return_percentage']:.2f}% return"
        elif metrics['return_percentage'] > -5:
            status = "BREAKEVEN"
            message = f"⚖️ Bot is roughly breakeven: {metrics['return_percentage']:.2f}% return"
        else:
            status = "UNPROFITABLE"
            message = f"❌ Bot is UNPROFITABLE: {metrics['return_percentage']:.2f}% return"
        
        # Add warnings
        warnings = []
        if is_risky:
            warnings.append("⚠️ HIGH RISK: Large position sizes detected")
        if is_over_trading:
            warnings.append("⚠️ OVER-TRADING: Too many trades per hour")
        if not has_good_confidence:
            warnings.append("⚠️ LOW CONFIDENCE: Average confidence below 60%")
        if not has_good_risk_reward:
            warnings.append("⚠️ POOR RISK/REWARD: Average ratio below 1.5")
        if not has_diversified_trading:
            warnings.append("⚠️ LOW ACTIVITY: Few trades executed")
        
        return status, message, warnings
    
    def generate_report(self):
        """Generate comprehensive profitability report"""
        print("=" * 80)
        print("🤖 AI TRADING BOT PROFITABILITY ANALYSIS")
        print("=" * 80)
        print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Fetch current status
        current_status = self.fetch_bot_status()
        if not current_status:
            print("❌ Cannot connect to bot. Make sure it's running on http://127.0.0.1:5001")
            return
        
        print("📊 CURRENT BOT STATUS:")
        print(f"   Status: {current_status.get('status', 'Unknown')}")
        print(f"   Balance: ${current_status.get('equity', 0):.2f}")
        print(f"   Daily P&L: ${current_status.get('daily_pnl', 0):.2f}")
        print(f"   Active Trades: {current_status.get('active_trades', 0)}")
        print(f"   AI Confidence: {current_status.get('confidence_level', 0)*100:.1f}%")
        print(f"   Market Regime: {current_status.get('market_regime', 'Unknown')}")
        print()
        
        # Calculate metrics
        metrics = self.calculate_profitability_metrics()
        if not metrics:
            print("❌ Insufficient data for analysis. Run the bot for at least 1 hour.")
            return
        
        print("📈 PROFITABILITY METRICS:")
        print(f"   Starting Balance: ${metrics['start_balance']:.2f}")
        print(f"   Current Balance: ${metrics['current_balance']:.2f}")
        print(f"   Total Return: ${metrics['total_return']:.2f}")
        print(f"   Return Percentage: {metrics['return_percentage']:.2f}%")
        print(f"   Analysis Duration: {metrics['time_span_hours']:.1f} hours")
        print()
        
        print("🎯 TRADING ACTIVITY:")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Buy Trades: {metrics['buy_trades']}")
        print(f"   Sell Trades: {metrics['sell_trades']}")
        print(f"   Trades per Hour: {metrics['trades_per_hour']:.2f}")
        print()
        
        print("🧠 AI PERFORMANCE:")
        print(f"   Average Confidence: {metrics['avg_confidence']*100:.1f}%")
        print(f"   High Confidence Trades: {metrics['high_confidence_trades']}")
        print(f"   Average Position Size: ${metrics['avg_position_size']:.2f}")
        print(f"   Max Position Size: ${metrics['max_position_size']:.2f}")
        print(f"   Average Risk/Reward: {metrics['avg_risk_reward']:.2f}")
        print()
        
        # Determine profitability
        status, message, warnings = self.determine_profitability(metrics)
        
        print("🏆 PROFITABILITY ASSESSMENT:")
        print(f"   {message}")
        print()
        
        if warnings:
            print("⚠️ WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if status in ["HIGHLY_PROFITABLE", "PROFITABLE"]:
            print("   ✅ Bot is performing well! Consider:")
            print("   • Continue monitoring for consistency")
            print("   • Consider increasing position sizes gradually")
            print("   • Monitor for any performance degradation")
        elif status == "SLIGHTLY_PROFITABLE":
            print("   📈 Bot shows promise but needs optimization:")
            print("   • Monitor for longer periods")
            print("   • Check if confidence thresholds need adjustment")
            print("   • Consider market conditions")
        elif status == "BREAKEVEN":
            print("   ⚖️ Bot is not losing money but not profitable:")
            print("   • Review trading parameters")
            print("   • Check market conditions")
            print("   • Consider adjusting confidence thresholds")
        else:
            print("   ❌ Bot needs immediate attention:")
            print("   • Stop trading and review strategy")
            print("   • Check for technical issues")
            print("   • Consider different market conditions")
            print("   • Review risk management settings")
        
        print()
        print("=" * 80)
        
        return {
            'status': status,
            'metrics': metrics,
            'warnings': warnings,
            'recommendations': status
        }
    
    def run_continuous_analysis(self, duration_minutes=60, interval_minutes=5):
        """Run continuous analysis for specified duration"""
        print(f"🔄 Starting continuous analysis for {duration_minutes} minutes...")
        print(f"📊 Checking every {interval_minutes} minutes")
        print()
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Analyzing...")
            
            analysis_point = self.log_analysis_point()
            if analysis_point:
                print(f"   Balance: ${analysis_point['equity']:.2f}")
                print(f"   Active Trades: {analysis_point['active_trades']}")
                print(f"   Confidence: {analysis_point['confidence_level']*100:.1f}%")
            
            print(f"   Next check in {interval_minutes} minutes...")
            print()
            
            time.sleep(interval_minutes * 60)
        
        print("🏁 Analysis complete! Generating final report...")
        print()
        return self.generate_report()

def main():
    """Main function to run profitability analysis"""
    analyzer = ProfitabilityAnalyzer()
    
    print("🤖 AI Trading Bot Profitability Analyzer")
    print("=" * 50)
    print()
    print("Choose analysis mode:")
    print("1. Quick Analysis (current status only)")
    print("2. Continuous Analysis (monitor for 1 hour)")
    print("3. Extended Analysis (monitor for 4 hours)")
    print()
    
    try:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("🚀 Running quick analysis...")
            analyzer.generate_report()
        elif choice == "2":
            print("🔄 Running 1-hour continuous analysis...")
            analyzer.run_continuous_analysis(duration_minutes=60, interval_minutes=5)
        elif choice == "3":
            print("🔄 Running 4-hour extended analysis...")
            analyzer.run_continuous_analysis(duration_minutes=240, interval_minutes=10)
        else:
            print("❌ Invalid choice. Running quick analysis...")
            analyzer.generate_report()
            
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()
