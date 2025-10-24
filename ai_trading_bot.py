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
    volatility: float = 0.02  # Default volatility

class AITradingBot:
    def __init__(self):
        self.exchange = None
        self.config = self.load_config()
        self.positions = {}  # Track open positions: {symbol: {quantity, avg_price, entry_time, stop_loss, take_profit}}
        self.daily_pnl = 0.0
        self.start_equity = 0.0
        self.market_regime = MarketRegime.SIDEWAYS
        self.ai_analysis = []
        self.recent_decisions = []
        self.position_history = []  # Track all trades for analysis
        self.daily_start_balance = 0.0  # Track daily starting balance
        self.daily_trades = []  # Track today's trades
        self.performance_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0
        }
        
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
                "confidence_threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.49")),
                "max_position_size_pct": float(os.getenv("MAX_POSITION_SIZE_PCT", "0.15")),  # Max 15% of portfolio per trade
                "min_position_size_pct": float(os.getenv("MIN_POSITION_SIZE_PCT", "0.02")),  # Min 2% of portfolio per trade
                "volatility_adjustment": True,
                "base_profit_target_pct": float(os.getenv("BASE_PROFIT_TARGET_PCT", "0.03")),  # Base 3% profit target
                "base_stop_loss_pct": float(os.getenv("BASE_STOP_LOSS_PCT", "0.02")),  # Base 2% stop loss
                "max_positions_per_coin": int(os.getenv("MAX_POSITIONS_PER_COIN", "2")),  # Max 2 positions per coin
                "max_total_exposure_pct": float(os.getenv("MAX_TOTAL_EXPOSURE_PCT", "0.8")),  # Max 80% of account in positions
                "max_daily_loss_pct": float(os.getenv("MAX_DAILY_LOSS_PCT", "0.05")),  # Max 5% daily loss
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
            "options": {
                "defaultType": "unified",
                "recvWindow": 10000,  # Increase receive window
                "timeDifference": 0,  # Let ccxt handle timestamp sync
            },
        })
        self.exchange.set_sandbox_mode(True)  # Testnet mode
        
        # Test connection with a simple call
        try:
            balance = self.exchange.fetch_balance()
            LOGGER.info("✅ Connected to Bybit API (Testnet) - Balance: $%.2f", 
                       balance.get('total', {}).get('USDT', 0))
        except Exception as e:
            LOGGER.error("❌ API connection test failed: %s", e)
            raise e
        
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
            
            # Add position information and performance stats
            update_data.update({
                'active_trades': len(self.positions),
                'positions': self.positions,
                'daily_pnl': self.daily_pnl,
                'position_history': self.position_history[-10:],  # Last 10 trades
                'performance_stats': self.performance_stats,
                'total_exposure_pct': self.calculate_total_exposure() * 100,
                'daily_loss_pct': self.calculate_daily_loss_pct()
            })
            
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
                signal_strength=signal_strength,
                volatility=volatility
            )
            
        except Exception as e:
            LOGGER.error("Error in AI analysis for %s: %s", symbol, e)
            return None
    
    def calculate_dynamic_targets(self, symbol: str, confidence: float, volatility: float, 
                                 market_regime: MarketRegime, risk_reward_ratio: float) -> Tuple[float, float]:
        """Calculate dynamic profit target and stop-loss based on trade characteristics"""
        
        # Base targets
        base_profit = self.config['ai_parameters']['base_profit_target_pct']
        base_stop = self.config['ai_parameters']['base_stop_loss_pct']
        
        # Confidence multiplier (higher confidence = higher targets)
        confidence_multiplier = 0.5 + (confidence * 1.5)  # 0.5 to 2.0 range
        
        # Volatility adjustment (higher volatility = wider targets)
        volatility_multiplier = 0.8 + (volatility * 2.0)  # 0.8 to 2.8 range
        
        # Market regime adjustment
        regime_multiplier = {
            MarketRegime.BULL: 1.3,      # Higher targets in bull market
            MarketRegime.BEAR: 0.7,      # Lower targets in bear market
            MarketRegime.SIDEWAYS: 1.0,  # Normal targets in sideways
            MarketRegime.VOLATILE: 1.2   # Slightly higher in volatile
        }.get(market_regime, 1.0)
        
        # Risk/reward ratio adjustment (better ratios = higher targets)
        risk_reward_multiplier = min(1.5, max(0.5, risk_reward_ratio / 2.0))
        
        # Calculate dynamic targets
        profit_target = base_profit * confidence_multiplier * volatility_multiplier * regime_multiplier * risk_reward_multiplier
        stop_loss = base_stop * confidence_multiplier * volatility_multiplier * regime_multiplier
        
        # Apply reasonable limits
        profit_target = min(0.15, max(0.02, profit_target))  # 2% to 15% range
        stop_loss = min(0.08, max(0.01, stop_loss))          # 1% to 8% range
        
        # Ensure profit target is higher than stop loss
        if profit_target <= stop_loss:
            profit_target = stop_loss * 1.5
        
        return profit_target, stop_loss
    
    def check_profit_taking(self, symbol: str, current_price: float) -> bool:
        """Check if we should take profit on existing positions using dynamic targets"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        entry_price = position['avg_price']
        profit_pct = (current_price - entry_price) / entry_price
        
        # Use the position's specific profit target (stored when position was created)
        profit_target = position.get('profit_target_pct', self.config['ai_parameters']['base_profit_target_pct'])
        
        # Take profit if we've reached our dynamic target
        if profit_pct >= profit_target:
            LOGGER.info("💰 DYNAMIC PROFIT TARGET REACHED: %s - %.2f%% profit (Target: %.2f%%, Entry: $%.2f, Current: $%.2f)", 
                       symbol, profit_pct * 100, profit_target * 100, entry_price, current_price)
            return True
        
        return False
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """Check if we should stop loss on existing positions using dynamic targets"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        entry_price = position['avg_price']
        loss_pct = (entry_price - current_price) / entry_price
        
        # Use the position's specific stop loss (stored when position was created)
        stop_loss = position.get('stop_loss_pct', self.config['ai_parameters']['base_stop_loss_pct'])
        
        # Stop loss if we've hit our dynamic limit
        if loss_pct >= stop_loss:
            LOGGER.info("🛑 DYNAMIC STOP LOSS TRIGGERED: %s - %.2f%% loss (Stop: %.2f%%, Entry: $%.2f, Current: $%.2f)", 
                       symbol, loss_pct * 100, stop_loss * 100, entry_price, current_price)
            return True
        
        return False
    
    def calculate_total_exposure(self) -> float:
        """Calculate total exposure as percentage of account"""
        try:
            if not self.positions:
                return 0.0
            
            total_exposure = 0.0
            for position in self.positions.values():
                if 'quantity' in position and 'avg_price' in position:
                    position_value = position['quantity'] * position['avg_price']
                    total_exposure += position_value
            
            # Get current account balance
            balance_info = self.fetch_account_balance()
            if balance_info and balance_info.get('equity', 0) > 0:
                return total_exposure / balance_info['equity']
            return 0.0
        except Exception as e:
            LOGGER.error("Error calculating total exposure: %s", e)
            return 0.0  # Return 0 if there's an error
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been exceeded"""
        if self.daily_start_balance <= 0:
            return False
        
        current_balance = self.fetch_account_balance()
        if not current_balance or current_balance.get('equity', 0) <= 0:
            return False
        
        daily_loss_pct = (self.daily_start_balance - current_balance['equity']) / self.daily_start_balance
        max_daily_loss = self.config['ai_parameters']['max_daily_loss_pct']
        
        if daily_loss_pct >= max_daily_loss:
            LOGGER.warning("🛑 DAILY LOSS LIMIT EXCEEDED: %.2f%% loss (Limit: %.2f%%) - Stopping trading", 
                          daily_loss_pct * 100, max_daily_loss * 100)
            return True
        
        return False
    
    def can_open_new_position(self, symbol: str) -> bool:
        """Check if we can open a new position for this symbol with portfolio risk management"""
        try:
            # Check if exchange is connected
            if not self.exchange:
                LOGGER.warning("⚠️ No exchange connection - Cannot open new position")
                return False
            
            # Check daily loss limit first
            if self.check_daily_loss_limit():
                return False
            
            # Count existing positions for this symbol
            position_count = sum(1 for pos_symbol in self.positions.keys() if pos_symbol == symbol)
            max_positions = self.config['ai_parameters']['max_positions_per_coin']
            
            if position_count >= max_positions:
                return False
            
            # Check total exposure limit
            current_exposure = self.calculate_total_exposure()
            max_exposure = self.config['ai_parameters']['max_total_exposure_pct']
            
            if current_exposure >= max_exposure:
                LOGGER.info("⏸️ MAX EXPOSURE REACHED: %.2f%% (Limit: %.2f%%) - Cannot open new position", 
                           current_exposure * 100, max_exposure * 100)
                return False
            
            return True
        except Exception as e:
            LOGGER.error("Error checking if can open new position: %s", e)
            return False  # Fail safe - don't open new positions if there's an error
    
    def calculate_daily_loss_pct(self) -> float:
        """Calculate daily loss percentage"""
        if self.daily_start_balance <= 0:
            return 0.0
        
        current_balance = self.fetch_account_balance()
        if not current_balance or current_balance.get('equity', 0) <= 0:
            return 0.0
        
        daily_loss_pct = (self.daily_start_balance - current_balance['equity']) / self.daily_start_balance
        return max(0.0, daily_loss_pct)  # Return 0 if gain
    
    def initialize_daily_tracking(self):
        """Initialize daily tracking at start of trading day"""
        balance_info = self.fetch_account_balance()
        if balance_info and balance_info.get('equity', 0) > 0:
            self.daily_start_balance = balance_info['equity']
            self.daily_pnl = 0.0
            self.daily_trades = []
            LOGGER.info("📊 DAILY TRACKING INITIALIZED: Starting balance: $%.2f", self.daily_start_balance)
    
    def close_position(self, symbol: str, reason: str = "Manual"):
        """Close an existing position"""
        if symbol not in self.positions:
            return False
        
        try:
            position = self.positions[symbol]
            quantity = position['quantity']
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Place sell order
            order = self.exchange.create_market_sell_order(symbol, quantity)
            
            # Calculate P&L
            entry_price = position['avg_price']
            pnl = (current_price - entry_price) * quantity
            pnl_pct = (current_price - entry_price) / entry_price * 100
            
            # Log the trade
            LOGGER.info("✅ POSITION CLOSED: %s - %s - Qty: %.6f, Entry: $%.2f, Exit: $%.2f, P&L: $%.2f (%.2f%%)", 
                       symbol, reason, quantity, entry_price, current_price, pnl, pnl_pct)
            
            # Record in history
            self.position_history.append({
                'symbol': symbol,
                'action': 'SELL',
                'quantity': quantity,
                'entry_price': entry_price,
                'exit_price': current_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'reason': reason,
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Update daily P&L and performance stats
            self.daily_pnl += pnl
            self.update_performance_stats(pnl, pnl_pct)
            
            # Remove from positions
            del self.positions[symbol]
            
            return True
            
        except Exception as e:
            LOGGER.error("Error closing position for %s: %s", symbol, e)
            return False
    
    def update_position(self, symbol: str, quantity: float, price: float, 
                       profit_target_pct: float, stop_loss_pct: float):
        """Update or create position tracking with dynamic targets"""
        if symbol in self.positions:
            # Update existing position (average price)
            existing = self.positions[symbol]
            total_quantity = existing['quantity'] + quantity
            total_value = (existing['quantity'] * existing['avg_price']) + (quantity * price)
            new_avg_price = total_value / total_quantity
            
            # Update targets (use weighted average or keep original if better)
            existing_profit_target = existing.get('profit_target_pct', profit_target_pct)
            existing_stop_loss = existing.get('stop_loss_pct', stop_loss_pct)
            
            self.positions[symbol] = {
                'quantity': total_quantity,
                'avg_price': new_avg_price,
                'entry_time': existing['entry_time'],  # Keep original entry time
                'profit_target_pct': max(existing_profit_target, profit_target_pct),  # Use higher profit target
                'stop_loss_pct': min(existing_stop_loss, stop_loss_pct),  # Use tighter stop loss
                'stop_loss': price * (1 - stop_loss_pct),  # Keep for compatibility
                'take_profit': price * (1 + profit_target_pct)  # Keep for compatibility
            }
        else:
            # Create new position with dynamic targets
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': price,
                'entry_time': datetime.now(timezone.utc),
                'profit_target_pct': profit_target_pct,
                'stop_loss_pct': stop_loss_pct,
                'stop_loss': price * (1 - stop_loss_pct),  # Keep for compatibility
                'take_profit': price * (1 + profit_target_pct),  # Keep for compatibility
                'trailing_stop_active': False,
                'trailing_stop_distance': stop_loss_pct,
                'highest_price': price
            }
    
    def check_all_positions(self):
        """Check all existing positions for profit-taking and stop-loss"""
        if not self.positions:
            return
        
        positions_to_close = []
        
        for symbol, position in self.positions.items():
            try:
                # Get current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Check profit-taking
                if self.check_profit_taking(symbol, current_price):
                    positions_to_close.append((symbol, "Profit Target"))
                    continue
                
                # Check stop-loss
                if self.check_stop_loss(symbol, current_price):
                    positions_to_close.append((symbol, "Stop Loss"))
                    continue
                
                # Update trailing stop
                self.update_trailing_stop(symbol, current_price)
                
                # Log position status
                entry_price = position['avg_price']
                profit_pct = (current_price - entry_price) / entry_price * 100
                trailing_status = " (Trailing)" if position.get('trailing_stop_active', False) else ""
                LOGGER.info("📊 POSITION STATUS: %s - Entry: $%.2f, Current: $%.2f, P&L: %.2f%%%s", 
                           symbol, entry_price, current_price, profit_pct, trailing_status)
                
            except Exception as e:
                LOGGER.error("Error checking position %s: %s", symbol, e)
        
        # Close positions that need to be closed
        for symbol, reason in positions_to_close:
            self.close_position(symbol, reason)
    
    def update_trailing_stop(self, symbol: str, current_price: float):
        """Update trailing stop for a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        entry_price = position['avg_price']
        profit_pct = (current_price - entry_price) / entry_price
        
        # Activate trailing stop when position is profitable
        if profit_pct > 0.02:  # 2% profit threshold to activate trailing
            if not position.get('trailing_stop_active', False):
                position['trailing_stop_active'] = True
                LOGGER.info("🎯 TRAILING STOP ACTIVATED: %s - Price: $%.2f, Profit: %.2f%%", 
                           symbol, current_price, profit_pct * 100)
            
            # Update highest price
            if current_price > position.get('highest_price', entry_price):
                position['highest_price'] = current_price
                
                # Update trailing stop distance
                trailing_distance = position.get('trailing_stop_distance', 0.02)
                new_stop_price = current_price * (1 - trailing_distance)
                
                # Only move stop loss up, never down
                if new_stop_price > position.get('stop_loss', entry_price * 0.98):
                    position['stop_loss'] = new_stop_price
                    position['stop_loss_pct'] = trailing_distance
                    LOGGER.info("📈 TRAILING STOP UPDATED: %s - New Stop: $%.2f (Distance: %.2f%%)", 
                               symbol, new_stop_price, trailing_distance * 100)
    
    def update_performance_stats(self, pnl: float, pnl_pct: float):
        """Update performance statistics"""
        self.performance_stats['total_trades'] += 1
        self.performance_stats['total_pnl'] += pnl
        
        if pnl > 0:
            self.performance_stats['winning_trades'] += 1
        else:
            self.performance_stats['losing_trades'] += 1
        
        # Calculate win rate
        if self.performance_stats['total_trades'] > 0:
            self.performance_stats['win_rate'] = (
                self.performance_stats['winning_trades'] / self.performance_stats['total_trades']
            )
        
        # Update max drawdown
        if pnl < 0:
            current_drawdown = abs(pnl_pct)
            if current_drawdown > self.performance_stats['max_drawdown']:
                self.performance_stats['max_drawdown'] = current_drawdown
    
    def log_performance_summary(self):
        """Log performance summary"""
        stats = self.performance_stats
        exposure_pct = self.calculate_total_exposure() * 100
        daily_loss_pct = self.calculate_daily_loss_pct() * 100
        
        LOGGER.info("📊 PERFORMANCE SUMMARY:")
        LOGGER.info("   💰 Total Trades: %d | Win Rate: %.1f%% | Total P&L: $%.2f", 
                   stats['total_trades'], stats['win_rate'] * 100, stats['total_pnl'])
        LOGGER.info("   📈 Portfolio Exposure: %.1f%% | Daily Loss: %.1f%% | Max Drawdown: %.1f%%", 
                   exposure_pct, daily_loss_pct, stats['max_drawdown'])
        LOGGER.info("   🎯 Active Positions: %d | Daily P&L: $%.2f", 
                   len(self.positions), self.daily_pnl)
    
    def execute_trade(self, decision: TradingDecision):
        """Execute trade based on AI decision with profit-taking logic"""
        if decision.action == "HOLD" or decision.position_size_usd <= 0:
            return
        
        try:
            # Get current price
            ticker = self.exchange.fetch_ticker(decision.symbol)
            current_price = ticker['last']
            
            # Check existing positions for profit-taking or stop-loss
            if decision.symbol in self.positions:
                if self.check_profit_taking(decision.symbol, current_price):
                    self.close_position(decision.symbol, "Profit Target")
                    return
                elif self.check_stop_loss(decision.symbol, current_price):
                    self.close_position(decision.symbol, "Stop Loss")
                    return
            
            # For BUY orders, check if we can open new position
            if decision.action == "BUY":
                if not self.can_open_new_position(decision.symbol):
                    LOGGER.info("⏸️ MAX POSITIONS REACHED: %s - Skipping new BUY order", decision.symbol)
                    return
                
                # Calculate quantity based on position size
                quantity = decision.position_size_usd / current_price
                
                # Place buy order
                order = self.exchange.create_market_buy_order(
                    decision.symbol, 
                    quantity
                )
                LOGGER.info("✅ BUY ORDER PLACED: %s - Qty: %.6f, Price: $%.2f", 
                           decision.symbol, quantity, current_price)
                
                # Calculate dynamic targets for this specific trade
                profit_target_pct, stop_loss_pct = self.calculate_dynamic_targets(
                    decision.symbol, 
                    decision.confidence, 
                    decision.volatility,
                    decision.market_regime,
                    decision.risk_reward_ratio
                )
                
                # Update position tracking with dynamic targets
                self.update_position(decision.symbol, quantity, current_price, 
                                   profit_target_pct, stop_loss_pct)
                
                LOGGER.info("🎯 DYNAMIC TARGETS SET: %s - Profit: %.2f%%, Stop: %.2f%% (Confidence: %.2f, Volatility: %.4f)", 
                           decision.symbol, profit_target_pct * 100, stop_loss_pct * 100, 
                           decision.confidence, decision.volatility)
                
                # Record in history
                self.position_history.append({
                    'symbol': decision.symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'entry_price': current_price,
                    'exit_price': None,
                    'pnl': 0,
                    'pnl_pct': 0,
                    'reason': 'AI Decision',
                    'timestamp': datetime.now(timezone.utc)
                })
                
            elif decision.action == "SELL":
                # Only sell if we have a position
                if decision.symbol in self.positions:
                    self.close_position(decision.symbol, "AI Sell Signal")
                else:
                    LOGGER.info("⏸️ NO POSITION TO SELL: %s - Skipping SELL order", decision.symbol)
            
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
        
        # Initialize daily tracking
        self.initialize_daily_tracking()
        
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
                
                # First, check existing positions for profit-taking and stop-loss
                self.check_all_positions()
                
                # Log performance stats every 10 minutes
                if len(self.position_history) > 0 and len(self.position_history) % 10 == 0:
                    self.log_performance_summary()
                
                # Analyze each coin with AI
                current_analysis = []
                active_trades = len(self.positions)
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
