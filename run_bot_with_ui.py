#!/usr/bin/env python3
"""
Run the trading bot with web UI
"""

import subprocess
import sys
import time
import threading
import os

def run_web_ui():
    """Run the web UI in a separate process"""
    print("Starting Web UI...")
    subprocess.run([sys.executable, "web_ui.py"])

def run_bot():
    """Run the trading bot"""
    print("Starting Trading Bot...")
    subprocess.run([sys.executable, "bybit_bot.py"])

if __name__ == "__main__":
    print("🤖 Starting Bybit Trading Bot with Web UI")
    print("=" * 50)
    print("Web UI will be available at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Start web UI in background
        ui_thread = threading.Thread(target=run_web_ui, daemon=True)
        ui_thread.start()
        
        # Wait a moment for UI to start
        time.sleep(2)
        
        # Start the bot (this will block)
        run_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)
