#!/usr/bin/env python3
"""
Main Automation Runner for Auto Job Apply System
Orchestrates Flutter integration tests, Python backend tests, and screenshot validation
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List
import argparse
import shutil

class AutomationRunner:
    """Main class to orchestrate all automation tests"""
    
    def __init__(self, config_path: str = None):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.automation_dir = os.path.join(self.project_root, "automation")
        self.config = self.load_config(config_path)
        self.results = {
            'start_time': datetime.now().isoformat(),
            'flutter_tests': {},
            'backend_tests': {},
            'screenshot_validation': {},
            'overall_status': 'running'
        }
    
    def load_config(self, config_path: str = None) -> Dict:
        """Load automation configuration"""
        default_config = {
            'services': {
                'auth': {'port': 8001, 'required': True},
                'core': {'port': 8002, 'required': True},
                'ml': {'port': 8003, 'required': True},
                'payment': {'port': 8004, 'required': True}
            },
            'flutter': {
                'test_timeout': 300,
                'screenshot_delay': 2
            },
            'backend': {
                'test_timeout': 60,
                'retry_count': 3
            },
            'screenshot': {
                'similarity_threshold': 0.95,
                'auto_fix_enabled': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check Flutter installation
        try:
            result = subprocess.run(['flutter', '--version'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print("❌ Flutter not found or not working")
                return False
            print("✅ Flutter is available")
        except Exception as e:
            print(f"❌ Flutter check failed: {e}")
            return False
        
        # Check Python dependencies
        required_packages = ['pytest', 'requests', 'psycopg2', 'opencv-python', 'pillow']
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} is available")
            except ImportError:
                print(f"❌ {package} not found. Install with: pip install {package}")
                return False
        
        # Check if backend services are running
        import requests
        for service_name, service_config in self.config['services'].items():
            if service_config['required']:
                try:
                    url = f"http://localhost:{service_config['port']}/health"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service_name} service is running")
                    else:
                        print(f"⚠️  {service_name} service returned status {response.status_code}")
                except Exception as e:
                    print(f"❌ {service_name} service not accessible: {e}")
                    if service_config['required']:
                        return False
        
        return True
    
    def run_flutter_tests(self) -> Dict:
        """Run Flutter integration tests with screenshot capture"""
        print("\n🧪 Running Flutter Integration Tests...")
        
        flutter_result = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'screenshots_captured': 0,
            'errors': []
        }
        
        try:
            # Change to frontend directory
            frontend_dir = os.path.join(self.project_root, 'frontend')
            
            # Create integration_test directory if it doesn't exist
            integration_test_dir = os.path.join(frontend_dir, 'integration_test')
            os.makedirs(integration_test_dir, exist_ok=True)
            
            # Copy our test file to integration_test directory
            test_source = os.path.join(self.automation_dir, 'tests', 'flutter_integration_test.dart')
            test_dest = os.path.join(integration_test_dir, 'app_test.dart')
            
            if os.path.exists(test_source):
                shutil.copy2(test_source, test_dest)
            
            # Run Flutter integration tests
            cmd = ['flutter', 'test', 'integration_test', '--verbose']
            
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=self.config['flutter']['test_timeout'])
            
            # Parse results
            if process.returncode == 0:
                flutter_result['status'] = 'passed'
                # Count screenshots
                screenshots_dir = os.path.join(self.automation_dir, 'screenshots')
                if os.path.exists(screenshots_dir):
                    for root, dirs, files in os.walk(screenshots_dir):
                        flutter_result['screenshots_captured'] += len([f for f in files if f.endswith('.png')])
            else:
                flutter_result['status'] = 'failed'
                flutter_result['errors'].append(stderr)
            
            flutter_result['stdout'] = stdout
            flutter_result['stderr'] = stderr
            
        except subprocess.TimeoutExpired:
            flutter_result['status'] = 'timeout'
            flutter_result['errors'].append('Flutter tests timed out')
        except Exception as e:
            flutter_result['status'] = 'error'
            flutter_result['errors'].append(str(e))
        
        flutter_result['end_time'] = datetime.now().isoformat()
        self.results['flutter_tests'] = flutter_result
        
        print(f"📱 Flutter tests: {flutter_result['status']}")
        print(f"   Screenshots captured: {flutter_result['screenshots_captured']}")
        
        return flutter_result
    
    def run_backend_tests(self) -> Dict:
        """Run Python backend tests"""
        print("\n🐍 Running Backend Tests...")
        
        backend_result = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'api_responses_captured': 0,
            'errors': []
        }
        
        try:
            # Run pytest on backend tests
            test_file = os.path.join(self.automation_dir, 'tests', 'backend_automation_test.py')
            
            cmd = ['python', '-m', 'pytest', test_file, '-v', '--tb=short', '--json-report', 
                   '--json-report-file=automation/reports/backend_test_results.json']
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=self.config['backend']['test_timeout'])
            
            # Parse results
            if process.returncode == 0:
                backend_result['status'] = 'passed'
            else:
                backend_result['status'] = 'failed'
                backend_result['errors'].append(stderr)
            
            # Count API response screenshots
            api_responses_dir = os.path.join(self.automation_dir, 'screenshots', 'api_responses')
            if os.path.exists(api_responses_dir):
                backend_result['api_responses_captured'] = len([f for f in os.listdir(api_responses_dir) if f.endswith('.json')])
            
            backend_result['stdout'] = stdout
            backend_result['stderr'] = stderr
            
        except subprocess.TimeoutExpired:
            backend_result['status'] = 'timeout'
            backend_result['errors'].append('Backend tests timed out')
        except Exception as e:
            backend_result['status'] = 'error'
            backend_result['errors'].append(str(e))
        
        backend_result['end_time'] = datetime.now().isoformat()
        self.results['backend_tests'] = backend_result
        
        print(f"🔧 Backend tests: {backend_result['status']}")
        print(f"   API responses captured: {backend_result['api_responses_captured']}")
        
        return backend_result
    
    def run_screenshot_validation(self) -> Dict:
        """Run screenshot validation and auto-fixing"""
        print("\n📸 Running Screenshot Validation...")
        
        validation_result = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'total_screenshots': 0,
            'passed': 0,
            'failed': 0,
            'auto_fixed': 0,
            'errors': []
        }
        
        try:
            # Import and run screenshot validator
            sys.path.append(self.automation_dir)
            from screenshot_validator import ScreenshotValidator
            
            validator = ScreenshotValidator()
            
            # Run validation
            validation_report = validator.validate_all_screenshots()
            
            validation_result['total_screenshots'] = validation_report['total_screenshots']
            validation_result['passed'] = validation_report['passed']
            validation_result['failed'] = validation_report['failed']
            
            # If there are failures and auto-fix is enabled, try to fix them
            if validation_report['failed'] > 0 and self.config['screenshot']['auto_fix_enabled']:
                print("🛠️  Auto-fixing UI issues...")
                
                failed_results = [r for r in validation_report['results'] if r['status'] == 'fail']
                ui_issues = validator.identify_ui_issues(failed_results)
                fix_report = validator.auto_fix_ui_issues(ui_issues)
                
                validation_result['auto_fixed'] = fix_report['fixed']
                
                # If fixes were applied, re-run Flutter tests to capture new screenshots
                if fix_report['fixed'] > 0:
                    print("🔄 Re-running Flutter tests after fixes...")
                    self.run_flutter_tests()
                    
                    # Re-validate screenshots
                    validation_report = validator.validate_all_screenshots()
                    validation_result['passed'] = validation_report['passed']
                    validation_result['failed'] = validation_report['failed']
            
            # Generate validation report
            report_path = validator.generate_validation_report()
            validation_result['report_path'] = report_path
            
            validation_result['status'] = 'passed' if validation_report['failed'] == 0 else 'failed'
            
        except Exception as e:
            validation_result['status'] = 'error'
            validation_result['errors'].append(str(e))
        
        validation_result['end_time'] = datetime.now().isoformat()
        self.results['screenshot_validation'] = validation_result
        
        print(f"📊 Screenshot validation: {validation_result['status']}")
        print(f"   Total: {validation_result['total_screenshots']}")
        print(f"   Passed: {validation_result['passed']}")
        print(f"   Failed: {validation_result['failed']}")
        print(f"   Auto-fixed: {validation_result['auto_fixed']}")
        
        return validation_result
    
    def generate_final_report(self) -> str:
        """Generate comprehensive final report"""
        self.results['end_time'] = datetime.now().isoformat()
        
        # Determine overall status
        all_passed = (
            self.results['flutter_tests'].get('status') == 'passed' and
            self.results['backend_tests'].get('status') == 'passed' and
            self.results['screenshot_validation'].get('status') == 'passed'
        )
        
        self.results['overall_status'] = 'passed' if all_passed else 'failed'
        
        # Save results to JSON
        results_path = os.path.join(self.automation_dir, 'reports', f'automation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate HTML report
        html_report = self.generate_html_report()
        
        print(f"\n📄 Final report saved: {results_path}")
        print(f"📄 HTML report saved: {html_report}")
        
        return results_path
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Auto Job Apply - Automation Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                .header {{ text-align: center; background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
                .status-pass {{ color: #059669; font-weight: bold; }}
                .status-fail {{ color: #DC2626; font-weight: bold; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .metric {{ background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; }}
                .metric h3 {{ margin: 0 0 10px 0; color: #374151; }}
                .metric p {{ margin: 0; font-size: 24px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Auto Job Apply - Automation Test Report</h1>
                    <p>Generated: {self.results.get('end_time', 'N/A')}</p>
                    <p class="{'status-pass' if self.results['overall_status'] == 'passed' else 'status-fail'}">
                        Overall Status: {self.results['overall_status'].upper()}
                    </p>
                </div>
                
                <div class="section">
                    <h2>📱 Flutter Integration Tests</h2>
                    <p class="{'status-pass' if self.results['flutter_tests'].get('status') == 'passed' else 'status-fail'}">
                        Status: {self.results['flutter_tests'].get('status', 'N/A').upper()}
                    </p>
                    <div class="metrics">
                        <div class="metric">
                            <h3>Screenshots Captured</h3>
                            <p>{self.results['flutter_tests'].get('screenshots_captured', 0)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🐍 Backend API Tests</h2>
                    <p class="{'status-pass' if self.results['backend_tests'].get('status') == 'passed' else 'status-fail'}">
                        Status: {self.results['backend_tests'].get('status', 'N/A').upper()}
                    </p>
                    <div class="metrics">
                        <div class="metric">
                            <h3>API Responses Captured</h3>
                            <p>{self.results['backend_tests'].get('api_responses_captured', 0)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📸 Screenshot Validation</h2>
                    <p class="{'status-pass' if self.results['screenshot_validation'].get('status') == 'passed' else 'status-fail'}">
                        Status: {self.results['screenshot_validation'].get('status', 'N/A').upper()}
                    </p>
                    <div class="metrics">
                        <div class="metric">
                            <h3>Total Screenshots</h3>
                            <p>{self.results['screenshot_validation'].get('total_screenshots', 0)}</p>
                        </div>
                        <div class="metric">
                            <h3>Passed</h3>
                            <p>{self.results['screenshot_validation'].get('passed', 0)}</p>
                        </div>
                        <div class="metric">
                            <h3>Failed</h3>
                            <p>{self.results['screenshot_validation'].get('failed', 0)}</p>
                        </div>
                        <div class="metric">
                            <h3>Auto-Fixed</h3>
                            <p>{self.results['screenshot_validation'].get('auto_fixed', 0)}</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        report_path = os.path.join(self.automation_dir, 'reports', f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def run_full_automation(self) -> bool:
        """Run complete automation suite"""
        print("🚀 Starting Full Automation Suite...")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Aborting automation.")
            return False
        
        # Run all test suites
        flutter_result = self.run_flutter_tests()
        backend_result = self.run_backend_tests()
        validation_result = self.run_screenshot_validation()
        
        # Generate final report
        self.generate_final_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 AUTOMATION COMPLETE")
        print("=" * 60)
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        print(f"Flutter Tests: {flutter_result.get('status', 'N/A').upper()}")
        print(f"Backend Tests: {backend_result.get('status', 'N/A').upper()}")
        print(f"Screenshot Validation: {validation_result.get('status', 'N/A').upper()}")
        
        return self.results['overall_status'] == 'passed'

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Auto Job Apply Automation Runner')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--flutter-only', action='store_true', help='Run only Flutter tests')
    parser.add_argument('--backend-only', action='store_true', help='Run only backend tests')
    parser.add_argument('--validation-only', action='store_true', help='Run only screenshot validation')
    
    args = parser.parse_args()
    
    runner = AutomationRunner(args.config)
    
    if args.flutter_only:
        result = runner.run_flutter_tests()
        success = result.get('status') == 'passed'
    elif args.backend_only:
        result = runner.run_backend_tests()
        success = result.get('status') == 'passed'
    elif args.validation_only:
        result = runner.run_screenshot_validation()
        success = result.get('status') == 'passed'
    else:
        success = runner.run_full_automation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
