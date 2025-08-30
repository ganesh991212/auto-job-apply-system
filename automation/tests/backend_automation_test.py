#!/usr/bin/env python3
"""
Backend Automation Tests for Auto Job Apply System
Comprehensive API testing with screenshot validation for API responses
"""

import pytest
import requests
import json
import time
import psycopg2
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BackendTestConfig:
    """Configuration for backend tests"""
    BASE_URL = "http://localhost"
    SERVICES = {
        'auth': 8001,
        'core': 8002,
        'ml': 8003,
        'payment': 8004
    }
    DATABASE_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': '9912129398',
        'database': 'AutoJobApply'
    }
    SCREENSHOT_DIR = "automation/screenshots/api_responses"
    TIMEOUT = 10

class APITestHelper:
    """Helper class for API testing and screenshot capture"""
    
    @staticmethod
    def save_response_screenshot(response_data: Dict, endpoint: str, test_name: str):
        """Save API response as JSON screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{endpoint}_{test_name}_{timestamp}.json"
        
        # Create directory if it doesn't exist
        os.makedirs(BackendTestConfig.SCREENSHOT_DIR, exist_ok=True)
        
        filepath = os.path.join(BackendTestConfig.SCREENSHOT_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(response_data, f, indent=2, default=str)
        
        print(f"📸 API Response saved: {filepath}")
        return filepath
    
    @staticmethod
    def get_service_url(service: str) -> str:
        """Get full URL for a service"""
        port = BackendTestConfig.SERVICES.get(service)
        if not port:
            raise ValueError(f"Unknown service: {service}")
        return f"{BackendTestConfig.BASE_URL}:{port}"

class TestAuthService:
    """Test cases for Authentication Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = APITestHelper.get_service_url('auth')
        self.test_user = {
            'email': 'automation_test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Automation',
            'last_name': 'Test'
        }
    
    def test_health_endpoint(self):
        """Test auth service health endpoint"""
        response = requests.get(f"{self.base_url}/health", timeout=BackendTestConfig.TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        
        # Save response screenshot
        APITestHelper.save_response_screenshot(data, 'auth_health', 'success')
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        response = requests.post(
            f"{self.base_url}/register",
            json=self.test_user,
            timeout=BackendTestConfig.TIMEOUT
        )
        
        # Save response regardless of status for debugging
        if response.status_code in [200, 201]:
            data = response.json()
            APITestHelper.save_response_screenshot(data, 'auth_register', 'success')
            assert 'user_id' in data or 'id' in data
        else:
            error_data = {'status_code': response.status_code, 'error': response.text}
            APITestHelper.save_response_screenshot(error_data, 'auth_register', 'error')
    
    def test_user_login(self):
        """Test user login endpoint"""
        login_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password']
        }
        
        response = requests.post(
            f"{self.base_url}/login",
            json=login_data,
            timeout=BackendTestConfig.TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            APITestHelper.save_response_screenshot(data, 'auth_login', 'success')
            assert 'access_token' in data or 'token' in data
        else:
            error_data = {'status_code': response.status_code, 'error': response.text}
            APITestHelper.save_response_screenshot(error_data, 'auth_login', 'error')

class TestCoreService:
    """Test cases for Core Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = APITestHelper.get_service_url('core')
    
    def test_health_endpoint(self):
        """Test core service health endpoint"""
        response = requests.get(f"{self.base_url}/health", timeout=BackendTestConfig.TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        
        APITestHelper.save_response_screenshot(data, 'core_health', 'success')
    
    def test_jobs_endpoint(self):
        """Test jobs listing endpoint"""
        response = requests.get(f"{self.base_url}/jobs", timeout=BackendTestConfig.TIMEOUT)
        
        # Save response regardless of status
        if response.status_code == 200:
            data = response.json()
            APITestHelper.save_response_screenshot(data, 'core_jobs', 'success')
        else:
            error_data = {'status_code': response.status_code, 'error': response.text}
            APITestHelper.save_response_screenshot(error_data, 'core_jobs', 'error')

class TestMLService:
    """Test cases for ML Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = APITestHelper.get_service_url('ml')
    
    def test_health_endpoint(self):
        """Test ML service health endpoint"""
        response = requests.get(f"{self.base_url}/health", timeout=BackendTestConfig.TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        
        APITestHelper.save_response_screenshot(data, 'ml_health', 'success')
    
    def test_resume_analysis(self):
        """Test resume analysis endpoint"""
        test_resume = {
            'resume_text': 'John Doe\nSoftware Engineer\n5 years experience in Python, JavaScript, React'
        }
        
        response = requests.post(
            f"{self.base_url}/analyze-resume",
            json=test_resume,
            timeout=BackendTestConfig.TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            APITestHelper.save_response_screenshot(data, 'ml_resume_analysis', 'success')
        else:
            error_data = {'status_code': response.status_code, 'error': response.text}
            APITestHelper.save_response_screenshot(error_data, 'ml_resume_analysis', 'error')

class TestPaymentService:
    """Test cases for Payment Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = APITestHelper.get_service_url('payment')
    
    def test_health_endpoint(self):
        """Test payment service health endpoint"""
        response = requests.get(f"{self.base_url}/health", timeout=BackendTestConfig.TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        
        APITestHelper.save_response_screenshot(data, 'payment_health', 'success')
    
    def test_subscriptions_endpoint(self):
        """Test subscriptions endpoint"""
        response = requests.get(f"{self.base_url}/subscriptions", timeout=BackendTestConfig.TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            APITestHelper.save_response_screenshot(data, 'payment_subscriptions', 'success')
        else:
            error_data = {'status_code': response.status_code, 'error': response.text}
            APITestHelper.save_response_screenshot(error_data, 'payment_subscriptions', 'error')

class TestDatabaseOperations:
    """Test database operations and data integrity"""
    
    def setup_method(self):
        """Setup database connection"""
        self.conn = psycopg2.connect(**BackendTestConfig.DATABASE_CONFIG)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup database connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def test_database_connection(self):
        """Test database connectivity"""
        self.cursor.execute("SELECT version();")
        version = self.cursor.fetchone()[0]
        
        db_info = {
            'status': 'connected',
            'version': version,
            'timestamp': datetime.now().isoformat()
        }
        
        APITestHelper.save_response_screenshot(db_info, 'database_connection', 'success')
        assert 'PostgreSQL' in version
    
    def test_user_table_operations(self):
        """Test user table CRUD operations"""
        # Test insert
        test_user_data = {
            'email': 'db_test@automation.com',
            'password_hash': 'hashed_password_123',
            'first_name': 'DB',
            'last_name': 'Test',
            'is_active': True
        }
        
        try:
            self.cursor.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, is_active)
                VALUES (%(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(is_active)s)
                ON CONFLICT (email) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name
                RETURNING id, email, created_at;
            """, test_user_data)
            
            result = self.cursor.fetchone()
            self.conn.commit()
            
            db_result = {
                'operation': 'user_insert',
                'user_id': result[0],
                'email': result[1],
                'created_at': result[2].isoformat(),
                'status': 'success'
            }
            
            APITestHelper.save_response_screenshot(db_result, 'database_user_ops', 'insert_success')
            
        except Exception as e:
            error_data = {
                'operation': 'user_insert',
                'error': str(e),
                'status': 'failed'
            }
            APITestHelper.save_response_screenshot(error_data, 'database_user_ops', 'insert_error')
            raise

class TestPerformanceMetrics:
    """Test system performance and response times"""
    
    def test_service_response_times(self):
        """Test response times for all services"""
        performance_data = {}
        
        for service_name, port in BackendTestConfig.SERVICES.items():
            url = f"{BackendTestConfig.BASE_URL}:{port}/health"
            
            start_time = time.time()
            try:
                response = requests.get(url, timeout=BackendTestConfig.TIMEOUT)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                performance_data[service_name] = {
                    'response_time_ms': round(response_time, 2),
                    'status_code': response.status_code,
                    'status': 'success' if response.status_code == 200 else 'error'
                }
                
            except Exception as e:
                performance_data[service_name] = {
                    'response_time_ms': None,
                    'status_code': None,
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Add overall metrics
        successful_services = [s for s in performance_data.values() if s['status'] == 'success']
        if successful_services:
            avg_response_time = sum(s['response_time_ms'] for s in successful_services) / len(successful_services)
            performance_data['overall_metrics'] = {
                'average_response_time_ms': round(avg_response_time, 2),
                'successful_services': len(successful_services),
                'total_services': len(BackendTestConfig.SERVICES),
                'success_rate': round(len(successful_services) / len(BackendTestConfig.SERVICES) * 100, 2)
            }
        
        APITestHelper.save_response_screenshot(performance_data, 'performance_metrics', 'complete')
        
        # Assert performance criteria
        for service_name, metrics in performance_data.items():
            if service_name != 'overall_metrics' and metrics['status'] == 'success':
                assert metrics['response_time_ms'] < 5000, f"{service_name} response time too slow: {metrics['response_time_ms']}ms"

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
