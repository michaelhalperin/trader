#!/usr/bin/env python3
"""
Coin Analyzer - Test any coin for AI buy/sell analysis
Usage: python3 coin_analyzer.py
"""

import os
import sys
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_trading_bot import AITradingBot, MarketRegime, SignalStrength

class CoinAnalyzer:
    def __init__(self):
        """Initialize the coin analyzer"""
        self.bot = AITradingBot()
        self.bot.connect_api()
        print("🔌 Connected to Bybit API")
    
    def analyze_coin(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analyze a specific coin for trading decisions"""
        try:
            print(f"\n🔍 Analyzing {symbol}...")
            
            # Get market data
            ticker = self.bot.exchange.fetch_ticker(symbol)
            print(f"📊 Current Price: ${ticker['last']:.2f}")
            
            # Get historical data for analysis
            ohlcv = self.bot.exchange.fetch_ohlcv(symbol, '1m', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate technical indicators
            df['sma_5'] = df['close'].rolling(window=5).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['rsi'] = self.calculate_rsi(df['close'])
            df['macd'] = self.calculate_macd(df['close'])
            
            # Get latest values
            current_price = df['close'].iloc[-1]
            sma_5 = df['sma_5'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            macd = df['macd'].iloc[-1]
            volatility = df['close'].pct_change().std()
            
            # AI Analysis
            decision = self.bot.analyze_coin_ai(symbol)
            
            if decision:
                # Create analysis result
                analysis = {
                    'symbol': symbol,
                    'current_price': current_price,
                    'sma_5': sma_5,
                    'sma_20': sma_20,
                    'rsi': rsi,
                    'macd': macd,
                    'volatility': volatility,
                    'action': decision.action,
                    'confidence': decision.confidence,
                    'reasoning': decision.reasoning,
                    'position_size_usd': decision.position_size_usd,
                    'stop_loss': decision.stop_loss,
                    'take_profit': decision.take_profit,
                    'risk_reward_ratio': decision.risk_reward_ratio,
                    'market_regime': decision.market_regime.value,
                    'signal_strength': decision.signal_strength.name
                }
                
                return analysis
            else:
                print(f"❌ Could not analyze {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def display_analysis(self, analysis: Dict[str, Any]):
        """Display the analysis results in a formatted way"""
        print(f"\n{'='*60}")
        print(f"🎯 COIN ANALYSIS: {analysis['symbol']}")
        print(f"{'='*60}")
        
        # Price Information
        print(f"\n💰 PRICE DATA:")
        print(f"   Current Price: ${analysis['current_price']:.2f}")
        print(f"   SMA(5): ${analysis['sma_5']:.2f}")
        print(f"   SMA(20): ${analysis['sma_20']:.2f}")
        print(f"   Volatility: {analysis['volatility']*100:.2f}%")
        
        # Technical Indicators
        print(f"\n📊 TECHNICAL INDICATORS:")
        print(f"   RSI: {analysis['rsi']:.2f}")
        print(f"   MACD: {analysis['macd']:.4f}")
        
        # AI Decision
        print(f"\n🤖 AI DECISION:")
        action_emoji = "🟢" if analysis['action'] == "BUY" else "🔴" if analysis['action'] == "SELL" else "⏸️"
        print(f"   Action: {action_emoji} {analysis['action']}")
        print(f"   Confidence: {analysis['confidence']*100:.1f}%")
        print(f"   Signal Strength: {analysis['signal_strength']}")
        print(f"   Market Regime: {analysis['market_regime']}")
        
        # Trading Parameters
        if analysis['action'] != "HOLD":
            print(f"\n💼 TRADING PARAMETERS:")
            print(f"   Position Size: ${analysis['position_size_usd']:.2f}")
            print(f"   Stop Loss: ${analysis['stop_loss']:.2f}")
            print(f"   Take Profit: ${analysis['take_profit']:.2f}")
            print(f"   Risk/Reward: {analysis['risk_reward_ratio']:.2f}")
        
        # Reasoning
        print(f"\n🧠 AI REASONING:")
        print(f"   {analysis['reasoning']}")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION:")
        if analysis['confidence'] >= 0.6:
            if analysis['action'] == "BUY":
                print(f"   ✅ STRONG BUY SIGNAL - High confidence ({analysis['confidence']*100:.1f}%)")
            elif analysis['action'] == "SELL":
                print(f"   ✅ STRONG SELL SIGNAL - High confidence ({analysis['confidence']*100:.1f}%)")
            else:
                print(f"   ✅ STRONG HOLD SIGNAL - High confidence ({analysis['confidence']*100:.1f}%)")
        elif analysis['confidence'] >= 0.4:
            print(f"   ⚠️ MODERATE SIGNAL - Medium confidence ({analysis['confidence']*100:.1f}%)")
        else:
            print(f"   ❌ WEAK SIGNAL - Low confidence ({analysis['confidence']*100:.1f}%)")
        
        print(f"\n{'='*60}")

def main():
    """Main function to run the coin analyzer"""
    print("🔍 AI COIN ANALYZER")
    print("=" * 50)
    print("Analyze any coin for AI-powered buy/sell decisions")
    print("Enter coin symbols like: BTC/USDT, ETH/USDT, SOL/USDT, etc.")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    try:
        analyzer = CoinAnalyzer()
        
        while True:
            # Get user input
            symbol = input("\n🎯 Enter coin symbol (e.g., BTC/USDT): ").strip().upper()
            
            if symbol.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if not symbol:
                print("❌ Please enter a valid coin symbol")
                continue
            
            # Add /USDT if not provided
            if '/' not in symbol:
                symbol = f"{symbol}/USDT"
            
            # Analyze the coin
            analysis = analyzer.analyze_coin(symbol)
            
            if analysis:
                analyzer.display_analysis(analysis)
            else:
                print(f"❌ Could not analyze {symbol}")
                print("💡 Make sure the symbol exists on Bybit (e.g., BTC/USDT, ETH/USDT)")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
