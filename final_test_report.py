#!/usr/bin/env python3
"""
Final Comprehensive Test Report for Auto Job Apply System
Complete system validation and status report
"""

import requests
import json
import time
import os
import subprocess
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class FinalTestReport:
    def __init__(self):
        self.services = {
            'auth': {'url': 'http://localhost:8001', 'name': 'Authentication Service'},
            'core': {'url': 'http://localhost:8002', 'name': 'Core Application Service'}, 
            'ml': {'url': 'http://localhost:8003', 'name': 'Machine Learning Service'},
            'payment': {'url': 'http://localhost:8004', 'name': 'Payment Processing Service'}
        }
        self.frontend_url = 'http://localhost:3000'
        self.database_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': '9912129398',
            'database': 'AutoJobApply'
        }
        
    def log(self, message, color=Colors.ENDC):
        print(f"{color}{message}{Colors.ENDC}")
        
    def print_header(self):
        """Print report header"""
        self.log("=" * 80, Colors.CYAN)
        self.log(f"{Colors.BOLD}🚀 AUTO JOB APPLY SYSTEM - FINAL TEST REPORT{Colors.ENDC}", Colors.CYAN)
        self.log(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.CYAN)
        self.log("=" * 80, Colors.CYAN)
        
    def test_system_requirements(self):
        """Test system requirements"""
        self.log(f"\n{Colors.PURPLE}📋 SYSTEM REQUIREMENTS CHECK{Colors.ENDC}")
        self.log("-" * 50)
        
        requirements = {
            'Python': 'python --version',
            'Git': 'git --version',
            'Flutter': 'flutter --version',
            'PostgreSQL': 'psql --version'
        }
        
        for req, command in requirements.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.log(f"✅ {req}: {version}", Colors.GREEN)
                else:
                    self.log(f"❌ {req}: Not found or error", Colors.RED)
            except Exception as e:
                self.log(f"❌ {req}: {str(e)}", Colors.RED)
                
    def test_backend_services(self):
        """Test all backend services"""
        self.log(f"\n{Colors.BLUE}🔧 BACKEND SERVICES STATUS{Colors.ENDC}")
        self.log("-" * 50)
        
        all_healthy = True
        for service_key, service_info in self.services.items():
            try:
                # Test health endpoint
                response = requests.get(f"{service_info['url']}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'healthy':
                        self.log(f"✅ {service_info['name']}: RUNNING ({service_info['url']})", Colors.GREEN)
                    else:
                        self.log(f"⚠️  {service_info['name']}: UNHEALTHY ({service_info['url']})", Colors.YELLOW)
                        all_healthy = False
                else:
                    self.log(f"❌ {service_info['name']}: HTTP {response.status_code} ({service_info['url']})", Colors.RED)
                    all_healthy = False
            except Exception as e:
                self.log(f"❌ {service_info['name']}: OFFLINE ({service_info['url']})", Colors.RED)
                all_healthy = False
                
        return all_healthy
        
    def test_database(self):
        """Test database connectivity"""
        self.log(f"\n{Colors.BLUE}🗄️  DATABASE STATUS{Colors.ENDC}")
        self.log("-" * 50)
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=self.database_config['host'],
                port=self.database_config['port'],
                user=self.database_config['user'],
                password=self.database_config['password'],
                database=self.database_config['database']
            )
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            self.log(f"✅ PostgreSQL Database: CONNECTED", Colors.GREEN)
            self.log(f"   Host: {self.database_config['host']}:{self.database_config['port']}", Colors.CYAN)
            self.log(f"   Database: {self.database_config['database']}", Colors.CYAN)
            self.log(f"   Version: {version.split(',')[0]}", Colors.CYAN)
            return True
            
        except Exception as e:
            self.log(f"❌ PostgreSQL Database: CONNECTION FAILED", Colors.RED)
            self.log(f"   Error: {str(e)}", Colors.RED)
            return False
            
    def test_frontend(self):
        """Test frontend application"""
        self.log(f"\n{Colors.BLUE}🌐 FRONTEND APPLICATION STATUS{Colors.ENDC}")
        self.log("-" * 50)
        
        # Check Flutter project structure
        flutter_files = ['pubspec.yaml', 'lib/main.dart', 'web/index.html']
        project_ok = True
        
        for file_path in flutter_files:
            full_path = os.path.join('frontend', file_path)
            if os.path.exists(full_path):
                self.log(f"✅ Flutter File: {file_path}", Colors.GREEN)
            else:
                self.log(f"❌ Flutter File: {file_path} NOT FOUND", Colors.RED)
                project_ok = False
                
        # Test if Flutter web is running
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log(f"✅ Flutter Web App: RUNNING ({self.frontend_url})", Colors.GREEN)
                web_running = True
            else:
                self.log(f"⚠️  Flutter Web App: HTTP {response.status_code} ({self.frontend_url})", Colors.YELLOW)
                web_running = False
        except Exception:
            self.log(f"❌ Flutter Web App: NOT RUNNING ({self.frontend_url})", Colors.RED)
            web_running = False
            
        return project_ok and web_running
        
    def print_api_documentation(self):
        """Print API documentation links"""
        self.log(f"\n{Colors.PURPLE}📚 API DOCUMENTATION{Colors.ENDC}")
        self.log("-" * 50)
        
        for service_key, service_info in self.services.items():
            docs_url = f"{service_info['url']}/docs"
            self.log(f"📖 {service_info['name']}: {docs_url}", Colors.CYAN)
            
    def print_access_points(self):
        """Print system access points"""
        self.log(f"\n{Colors.PURPLE}🌐 SYSTEM ACCESS POINTS{Colors.ENDC}")
        self.log("-" * 50)
        
        self.log(f"🖥️  Frontend Application: {self.frontend_url}", Colors.CYAN)
        self.log(f"🧪 Test Dashboard: file:///c:/Users/Admin/Desktop/Auto-Apply%20Job/frontend/web_test/index.html", Colors.CYAN)
        
        for service_key, service_info in self.services.items():
            self.log(f"🔧 {service_info['name']}: {service_info['url']}", Colors.CYAN)
            
    def generate_final_report(self):
        """Generate complete final report"""
        self.print_header()
        
        # Test system requirements
        self.test_system_requirements()
        
        # Test backend services
        backend_status = self.test_backend_services()
        
        # Test database
        database_status = self.test_database()
        
        # Test frontend
        frontend_status = self.test_frontend()
        
        # Print documentation and access points
        self.print_api_documentation()
        self.print_access_points()
        
        # Final summary
        self.log(f"\n{Colors.BOLD}🎯 FINAL SYSTEM STATUS{Colors.ENDC}")
        self.log("=" * 50)
        
        if backend_status and database_status:
            self.log("🎉 BACKEND SYSTEM: FULLY OPERATIONAL", Colors.GREEN)
        else:
            self.log("⚠️  BACKEND SYSTEM: ISSUES DETECTED", Colors.YELLOW)
            
        if frontend_status:
            self.log("🎉 FRONTEND SYSTEM: FULLY OPERATIONAL", Colors.GREEN)
        else:
            self.log("⚠️  FRONTEND SYSTEM: SETUP NEEDED", Colors.YELLOW)
            
        overall_status = backend_status and database_status
        if overall_status:
            self.log(f"\n🚀 AUTO JOB APPLY SYSTEM IS READY FOR USE!", Colors.GREEN)
        else:
            self.log(f"\n🔧 SYSTEM REQUIRES ATTENTION BEFORE USE", Colors.YELLOW)
            
        self.log("=" * 80, Colors.CYAN)
        return overall_status

if __name__ == "__main__":
    report = FinalTestReport()
    report.generate_final_report()
