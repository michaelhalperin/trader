#!/usr/bin/env python3
"""
Bybit Testnet Unified Trading SMA Crossover Bot (BTC/USDT)

Features:
- Connects to Bybit testnet using REST (ccxt) and WebSocket (public v3)
- Fetches 1m OHLCV data and computes SMA(5) and SMA(20)
- Generates BUY when SMA5 crosses above SMA20; SELL when SMA5 crosses below SMA20
- Risk controls: max trade size (USD), SL/TP %, daily loss kill-switch
- Market execution with retries and logging to CSV
- Continuous loop running every minute; virtual SL/TP monitored with live prices
- Graceful shutdown (closes WS and stops loop)

Important notes:
- This script targets Bybit UNIFIED testnet (derivatives/perpetuals).
- True shorting is now available on unified trading.
- BTC/USDT will trade as BTCUSDT perpetual contract.
- Unified trading allows both long and short positions with proper margin.
"""

"""
api_key = S2kUTR5K1FSp1c9ihh
api_secret = IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU
"""

import os
import json
import time
import math
import hmac
import hashlib
import signal
import threading
import logging
import csv
import requests
from datetime import datetime, timezone, date
from typing import Dict, Any, Optional, Tuple

import pandas as pd
from ta.trend import SMAIndicator
import ccxt
from websocket import WebSocketApp


# -------------------------------
# Web UI Integration
# -------------------------------

def send_ui_update(update_data: Dict[str, Any]) -> None:
    """Send update to web UI"""
    try:
        requests.post('http://127.0.0.1:5000/api/update', 
                     json=update_data, 
                     timeout=1)
    except Exception:
        # UI not running, ignore
        pass

# -------------------------------
# Logging setup
# -------------------------------

LOGGER = logging.getLogger("bybit_bot")
LOGGER.setLevel(logging.INFO)

_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.INFO)
_console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_console_handler.setFormatter(_console_formatter)
LOGGER.addHandler(_console_handler)


# -------------------------------
# Configuration helpers
# -------------------------------

DEFAULT_CONFIG = {
    "symbol": "BTC/USDT",
    "exchange": "bybit",
    "timeframe": "1m",
    "fast_period": 5,
    "slow_period": 20,
    "trade_size_pct": 0.05,
    "max_trade_usd": 100.0,
    "min_trade_usd": 10.0,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.03,
    "daily_loss_limit_pct": 0.05,
    "testnet": True,
    "allow_short": True  # unified trading allows shorting
}


def load_config(config_path: str) -> Dict[str, Any]:
    """Load JSON config or fall back to defaults if missing."""
    if not os.path.exists(config_path):
        LOGGER.warning("Config file not found at %s. Using defaults.", config_path)
        return DEFAULT_CONFIG.copy()
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Merge defaults with provided config
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg


# -------------------------------
# WebSocket client (Bybit Spot Public v3)
# -------------------------------

class BybitSpotPublicWS:
    """Minimal WebSocket client to track latest ticker price for a symbol.

    Subscribes to `tickers.<SYMBOL>` on testnet.
    """

    def __init__(self, symbol: str, url: str = "wss://stream-testnet.bybit.com/v5/public/spot") -> None:
        self.symbol = symbol.replace("/", "")  # e.g., BTC/USDT -> BTCUSDT
        self.url = url
        self.ws: Optional[WebSocketApp] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.last_price_lock = threading.Lock()
        self._last_price: Optional[float] = None

    @property
    def last_price(self) -> Optional[float]:
        with self.last_price_lock:
            return self._last_price

    def _on_message(self, _, message: str) -> None:
        try:
            data = json.loads(message)
        except Exception:
            return
        # Ticker payload example (public v3): {"topic":"tickers","type":"snapshot","ts":...,"data":[{"symbol":"BTCUSDT","lastPrice":"..."}]} or incremental
        try:
            if isinstance(data, dict):
                if data.get("topic") == "tickers" and "data" in data:
                    entries = data.get("data")
                    if isinstance(entries, list):
                        for item in entries:
                            if item.get("symbol") == self.symbol:
                                price_str = item.get("lastPrice") or item.get("lp")
                                if price_str is not None:
                                    with self.last_price_lock:
                                        self._last_price = float(price_str)
        except Exception:
            # Ignore malformed updates
            pass

    def _on_open(self, ws: WebSocketApp) -> None:
        sub = {"op": "subscribe", "args": [f"tickers.{self.symbol}"]}
        ws.send(json.dumps(sub))

    def _on_error(self, _, error: Exception) -> None:
        LOGGER.error("WebSocket error: %s", error)

    def _on_close(self, *_args) -> None:
        LOGGER.info("WebSocket closed")

    def start(self) -> None:
        def _run():
            self.ws = WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            # Run forever until stop_event set
            while not self.stop_event.is_set():
                try:
                    self.ws.run_forever(ping_interval=20, ping_timeout=10)
                except Exception as e:
                    LOGGER.error("WS run_forever exception: %s", e)
                    time.sleep(3)
                # Reconnect loop
                if not self.stop_event.is_set():
                    time.sleep(1)

        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        try:
            if self.ws is not None:
                self.ws.close()
        except Exception:
            pass
        if self.thread is not None:
            self.thread.join(timeout=5)


