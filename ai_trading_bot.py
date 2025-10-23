#!/usr/bin/env python3
"""
AI-Powered Multi-Coin Trading Bot with 190 IQ Decision Making
Advanced technical analysis, market sentiment, and intelligent position sizing
"""

import os
import json
import time
import logging
import pandas as pd
import numpy as np
import ccxt
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
import requests
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
LOGGER = logging.getLogger(__name__)

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

class SignalStrength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

@dataclass
class TradingDecision:
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    position_size_usd: float
    stop_loss: float
    take_profit: float
    reasoning: str
    risk_reward_ratio: float
    market_regime: MarketRegime
    signal_strength: SignalStrength

class AITradingBot:
    def __init__(self):
        self.exchange = None
        self.config = self.load_config()
        self.positions = {}
        self.daily_pnl = 0.0
        self.start_equity = 0.0
        self.market_regime = MarketRegime.SIDEWAYS
        self.ai_analysis = []
        self.recent_decisions = []
        
    def load_config(self):
        """Load AI-enhanced configuration"""
        return {
            "coins": [
                {"symbol": "BTC/USDT", "enabled": True, "base_allocation": 0.4},
                {"symbol": "ETH/USDT", "enabled": True, "base_allocation": 0.3},
                {"symbol": "SOL/USDT", "enabled": True, "base_allocation": 0.2},
                {"symbol": "ADA/USDT", "enabled": True, "base_allocation": 0.1}
            ],
            "ai_parameters": {
                "confidence_threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.6")),
                "max_position_size_pct": float(os.getenv("MAX_POSITION_SIZE_PCT", "0.15")),  # Max 15% of portfolio per trade
                "min_position_size_pct": float(os.getenv("MIN_POSITION_SIZE_PCT", "0.02")),  # Min 2% of portfolio per trade
                "volatility_adjustment": True,
                "correlation_limit": 0.7,
                "trend_strength_weight": 0.3,
                "volume_weight": 0.2,
                "momentum_weight": 0.25,
                "support_resistance_weight": 0.25
            },
            "risk_management": {
                "max_daily_loss_pct": float(os.getenv("MAX_DAILY_LOSS_PCT", "0.05")),
                "max_drawdown_pct": float(os.getenv("MAX_DRAWDOWN_PCT", "0.10")),
                "position_sizing_method": "kelly",  # kelly, fixed, volatility_adjusted
                "stop_loss_method": "atr",  # atr, percentage, support_resistance
                "take_profit_method": "risk_reward"  # risk_reward, resistance, trailing
            },
            "api": {
                "api_key": os.getenv("BYBIT_API_KEY", ""),
                "api_secret": os.getenv("BYBIT_API_SECRET", ""),
                "testnet": os.getenv("BYBIT_TESTNET", "true").lower() == "true"
            }
        }
    
    def connect_api(self):
        """Connect to Bybit API"""
        api_config = self.config["api"]
        
        self.exchange = ccxt.bybit({
            "apiKey": api_config["api_key"],
            "secret": api_config["api_secret"],
            "enableRateLimit": True,
            "options": {"defaultType": "unified"},
        })
        self.exchange.set_sandbox_mode(True)  # Testnet mode
        return self.exchange
    
    def fetch_account_balance(self):
        """Fetch account balance from exchange"""
        try:
            if self.exchange:
                balance = self.exchange.fetch_balance()
                usdt_balance = balance.get('USDT', {}).get('free', 0.0)
                total_balance = balance.get('total', {}).get('USDT', 0.0)
                
                # Only return real data if we got valid values
                if total_balance > 0:
                    return {
                        'equity': total_balance,
                        'free_balance': usdt_balance,
                        'total_balance': total_balance
                    }
        except Exception as e:
            LOGGER.error("Error fetching balance: %s", e)
        
        # Don't update balance if API fails - keep existing values
        return None
    
    def send_ui_update(self, update_data: Dict[str, Any]) -> None:
        """Send update to AI dashboard"""
        try:
            # Add balance information to update only if we have valid data
            balance_info = self.fetch_account_balance()
            if balance_info:
                update_data.update(balance_info)
            
            requests.post('http://127.0.0.1:5001/api/update', 
                         json=update_data, 
                         timeout=1)
        except Exception:
            pass
    
    def fetch_enhanced_data(self, symbol: str, timeframe: str = "1m", limit: int = 200):
        """Fetch comprehensive market data"""
        try:
            # Get OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Get ticker for current price and volume
            ticker = self.exchange.fetch_ticker(symbol)
            
            return df, ticker
        except Exception as e:
            LOGGER.error("Error fetching data for %s: %s", symbol, e)
            return pd.DataFrame(), None
    
    def calculate_technical_indicators(self, df: pd.DataFrame):
        """Calculate comprehensive technical indicators"""
        if df.empty or len(df) < 50:
            return df
        
        # Moving Averages
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price momentum
        df['momentum'] = df['close'] / df['close'].shift(10) - 1
        df['price_change'] = df['close'].pct_change()
        
        # Volatility
        df['volatility'] = df['price_change'].rolling(window=20).std()
        
        return df
    
    def detect_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Detect current market regime using multiple indicators"""
        if df.empty or len(df) < 50:
            return MarketRegime.SIDEWAYS
        
        recent = df.tail(20)
        
        # Trend analysis
        sma_20 = recent['sma_20'].iloc[-1]
        sma_50 = recent['sma_50'].iloc[-1] if not pd.isna(recent['sma_50'].iloc[-1]) else sma_20
        current_price = recent['close'].iloc[-1]
        
        # Volatility analysis
        volatility = recent['volatility'].iloc[-1]
        bb_width = recent['bb_width'].iloc[-1]
        
        # Volume analysis
        avg_volume = recent['volume'].mean()
        recent_volume = recent['volume'].iloc[-5:].mean()
        volume_trend = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # Determine regime
        if volatility > 0.05 or bb_width > 0.1:
            return MarketRegime.VOLATILE
        elif current_price > sma_20 > sma_50 and volume_trend > 1.2:
            return MarketRegime.BULL
        elif current_price < sma_20 < sma_50 and volume_trend > 1.2:
            return MarketRegime.BEAR
        else:
            return MarketRegime.SIDEWAYS
    
    def calculate_signal_strength(self, df: pd.DataFrame) -> SignalStrength:
        """Calculate signal strength based on multiple confirmations"""
        if df.empty or len(df) < 20:
            return SignalStrength.WEAK
        
        recent = df.tail(5)
        confirmations = 0
        max_confirmations = 8
        
        # RSI confirmation
        rsi = recent['rsi'].iloc[-1]
        if 30 < rsi < 70:  # Not overbought/oversold
            confirmations += 1
        
        # MACD confirmation
        macd = recent['macd'].iloc[-1]
        macd_signal = recent['macd_signal'].iloc[-1]
        if macd > macd_signal:
            confirmations += 1
        
        # Bollinger Bands confirmation
        bb_pos = recent['bb_position'].iloc[-1]
        if 0.2 < bb_pos < 0.8:  # Not at extremes
            confirmations += 1
        
        # Volume confirmation
        vol_ratio = recent['volume_ratio'].iloc[-1]
        if vol_ratio > 1.1:  # Above average volume
            confirmations += 1
        
        # Trend confirmation
        sma_5 = recent['sma_5'].iloc[-1]
        sma_20 = recent['sma_20'].iloc[-1]
        if sma_5 > sma_20:
            confirmations += 1
        
        # Momentum confirmation
        momentum = recent['momentum'].iloc[-1]
        if abs(momentum) > 0.02:  # Significant momentum
            confirmations += 1
        
        # ATR confirmation (volatility)
        atr = recent['atr'].iloc[-1]
        price = recent['close'].iloc[-1]
        atr_pct = atr / price
        if 0.01 < atr_pct < 0.05:  # Reasonable volatility
            confirmations += 1
        
        # Price action confirmation
        price_change = recent['price_change'].iloc[-1]
        if abs(price_change) > 0.005:  # Significant price movement
            confirmations += 1
        
        # Determine strength
        strength_ratio = confirmations / max_confirmations
        if strength_ratio >= 0.875:
            return SignalStrength.VERY_STRONG
        elif strength_ratio >= 0.75:
            return SignalStrength.STRONG
        elif strength_ratio >= 0.5:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK
    
    def calculate_position_size(self, symbol: str, confidence: float, volatility: float, 
                              current_price: float) -> float:
        """Calculate intelligent position size using Kelly Criterion and volatility adjustment"""
        try:
            # Get current balance
            balance = self.exchange.fetch_balance()
            total_balance = balance['USDT']['total'] if 'USDT' in balance else 0.0
            
            if total_balance <= 0:
                return 0.0
            
            # Base allocation from config
            base_allocation = next(
                (coin['base_allocation'] for coin in self.config['coins'] 
                 if coin['symbol'] == symbol), 0.1
            )
            
            # Kelly Criterion adjustment
            win_rate = 0.6  # Estimated win rate (can be learned from historical data)
            avg_win = 0.03  # Average win percentage
            avg_loss = 0.02  # Average loss percentage
            
            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            
            # Confidence adjustment
            confidence_multiplier = confidence ** 2  # Square to emphasize high confidence
            
            # Volatility adjustment (reduce size in high volatility)
            volatility_adjustment = max(0.5, 1 - (volatility * 2))
            
            # Calculate final position size
            max_position_pct = self.config['ai_parameters']['max_position_size_pct']
            min_position_pct = self.config['ai_parameters']['min_position_size_pct']
            
            position_pct = base_allocation * confidence_multiplier * volatility_adjustment * kelly_fraction
            position_pct = max(min_position_pct, min(position_pct, max_position_pct))
            
            position_size_usd = total_balance * position_pct
            
            LOGGER.info("Position sizing for %s: %.2f%% of balance (%.2f USD) - Confidence: %.2f, Volatility: %.4f", 
                       symbol, position_pct * 100, position_size_usd, confidence, volatility)
            
            return position_size_usd
            
        except Exception as e:
            LOGGER.error("Error calculating position size for %s: %s", symbol, e)
            return 0.0
    
    def calculate_stop_loss_take_profit(self, df: pd.DataFrame, action: str, 
                                      current_price: float) -> Tuple[float, float]:
        """Calculate intelligent stop loss and take profit levels"""
        if df.empty:
            return current_price * 0.98, current_price * 1.02
        
        recent = df.tail(20)
        atr = recent['atr'].iloc[-1]
        
        if action == "BUY":
            # Stop loss: Below recent low or ATR-based
            recent_low = recent['low'].min()
            atr_stop = current_price - (atr * 2)
            stop_loss = max(recent_low * 0.995, atr_stop)  # 0.5% below recent low or 2*ATR
            
            # Take profit: Risk-reward ratio of 1:2 or resistance-based
            risk = current_price - stop_loss
            take_profit = current_price + (risk * 2.5)  # 1:2.5 risk-reward
            
        else:  # SELL
            # Stop loss: Above recent high or ATR-based
            recent_high = recent['high'].max()
            atr_stop = current_price + (atr * 2)
            stop_loss = min(recent_high * 1.005, atr_stop)  # 0.5% above recent high or 2*ATR
            
            # Take profit: Risk-reward ratio of 1:2 or support-based
            risk = stop_loss - current_price
            take_profit = current_price - (risk * 2.5)  # 1:2.5 risk-reward
        
        return stop_loss, take_profit
    
    def analyze_coin_ai(self, symbol: str) -> TradingDecision:
        """AI-powered analysis of a single coin"""
        try:
            # Fetch data
            df, ticker = self.fetch_enhanced_data(symbol)
            if df.empty or ticker is None:
                return None
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            if df.empty:
                return None
            
            # Get current market data
            current_price = ticker['last']
            current_volume = ticker['baseVolume']
            
            # Detect market regime
            market_regime = self.detect_market_regime(df)
            
            # Calculate signal strength
            signal_strength = self.calculate_signal_strength(df)
            
            # Get latest indicators
            recent = df.tail(1).iloc[0]
            
            # AI Decision Making
            confidence = 0.0
            action = "HOLD"
            reasoning_parts = []
            
            # Trend analysis (30% weight)
            sma_5 = recent['sma_5']
            sma_20 = recent['sma_20']
            sma_50 = recent['sma_50']
            
            if not pd.isna(sma_5) and not pd.isna(sma_20):
                if sma_5 > sma_20:
                    confidence += 0.3
                    reasoning_parts.append("Uptrend (SMA5 > SMA20)")
                else:
                    confidence -= 0.2
                    reasoning_parts.append("Downtrend (SMA5 < SMA20)")
            
            # RSI analysis (20% weight)
            rsi = recent['rsi']
            if not pd.isna(rsi):
                if rsi < 30:
                    confidence += 0.2
                    reasoning_parts.append("Oversold (RSI < 30)")
                elif rsi > 70:
                    confidence -= 0.2
                    reasoning_parts.append("Overbought (RSI > 70)")
                else:
                    confidence += 0.1
                    reasoning_parts.append("Neutral RSI")
            
            # MACD analysis (25% weight)
            macd = recent['macd']
            macd_signal = recent['macd_signal']
            if not pd.isna(macd) and not pd.isna(macd_signal):
                if macd > macd_signal:
                    confidence += 0.25
                    reasoning_parts.append("MACD Bullish")
                else:
                    confidence -= 0.15
                    reasoning_parts.append("MACD Bearish")
            
            # Bollinger Bands analysis (25% weight)
            bb_position = recent['bb_position']
            if not pd.isna(bb_position):
                if bb_position < 0.2:
                    confidence += 0.25
                    reasoning_parts.append("Near Lower Bollinger Band")
                elif bb_position > 0.8:
                    confidence -= 0.25
                    reasoning_parts.append("Near Upper Bollinger Band")
                else:
                    confidence += 0.1
                    reasoning_parts.append("Middle Bollinger Band")
            
            # Volume confirmation
            volume_ratio = recent['volume_ratio']
            if not pd.isna(volume_ratio) and volume_ratio > 1.2:
                confidence += 0.1
                reasoning_parts.append("High Volume Confirmation")
            
            # Market regime adjustment
            if market_regime == MarketRegime.BULL:
                confidence += 0.1
                reasoning_parts.append("Bull Market Regime")
            elif market_regime == MarketRegime.BEAR:
                confidence -= 0.1
                reasoning_parts.append("Bear Market Regime")
            elif market_regime == MarketRegime.VOLATILE:
                confidence *= 0.8  # Reduce confidence in volatile markets
                reasoning_parts.append("Volatile Market - Reduced Confidence")
            
            # Determine action
            if confidence > self.config['ai_parameters']['confidence_threshold']:
                action = "BUY"
            elif confidence < -self.config['ai_parameters']['confidence_threshold']:
                action = "SELL"
            else:
                action = "HOLD"
            
            # Calculate position size
            volatility = recent['volatility'] if not pd.isna(recent['volatility']) else 0.02
            position_size = self.calculate_position_size(symbol, abs(confidence), volatility, current_price)
            
            # Calculate stop loss and take profit
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(df, action, current_price)
            
            # Calculate risk-reward ratio
            if action == "BUY":
                risk = current_price - stop_loss
                reward = take_profit - current_price
            else:
                risk = stop_loss - current_price
                reward = current_price - take_profit
            
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            return TradingDecision(
                symbol=symbol,
                action=action,
                confidence=abs(confidence),
                position_size_usd=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning="; ".join(reasoning_parts),
                risk_reward_ratio=risk_reward_ratio,
                market_regime=market_regime,
                signal_strength=signal_strength
            )
            
        except Exception as e:
            LOGGER.error("Error in AI analysis for %s: %s", symbol, e)
            return None
    
    def execute_trade(self, decision: TradingDecision):
        """Execute trade based on AI decision"""
        if decision.action == "HOLD" or decision.position_size_usd <= 0:
            return
        
        try:
            # Get current price
            ticker = self.exchange.fetch_ticker(decision.symbol)
            current_price = ticker['last']
            
            # Calculate quantity based on position size
            quantity = decision.position_size_usd / current_price
            
            # Place order
            if decision.action == "BUY":
                order = self.exchange.create_market_buy_order(
                    decision.symbol, 
                    quantity
                )
                LOGGER.info("✅ BUY ORDER PLACED: %s - Qty: %.6f, Price: $%.2f", 
                           decision.symbol, quantity, current_price)
                
            elif decision.action == "SELL":
                order = self.exchange.create_market_sell_order(
                    decision.symbol, 
                    quantity
                )
                LOGGER.info("✅ SELL ORDER PLACED: %s - Qty: %.6f, Price: $%.2f", 
                           decision.symbol, quantity, current_price)
            
            # Log the decision
            LOGGER.info("🤖 AI DECISION: %s %s - Confidence: %.2f, Size: $%.2f, SL: $%.2f, TP: $%.2f", 
                       decision.action, decision.symbol, decision.confidence, 
                       decision.position_size_usd, decision.stop_loss, decision.take_profit)
            LOGGER.info("🧠 REASONING: %s", decision.reasoning)
            LOGGER.info("📊 RISK/REWARD: %.2f, REGIME: %s, STRENGTH: %s", 
                       decision.risk_reward_ratio, decision.market_regime.value, 
                       decision.signal_strength.name)
            
        except Exception as e:
            LOGGER.error("Error executing trade for %s: %s", decision.symbol, e)
    
    def run_ai_bot(self):
        """Main AI trading loop"""
        self.connect_api()
        
        LOGGER.info("🧠 Starting AI-Powered Trading Bot (190 IQ)")
        LOGGER.info("🤖 Advanced Technical Analysis + Market Sentiment + Intelligent Position Sizing")
        
        # Send initial status
        self.send_ui_update({
            "status": "running",
            "mode": "ai_powered",
            "total_coins": len([c for c in self.config['coins'] if c.get('enabled', True)]),
            "equity": 0.0,
            "daily_pnl": 0.0,
            "confidence_level": 0.0,
            "market_regime": "sideways"
        })
        
        while True:
            try:
                LOGGER.info("🔍 AI Analyzing Market Conditions...")
                
                # Analyze each coin with AI
                current_analysis = []
                active_trades = 0
                total_confidence = 0.0
                
                for coin_config in self.config['coins']:
                    if not coin_config.get('enabled', True):
                        continue
                    
                    symbol = coin_config['symbol']
                    decision = self.analyze_coin_ai(symbol)
                    
                    if decision:
                        # Convert decision to dict for UI
                        decision_dict = {
                            "symbol": decision.symbol,
                            "action": decision.action,
                            "confidence": decision.confidence,
                            "position_size_usd": decision.position_size_usd,
                            "stop_loss": decision.stop_loss,
                            "take_profit": decision.take_profit,
                            "reasoning": decision.reasoning,
                            "risk_reward_ratio": decision.risk_reward_ratio,
                            "market_regime": decision.market_regime.value,
                            "signal_strength": decision.signal_strength.name
                        }
                        
                        current_analysis.append(decision_dict)
                        total_confidence += decision.confidence
                        
                        # Log AI analysis
                        LOGGER.info("📈 %s Analysis: %s (Confidence: %.2f%%)", 
                                   symbol, decision.action, decision.confidence * 100)
                        
                        # Execute if confidence is high enough
                        if decision.confidence > self.config['ai_parameters']['confidence_threshold']:
                            self.execute_trade(decision)
                            active_trades += 1
                
                # Update AI analysis
                self.ai_analysis = current_analysis
                avg_confidence = total_confidence / len(current_analysis) if current_analysis else 0.0
                
                # Send updates to UI
                self.send_ui_update({
                    "ai_analysis": current_analysis,
                    "active_trades": active_trades,
                    "confidence_level": avg_confidence,
                    "market_regime": self.market_regime.value,
                    "last_update": datetime.now().isoformat()
                })
                
                # Wait for next analysis
                time.sleep(60)  # Analyze every minute
                
            except KeyboardInterrupt:
                LOGGER.info("🤖 AI Bot stopped by user")
                self.send_ui_update({"status": "stopped"})
                break
            except Exception as e:
                LOGGER.error("❌ Error in AI bot: %s", e)
                time.sleep(10)

if __name__ == "__main__":
    bot = AITradingBot()
    bot.run_ai_bot()
