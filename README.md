# AI-Powered Multi-Coin Trading Bot with Dashboard

An advanced AI-powered trading bot with real-time web dashboard for multiple cryptocurrencies on Bybit testnet using intelligent technical analysis and position sizing.

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
pip install -r requirements.txt
```

## ⚙️ Setup

1. **Environment Variables**: Copy `.env` file and update with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

2. **API Keys**: Update `.env` file with your Bybit testnet credentials
3. **Testnet Funds**: Ensure you have USDT in your testnet derivatives wallet

## 🚀 Running the Bot

### Option 1: AI System with Dashboard (Recommended)
```bash
python3 run_ai_system.py
```
- Opens AI dashboard at: http://127.0.0.1:5001
- Runs AI bot and dashboard together
- Press Ctrl+C to stop both

### Option 2: AI Bot Only
```bash
python3 ai_trading_bot.py
```

### Option 3: Dashboard Only
```bash
python3 ai_dashboard.py
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

- `ai_trading_bot.py` - AI-powered trading bot
- `ai_dashboard.py` - AI dashboard server
- `templates/ai_dashboard.html` - AI dashboard UI
- `run_ai_system.py` - Combined launcher
- `.env` - Environment variables (API keys, configuration)
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore file for sensitive data

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

---------------------------------------------------------------------

# 🤖 AI Trading Bot Profitability Analyzer

## Overview
This tool analyzes your AI trading bot's performance and determines if it's profitable or not.

## Features
- **Real-time Analysis**: Monitors bot performance in real-time
- **Comprehensive Metrics**: Tracks returns, trades, confidence, risk/reward
- **Smart Assessment**: Determines profitability with detailed reasoning
- **Warnings & Recommendations**: Provides actionable insights

## Usage

### Quick Analysis (Current Status)
```bash
python3 profitability_analyzer.py
# Choose option 1
```

### Continuous Monitoring (1 Hour)
```bash
python3 profitability_analyzer.py
# Choose option 2
```

### Extended Analysis (4 Hours)
```bash
python3 profitability_analyzer.py
# Choose option 3
```

## What It Analyzes

### 📊 Profitability Metrics
- **Starting vs Current Balance**
- **Total Return & Percentage**
- **Daily P&L**
- **Time-based Performance**

### 🎯 Trading Activity
- **Total Trades Executed**
- **Buy vs Sell Ratio**
- **Trades per Hour**
- **Position Sizing**

### 🧠 AI Performance
- **Average Confidence Level**
- **High Confidence Trades**
- **Risk/Reward Ratios**
- **Market Regime Analysis**

## Profitability Assessment

### 🚀 HIGHLY PROFITABLE
- Return > 15%
- High confidence trades
- Good risk/reward ratios

### ✅ PROFITABLE
- Return > 5%
- Decent confidence levels
- Positive returns

### 📈 SLIGHTLY PROFITABLE
- Small positive returns
- Needs optimization

### ⚖️ BREAKEVEN
- Near zero returns
- Needs strategy review

### ❌ UNPROFITABLE
- Negative returns
- Immediate attention needed

## Warnings & Recommendations

The analyzer provides warnings for:
- **High Risk**: Large position sizes
- **Over-trading**: Too many trades
- **Low Confidence**: Poor AI decisions
- **Poor Risk/Reward**: Bad trade quality

## Requirements
- Bot must be running on http://127.0.0.1:5001
- Python 3.6+
- Required packages: requests, pandas

## Example Output
```
🤖 AI TRADING BOT PROFITABILITY ANALYSIS
================================================================================
📅 Analysis Time: 2025-10-23 16:45:00

📊 CURRENT BOT STATUS:
   Status: running
   Balance: $7,942.24
   Daily P&L: $0.00
   Active Trades: 2
   AI Confidence: 61.2%
   Market Regime: sideways

📈 PROFITABILITY METRICS:
   Starting Balance: $7,942.24
   Current Balance: $7,942.24
   Total Return: $0.00
   Return Percentage: 0.00%
   Analysis Duration: 0.5 hours

🏆 PROFITABILITY ASSESSMENT:
   ⚖️ Bot is roughly breakeven: 0.00% return

💡 RECOMMENDATIONS:
   ⚖️ Bot is not losing money but not profitable:
   • Review trading parameters
   • Check market conditions
   • Consider adjusting confidence thresholds
```

## Best Practices
1. **Run for at least 1 hour** to get meaningful data
2. **Monitor during different market conditions**
3. **Check warnings regularly**
4. **Use extended analysis for long-term assessment**
5. **Stop trading if UNPROFITABLE status appears**

## Troubleshooting
- **Cannot connect**: Make sure bot is running
- **Insufficient data**: Run for longer periods
- **No trades**: Check bot configuration
- **API errors**: Verify bot connection
