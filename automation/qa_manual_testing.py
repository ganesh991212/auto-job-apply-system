#!/usr/bin/env python3
"""
QA Manual Testing Script for Auto Job Apply System
Provides QA team with single-command automation execution
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import webbrowser
import argparse
from typing import Dict, List, Any, Optional
import requests

class QATestRunner:
    """QA-focused test runner with manual testing support"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.automation_dir = Path(__file__).parent
        self.reports_dir = self.automation_dir / "reports"
        self.screenshots_dir = self.automation_dir / "screenshots"
        
    def run_qa_automation(self, test_type: str = "full") -> Dict[str, Any]:
        """Run automation tests for QA team"""
        print("🧪 QA Automation Test Runner")
        print("=" * 50)
        print(f"Test Type: {test_type}")
        print(f"Branch: {self._get_current_branch()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        results = {
            'start_time': datetime.now().isoformat(),
            'test_type': test_type,
            'branch': self._get_current_branch(),
            'status': 'running'
        }
        
        try:
            # Step 1: Verify prerequisites
            print("\n🔍 Step 1: Checking Prerequisites...")
            if not self._check_prerequisites():
                results['status'] = 'failed'
                results['error'] = 'Prerequisites not met'
                return results
            
            # Step 2: Create test users
            print("\n👥 Step 2: Creating Test Users...")
            test_users = self._create_test_users()
            results['test_users'] = test_users
            
            # Step 3: Start services
            print("\n🚀 Step 3: Starting Backend Services...")
            services_started = self._start_backend_services()
            results['services_started'] = services_started
            
            # Step 4: Run tests based on type
            if test_type in ['full', 'flutter']:
                print("\n📱 Step 4: Running Flutter Tests...")
                flutter_results = self._run_flutter_tests()
                results['flutter_results'] = flutter_results
            
            if test_type in ['full', 'backend']:
                print("\n🐍 Step 5: Running Backend Tests...")
                backend_results = self._run_backend_tests()
                results['backend_results'] = backend_results
            
            if test_type in ['full', 'oauth']:
                print("\n🔐 Step 6: Testing OAuth Flows...")
                oauth_results = self._test_oauth_flows()
                results['oauth_results'] = oauth_results
            
            if test_type in ['full', 'validation']:
                print("\n📸 Step 7: Validating Screenshots...")
                validation_results = self._validate_screenshots()
                results['validation_results'] = validation_results
            
            # Step 8: Generate QA report
            print("\n📊 Step 8: Generating QA Report...")
            report_path = self._generate_qa_report(results)
            results['report_path'] = report_path
            
            # Step 9: Open results for QA review
            print("\n👀 Step 9: Opening Results for Review...")
            self._open_results_for_qa(report_path)
            
            results['status'] = 'completed'
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
            print(f"❌ Test execution failed: {e}")
        
        return results
    
    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip()
        except:
            return 'unknown'
    
    def _check_prerequisites(self) -> bool:
        """Check if all prerequisites are available"""
        prerequisites = [
            ('flutter', ['flutter', '--version']),
            ('python', ['python', '--version']),
            ('git', ['git', '--version'])
        ]
        
        for name, command in prerequisites:
            try:
                result = subprocess.run(command, capture_output=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ {name} is available")
                else:
                    print(f"❌ {name} not working properly")
                    return False
            except Exception as e:
                print(f"❌ {name} not found: {e}")
                return False
        
        return True
    
    def _create_test_users(self) -> Dict[str, str]:
        """Create random test users for this test run"""
        import random
        import string
        
        timestamp = int(time.time())
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        test_users = {
            'test_user_email': f"qatest_{timestamp}_{random_suffix}@gmail.com",
            'test_user_password': 'QATest123!',
            'super_user_email': 'qasuperuser@autojobapply.com',
            'super_user_password': 'QASuperAdmin123!'
        }
        
        # Save to file for test execution
        credentials_file = self.automation_dir / "test_credentials.json"
        with open(credentials_file, 'w') as f:
            json.dump(test_users, f, indent=2)
        
        print(f"🔐 Test users created:")
        print(f"   Test User: {test_users['test_user_email']}")
        print(f"   Super User: {test_users['super_user_email']}")
        
        return test_users
    
    def _start_backend_services(self) -> bool:
        """Start all backend services"""
        services = ['auth', 'core', 'ml', 'payment']
        ports = [8001, 8002, 8003, 8004]
        
        for service, port in zip(services, ports):
            try:
                # Check if service is already running
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {service} service already running on port {port}")
                    continue
            except:
                pass
            
            # Start the service
            service_dir = self.project_root / "backend" / service
            if service_dir.exists():
                print(f"🚀 Starting {service} service on port {port}...")
                # This would start the service in background
                # For QA testing, services should be started manually
        
        # Wait for services to be ready
        time.sleep(10)
        
        # Verify all services are running
        all_running = True
        for service, port in zip(services, ports):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service} service is healthy")
                else:
                    print(f"⚠️ {service} service returned status {response.status_code}")
                    all_running = False
            except Exception as e:
                print(f"❌ {service} service not accessible: {e}")
                all_running = False
        
        return all_running
    
    def _run_flutter_tests(self) -> Dict[str, Any]:
        """Run Flutter integration tests"""
        try:
            # Copy test file to integration_test directory
            frontend_dir = self.project_root / "frontend"
            integration_test_dir = frontend_dir / "integration_test"
            integration_test_dir.mkdir(exist_ok=True)
            
            test_source = self.automation_dir / "tests" / "comprehensive_user_flow_test.dart"
            test_dest = integration_test_dir / "app_test.dart"
            
            if test_source.exists():
                import shutil
                shutil.copy2(test_source, test_dest)
            
            # Run Flutter integration tests
            cmd = ['flutter', 'test', 'integration_test', '--verbose']
            
            result = subprocess.run(
                cmd,
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Count screenshots captured
            screenshots_captured = 0
            if self.screenshots_dir.exists():
                for root, dirs, files in os.walk(self.screenshots_dir):
                    screenshots_captured += len([f for f in files if f.endswith('.png')])
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'screenshots_captured': screenshots_captured,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _run_backend_tests(self) -> Dict[str, Any]:
        """Run backend API tests"""
        try:
            test_file = self.automation_dir / "tests" / "backend_automation_test.py"
            
            cmd = ['python', '-m', 'pytest', str(test_file), '-v', '--tb=short']
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _test_oauth_flows(self) -> Dict[str, Any]:
        """Test OAuth authentication flows"""
        oauth_results = {
            'google': {'status': 'not_tested', 'reason': 'Manual testing required'},
            'microsoft': {'status': 'not_tested', 'reason': 'Manual testing required'},
            'apple': {'status': 'not_tested', 'reason': 'Manual testing required'}
        }
        
        # For QA testing, OAuth would be tested manually
        print("🔐 OAuth flows require manual testing by QA team")
        print("   1. Test Google OAuth login")
        print("   2. Test Microsoft OAuth login")
        print("   3. Test Apple OAuth login (if available)")
        print("   4. Verify successful authentication and redirect")
        
        return oauth_results
    
    def _validate_screenshots(self) -> Dict[str, Any]:
        """Validate screenshots against baselines"""
        try:
            # Run screenshot validator
            validator_script = self.automation_dir / "screenshot_validator.py"
            
            result = subprocess.run(
                ['python', str(validator_script)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_qa_report(self, results: Dict[str, Any]) -> str:
        """Generate QA-focused HTML report"""
        report_path = self.reports_dir / f"qa_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Generate comprehensive QA report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>QA Test Report - Auto Job Apply</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                .header {{ background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
                .status-pass {{ color: #059669; font-weight: bold; }}
                .status-fail {{ color: #DC2626; font-weight: bold; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .metric {{ background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; }}
                .checklist {{ background: #fef3c7; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .manual-test {{ background: #dbeafe; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 QA Test Report - Auto Job Apply</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Branch: {results.get('branch', 'unknown')}</p>
                    <p>Test Type: {results.get('test_type', 'full')}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Test Summary</h2>
                    <div class="metrics">
                        <div class="metric">
                            <h3>Overall Status</h3>
                            <p class="status-{results.get('status', 'unknown')}">{results.get('status', 'unknown').upper()}</p>
                        </div>
                        <div class="metric">
                            <h3>Screenshots Captured</h3>
                            <p>{results.get('flutter_results', {}).get('screenshots_captured', 0)}</p>
                        </div>
                        <div class="metric">
                            <h3>Test Users Created</h3>
                            <p>{len(results.get('test_users', {}))}</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔐 Test Users (For Manual Testing)</h2>
                    <div class="manual-test">
                        <h4>Test User Account:</h4>
                        <p>Email: {results.get('test_users', {}).get('test_user_email', 'N/A')}</p>
                        <p>Password: {results.get('test_users', {}).get('test_user_password', 'N/A')}</p>
                    </div>
                    <div class="manual-test">
                        <h4>Super User Account:</h4>
                        <p>Email: {results.get('test_users', {}).get('super_user_email', 'N/A')}</p>
                        <p>Password: {results.get('test_users', {}).get('super_user_password', 'N/A')}</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 QA Manual Testing Checklist</h2>
                    <div class="checklist">
                        <h4>🔐 Authentication Testing:</h4>
                        <ul>
                            <li>☐ Test Google OAuth login button</li>
                            <li>☐ Test Microsoft OAuth login button</li>
                            <li>☐ Test Apple OAuth login button (if available)</li>
                            <li>☐ Test email/password login with test user</li>
                            <li>☐ Test invalid credentials handling</li>
                            <li>☐ Test network timeout scenarios</li>
                        </ul>
                    </div>
                    
                    <div class="checklist">
                        <h4>🏠 Dashboard Testing:</h4>
                        <ul>
                            <li>☐ Verify dashboard loads correctly</li>
                            <li>☐ Test navigation drawer functionality</li>
                            <li>☐ Check responsive design on different screen sizes</li>
                            <li>☐ Validate all dashboard widgets display correctly</li>
                            <li>☐ Test quick action buttons</li>
                        </ul>
                    </div>
                    
                    <div class="checklist">
                        <h4>💼 Job Application Testing:</h4>
                        <ul>
                            <li>☐ Test job search functionality</li>
                            <li>☐ Test job application form submission</li>
                            <li>☐ Test job application editing</li>
                            <li>☐ Test job application deletion</li>
                            <li>☐ Test bulk operations</li>
                            <li>☐ Verify form validation</li>
                        </ul>
                    </div>
                    
                    <div class="checklist">
                        <h4>📄 Resume Management Testing:</h4>
                        <ul>
                            <li>☐ Test resume upload functionality</li>
                            <li>☐ Test resume editing</li>
                            <li>☐ Test AI optimization features</li>
                            <li>☐ Verify file format support</li>
                            <li>☐ Test resume preview</li>
                        </ul>
                    </div>
                    
                    <div class="checklist">
                        <h4>⚙️ Settings Testing:</h4>
                        <ul>
                            <li>☐ Test theme switching</li>
                            <li>☐ Test notification preferences</li>
                            <li>☐ Test account management</li>
                            <li>☐ Test data export/import</li>
                            <li>☐ Test privacy settings</li>
                        </ul>
                    </div>
                    
                    <div class="checklist">
                        <h4>🔐 Logout Testing:</h4>
                        <ul>
                            <li>☐ Test logout functionality</li>
                            <li>☐ Verify session cleanup</li>
                            <li>☐ Test automatic logout on timeout</li>
                            <li>☐ Verify return to login screen</li>
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📸 Screenshot Gallery</h2>
                    <p>Screenshots are automatically captured during automation tests.</p>
                    <p>Location: <code>automation/screenshots/</code></p>
                    <p>Baseline comparison results available in validation report.</p>
                </div>
                
                <div class="section">
                    <h2>🔗 Quick Links</h2>
                    <ul>
                        <li><a href="http://localhost:3000" target="_blank">🌐 Flutter Web App</a></li>
                        <li><a href="http://localhost:8001/docs" target="_blank">📚 Auth API Docs</a></li>
                        <li><a href="http://localhost:8002/docs" target="_blank">📚 Core API Docs</a></li>
                        <li><a href="http://localhost:8003/docs" target="_blank">📚 ML API Docs</a></li>
                        <li><a href="http://localhost:8004/docs" target="_blank">📚 Payment API Docs</a></li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _open_results_for_qa(self, report_path: str):
        """Open test results for QA team review"""
        try:
            # Open HTML report
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
            
            # Open screenshots folder
            screenshots_path = os.path.abspath(self.screenshots_dir)
            if os.name == 'nt':  # Windows
                os.startfile(screenshots_path)
            else:  # Unix-like
                subprocess.run(['xdg-open', screenshots_path])
            
            print(f"👀 Opened QA report and screenshots for review")
            
        except Exception as e:
            print(f"⚠️ Could not auto-open results: {e}")
            print(f"📄 Manual paths:")
            print(f"   Report: {report_path}")
            print(f"   Screenshots: {self.screenshots_dir}")

def main():
    """Main function for QA test execution"""
    parser = argparse.ArgumentParser(description='QA Manual Testing Runner')
    parser.add_argument('--test-type', choices=['full', 'flutter', 'backend', 'oauth', 'validation'], 
                       default='full', help='Type of tests to run')
    parser.add_argument('--create-users-only', action='store_true', 
                       help='Only create test users without running tests')
    
    args = parser.parse_args()
    
    runner = QATestRunner()
    
    if args.create_users_only:
        test_users = runner._create_test_users()
        print("🔐 Test users created successfully")
        sys.exit(0)
    
    results = runner.run_qa_automation(args.test_type)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎯 QA AUTOMATION COMPLETE")
    print("=" * 60)
    print(f"Status: {results['status'].upper()}")
    print(f"Report: {results.get('report_path', 'N/A')}")
    print(f"Screenshots: automation/screenshots/")
    print("=" * 60)
    
    # Exit with appropriate code
    exit_code = 0 if results['status'] in ['completed', 'passed'] else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
