#!/usr/bin/env python3
"""
Auto Job Apply System Setup Script
This script helps set up the development environment for the Auto Job Apply System
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """Run a shell command"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_prerequisites():
    """Check if required tools are installed"""
    print("Checking prerequisites...")
    
    required_tools = {
        'python': 'python --version',
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version',
        'flutter': 'flutter --version'
    }
    
    missing_tools = []
    
    for tool, command in required_tools.items():
        result = run_command(command, check=False)
        if result.returncode != 0:
            missing_tools.append(tool)
        else:
            print(f"✓ {tool} is installed")
    
    if missing_tools:
        print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
        print("\nPlease install the missing tools and run setup again.")
        print("\nInstallation guides:")
        print("- Python: https://www.python.org/downloads/")
        print("- Docker: https://docs.docker.com/get-docker/")
        print("- Flutter: https://docs.flutter.dev/get-started/install")
        sys.exit(1)
    
    print("✓ All prerequisites are installed")


def setup_environment():
    """Set up environment files"""
    print("\nSetting up environment files...")
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from .env.example")
            print("⚠️  Please update the .env file with your actual configuration values")
        else:
            print("❌ .env.example file not found")
    else:
        print("✓ .env file already exists")


def install_backend_dependencies():
    """Install Python dependencies for all backend services"""
    print("\nInstalling backend dependencies...")
    
    services = ['auth', 'core', 'ml', 'payment']
    
    for service in services:
        service_path = f"backend/{service}"
        if os.path.exists(f"{service_path}/requirements.txt"):
            print(f"\nInstalling dependencies for {service} service...")
            
            # Create virtual environment
            venv_path = f"{service_path}/venv"
            if not os.path.exists(venv_path):
                run_command(f"python -m venv {venv_path}")
            
            # Install dependencies
            if os.name == 'nt':  # Windows
                pip_path = f"{venv_path}/Scripts/pip"
            else:  # Unix/Linux/Mac
                pip_path = f"{venv_path}/bin/pip"
            
            run_command(f"{pip_path} install -r requirements.txt", cwd=service_path)
            print(f"✓ {service} service dependencies installed")


def setup_flutter():
    """Set up Flutter web project"""
    print("\nSetting up Flutter web project...")
    
    frontend_path = "frontend"
    if os.path.exists(f"{frontend_path}/pubspec.yaml"):
        print("Getting Flutter dependencies...")
        run_command("flutter pub get", cwd=frontend_path)
        
        print("Enabling Flutter web...")
        run_command("flutter config --enable-web", cwd=frontend_path)
        
        print("✓ Flutter web project set up successfully")
    else:
        print("❌ Flutter pubspec.yaml not found")


def setup_database():
    """Set up PostgreSQL database"""
    print("\nSetting up database...")
    
    # Start PostgreSQL with Docker
    print("Starting PostgreSQL database...")
    run_command("docker-compose up -d postgres")
    
    # Wait for database to be ready
    print("Waiting for database to be ready...")
    import time
    time.sleep(10)
    
    print("✓ Database setup completed")


def main():
    """Main setup function"""
    print("🚀 Auto Job Apply System Setup")
    print("=" * 50)
    
    # Check prerequisites
    check_prerequisites()
    
    # Setup environment
    setup_environment()
    
    # Install backend dependencies
    install_backend_dependencies()
    
    # Setup Flutter
    setup_flutter()
    
    # Setup database
    setup_database()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update the .env file with your actual configuration values")
    print("2. Run 'docker-compose up' to start all services")
    print("3. Access the application at http://localhost:3000")
    print("\nFor development:")
    print("- Backend services will be available on ports 8001-8004")
    print("- Database will be available on port 5432")
    print("- Frontend will be available on port 3000")


if __name__ == "__main__":
    main()
