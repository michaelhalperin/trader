# Bybit Testnet Unified Trading Bot with Web UI

A Python trading bot with real-time web dashboard for BTC/USDT on Bybit testnet using SMA crossover strategy.

## 🚀 Features

### Trading Bot
- **Unified Trading**: Derivatives/perpetuals with true shorting capability
- **SMA Strategy**: 5/20 period crossover signals (BUY/SELL)
- **Risk Management**: Max trade size, stop-loss, take-profit, daily loss limits
- **Real-time Monitoring**: WebSocket price updates and REST API
- **CSV Logging**: All trades logged with detailed metrics

### Web Dashboard
- **Real-time Updates**: Live bot status, positions, and P&L
- **Transaction History**: Detailed trade log with percentages
- **SMA Indicators**: Current fast/slow moving averages
- **Risk Metrics**: Daily P&L, equity, position status
- **Responsive Design**: Works on desktop and mobile

## 📊 Dashboard Metrics

- **Bot Status**: Running/Stopped with current position
- **Equity**: Current account value in USDT
- **Daily P&L**: Profit/Loss with percentage
- **SMA Indicators**: Live SMA(5) and SMA(20) values
- **Transaction Details**: Price, size, P&L, P&L%, SL/TP levels

## 🛠️ Requirements

```bash
pip install ccxt pandas ta websocket-client python-dotenv flask requests
```

## ⚙️ Setup

1. **API Keys**: Edit `api_keys.env` with your Bybit testnet credentials
2. **Configuration**: Adjust `config.json` for strategy parameters
3. **Testnet Funds**: Ensure you have USDT in your testnet derivatives wallet

## 🚀 Running the Bot

### Option 1: Bot with Web UI (Recommended)
```bash
python3 run_bot_with_ui.py
```
- Opens web dashboard at: http://127.0.0.1:5000
- Runs bot and UI together
- Press Ctrl+C to stop both

### Option 2: Bot Only
```bash
python3 bybit_bot.py
```

### Option 3: Web UI Only
```bash
python3 web_ui.py
```

## 📈 Understanding the Dashboard

### Status Cards
- **Bot Status**: Shows if bot is running/stopped
- **Current Position**: Long/Short/Flat with color coding
- **Equity**: Total account value in USDT
- **Daily P&L**: Today's profit/loss with percentage
- **Last Signal**: Most recent BUY/SELL signal
- **SMA Indicators**: Current moving average values

### Transaction Table
- **Time**: When the trade occurred
- **Signal**: BUY/SELL/close_long/stop_loss/take_profit
- **Side**: buy/sell direction
- **Price**: Execution price in USDT
- **Size**: Quantity traded
- **P&L**: Profit/Loss in USDT
- **P&L %**: Percentage return on trade
- **SL/TP**: Stop-loss and take-profit levels
- **Order ID**: Exchange order identifier

## ⚙️ Configuration

Edit `config.json`:
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1m",
  "fast_period": 5,
  "slow_period": 20,
  "max_trade_usd": 50,
  "stop_loss_pct": 0.02,
  "take_profit_pct": 0.03,
  "daily_loss_limit_pct": 0.05,
  "testnet": true,
  "allow_short": true,
  "trading_type": "unified"
}
```

## 📁 Files

- `bybit_bot.py` - Main trading bot
- `web_ui.py` - Web dashboard server
- `templates/dashboard.html` - Dashboard UI
- `config.json` - Bot configuration
- `api_keys.env` - API credentials
- `trades.csv` - Transaction log
- `run_bot_with_ui.py` - Combined launcher

## 🔒 Safety Notes

- **Testnet Only**: All trading is on Bybit testnet (fake money)
- **Unified Trading**: Uses derivatives/perpetuals for true shorting
- **Risk Controls**: Built-in stop-loss, take-profit, and daily loss limits
- **Real-time Monitoring**: Web dashboard shows all activity

## 🎯 Strategy Details

1. **Data Fetching**: Gets 1-minute BTC/USDT candles every minute
2. **SMA Calculation**: Computes SMA(5) and SMA(20) on close prices
3. **Signal Generation**: 
   - BUY when SMA(5) crosses above SMA(20)
   - SELL when SMA(5) crosses below SMA(20)
4. **Position Management**: True long/short positions with margin
5. **Risk Management**: Virtual stop-loss and take-profit monitoring
6. **Logging**: All trades saved to CSV with detailed metrics
