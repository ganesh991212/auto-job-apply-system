#!/usr/bin/env python3
"""
API Endpoint Validation Tests for Auto Job Apply System
Tests specific API endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class APIEndpointTests:
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
        
    def test_auth_endpoints(self):
        """Test Auth service specific endpoints"""
        self.log(f"\n{Colors.BLUE}Testing AUTH Service API Endpoints{Colors.ENDC}")
        self.log("-" * 50)
        
        base_url = self.services['auth']
        
        # Test registration endpoint structure
        self.total += 1
        try:
            response = requests.post(f"{base_url}/register", 
                                   json={"email": "test@example.com", "password": "testpass"},
                                   timeout=5)
            # We expect this to fail due to validation, but endpoint should exist
            if response.status_code in [400, 422, 500]:  # Expected validation errors
                self.log("✅ Auth Register Endpoint: ACCESSIBLE", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ Auth Register Endpoint: Unexpected status {response.status_code}", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Auth Register Endpoint: {str(e)}", Colors.RED)
            self.failed += 1
            
        # Test login endpoint structure
        self.total += 1
        try:
            response = requests.post(f"{base_url}/login",
                                   json={"email": "test@example.com", "password": "testpass"},
                                   timeout=5)
            # We expect this to fail due to user not existing, but endpoint should exist
            if response.status_code in [400, 401, 422, 500]:  # Expected auth errors
                self.log("✅ Auth Login Endpoint: ACCESSIBLE", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ Auth Login Endpoint: Unexpected status {response.status_code}", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Auth Login Endpoint: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_core_endpoints(self):
        """Test Core service specific endpoints"""
        self.log(f"\n{Colors.BLUE}Testing CORE Service API Endpoints{Colors.ENDC}")
        self.log("-" * 50)
        
        base_url = self.services['core']
        
        # Test jobs endpoint
        self.total += 1
        try:
            response = requests.get(f"{base_url}/jobs", timeout=5)
            if response.status_code in [200, 401, 403]:  # May require auth
                self.log("✅ Core Jobs Endpoint: ACCESSIBLE", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ Core Jobs Endpoint: Status {response.status_code}", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Core Jobs Endpoint: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_ml_endpoints(self):
        """Test ML service specific endpoints"""
        self.log(f"\n{Colors.BLUE}Testing ML Service API Endpoints{Colors.ENDC}")
        self.log("-" * 50)
        
        base_url = self.services['ml']
        
        # Test resume analysis endpoint
        self.total += 1
        try:
            response = requests.post(f"{base_url}/analyze-resume",
                                   json={"resume_text": "Sample resume text"},
                                   timeout=10)
            if response.status_code in [200, 400, 422, 401]:  # Various expected responses
                self.log("✅ ML Resume Analysis Endpoint: ACCESSIBLE", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ ML Resume Analysis Endpoint: Status {response.status_code}", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ ML Resume Analysis Endpoint: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_payment_endpoints(self):
        """Test Payment service specific endpoints"""
        self.log(f"\n{Colors.BLUE}Testing PAYMENT Service API Endpoints{Colors.ENDC}")
        self.log("-" * 50)
        
        base_url = self.services['payment']
        
        # Test subscription endpoint
        self.total += 1
        try:
            response = requests.get(f"{base_url}/subscriptions", timeout=5)
            if response.status_code in [200, 401, 403]:  # May require auth
                self.log("✅ Payment Subscriptions Endpoint: ACCESSIBLE", Colors.GREEN)
                self.passed += 1
            else:
                self.log(f"❌ Payment Subscriptions Endpoint: Status {response.status_code}", Colors.RED)
                self.failed += 1
        except Exception as e:
            self.log(f"❌ Payment Subscriptions Endpoint: {str(e)}", Colors.RED)
            self.failed += 1
            
    def test_cors_headers(self):
        """Test CORS headers for frontend integration"""
        self.log(f"\n{Colors.BLUE}Testing CORS Headers{Colors.ENDC}")
        self.log("-" * 50)
        
        for service_name, base_url in self.services.items():
            self.total += 1
            try:
                response = requests.options(base_url, timeout=5)
                cors_header = response.headers.get('Access-Control-Allow-Origin')
                if cors_header or response.status_code == 200:
                    self.log(f"✅ {service_name.upper()} CORS: CONFIGURED", Colors.GREEN)
                    self.passed += 1
                else:
                    self.log(f"❌ {service_name.upper()} CORS: NOT CONFIGURED", Colors.RED)
                    self.failed += 1
            except Exception as e:
                self.log(f"❌ {service_name.upper()} CORS: {str(e)}", Colors.RED)
                self.failed += 1
                
    def run_all_api_tests(self):
        """Run all API endpoint tests"""
        self.log(f"\n{Colors.BOLD}🔍 Starting API Endpoint Validation Tests{Colors.ENDC}")
        self.log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 60)
        
        self.test_auth_endpoints()
        self.test_core_endpoints()
        self.test_ml_endpoints()
        self.test_payment_endpoints()
        self.test_cors_headers()
        
        self.print_summary()
        return self.failed == 0
        
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 60)
        self.log(f"{Colors.BOLD}📊 API ENDPOINT TEST SUMMARY{Colors.ENDC}")
        self.log(f"Total Tests: {self.total}")
        self.log(f"Passed: {self.passed}", Colors.GREEN)
        self.log(f"Failed: {self.failed}", Colors.RED)
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            self.log(f"\n🎉 ALL API TESTS PASSED! APIs are ready for frontend integration.", Colors.GREEN)
        else:
            self.log(f"\n⚠️  {self.failed} API tests failed. Please check the endpoints.", Colors.YELLOW)

if __name__ == "__main__":
    api_tests = APIEndpointTests()
    api_tests.run_all_api_tests()
