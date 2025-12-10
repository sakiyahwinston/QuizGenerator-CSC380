import os
import subprocess
import sys
import platform

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.check_call(cmd, shell=True)

# 1. Create venv
if not os.path.exists("venv"):
    print("Creating virtual environment...")
    run(f"{sys.executable} -m venv venv")

# 2. Activate venv depending on OS
if platform.system() == "Windows":
    activate = r"venv\Scripts\activate"
else:
    activate = "source venv/bin/activate"

# 3. Install requirements
if os.path.exists("requirements.txt"):
    print("Installing requirements...")
    run(f"{activate} && pip install -r requirements.txt")

# 4. Run the program
print("Starting QuizGenerator...")
run(f"{activate} && python main.py")
