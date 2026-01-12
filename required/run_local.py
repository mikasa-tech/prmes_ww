#!/usr/bin/env python3
"""
Local Flask App Launcher
Starts the PRMES evaluation system on localhost only
"""

import os
import sys
import webbrowser
from pathlib import Path

def main():
    print("=" * 50)
    print("🚀 Starting PRMES Evaluation System")
    print("=" * 50)
    print("📍 Running on: http://127.0.0.1:5000")
    print("🔒 Local access only (secure)")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found!")
        print("Make sure you're running this from the project directory.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Ask if user wants to auto-open browser
    try:
        choice = input("🌐 Open browser automatically? (y/n): ").lower().strip()
        auto_open = choice in ['y', 'yes', '']
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
        sys.exit(0)
    
    print("\n🔄 Starting server...")
    
    # Auto-open browser after a short delay if requested
    if auto_open:
        import threading
        import time
        def open_browser():
            time.sleep(2)  # Give server time to start
            webbrowser.open('http://127.0.0.1:5000')
        
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    
    # Start the Flask app
    try:
        from app import create_app
        app = create_app()
        app.run(host="127.0.0.1", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()