import subprocess, sys, os

# Install deps first
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q", "--disable-pip-version-check"],
    cwd="/code", check=False
)

# Then start uvicorn
os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"])