# -------------------------------
# API connection (ccxt)
# -------------------------------

def connect_api(config: Dict[str, Any]) -> ccxt.Exchange:
    """Create and return a CCXT Bybit exchange client configured for testnet spot.

    Uses hardcoded API keys for testnet.
    """
    api_key = "S2kUTR5K1FSp1c9ihh"
    api_secret = "IqCEE9xKQ2hY1mVrz4rZToGaxrUynkSt4hWU"

    exchange = ccxt.bybit({
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
        "options": {
            "defaultType": "unified",  # Use Unified Trading (derivatives)
        },
    })

    # Use sandbox/testnet endpoints
    if hasattr(exchange, "set_sandbox_mode"):
        exchange.set_sandbox_mode(config.get("testnet", True))

    exchange.load_markets()
    return exchange


# -------------------------------
# Market data
# -------------------------------

def fetch_data(exchange: ccxt.Exchange, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
    """Fetch historical OHLCV and return a pandas DataFrame with close prices.

    Columns: [timestamp, open, high, low, close, volume, datetime]
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("UTC")
    return df


# -------------------------------
# Strategy
# -------------------------------

def calculate_sma(df: pd.DataFrame, fast_period: int, slow_period: int) -> pd.DataFrame:
    """Add SMA columns and crossover signal to the DataFrame.

    Adds columns: sma_fast, sma_slow, signal
    signal: 1 for bullish cross (fast>slow and previous fast<=slow),
            -1 for bearish cross (fast<slow and previous fast>=slow),
            0 otherwise.
    """
    if len(df) < max(fast_period, slow_period) + 2:
        # Not enough data
        df = df.copy()
        df["sma_fast"] = float("nan")
        df["sma_slow"] = float("nan")
        df["signal"] = 0
        return df

    df = df.copy()
    df["sma_fast"] = SMAIndicator(close=df["close"], window=fast_period).sma_indicator()
    df["sma_slow"] = SMAIndicator(close=df["close"], window=slow_period).sma_indicator()

    # Compute crossovers
    df["fast_gt_slow"] = df["sma_fast"] > df["sma_slow"]
    df["fast_lt_slow"] = df["sma_fast"] < df["sma_slow"]
    df["fast_gt_slow_prev"] = df["fast_gt_slow"].shift(1)
    df["fast_lt_slow_prev"] = df["fast_lt_slow"].shift(1)

    signals = []
    for i in range(len(df)):
        if i == 0 or pd.isna(df.loc[i, "fast_gt_slow_prev"]) or pd.isna(df.loc[i, "fast_lt_slow_prev"]):
            signals.append(0)
            continue
        bullish = bool(df.loc[i, "fast_gt_slow"]) and not bool(df.loc[i, "fast_gt_slow_prev"])  # crossed up
        bearish = bool(df.loc[i, "fast_lt_slow"]) and not bool(df.loc[i, "fast_lt_slow_prev"])  # crossed down
        if bullish:
            signals.append(1)
        elif bearish:
            signals.append(-1)
        else:
            signals.append(0)
    df["signal"] = signals
    return df


# -------------------------------
# Risk management and sizing
# -------------------------------

class BotState:
    """Holds mutable runtime state across iterations."""

    def __init__(self) -> None:
        self.current_position: str = "flat"  # "long" | "short" | "flat"
        self.position_size_base: float = 0.0  # BTC amount held when long
        self.entry_price: Optional[float] = None
        self.stop_loss: Optional[float] = None
        self.take_profit: Optional[float] = None
        self.last_signal: int = 0  # to avoid duplicates
        self.daily_start_equity_usdt: Optional[float] = None
        self.daily_date: Optional[date] = None
        self.kill_switched: bool = False


def _get_equity_usdt(exchange: ccxt.Exchange, symbol: str, last_price: Optional[float]) -> float:
    """Compute spot equity in USDT terms: free+used balances in base and quote valued at last price."""
    balances = exchange.fetch_balance()
    market = exchange.market(symbol)
    base_ccy = market["base"]
    quote_ccy = market["quote"]
    base_total = balances.get(base_ccy, {}).get("total", 0.0) or 0.0
    quote_total = balances.get(quote_ccy, {}).get("total", 0.0) or 0.0
    px = float(last_price) if last_price is not None else None
    if px is None or px <= 0:
        # Fallback to ticker if needed
        ticker = exchange.fetch_ticker(symbol)
        px = float(ticker.get("last") or ticker.get("close") or ticker["info"].get("lastPrice") or 0.0)
    return float(quote_total + base_total * px)


def _floor_to_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return math.floor(value / step) * step


def check_risk(exchange: ccxt.Exchange, state: BotState, config: Dict[str, Any], last_price: Optional[float]) -> Tuple[bool, float]:
    """Check balances and daily kill-switch. Return (ok_to_trade, size_in_base).

    Sizing: quote_size_usd -> base_qty using last price; floored to lot step.
    """
    if state.kill_switched:
        return False, 0.0

    symbol = config["symbol"]
    market = exchange.market(symbol)
    price = float(last_price) if last_price is not None else None
    if price is None or price <= 0:
        ticker = exchange.fetch_ticker(symbol)
        price = float(ticker.get("last") or ticker.get("close") or ticker["info"].get("lastPrice") or 0.0)
    if price <= 0:
        LOGGER.warning("No valid price; skipping trade")
        return False, 0.0

    # Daily equity and kill-switch
    today = datetime.now(timezone.utc).date()
    equity = _get_equity_usdt(exchange, symbol, price)
    if state.daily_start_equity_usdt is None or state.daily_date != today:
        state.daily_start_equity_usdt = equity
        state.daily_date = today
        LOGGER.info("Daily start equity set to %.2f USDT", equity)
        # Send UI update
        send_ui_update({"equity": equity, "status": "running"})
    else:
        pnl_pct = (equity - state.daily_start_equity_usdt) / max(1e-9, state.daily_start_equity_usdt)
        if pnl_pct <= -abs(config["daily_loss_limit_pct"]):
            LOGGER.error("Kill-switch activated: daily loss %.2f%% <= limit %.2f%%", pnl_pct * 100, config["daily_loss_limit_pct"] * 100)
            state.kill_switched = True
            send_ui_update({"status": "stopped"})
            return False, 0.0

    # Balance check and dynamic sizing
    balances = exchange.fetch_balance()
    quote_ccy = market["quote"]
    free_quote = float(balances.get(quote_ccy, {}).get("free", 0.0) or 0.0)
    total_quote = float(balances.get(quote_ccy, {}).get("total", 0.0) or 0.0)

    # Dynamic trade sizing based on account balance
    trade_size_pct = float(config.get("trade_size_pct", 0.05))  # 5% of account by default
    max_trade_usd = float(config.get("max_trade_usd", 100))  # Maximum trade size
    min_trade_usd = float(config.get("min_trade_usd", 10))   # Minimum trade size
    
    # Calculate trade size as percentage of total balance
    calculated_trade_size = total_quote * trade_size_pct
    
    # Apply min/max limits
    usd_to_use = max(min_trade_usd, min(calculated_trade_size, max_trade_usd, free_quote))
    
    if usd_to_use < min_trade_usd:
        LOGGER.warning("Insufficient balance for minimum trade size: %.2f %s (need %.2f)", 
                      free_quote, quote_ccy, min_trade_usd)
        return False, 0.0

    LOGGER.info("Dynamic trade sizing: %.2f%% of %.2f %s = %.2f %s (capped at %.2f)", 
               trade_size_pct * 100, total_quote, quote_ccy, usd_to_use, quote_ccy, max_trade_usd)

    base_qty = usd_to_use / price
    # Apply lot size/precision
    lot_step = market.get("limits", {}).get("amount", {}).get("min", 0.0) or market.get("precision", {}).get("amount")
    if lot_step is None:
        lot_step = 1e-6
    base_qty = _floor_to_step(base_qty, lot_step)
    base_qty = float(f"{base_qty:.8f}")
    if base_qty <= 0:
        return False, 0.0
    return True, base_qty


# -------------------------------
# Execution
# -------------------------------

def place_order(exchange: ccxt.Exchange, symbol: str, side: str, quantity_base: float, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Place a spot market order with limited retries. Returns order dict or None."""
    assert side in ("buy", "sell")
    for attempt in range(1, max_retries + 1):
        try:
            order = exchange.create_order(symbol=symbol, type="market", side=side, amount=quantity_base)
            # Normalize basic fields
            order_id = order.get("id")
            filled = float(order.get("filled") or 0)
            avgpx = order.get("average") or order.get("price")
            avgpx = float(avgpx) if avgpx is not None else None
            ts = order.get("timestamp") or int(time.time() * 1000)
            return {
                "id": order_id,
                "filled": filled,
                "avg_price": avgpx,
                "timestamp": ts,
                "raw": order,
            }
        except Exception as e:
            LOGGER.error("Order attempt %d failed: %s", attempt, e)
            time.sleep(1 + attempt)
    return None


# -------------------------------
# Logging persistence
# -------------------------------

TRADES_CSV = "trades.csv"


def _ensure_trades_csv_header(path: str) -> None:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "symbol",
                "signal",
                "side",
                "executed_price",
                "executed_size",
                "stop_loss",
                "take_profit",
                "order_id",
                "pnl_usdt",
            ])


