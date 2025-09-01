#!/usr/bin/env python3
"""
Setup script for yak-hole
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error running: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        else:
            print(f"✅ Successfully ran: {cmd}")
            return True
    except Exception as e:
        print(f"❌ Exception running {cmd}: {e}")
        return False

def main():
    print("🕳️  Setting up Yak Hole...")
    
    # Check if we're in the right directory
    if not Path("package.json").exists() or not Path("backend").exists():
        print("❌ Please run this from the yak-hole project root directory")
        sys.exit(1)
    
    print("\n1. Installing Python backend dependencies...")
    if not run_command("pip3 install fastapi uvicorn sentence-transformers chromadb PyPDF2 httpx python-dotenv markdown", cwd="backend"):
        print("⚠️  Backend dependencies installation failed, but continuing...")
    
    print("\n2. Installing Node.js dependencies...")
    if not run_command("npm install"):
        print("❌ Node.js dependencies installation failed")
        return False
    
    print("\n3. Creating data directories...")
    Path("backend/data").mkdir(exist_ok=True)
    Path("backend/data/vector_db").mkdir(exist_ok=True)
    Path("backend/data/chat_history").mkdir(exist_ok=True)
    print("✅ Data directories created")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Make sure Ollama is installed and running: ollama serve")
    print("2. Ingest your notes: npm run ingest")
    print("3. Start the backend: npm run backend")
    print("4. Start the React Native app: npm start")
    print("5. Or run both together: npm run dev")
    
    return True

if __name__ == "__main__":
    main()