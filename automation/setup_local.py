#!/usr/bin/env python3
"""
Local Setup Script for Auto Job Apply Automation
Sets up the complete automation environment on local machine
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List

class LocalSetup:
    """Setup automation environment locally"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.automation_dir = self.project_root / "automation"
        self.system = platform.system().lower()
        self.setup_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log setup messages"""
        log_entry = f"[{level}] {message}"
        print(log_entry)
        self.setup_log.append(log_entry)
    
    def run_command(self, command: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        try:
            self.log(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                self.log(f"Error: {e.stderr.strip()}", "ERROR")
            raise
    
    def check_system_requirements(self) -> bool:
        """Check if system requirements are met"""
        self.log("🔍 Checking system requirements...")
        
        requirements = {
            'python': {'command': ['python', '--version'], 'min_version': '3.8'},
            'git': {'command': ['git', '--version'], 'required': True},
            'flutter': {'command': ['flutter', '--version'], 'required': True},
            'node': {'command': ['node', '--version'], 'min_version': '16'},
            'npm': {'command': ['npm', '--version'], 'required': True}
        }
        
        missing_requirements = []
        
        for req_name, req_config in requirements.items():
            try:
                result = self.run_command(req_config['command'], check=False)
                if result.returncode == 0:
                    self.log(f"✅ {req_name} is available")
                else:
                    missing_requirements.append(req_name)
                    self.log(f"❌ {req_name} not found", "ERROR")
            except FileNotFoundError:
                missing_requirements.append(req_name)
                self.log(f"❌ {req_name} not found", "ERROR")
        
        if missing_requirements:
            self.log("Missing requirements. Please install:", "ERROR")
            for req in missing_requirements:
                self.log(f"  - {req}", "ERROR")
            return False
        
        return True
    
    def setup_python_environment(self) -> bool:
        """Setup Python virtual environment and dependencies"""
        self.log("🐍 Setting up Python environment...")
        
        try:
            # Create virtual environment for automation
            venv_path = self.automation_dir / "venv"
            if not venv_path.exists():
                self.run_command(['python', '-m', 'venv', str(venv_path)])
                self.log("✅ Virtual environment created")
            
            # Determine activation script based on OS
            if self.system == "windows":
                activate_script = venv_path / "Scripts" / "activate.bat"
                pip_executable = venv_path / "Scripts" / "pip.exe"
            else:
                activate_script = venv_path / "bin" / "activate"
                pip_executable = venv_path / "bin" / "pip"
            
            # Install requirements
            requirements_file = self.automation_dir / "requirements.txt"
            if requirements_file.exists():
                self.run_command([str(pip_executable), 'install', '-r', str(requirements_file)])
                self.log("✅ Python dependencies installed")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to setup Python environment: {e}", "ERROR")
            return False
    
    def setup_flutter_environment(self) -> bool:
        """Setup Flutter environment"""
        self.log("📱 Setting up Flutter environment...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            # Enable web support
            self.run_command(['flutter', 'config', '--enable-web'])
            self.log("✅ Flutter web enabled")
            
            # Get dependencies
            self.run_command(['flutter', 'pub', 'get'], cwd=frontend_dir)
            self.log("✅ Flutter dependencies installed")
            
            # Build runner for code generation
            self.run_command(['flutter', 'packages', 'pub', 'run', 'build_runner', 'build'], 
                           cwd=frontend_dir, check=False)
            self.log("✅ Code generation completed")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to setup Flutter environment: {e}", "ERROR")
            return False
    
    def setup_database(self) -> bool:
        """Setup database for testing"""
        self.log("🗄️ Setting up database...")
        
        try:
            # Check if PostgreSQL is running
            import psycopg2
            
            try:
                conn = psycopg2.connect(
                    host='localhost',
                    port=5432,
                    user='postgres',
                    password='9912129398',
                    database='postgres'
                )
                conn.close()
                self.log("✅ PostgreSQL is accessible")
                
                # Create database tables
                db_script = self.project_root / "create_database_tables.py"
                if db_script.exists():
                    self.run_command(['python', str(db_script)])
                    self.log("✅ Database tables created")
                
                return True
                
            except psycopg2.OperationalError as e:
                self.log(f"PostgreSQL connection failed: {e}", "ERROR")
                self.log("Please ensure PostgreSQL is running with correct credentials", "ERROR")
                return False
                
        except ImportError:
            self.log("psycopg2 not available, will be installed with requirements", "WARNING")
            return True
    
    def create_automation_config(self) -> bool:
        """Create automation configuration file"""
        self.log("⚙️ Creating automation configuration...")
        
        config = {
            "services": {
                "auth": {"port": 8001, "required": True},
                "core": {"port": 8002, "required": True},
                "ml": {"port": 8003, "required": True},
                "payment": {"port": 8004, "required": True}
            },
            "flutter": {
                "test_timeout": 300,
                "screenshot_delay": 2,
                "web_port": 3000
            },
            "backend": {
                "test_timeout": 60,
                "retry_count": 3
            },
            "screenshot": {
                "similarity_threshold": 0.95,
                "auto_fix_enabled": True,
                "baseline_update_mode": "manual"
            },
            "reporting": {
                "generate_html": True,
                "include_screenshots": True,
                "retention_days": 30
            },
            "local_setup": {
                "setup_date": "2025-08-30",
                "system": self.system,
                "project_root": str(self.project_root)
            }
        }
        
        config_file = self.automation_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log(f"✅ Configuration saved to {config_file}")
        return True
    
    def create_run_scripts(self) -> bool:
        """Create convenient run scripts"""
        self.log("📝 Creating run scripts...")
        
        try:
            # Create batch script for Windows
            if self.system == "windows":
                batch_script = self.project_root / "run_automation.bat"
                with open(batch_script, 'w') as f:
                    f.write(f"""@echo off
