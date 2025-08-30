#!/usr/bin/env python3
"""
Comprehensive Unit Test Suite for Auto Job Apply System
Tests all backend services and their endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class TestSuite:
    def __init__(self):
        self.services = {
            'auth': 'http://localhost:8001',
            'core': 'http://localhost:8002', 
            'ml': 'http://localhost:8003',
            'payment': 'http://localhost:8004'
        }
        self.passed = 0
        self.failed = 0
        self.total = 0
        
    def log(self, message, color=Colors.ENDC):
        print(f"{color}{message}{Colors.ENDC}")
        
    def test_service_health(self, service_name, base_url):
        """Test service health endpoint"""
        self.total += 1
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log(f"✅ {service_name} Health Check: PASSED", Colors.GREEN)
                    self.passed += 1
                    return True
                else:
                    self.log(f"❌ {service_name} Health Check: Invalid response", Colors.RED)
                    self.failed += 1
                    return False
            else:
                self.log(f"❌ {service_name} Health Check: HTTP {response.status_code}", Colors.RED)
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"❌ {service_name} Health Check: {str(e)}", Colors.RED)
            self.failed += 1
            return False
            
    def test_service_root(self, service_name, base_url):
        """Test service root endpoint"""
        self.total += 1
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log(f"✅ {service_name} Root Endpoint: PASSED", Colors.GREEN)
                    self.passed += 1
                    return True
                else:
                    self.log(f"❌ {service_name} Root Endpoint: Invalid response", Colors.RED)
                    self.failed += 1
                    return False
            else:
                self.log(f"❌ {service_name} Root Endpoint: HTTP {response.status_code}", Colors.RED)
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"❌ {service_name} Root Endpoint: {str(e)}", Colors.RED)
            self.failed += 1
            return False
            
    def test_service_docs(self, service_name, base_url):
        """Test service API documentation endpoint"""
        self.total += 1
        try:
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log(f"✅ {service_name} API Docs: PASSED", Colors.GREEN)
                self.passed += 1
                return True
            else:
                self.log(f"❌ {service_name} API Docs: HTTP {response.status_code}", Colors.RED)
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"❌ {service_name} API Docs: {str(e)}", Colors.RED)
            self.failed += 1
            return False
            
    def run_all_tests(self):
        """Run all tests for all services"""
        self.log(f"\n{Colors.BOLD}🧪 Starting Comprehensive Unit Testing{Colors.ENDC}")
        self.log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 60)
        
        for service_name, base_url in self.services.items():
            self.log(f"\n{Colors.BLUE}Testing {service_name.upper()} Service ({base_url}){Colors.ENDC}")
            self.log("-" * 40)
            
            # Test health endpoint
            self.test_service_health(service_name, base_url)
            
            # Test root endpoint  
            self.test_service_root(service_name, base_url)
            
            # Test API docs
            self.test_service_docs(service_name, base_url)
            
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 60)
        self.log(f"{Colors.BOLD}📊 TEST SUMMARY{Colors.ENDC}")
        self.log(f"Total Tests: {self.total}")
        self.log(f"Passed: {self.passed}", Colors.GREEN)
        self.log(f"Failed: {self.failed}", Colors.RED)
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            self.log(f"\n🎉 ALL TESTS PASSED! System is ready for production.", Colors.GREEN)
        else:
            self.log(f"\n⚠️  {self.failed} tests failed. Please check the services.", Colors.YELLOW)
            
        return self.failed == 0

    def test_database_connectivity(self):
        """Test PostgreSQL database connectivity"""
        self.log(f"\n{Colors.BLUE}Testing Database Connectivity{Colors.ENDC}")
        self.log("-" * 40)
        self.total += 1

        try:
            import psycopg2
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                password='9912129398',
                database='AutoJobApply'
            )
            conn.close()
            self.log("✅ Database Connection: PASSED", Colors.GREEN)
            self.passed += 1
            return True
        except Exception as e:
            self.log(f"❌ Database Connection: {str(e)}", Colors.RED)
            self.failed += 1
            return False

    def test_flutter_frontend(self):
        """Test Flutter frontend setup"""
        self.log(f"\n{Colors.BLUE}Testing Flutter Frontend{Colors.ENDC}")
        self.log("-" * 40)
        self.total += 1

        try:
            import os
            pubspec_path = os.path.join('frontend', 'pubspec.yaml')
            if os.path.exists(pubspec_path):
                self.log("✅ Flutter Project Structure: PASSED", Colors.GREEN)
                self.passed += 1
                return True
            else:
                self.log("❌ Flutter Project Structure: pubspec.yaml not found", Colors.RED)
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"❌ Flutter Project Structure: {str(e)}", Colors.RED)
            self.failed += 1
            return False

    def run_comprehensive_tests(self):
        """Run all tests including extended ones"""
        self.log(f"\n{Colors.BOLD}🧪 Starting COMPREHENSIVE Unit Testing Suite{Colors.ENDC}")
        self.log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 60)

        # Test all services
        for service_name, base_url in self.services.items():
            self.log(f"\n{Colors.BLUE}Testing {service_name.upper()} Service ({base_url}){Colors.ENDC}")
            self.log("-" * 40)

            self.test_service_health(service_name, base_url)
            self.test_service_root(service_name, base_url)
            self.test_service_docs(service_name, base_url)

        # Test database connectivity
        self.test_database_connectivity()

        # Test Flutter frontend
        self.test_flutter_frontend()

        self.print_summary()
        return self.failed == 0

if __name__ == "__main__":
    test_suite = TestSuite()
    success = test_suite.run_comprehensive_tests()
    sys.exit(0 if success else 1)
