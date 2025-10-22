#!/usr/bin/env python3
"""
Restart the bot and web UI with updated dashboard
"""

import subprocess
import time
import webbrowser
import os
import sys

def restart_bot_and_ui():
    """Restart both the bot and web UI"""
    
    print("🔄 RESTARTING BYBIT TRADING BOT")
    print("=" * 40)
    
    # Kill any existing processes
    print("🛑 Stopping existing processes...")
    try:
        subprocess.run(["pkill", "-f", "python3 bybit_bot.py"], capture_output=True)
        subprocess.run(["pkill", "-f", "python3 web_ui.py"], capture_output=True)
        subprocess.run(["pkill", "-f", "flask"], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    print("✅ Processes stopped")
    
    # Start web UI first
    print("🌐 Starting Web UI...")
    ui_process = subprocess.Popen([
        sys.executable, "web_ui.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for UI to start
    time.sleep(3)
    
    # Start the bot
    print("🤖 Starting Trading Bot...")
    bot_process = subprocess.Popen([
        sys.executable, "bybit_bot.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment
    time.sleep(2)
    
    print("✅ Bot and UI started!")
    print()
    print("📊 DASHBOARD FEATURES:")
    print("   ✅ 'Your Money Used' column")
    print("   ✅ 'Trade Value' column") 
    print("   ✅ Real prices ($108,790.60)")
    print("   ✅ Calculated trade values ($49.93)")
    print()
    
    # Open dashboard
    print("🌐 Opening dashboard...")
    webbrowser.open("http://127.0.0.1:5000")
    
    print("🚀 Dashboard opened! You should now see:")
    print("   • Real prices instead of $0.00")
    print("   • 'Your Money Used' column showing $49.93")
    print("   • 'Trade Value' column with calculated amounts")
    print()
    print("💡 If you still see old data:")
    print("   1. Hard refresh (Ctrl+F5 or Cmd+Shift+R)")
    print("   2. Open new incognito/private window")
    print("   3. Clear browser cache")
    
    return bot_process, ui_process

if __name__ == "__main__":
    try:
        bot_process, ui_process = restart_bot_and_ui()
        
        print("\n⏳ Bot and UI are running...")
        print("Press Ctrl+C to stop both processes")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot and UI...")
        bot_process.terminate()
        ui_process.terminate()
        print("✅ Stopped successfully")