echo Starting Auto Job Apply Automation Suite...
cd /d "{self.project_root}"
call automation\\venv\\Scripts\\activate.bat
python automation\\run_automation.py %*
pause
""")
                self.log("✅ Windows batch script created")
            
            # Create shell script for Unix-like systems
            else:
                shell_script = self.project_root / "run_automation.sh"
                with open(shell_script, 'w') as f:
                    f.write(f"""#!/bin/bash
echo "Starting Auto Job Apply Automation Suite..."
cd "{self.project_root}"
source automation/venv/bin/activate
python automation/run_automation.py "$@"
""")
                os.chmod(shell_script, 0o755)
                self.log("✅ Shell script created")
            
            # Create quick test scripts
            quick_scripts = {
                'test_flutter.py': 'python automation/run_automation.py --flutter-only',
                'test_backend.py': 'python automation/run_automation.py --backend-only',
                'validate_screenshots.py': 'python automation/run_automation.py --validation-only'
            }
            
            for script_name, command in quick_scripts.items():
                script_path = self.automation_dir / script_name
                with open(script_path, 'w') as f:
                    f.write(f"""#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir(r"{self.project_root}")
result = subprocess.run([{repr(command.split())}], shell=False)
sys.exit(result.returncode)
""")
                if self.system != "windows":
                    os.chmod(script_path, 0o755)
            
            self.log("✅ Quick test scripts created")
            return True
            
        except Exception as e:
            self.log(f"Failed to create run scripts: {e}", "ERROR")
            return False
    
    def setup_ide_integration(self) -> bool:
        """Setup IDE integration files"""
        self.log("🔧 Setting up IDE integration...")
        
        try:
            # VS Code settings
            vscode_dir = self.project_root / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            # Launch configuration for debugging
            launch_config = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Run Full Automation",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/automation/run_automation.py",
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    },
                    {
                        "name": "Run Flutter Tests Only",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/automation/run_automation.py",
                        "args": ["--flutter-only"],
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    },
                    {
                        "name": "Run Backend Tests Only",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/automation/run_automation.py",
                        "args": ["--backend-only"],
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    }
                ]
            }
            
            with open(vscode_dir / "launch.json", 'w') as f:
                json.dump(launch_config, f, indent=2)
            
            # Tasks configuration
            tasks_config = {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "Run Automation Suite",
                        "type": "shell",
                        "command": "python",
                        "args": ["automation/run_automation.py"],
                        "group": "test",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "shared"
                        }
                    },
                    {
                        "label": "Validate Screenshots",
                        "type": "shell",
                        "command": "python",
                        "args": ["automation/screenshot_validator.py"],
                        "group": "test"
                    }
                ]
            }
            
            with open(vscode_dir / "tasks.json", 'w') as f:
                json.dump(tasks_config, f, indent=2)
            
            self.log("✅ VS Code integration configured")
            return True
            
        except Exception as e:
            self.log(f"Failed to setup IDE integration: {e}", "ERROR")
            return False
    
    def run_setup(self) -> bool:
        """Run complete setup process"""
        self.log("🚀 Starting Auto Job Apply Automation Setup")
        self.log("=" * 60)
        
        setup_steps = [
            ("System Requirements", self.check_system_requirements),
            ("Python Environment", self.setup_python_environment),
            ("Flutter Environment", self.setup_flutter_environment),
            ("Database Setup", self.setup_database),
            ("Automation Config", self.create_automation_config),
            ("Run Scripts", self.create_run_scripts),
            ("IDE Integration", self.setup_ide_integration)
        ]
        
        failed_steps = []
        
        for step_name, step_function in setup_steps:
            self.log(f"\n📋 {step_name}...")
            try:
                if step_function():
                    self.log(f"✅ {step_name} completed successfully")
                else:
                    self.log(f"❌ {step_name} failed", "ERROR")
                    failed_steps.append(step_name)
            except Exception as e:
                self.log(f"❌ {step_name} failed with exception: {e}", "ERROR")
                failed_steps.append(step_name)
        
        # Save setup log
        log_file = self.automation_dir / "setup_log.txt"
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.setup_log))
        
        # Print summary
        self.log("\n" + "=" * 60)
        self.log("🎯 SETUP SUMMARY")
        self.log("=" * 60)
        
        if not failed_steps:
            self.log("🎉 Setup completed successfully!")
            self.log("\n📋 Next steps:")
            self.log("1. Start your backend services")
            self.log("2. Run: python automation/run_automation.py")
            self.log("3. Check automation/reports/ for results")
            return True
        else:
            self.log(f"⚠️  Setup completed with {len(failed_steps)} issues:")
            for step in failed_steps:
                self.log(f"   - {step}")
            self.log(f"\n📄 Check setup log: {log_file}")
            return False

def main():
    """Main setup function"""
    setup = LocalSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
