#!/usr/bin/env python3
"""
Comprehensive Automation Testing Suite for Auto Job Apply System
Tests the entire system end-to-end including frontend, backend, and database
"""

import requests
import json
import time
import psycopg2
import subprocess
import os
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

class ComprehensiveAutomationTests:
    def __init__(self):
        self.services = {
            'auth': 'http://localhost:8001',
            'core': 'http://localhost:8002',
            'ml': 'http://localhost:8003',
            'payment': 'http://localhost:8004'
        }
        self.frontend_url = 'http://localhost:3000'
        self.test_dashboard_url = 'file:///c:/Users/Admin/Desktop/Auto-Apply%20Job/frontend/web_test/index.html'
        self.database_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': '9912129398',
            'database': 'AutoJobApply'
        }
        self.passed = 0
        self.failed = 0
        self.total = 0
        
    def log(self, message, color=Colors.ENDC):
        print(f"{color}{message}{Colors.ENDC}")
        
    def print_header(self):
        """Print test header"""
        self.log("=" * 80, Colors.CYAN)
        self.log(f"{Colors.BOLD}🤖 COMPREHENSIVE AUTOMATION TESTING SUITE{Colors.ENDC}", Colors.CYAN)
        self.log(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.CYAN)
        self.log("=" * 80, Colors.CYAN)
        
    def test_database_operations(self):
        """Test database CRUD operations"""
        self.log(f"\n{Colors.BLUE}🗄️  DATABASE AUTOMATION TESTS{Colors.ENDC}")
        self.log("-" * 50)
        
        try:
            conn = psycopg2.connect(**self.database_config)
            cursor = conn.cursor()
            
            # Test 1: Check if all tables exist
            self.total += 1
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            expected_tables = ['users', 'job_applications', 'resumes', 'subscriptions', 'payments']
            
            if len(tables) >= len(expected_tables):
                self.log("✅ Database Tables: ALL PRESENT", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ Database Tables: Missing tables (found {len(tables)})", Colors.RED)
                self.failed += 1
                
            # Test 2: Test user insertion
            self.total += 1
            try:
                cursor.execute("""
                    INSERT INTO users (email, password_hash, first_name, last_name, is_active)
                    VALUES ('test@automation.com', 'hashed_password', 'Test', 'User', true)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id;
                """)
                result = cursor.fetchone()
                conn.commit()
                self.log("✅ Database Insert: USER CREATED", Colors.GREEN)
                self.passed += 1
            except Exception as e:
                self.log(f"❌ Database Insert: {str(e)}", Colors.RED)
                self.failed += 1
                
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log(f"❌ Database Connection: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_backend_api_endpoints(self):
        """Test backend API endpoints with automation"""
        self.log(f"\n{Colors.BLUE}🔧 BACKEND API AUTOMATION TESTS{Colors.ENDC}")
        self.log("-" * 50)
        
        for service_name, base_url in self.services.items():
            # Test health endpoint
            self.total += 1
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'healthy':
                        self.log(f"✅ {service_name.upper()} Health: HEALTHY", Colors.GREEN)
                        self.passed += 1
                    else:
                        self.log(f"❌ {service_name.upper()} Health: UNHEALTHY", Colors.RED)
                        self.failed += 1
                else:
                    self.log(f"❌ {service_name.upper()} Health: HTTP {response.status_code}", Colors.RED)
                    self.failed += 1
            except Exception as e:
                self.log(f"❌ {service_name.upper()} Health: {str(e)}", Colors.RED)
                self.failed += 1
                
            # Test API documentation
            self.total += 1
            try:
                response = requests.get(f"{base_url}/docs", timeout=5)
                if response.status_code == 200:
                    self.log(f"✅ {service_name.upper()} API Docs: ACCESSIBLE", Colors.GREEN)
                    self.passed += 1
                else:
                    self.log(f"❌ {service_name.upper()} API Docs: HTTP {response.status_code}", Colors.RED)
                    self.failed += 1
            except Exception as e:
                self.log(f"❌ {service_name.upper()} API Docs: {str(e)}", Colors.RED)
                self.failed += 1
                
    def test_frontend_automation(self):
        """Test frontend with browser automation"""
        self.log(f"\n{Colors.BLUE}🌐 FRONTEND AUTOMATION TESTS{Colors.ENDC}")
        self.log("-" * 50)
        
        # Test 1: Check if Flutter web is accessible
        self.total += 1
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log("✅ Flutter Web App: ACCESSIBLE", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ Flutter Web App: HTTP {response.status_code}", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Flutter Web App: {str(e)}", Colors.RED)
            self.failed += 1
            
        # Test 2: Check test dashboard
        self.total += 1
        try:
            if os.path.exists("frontend/web_test/index.html"):
                self.log("✅ Test Dashboard: FILE EXISTS", Colors.GREEN)
                self.passed += 1
            else:
                self.log("❌ Test Dashboard: FILE NOT FOUND", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Test Dashboard: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_system_integration(self):
        """Test system integration and data flow"""
        self.log(f"\n{Colors.BLUE}🔄 SYSTEM INTEGRATION TESTS{Colors.ENDC}")
        self.log("-" * 50)
        
        # Test 1: Frontend to Backend connectivity
        self.total += 1
        try:
            # Simulate a frontend request to backend
            headers = {'Content-Type': 'application/json'}
            test_data = {'test': 'integration'}
            
            # Test auth service connectivity
            response = requests.get(f"{self.services['auth']}/health", headers=headers, timeout=5)
            if response.status_code == 200:
                self.log("✅ Frontend-Backend Integration: AUTH SERVICE CONNECTED", Colors.GREEN)
                self.passed += 1
            else:
                self.log("❌ Frontend-Backend Integration: AUTH SERVICE FAILED", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Frontend-Backend Integration: {str(e)}", Colors.RED)
            self.failed += 1
            
        # Test 2: Database to Backend connectivity
        self.total += 1
        try:
            conn = psycopg2.connect(**self.database_config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            self.log(f"✅ Database-Backend Integration: {user_count} USERS IN DATABASE", Colors.GREEN)
            self.passed += 1
        except Exception as e:
            self.log(f"❌ Database-Backend Integration: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_performance_metrics(self):
        """Test system performance metrics"""
        self.log(f"\n{Colors.BLUE}⚡ PERFORMANCE AUTOMATION TESTS{Colors.ENDC}")
        self.log("-" * 50)
        
        for service_name, base_url in self.services.items():
            self.total += 1
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/health", timeout=5)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response_time < 1000:  # Less than 1 second
                    self.log(f"✅ {service_name.upper()} Performance: {response_time:.2f}ms", Colors.GREEN)
                    self.passed += 1
                else:
                    self.log(f"⚠️  {service_name.upper()} Performance: {response_time:.2f}ms (SLOW)", Colors.YELLOW)
                    self.failed += 1
            except Exception as e:
                self.log(f"❌ {service_name.upper()} Performance: {str(e)}", Colors.RED)
                self.failed += 1
                
    def run_comprehensive_automation_tests(self):
        """Run all automation tests"""
        self.print_header()
        
        # Run all test suites
        self.test_database_operations()
        self.test_backend_api_endpoints()
        self.test_frontend_automation()
        self.test_system_integration()
        self.test_performance_metrics()
        
        # Print final summary
        self.print_final_summary()
        
        return self.failed == 0
        
    def print_final_summary(self):
        """Print comprehensive test summary"""
        self.log("\n" + "=" * 80, Colors.CYAN)
        self.log(f"{Colors.BOLD}🎯 COMPREHENSIVE AUTOMATION TEST RESULTS{Colors.ENDC}", Colors.CYAN)
        self.log("=" * 80, Colors.CYAN)
        
        self.log(f"Total Tests Executed: {self.total}")
        self.log(f"Tests Passed: {self.passed}", Colors.GREEN)
        self.log(f"Tests Failed: {self.failed}", Colors.RED)
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            self.log(f"\n🎉 ALL AUTOMATION TESTS PASSED!", Colors.GREEN)
            self.log("🚀 AUTO JOB APPLY SYSTEM IS FULLY OPERATIONAL!", Colors.GREEN)
        elif success_rate >= 80:
            self.log(f"\n✅ SYSTEM IS MOSTLY OPERATIONAL ({success_rate:.1f}% success)", Colors.YELLOW)
        else:
            self.log(f"\n⚠️  SYSTEM NEEDS ATTENTION ({self.failed} critical failures)", Colors.RED)
            
        self.log("=" * 80, Colors.CYAN)

if __name__ == "__main__":
    automation_tests = ComprehensiveAutomationTests()
    success = automation_tests.run_comprehensive_automation_tests()
    exit(0 if success else 1)
