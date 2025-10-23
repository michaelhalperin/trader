#!/usr/bin/env python3
"""
AI Trading Bot Dashboard - Real-time monitoring of AI trading decisions
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Global data storage
bot_data = {
    "status": "stopped",
    "mode": "ai_powered",
    "total_coins": 4,
    "active_trades": 0,
    "daily_pnl": 0.0,
    "daily_pnl_pct": 0.0,
    "equity": 0.0,
    "ai_analysis": [],
    "recent_decisions": [],
    "market_regime": "sideways",
    "confidence_level": 0.0,
    "last_update": None
}

def load_trades_from_csv():
    """Load trades from CSV file if it exists"""
    trades = []
    csv_path = os.path.join(os.path.dirname(__file__), "ai_trades.csv")
    if os.path.exists(csv_path):
        try:
            import csv
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trades.append(row)
        except Exception as e:
            print(f"Error loading trades: {e}")
    return trades

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('ai_dashboard.html')

@app.route('/api/update', methods=['POST'])
def update_bot_data():
    """Receive updates from the AI bot"""
    global bot_data
    
    try:
        data = request.get_json()
        if data:
            # Update bot data
            bot_data.update(data)
            bot_data['last_update'] = datetime.now().isoformat()
            
            # Store AI analysis
            if 'ai_analysis' in data:
                bot_data['ai_analysis'] = data['ai_analysis']
            
            # Store recent decisions
            if 'recent_decisions' in data:
                bot_data['recent_decisions'] = data['recent_decisions']
            
            print(f"🤖 AI Bot Update: {data.get('status', 'unknown')}")
            return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error updating bot data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    return jsonify(bot_data)

@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    trades = load_trades_from_csv()
    return jsonify(trades)

def run_web_ui(port=None):
    """Start the web UI"""
    if port is None:
        port = int(os.getenv("DASHBOARD_PORT", "5001"))
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    print(f"🌐 Starting AI Trading Dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_web_ui()
