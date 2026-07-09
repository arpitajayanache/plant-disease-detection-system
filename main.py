import subprocess
import time
import webbrowser
import os
import sys

def run_leafai():
    print("="*60)
    print("🚀 Starting LeafAI — Plant Disease Detection System")
    print("="*60)

    # 1. Start Backend
    print("📦 Starting Flask Backend on port 5000...")
    backend_cmd = [sys.executable, "app.py"]
    backend_proc = subprocess.Popen(backend_cmd)

    # 2. Start Frontend Server
    print("🌐 Starting Frontend Server on port 3000...")
    frontend_cmd = [sys.executable, "-m", "http.server", "3000", "--directory", "leafai"]
    frontend_proc = subprocess.Popen(frontend_cmd)

    time.sleep(3) # Wait for servers to spin up

    # 3. Open Browser
    print("🌍 Opening LeafAI in your browser...")
    webbrowser.open("http://localhost:3000")

    print("\n✅ System is running!")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend : http://localhost:5000")
    print("\nPress Ctrl+C to stop both servers.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("✅ Done.")

if __name__ == "__main__":
    run_leafai()