def log_trade(row: Dict[str, Any], path: str = TRADES_CSV) -> None:
    _ensure_trades_csv_header(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            row.get("timestamp"),
            row.get("symbol"),
            row.get("signal"),
            row.get("side"),
            row.get("executed_price"),
            row.get("executed_size"),
            row.get("stop_loss"),
            row.get("take_profit"),
            row.get("order_id"),
            row.get("pnl_usdt"),
        ])


# -------------------------------
# Main loop and orchestration
# -------------------------------

RUNNING = True


def _signal_handler(signum, _frame):
    global RUNNING
    LOGGER.info("Received signal %s; shutting down...", signum)
    RUNNING = False


def _compute_sl_tp(entry_price: float, side: str, sl_pct: float, tp_pct: float) -> Tuple[float, float]:
    if side == "buy":
        return entry_price * (1 - sl_pct), entry_price * (1 + tp_pct)
    else:
        return entry_price * (1 + sl_pct), entry_price * (1 - tp_pct)


def main_loop() -> None:
    """Run the bot loop: data fetch, signals, risk, execution, SL/TP monitoring."""
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = load_config(config_path)
    LOGGER.info("Config loaded: %s", config)

    # Connect REST API
    LOGGER.info("Connecting to Bybit API...")
    try:
        exchange = connect_api(config)
        LOGGER.info("API connection successful")
        # Send initial status to UI
        send_ui_update({"status": "running"})
    except Exception as e:
        LOGGER.error("API connection failed: %s", e)
        send_ui_update({"status": "stopped"})
        return
    
    symbol = config["symbol"]
    timeframe = config["timeframe"]
    LOGGER.info("Trading %s on %s timeframe", symbol, timeframe)

    # Start WebSocket for live ticker price (disabled for now)
    ws = None  # BybitSpotPublicWS(symbol)
    # ws.start()

    # Prepare state
    state = BotState()

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    last_minute_checked: Optional[int] = None

    try:
        LOGGER.info("Starting main loop...")
        while RUNNING:
            now = datetime.now(timezone.utc)
            current_minute = int(now.timestamp() // 60)

            # Every minute: fetch latest candles and evaluate strategy
            if last_minute_checked is None or current_minute > last_minute_checked:
                last_minute_checked = current_minute
                LOGGER.info("Fetching data for minute %d", current_minute)
                try:
                    df = fetch_data(exchange, symbol, timeframe, limit=max(200, DEFAULT_CONFIG["slow_period"] * 4))
                    LOGGER.info("Fetched %d candles", len(df))
                    df = calculate_sma(df, config["fast_period"], config["slow_period"])
                    LOGGER.info("SMA calculated")
                except Exception as e:
                    LOGGER.error("Data/strategy error: %s", e)
                    time.sleep(2)
                    continue

                if df.empty:
                    time.sleep(5)
                    continue

                last_row = df.iloc[-1]
                signal_val: int = int(last_row["signal"] or 0)
                
                # Send SMA values to UI
                sma_fast = last_row.get("sma_fast")
                sma_slow = last_row.get("sma_slow")
                if not pd.isna(sma_fast) and not pd.isna(sma_slow):
                    send_ui_update({
                        "sma_fast": float(sma_fast),
                        "sma_slow": float(sma_slow)
                    })

                # Avoid duplicate action on same signal
                if signal_val != 0 and signal_val != state.last_signal:
                    side = "buy" if signal_val > 0 else "sell"

                    # For unified trading: shorting is allowed, no need to check base balance
                    # Unified trading allows both long and short positions
                    
                    # Send signal to UI
                    signal_name = "BUY" if signal_val > 0 else "SELL"
                    send_ui_update({
                        "last_signal": signal_name,
                        "current_position": state.current_position
                    })

                    # Get current price for risk check
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                        current_price = float(ticker.get("last") or ticker.get("close") or 0.0)
                    except Exception:
                        current_price = None
                    
                    ok_to_trade, qty = check_risk(exchange, state, config, current_price)
                    if not ok_to_trade:
                        state.last_signal = signal_val
                        continue

                    # If currently long and SELL signal, close existing first using held size
                    if side == "sell" and state.current_position == "long":
                        qty_to_sell = max(state.position_size_base, 0.0)
                        if qty_to_sell > 0:
                            order = place_order(exchange, symbol, "sell", qty_to_sell)
                            if order is not None:
                                exec_px = float(order.get("avg_price") or 0.0)
                                pnl = (exec_px - float(state.entry_price or exec_px)) * (-qty_to_sell)  # closing long -> negative qty
                                log_trade({
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "symbol": symbol,
                                    "signal": "close_long",
                                    "side": "sell",
                                    "executed_price": exec_px,
                                    "executed_size": qty_to_sell,
                                    "stop_loss": state.stop_loss,
                                    "take_profit": state.take_profit,
                                    "order_id": order.get("id"),
                                    "pnl_usdt": pnl,
                                })
                            state.current_position = "flat"
                            state.position_size_base = 0.0
                            state.entry_price = None
                            state.stop_loss = None
                            state.take_profit = None

                    # Entry (buy long) or (sell short if allowed)
                    if side == "buy":
                        order = place_order(exchange, symbol, "buy", qty)
                        if order is not None:
                            # Get execution price from multiple possible fields
                            exec_px = float(order.get("average") or order.get("avg_price") or order.get("price") or order.get("last") or 0.0)
                            
                            # If still 0, try to get current market price
                            if exec_px == 0.0:
                                try:
                                    ticker = exchange.fetch_ticker(symbol)
                                    exec_px = float(ticker.get("last") or ticker.get("close") or 0.0)
                                except:
                                    exec_px = 0.0
                            
                            # Get filled amount
                            filled_amount = float(order.get("filled") or order.get("amount") or qty)
                            
                            # Calculate trade value
                            trade_value_usd = exec_px * filled_amount if exec_px > 0 else 0.0
                            
                            sl, tp = _compute_sl_tp(exec_px, "buy", config["stop_loss_pct"], config["take_profit_pct"]) 
                            state.current_position = "long"
                            state.position_size_base = filled_amount
                            state.entry_price = exec_px
                            state.stop_loss = sl
                            state.take_profit = tp
                            
                            LOGGER.info("BUY ORDER EXECUTED: Price=$%.2f, Size=%.6f BTC, Value=$%.2f", 
                                       exec_px, filled_amount, trade_value_usd)
                            
                            log_trade({
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "symbol": symbol,
                                "signal": "buy",
                                "side": "buy",
                                "executed_price": exec_px,
                                "executed_size": filled_amount,
                                "trade_value_usd": trade_value_usd,
                                "stop_loss": sl,
                                "take_profit": tp,
                                "order_id": order.get("id"),
                                "pnl_usdt": None,
                            })
                    else:  # side == "sell" - SHORT ENTRY
                        # Unified trading allows true shorting
                        order = place_order(exchange, symbol, "sell", qty)
                        if order is not None:
                            # Get execution price from multiple possible fields
                            exec_px = float(order.get("average") or order.get("avg_price") or order.get("price") or order.get("last") or 0.0)
                            
                            # If still 0, try to get current market price
                            if exec_px == 0.0:
                                try:
                                    ticker = exchange.fetch_ticker(symbol)
                                    exec_px = float(ticker.get("last") or ticker.get("close") or 0.0)
                                except:
                                    exec_px = 0.0
                            
                            # Get filled amount
                            filled_amount = float(order.get("filled") or order.get("amount") or qty)
                            
                            # Calculate trade value
                            trade_value_usd = exec_px * filled_amount if exec_px > 0 else 0.0
                            
                            sl, tp = _compute_sl_tp(exec_px, "sell", config["stop_loss_pct"], config["take_profit_pct"]) 
                            state.current_position = "short"
                            state.position_size_base = -filled_amount
                            state.entry_price = exec_px
                            state.stop_loss = sl
                            state.take_profit = tp
                            
                            LOGGER.info("SELL ORDER EXECUTED: Price=$%.2f, Size=%.6f BTC, Value=$%.2f", 
                                       exec_px, filled_amount, trade_value_usd)
                            
                            log_trade({
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "symbol": symbol,
                                "signal": "sell",
                                "side": "sell",
                                "executed_price": exec_px,
                                "executed_size": filled_amount,
                                "trade_value_usd": trade_value_usd,
                                "stop_loss": sl,
                                "take_profit": tp,
                                "order_id": order.get("id"),
                                "pnl_usdt": None,
                            })

                    state.last_signal = signal_val

            # Monitor SL/TP using REST price in between minute ticks
            last_px = None
            try:
                ticker = exchange.fetch_ticker(symbol)
                last_px = float(ticker.get("last") or ticker.get("close") or 0.0)
            except Exception:
                pass
            
            if state.current_position != "flat" and last_px is not None and state.stop_loss and state.take_profit:
                if state.current_position == "long":
                    hit_sl = last_px <= float(state.stop_loss)
                    hit_tp = last_px >= float(state.take_profit)
                    if hit_sl or hit_tp:
                        qty_to_sell = max(state.position_size_base, 0.0)
                        if qty_to_sell > 0:
                            order = place_order(exchange, symbol, "sell", qty_to_sell)
                            if order is not None:
                                exec_px = float(order.get("avg_price") or 0.0)
                                pnl = (exec_px - float(state.entry_price or exec_px)) * qty_to_sell
                                reason = "stop_loss" if hit_sl else "take_profit"
                                log_trade({
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "symbol": symbol,
                                    "signal": reason,
                                    "side": "sell",
                                    "executed_price": exec_px,
                                    "executed_size": qty_to_sell,
                                    "stop_loss": state.stop_loss,
                                    "take_profit": state.take_profit,
                                    "order_id": order.get("id"),
                                    "pnl_usdt": pnl,
                                })
                        state.current_position = "flat"
                        state.position_size_base = 0.0
                        state.entry_price = None
                        state.stop_loss = None
                        state.take_profit = None
                elif state.current_position == "short":
                    hit_sl = last_px >= float(state.stop_loss)
                    hit_tp = last_px <= float(state.take_profit)
                    if hit_sl or hit_tp:
                        qty_to_buy = abs(state.position_size_base)  # Convert negative to positive
                        if qty_to_buy > 0:
                            order = place_order(exchange, symbol, "buy", qty_to_buy)
                            if order is not None:
                                exec_px = float(order.get("avg_price") or 0.0)
                                pnl = (float(state.entry_price or exec_px) - exec_px) * qty_to_buy  # Short PnL calculation
                                reason = "stop_loss" if hit_sl else "take_profit"
                                log_trade({
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "symbol": symbol,
                                    "signal": reason,
                                    "side": "buy",
                                    "executed_price": exec_px,
                                    "executed_size": qty_to_buy,
                                    "stop_loss": state.stop_loss,
                                    "take_profit": state.take_profit,
                                    "order_id": order.get("id"),
                                    "pnl_usdt": pnl,
                                })
                        state.current_position = "flat"
                        state.position_size_base = 0.0
                        state.entry_price = None
                        state.stop_loss = None
                        state.take_profit = None

            time.sleep(1)
    finally:
        # Graceful shutdown
        try:
            if ws is not None:
                ws.stop()
        except Exception:
            pass
        LOGGER.info("Bot stopped.")


if __name__ == "__main__":
    main_loop()


