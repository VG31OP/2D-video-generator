import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def download_and_install_ollama():
    installer_path = Path(r"E:\OllamaSetup.exe")
    url = "https://ollama.com/download/OllamaSetup.exe"
    
    print(f"Downloading Ollama installer from {url} to {installer_path}...")
    try:
        urllib.request.urlretrieve(url, str(installer_path))
        print(f"Downloaded successfully: {installer_path.stat().st_size / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"Download error: {e}")
        return False
        
    print("Running silent installer...")
    try:
        # InnoSetup silent flags
        res = subprocess.run([str(installer_path), "/VERYSILENT", "/NORESTART", "/DIR=E:\\Ollama"], capture_output=True, text=True, timeout=120)
        print(f"Install exited with code: {res.returncode}")
        return True
    except Exception as e:
        print(f"Install error: {e}")
        return False

if __name__ == "__main__":
    download_and_install_ollama()
