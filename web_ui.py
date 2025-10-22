#!/usr/bin/env python3
"""
Simple Web UI for Bybit Trading Bot
Displays real-time transactions, signals, and bot status
"""

import os
import json
import time
import csv
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import threading
import queue

app = Flask(__name__)

# Global data storage
bot_data = {
    "status": "stopped",
    "current_position": "flat",
    "equity": 0.0,
    "daily_pnl": 0.0,
    "daily_start_equity": 1000.0,
    "last_signal": None,
    "last_signal_time": None,
    "sma_fast": None,
    "sma_slow": None,
    "transactions": [],
    "last_update": None
}

# Queue for real-time updates
update_queue = queue.Queue()

def load_trades_from_csv():
    """Load trades from CSV file"""
    trades = []
    csv_path = "trades.csv"
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trades.append(row)
        except Exception as e:
            print(f"Error loading trades: {e}")
    return trades

def update_bot_data():
    """Update bot data from CSV and other sources"""
    global bot_data
    
    # Load latest trades
    trades = load_trades_from_csv()
    bot_data["transactions"] = trades[-50:]  # Keep last 50 transactions
    
    # Calculate daily PnL
    today = datetime.now().date()
    daily_trades = [t for t in trades if datetime.fromisoformat(t['timestamp'].replace('Z', '+00:00')).date() == today]
    daily_pnl = sum(float(t.get('pnl_usdt', 0) or 0) for t in daily_trades)
    bot_data["daily_pnl"] = daily_pnl
    
    # Update timestamp
    bot_data["last_update"] = datetime.now().isoformat()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard_v2.html')

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    update_bot_data()
    return jsonify(bot_data)

@app.route('/api/transactions')
def api_transactions():
    """API endpoint for transactions"""
    update_bot_data()
    return jsonify({
        "transactions": bot_data["transactions"],
        "total": len(bot_data["transactions"])
    })

@app.route('/api/update', methods=['POST'])
def api_update():
    """API endpoint to update bot status (called by bot)"""
    data = request.get_json()
    
    # Update bot data
    if 'status' in data:
        bot_data['status'] = data['status']
    if 'current_position' in data:
        bot_data['current_position'] = data['current_position']
    if 'equity' in data:
        bot_data['equity'] = data['equity']
    if 'last_signal' in data:
        bot_data['last_signal'] = data['last_signal']
        bot_data['last_signal_time'] = datetime.now().isoformat()
    if 'sma_fast' in data:
        bot_data['sma_fast'] = data['sma_fast']
    if 'sma_slow' in data:
        bot_data['sma_slow'] = data['sma_slow']
    if 'daily_start_equity' in data:
        bot_data['daily_start_equity'] = data['daily_start_equity']
    
    bot_data['last_update'] = datetime.now().isoformat()
    
    return jsonify({"status": "updated"})

def run_web_ui(host='127.0.0.1', port=5001):
    """Start the web UI server"""
    print(f"Starting Web UI at http://{host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    run_web_ui()
