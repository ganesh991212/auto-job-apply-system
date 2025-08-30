#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir(r"C:\Users\Admin\Desktop\Auto-Apply Job")
result = subprocess.run([['python', 'automation/run_automation.py', '--flutter-only']], shell=False)
sys.exit(result.returncode)
