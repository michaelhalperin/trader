#!/usr/bin/env python3
"""
Multi-coin trading bot that can trade multiple cryptocurrencies
"""

import os
import json
import time
import logging
import pandas as pd
import ccxt
from datetime import datetime, timezone
from typing import Dict, List, Any
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
LOGGER = logging.getLogger(__name__)

# -------------------------------
# Multi-Coin Configuration
# -------------------------------

def load_multi_coin_config():
    """Load configuration for multiple coins"""
    return {
        "coins": [
            {
                "symbol": "BTC/USDT",
                "max_trade_usd": 50,
                "enabled": True
            },
            {
                "symbol": "ETH/USDT", 
                "max_trade_usd": 30,
                "enabled": True
            },
            {
                "symbol": "SOL/USDT",
                "max_trade_usd": 20,
                "enabled": True
            },
            {
                "symbol": "ADA/USDT",
                "max_trade_usd": 15,
                "enabled": True
            }
        ],
        "strategy": {
            "fast_period": 5,
            "slow_period": 20,
            "timeframe": "1m"
        },
        "risk": {
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.03,
            "daily_loss_limit_pct": 0.05
        },
        "api": {
            "api_key": "S2kUTR5K1FSp1c9ihh",
            "api_secret": "IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU",
            "testnet": True
        }
    }

def connect_api():
    """Connect to Bybit API"""
    config = load_multi_coin_config()
    api_config = config["api"]
    
    exchange = ccxt.bybit({
        "apiKey": api_config["api_key"],
        "secret": api_config["api_secret"],
        "enableRateLimit": True,
        "options": {
            "defaultType": "unified",
        },
    })
    exchange.set_sandbox_mode(api_config["testnet"])
    return exchange

def fetch_data(exchange, symbol: str, timeframe: str = "1m", limit: int = 200):
    """Fetch historical data for a symbol"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        LOGGER.error("Error fetching data for %s: %s", symbol, e)
        return pd.DataFrame()

def calculate_sma(df: pd.DataFrame, fast_period: int = 5, slow_period: int = 20):
    """Calculate SMA indicators"""
    if df.empty or len(df) < slow_period:
        return df
    
    df['sma_fast'] = df['close'].rolling(window=fast_period).mean()
    df['sma_slow'] = df['close'].rolling(window=slow_period).mean()
    
    # Calculate signals
    df['signal'] = 0
    df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1   # BUY
    df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1   # SELL
    
    return df

def send_ui_update(update_data: Dict[str, Any]) -> None:
    """Send update to web UI"""
    try:
        requests.post('http://127.0.0.1:5000/api/update', 
                     json=update_data, 
                     timeout=1)
    except Exception:
        pass

def analyze_coin(exchange, coin_config: Dict, strategy_config: Dict):
    """Analyze a single coin and return trading signal"""
    symbol = coin_config["symbol"]
    
    try:
        # Fetch data
        df = fetch_data(exchange, symbol, strategy_config["timeframe"])
        if df.empty:
            return None
            
        # Calculate SMA
        df = calculate_sma(df, strategy_config["fast_period"], strategy_config["slow_period"])
        if df.empty:
            return None
            
        # Get latest signal
        last_row = df.iloc[-1]
        signal = int(last_row.get("signal", 0))
        sma_fast = last_row.get("sma_fast")
        sma_slow = last_row.get("sma_slow")
        
        return {
            "symbol": symbol,
            "signal": signal,
            "sma_fast": float(sma_fast) if not pd.isna(sma_fast) else None,
            "sma_slow": float(sma_slow) if not pd.isna(sma_slow) else None,
            "price": float(last_row["close"]),
            "enabled": coin_config.get("enabled", True),
            "max_trade_usd": coin_config.get("max_trade_usd", 50)
        }
        
    except Exception as e:
        LOGGER.error("Error analyzing %s: %s", symbol, e)
        return None

def main_loop():
    """Main trading loop for multiple coins"""
    config = load_multi_coin_config()
    exchange = connect_api()
    
    LOGGER.info("Starting Multi-Coin Trading Bot")
    LOGGER.info("Trading %d coins: %s", 
                len([c for c in config["coins"] if c.get("enabled", True)]),
                [c["symbol"] for c in config["coins"] if c.get("enabled", True)])
    
    # Send initial status
    send_ui_update({"status": "running", "mode": "multi_coin"})
    
    while True:
        try:
            LOGGER.info("Analyzing all coins...")
            
            # Analyze each coin
            coin_analysis = []
            for coin_config in config["coins"]:
                if not coin_config.get("enabled", True):
                    continue
                    
                analysis = analyze_coin(exchange, coin_config, config["strategy"])
                if analysis:
                    coin_analysis.append(analysis)
                    
                    # Log signal for each coin
                    if analysis["signal"] != 0:
                        signal_name = "BUY" if analysis["signal"] > 0 else "SELL"
                        LOGGER.info("%s: %s signal (SMA5: $%.2f, SMA20: $%.2f)", 
                                   analysis["symbol"], signal_name,
                                   analysis["sma_fast"] or 0, analysis["sma_slow"] or 0)
            
            # Send analysis to UI
            if coin_analysis:
                send_ui_update({
                    "coin_analysis": coin_analysis,
                    "total_coins": len(coin_analysis),
                    "signals": [a for a in coin_analysis if a["signal"] != 0]
                })
            
            # Wait for next analysis
            time.sleep(60)  # Analyze every minute
            
        except KeyboardInterrupt:
            LOGGER.info("Bot stopped by user")
            send_ui_update({"status": "stopped"})
            break
        except Exception as e:
            LOGGER.error("Error in main loop: %s", e)
            time.sleep(10)

if __name__ == "__main__":
    main_loop()
