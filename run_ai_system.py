#!/usr/bin/env python3
"""
Run AI Trading Bot with Dashboard
"""

import subprocess
import time
import sys
import os
from multiprocessing import Process

def run_ai_bot():
    """Run the AI trading bot"""
    print("🤖 Starting AI Trading Bot...")
    subprocess.run([sys.executable, "ai_trading_bot.py"])

def run_dashboard():
    """Run the AI dashboard"""
    print("🌐 Starting AI Dashboard...")
    subprocess.run([sys.executable, "ai_dashboard.py"])

if __name__ == "__main__":
    print("🧠 AI TRADING SYSTEM STARTUP")
    print("============================")
    print("")
    print("🚀 Starting AI Trading Bot + Dashboard...")
    print("")
    print("📊 Dashboard will be available at: http://127.0.0.1:5000")
    print("🤖 AI Bot will run in the background")
    print("")
    print("Press Ctrl+C to stop both services")
    print("")
    
    try:
        # Start dashboard in background
        dashboard_process = Process(target=run_dashboard)
        dashboard_process.start()
        
        # Wait a moment for dashboard to start
        time.sleep(3)
        
        # Start AI bot in foreground
        run_ai_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping AI Trading System...")
        dashboard_process.terminate()
        dashboard_process.join()
        print("✅ AI Trading System stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        dashboard_process.terminate()
        dashboard_process.join()
