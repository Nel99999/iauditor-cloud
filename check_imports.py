import os
import glob
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

files = glob.glob("backend/*_routes.py")
for f in files:
    module_name = f.replace("\\", ".").replace("/", ".").replace(".py", "")
    print(f"Checking {module_name}...")
    try:
        __import__(module_name)
        print(f"[OK] {module_name} OK")
    except Exception as e:
        print(f"[FAIL] {module_name} FAILED: {e}")
