@echo off
echo Starting Auto Job Apply Automation Suite...
cd /d "C:\Users\Admin\Desktop\Auto-Apply Job"
call automation\venv\Scripts\activate.bat
python automation\run_automation.py %*
pause
