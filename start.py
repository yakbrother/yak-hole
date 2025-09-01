#!/usr/bin/env python3
"""
Quick start script for yak-hole
"""
import subprocess
import sys
import time
import threading
from pathlib import Path

def run_backend():
    """Run the backend server"""
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], cwd="backend")
    except KeyboardInterrupt:
        print("🛑 Backend stopped")

def run_ingestion():
    """Run note ingestion"""
    try:
        print("🔄 Starting note ingestion...")
        result = subprocess.run([
            sys.executable, "ingest_notes.py", 
            "--notes-dir", "../data", "--incremental"
        ], cwd="backend", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Note ingestion completed")
        else:
            print(f"⚠️  Ingestion warning: {result.stderr}")
    except Exception as e:
        print(f"❌ Ingestion error: {e}")

def main():
    print("🕳️  Starting Yak Hole...")
    
    # Check if we're in the right directory
    if not Path("backend/main.py").exists():
        print("❌ Please run this from the yak-hole project root directory")
        sys.exit(1)
    
    # Check if Ollama is available
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("⚠️  Ollama might not be running. Start it with: ollama serve")
    except:
        print("⚠️  Cannot connect to Ollama. Make sure it's running: ollama serve")
    
    # Run ingestion first
    print("\n📚 Ingesting notes...")
    ingestion_thread = threading.Thread(target=run_ingestion)
    ingestion_thread.daemon = True
    ingestion_thread.start()
    
    # Wait a moment for ingestion to start
    time.sleep(2)
    
    # Start backend
    print("\n🚀 Starting backend server...")
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    try:
        run_backend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down yak-hole...")

if __name__ == "__main__":
    main()