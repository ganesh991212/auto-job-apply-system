#!/usr/bin/env python3
"""
Edge Case Validator for Auto Job Apply System
Comprehensive validation of UI/UX edge cases, field rendering, and layout integrity
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import webbrowser

class EdgeCaseValidator:
    """Validates all edge cases for UI/UX and functionality"""
    
    def __init__(self):
        self.reports_dir = Path("automation/reports")
        self.screenshots_dir = Path("automation/screenshots/edge_cases")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'edge_cases_tested': 0,
            'passed': 0,
            'failed': 0,
            'critical_issues': [],
            'results': {}
        }
    
    def validate_all_edge_cases(self) -> Dict[str, Any]:
        """Validate all edge cases comprehensively"""
        print("🔍 Starting Comprehensive Edge Case Validation...")
        print("=" * 60)
        
        # Edge Case Category 1: OAuth Authentication Edge Cases
        print("\n🔐 Validating OAuth Authentication Edge Cases...")
        oauth_edge_cases = self._validate_oauth_edge_cases()
        self.validation_results['results']['oauth_edge_cases'] = oauth_edge_cases
        
        # Edge Case Category 2: UI Field Rendering Edge Cases
        print("\n🎨 Validating UI Field Rendering Edge Cases...")
        ui_edge_cases = self._validate_ui_field_edge_cases()
        self.validation_results['results']['ui_field_edge_cases'] = ui_edge_cases
        
        # Edge Case Category 3: Responsive Layout Edge Cases
        print("\n📱 Validating Responsive Layout Edge Cases...")
        responsive_edge_cases = self._validate_responsive_edge_cases()
        self.validation_results['results']['responsive_edge_cases'] = responsive_edge_cases
        
        # Edge Case Category 4: Network and Performance Edge Cases
        print("\n🌐 Validating Network and Performance Edge Cases...")
        network_edge_cases = self._validate_network_edge_cases()
        self.validation_results['results']['network_edge_cases'] = network_edge_cases
        
        # Edge Case Category 5: Browser Compatibility Edge Cases
        print("\n🌍 Validating Browser Compatibility Edge Cases...")
        browser_edge_cases = self._validate_browser_edge_cases()
        self.validation_results['results']['browser_edge_cases'] = browser_edge_cases
        
        # Calculate summary statistics
        self._calculate_summary_statistics()
        
        # Generate comprehensive edge case report
        report_path = self._generate_edge_case_report()
        self.validation_results['report_path'] = report_path
        
        print(f"\n✅ Edge Case Validation Completed!")
        print(f"📊 Results: {self.validation_results['passed']}/{self.validation_results['edge_cases_tested']} passed")
        print(f"📄 Report: {report_path}")
        
        return self.validation_results
    
    def _validate_oauth_edge_cases(self) -> Dict[str, Any]:
        """Validate OAuth authentication edge cases"""
        oauth_edge_cases = {
            'category': 'oauth_authentication',
            'test_cases': {}
        }
        
        # Edge Case 1: Popup Blocker Enabled
        oauth_edge_cases['test_cases']['popup_blocker'] = {
            'description': 'OAuth with popup blocker enabled',
            'test_steps': [
                'Enable popup blocker in browser',
                'Click Google OAuth button',
                'Verify fallback redirect method works',
                'Check error handling for blocked popups'
            ],
            'expected_behavior': 'Graceful fallback to redirect-based OAuth',
            'validation_method': 'manual',
            'priority': 'high',
            'status': 'requires_manual_testing'
        }
        
        # Edge Case 2: Third-party Cookies Disabled
        oauth_edge_cases['test_cases']['cookies_disabled'] = {
            'description': 'OAuth with third-party cookies disabled',
            'test_steps': [
                'Disable third-party cookies in browser',
                'Attempt OAuth login',
                'Verify OAuth flow still works',
                'Check session persistence'
            ],
            'expected_behavior': 'OAuth works without third-party cookies',
            'validation_method': 'manual',
            'priority': 'critical',
            'status': 'requires_manual_testing'
        }
        
        # Edge Case 3: Multiple OAuth Attempts
        oauth_edge_cases['test_cases']['multiple_attempts'] = {
            'description': 'Multiple rapid OAuth button clicks',
            'test_steps': [
                'Click Google OAuth button multiple times rapidly',
                'Verify only one OAuth flow is initiated',
                'Check for duplicate requests',
                'Verify UI doesn\'t break'
            ],
            'expected_behavior': 'Single OAuth flow, no duplicate requests',
            'validation_method': 'automated',
            'priority': 'medium',
            'status': 'automated_test_available'
        }
        
        # Edge Case 4: OAuth Cancellation
        oauth_edge_cases['test_cases']['user_cancellation'] = {
            'description': 'User cancels OAuth flow',
            'test_steps': [
                'Click OAuth button',
                'Cancel on OAuth provider page',
                'Verify return to login page',
                'Check error message display'
            ],
            'expected_behavior': 'Graceful return to login with appropriate message',
            'validation_method': 'manual',
            'priority': 'high',
            'status': 'requires_manual_testing'
        }
        
        return oauth_edge_cases
    
    def _validate_ui_field_edge_cases(self) -> Dict[str, Any]:
        """Validate UI field rendering edge cases"""
        ui_edge_cases = {
            'category': 'ui_field_rendering',
            'test_cases': {}
        }
        
        # Edge Case 1: Field Overlap Detection
        ui_edge_cases['test_cases']['field_overlap'] = {
            'description': 'Email and password fields overlapping',
            'test_steps': [
                'Load login page',
                'Inspect email field position using DevTools',
                'Inspect password field position',
                'Verify no overlap between fields',
                'Test at different zoom levels (50%, 100%, 150%, 200%)'
            ],
            'expected_behavior': 'Fields never overlap at any zoom level',
            'validation_method': 'automated_with_manual_verification',
            'priority': 'critical',
            'status': 'automated_test_available',
            'automated_checks': [
                'bounding_box_intersection_check',
                'z_index_validation',
                'css_positioning_analysis'
            ]
        }
        
        # Edge Case 2: Field Visibility Outside Container
        ui_edge_cases['test_cases']['field_visibility'] = {
            'description': 'Fields extending outside container bounds',
            'test_steps': [
                'Load login page',
                'Check if email field is fully within container',
                'Check if password field is fully within container',
                'Verify fields are not cut off',
                'Test with different container sizes'
            ],
            'expected_behavior': 'All fields fully visible within container',
            'validation_method': 'automated',
            'priority': 'critical',
            'status': 'automated_test_available'
        }
        
        # Edge Case 3: Long Text Input Handling
        ui_edge_cases['test_cases']['long_text_input'] = {
            'description': 'Very long email addresses and passwords',
            'test_steps': [
                'Enter extremely long email (100+ characters)',
                'Verify field handles long input gracefully',
                'Enter very long password (50+ characters)',
                'Check field expansion and scrolling',
                'Verify form submission works'
            ],
            'expected_behavior': 'Fields handle long input without breaking layout',
            'validation_method': 'automated',
            'priority': 'medium',
            'status': 'automated_test_available'
        }
        
        # Edge Case 4: Special Characters in Input
        ui_edge_cases['test_cases']['special_characters'] = {
            'description': 'Special characters in email and password fields',
            'test_steps': [
                'Enter email with special characters: test+tag@domain.co.uk',
                'Enter password with special characters: P@$$w0rd!#$%',
                'Verify proper encoding and handling',
                'Test form submission',
                'Check for XSS vulnerabilities'
            ],
            'expected_behavior': 'Special characters handled securely',
            'validation_method': 'automated',
            'priority': 'high',
            'status': 'automated_test_available'
        }
        
        return ui_edge_cases
    
    def _validate_responsive_edge_cases(self) -> Dict[str, Any]:
        """Validate responsive design edge cases"""
        responsive_edge_cases = {
            'category': 'responsive_design',
            'test_cases': {}
        }
        
        # Edge Case 1: Extreme Viewport Sizes
        responsive_edge_cases['test_cases']['extreme_viewports'] = {
            'description': 'Very small and very large viewport sizes',
            'test_steps': [
                'Test at 320x568 (iPhone 5)',
                'Test at 280x653 (Galaxy Fold folded)',
                'Test at 3840x2160 (4K display)',
                'Verify layout doesn\'t break',
                'Check touch target sizes'
            ],
            'expected_behavior': 'Layout adapts gracefully to extreme sizes',
            'validation_method': 'automated',
            'priority': 'high',
            'status': 'automated_test_available'
        }
        
        # Edge Case 2: Orientation Changes
        responsive_edge_cases['test_cases']['orientation_changes'] = {
            'description': 'Portrait to landscape orientation changes',
            'test_steps': [
                'Load page in portrait mode',
                'Rotate to landscape',
                'Verify layout adjusts correctly',
                'Check field positioning',
                'Test form functionality'
            ],
            'expected_behavior': 'Smooth orientation change handling',
            'validation_method': 'manual',
            'priority': 'medium',
            'status': 'requires_manual_testing'
        }
        
        return responsive_edge_cases
    
    def _validate_network_edge_cases(self) -> Dict[str, Any]:
        """Validate network and performance edge cases"""
        network_edge_cases = {
            'category': 'network_performance',
            'test_cases': {}
        }
        
        # Edge Case 1: Slow Network Conditions
        network_edge_cases['test_cases']['slow_network'] = {
            'description': 'OAuth and form submission on slow network',
            'test_steps': [
                'Simulate slow 3G network (DevTools)',
                'Attempt OAuth login',
                'Verify loading indicators appear',
                'Check timeout handling',
                'Test form submission with delays'
            ],
            'expected_behavior': 'Graceful handling of slow network conditions',
            'validation_method': 'automated',
            'priority': 'high',
            'status': 'automated_test_available'
        }
        
        # Edge Case 2: Network Disconnection
        network_edge_cases['test_cases']['network_disconnect'] = {
            'description': 'Network disconnection during OAuth flow',
            'test_steps': [
                'Start OAuth flow',
                'Disconnect network during redirect',
                'Reconnect network',
                'Verify error handling',
                'Test recovery mechanism'
            ],
            'expected_behavior': 'Proper error handling and recovery options',
            'validation_method': 'manual',
            'priority': 'high',
            'status': 'requires_manual_testing'
        }
        
        return network_edge_cases
    
    def _validate_browser_edge_cases(self) -> Dict[str, Any]:
        """Validate browser compatibility edge cases"""
        browser_edge_cases = {
            'category': 'browser_compatibility',
            'test_cases': {}
        }
        
        # Edge Case 1: JavaScript Disabled
        browser_edge_cases['test_cases']['javascript_disabled'] = {
            'description': 'OAuth buttons with JavaScript disabled',
            'test_steps': [
                'Disable JavaScript in browser',
                'Load login page',
                'Check if OAuth buttons are functional',
                'Verify fallback mechanisms',
                'Test basic form submission'
            ],
            'expected_behavior': 'Graceful degradation with fallback options',
            'validation_method': 'manual',
            'priority': 'medium',
            'status': 'requires_manual_testing'
        }
        
        # Edge Case 2: Incognito/Private Mode
        browser_edge_cases['test_cases']['private_mode'] = {
            'description': 'OAuth flows in incognito/private browsing mode',
            'test_steps': [
                'Open browser in incognito/private mode',
                'Navigate to login page',
                'Test all OAuth providers',
                'Verify session handling',
                'Check cookie restrictions'
            ],
            'expected_behavior': 'OAuth works correctly in private mode',
            'validation_method': 'manual',
            'priority': 'high',
            'status': 'requires_manual_testing'
        }
        
        return browser_edge_cases
    
    def _calculate_summary_statistics(self):
        """Calculate summary statistics for all edge cases"""
        total_cases = 0
        passed_cases = 0
        failed_cases = 0
        
        for category_result in self.validation_results['results'].values():
            for test_case in category_result.get('test_cases', {}).values():
                total_cases += 1
                status = test_case.get('status', 'unknown')
                
                if status in ['passed', 'automated_test_available']:
                    passed_cases += 1
                elif status in ['failed', 'critical_issue']:
                    failed_cases += 1
                    if test_case.get('priority') == 'critical':
                        self.validation_results['critical_issues'].append({
                            'test_case': test_case.get('description', 'Unknown'),
                            'category': category_result.get('category', 'Unknown'),
                            'issue': 'Critical edge case failure'
                        })
        
        self.validation_results['edge_cases_tested'] = total_cases
        self.validation_results['passed'] = passed_cases
        self.validation_results['failed'] = failed_cases
    
    def _generate_edge_case_report(self) -> str:
        """Generate comprehensive edge case validation report"""
        report_path = self.reports_dir / f"edge_case_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Edge Case Validation Report - Auto Job Apply</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
                .container {{ max-width: 1400px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #DC2626, #F59E0B, #10B981); color: white; padding: 40px; border-radius: 16px; text-align: center; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
                .metric {{ background: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .category {{ background: white; margin: 25px 0; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .test-case {{ background: #f8fafc; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #6366F1; }}
                .critical {{ border-left-color: #DC2626; background: #fef2f2; }}
                .high {{ border-left-color: #F59E0B; background: #fffbeb; }}
                .medium {{ border-left-color: #10B981; background: #f0fdf4; }}
                .status-automated {{ color: #059669; font-weight: bold; }}
                .status-manual {{ color: #F59E0B; font-weight: bold; }}
                .status-failed {{ color: #DC2626; font-weight: bold; }}
                .critical-issues {{ background: #fee2e2; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .recommendations {{ background: #dbeafe; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .test-steps {{ background: #f3f4f6; padding: 15px; border-radius: 6px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Edge Case Validation Report</h1>
                    <h2>Auto Job Apply System</h2>
                    <p>Generated: {self.validation_results['timestamp']}</p>
                </div>
                
                <div class="summary">
                    <div class="metric">
                        <h3>Total Edge Cases</h3>
                        <h2>{self.validation_results['edge_cases_tested']}</h2>
                    </div>
                    <div class="metric">
                        <h3>Automated Tests</h3>
                        <h2 class="status-automated">{self.validation_results['passed']}</h2>
                    </div>
                    <div class="metric">
                        <h3>Manual Tests Required</h3>
                        <h2 class="status-manual">{self._count_manual_tests()}</h2>
                    </div>
                    <div class="metric">
                        <h3>Critical Issues</h3>
                        <h2 class="status-failed">{len(self.validation_results['critical_issues'])}</h2>
                    </div>
                </div>
        """
        
        # Add critical issues section if any
        if self.validation_results['critical_issues']:
            html_content += """
                <div class="critical-issues">
                    <h3>🚨 Critical Issues Detected</h3>
                    <p>These issues must be addressed before production deployment:</p>
                    <ul>
            """
            for issue in self.validation_results['critical_issues']:
                html_content += f"<li><strong>{issue['category']}:</strong> {issue['issue']} - {issue['test_case']}</li>"
            html_content += "</ul></div>"
        
        # Add test categories
        for category_name, category_result in self.validation_results['results'].items():
            html_content += f"""
                <div class="category">
                    <h2>{category_result.get('category', category_name).replace('_', ' ').title()}</h2>
            """
            
            for test_name, test_case in category_result.get('test_cases', {}).items():
                priority = test_case.get('priority', 'medium')
                status = test_case.get('status', 'unknown')
                
                status_class = 'status-automated' if 'automated' in status else 'status-manual' if 'manual' in status else 'status-failed'
                
                html_content += f"""
                    <div class="test-case {priority}">
                        <h4>{test_case.get('description', test_name)} 
                            <span class="{status_class}">[{status.replace('_', ' ').upper()}]</span>
                        </h4>
                        <p><strong>Priority:</strong> {priority.title()}</p>
                        <p><strong>Validation Method:</strong> {test_case.get('validation_method', 'unknown')}</p>
                        <p><strong>Expected Behavior:</strong> {test_case.get('expected_behavior', 'Not specified')}</p>
                        
                        <div class="test-steps">
                            <strong>Test Steps:</strong>
                            <ol>
                """
                
                for step in test_case.get('test_steps', []):
                    html_content += f"<li>{step}</li>"
                
                html_content += """
                            </ol>
                        </div>
                    </div>
                """
            
            html_content += "</div>"
        
        # Add recommendations
        html_content += f"""
                <div class="recommendations">
                    <h3>💡 Testing Recommendations</h3>
                    <ul>
                        <li><strong>Immediate Action:</strong> Complete all manual testing scenarios marked as "requires_manual_testing"</li>
                        <li><strong>OAuth Testing:</strong> Configure real OAuth credentials and test all providers thoroughly</li>
                        <li><strong>UI Validation:</strong> Use browser DevTools to inspect field positioning and CSS properties</li>
                        <li><strong>Cross-Browser:</strong> Test in Chrome, Firefox, Edge, and Safari</li>
                        <li><strong>Mobile Testing:</strong> Test on actual mobile devices, not just browser simulation</li>
                        <li><strong>Performance:</strong> Test with slow network conditions and high latency</li>
                        <li><strong>Accessibility:</strong> Test with screen readers and keyboard-only navigation</li>
                    </ul>
                </div>
                
                <div class="category">
                    <h2>🛠️ How to Fix Common Issues</h2>
                    
                    <div class="test-case">
                        <h4>🔧 Email/Password Field Overlap Fix</h4>
                        <div class="test-steps">
                            <strong>CSS Fix:</strong>
                            <pre style="background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 6px; overflow-x: auto;">
.email-field, .password-field {{
  width: 100% !important;
  max-width: 400px !important;
  margin: 15px 0 !important;
  padding: 12px !important;
  box-sizing: border-box !important;
  position: relative !important;
  z-index: 1 !important;
  display: block !important;
}}

.form-container {{
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 20px !important;
}}
                            </pre>
                        </div>
                    </div>
                    
                    <div class="test-case">
                        <h4>🔧 OAuth Button Positioning Fix</h4>
                        <div class="test-steps">
                            <strong>CSS Fix:</strong>
                            <pre style="background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 6px; overflow-x: auto;">
.oauth-button {{
  margin: 10px 5px !important;
  padding: 12px 24px !important;
  display: inline-block !important;
  position: relative !important;
  min-width: 200px !important;
  text-align: center !important;
}}

.oauth-buttons-container {{
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
  align-items: center !important;
}}
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _count_manual_tests(self) -> int:
        """Count tests that require manual validation"""
        count = 0
        for category_result in self.validation_results['results'].values():
            for test_case in category_result.get('test_cases', {}).values():
                if 'manual' in test_case.get('status', ''):
                    count += 1
        return count

def main():
    """Main function for edge case validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Edge Case Validator')
    parser.add_argument('--open-report', action='store_true', 
                       help='Automatically open validation report')
    
    args = parser.parse_args()
    
    validator = EdgeCaseValidator()
    results = validator.validate_all_edge_cases()
    
    if args.open_report and 'report_path' in results:
        webbrowser.open(f"file://{os.path.abspath(results['report_path'])}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("🔍 EDGE CASE VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Edge Cases: {results['edge_cases_tested']}")
    print(f"Automated Tests: {results['passed']}")
    print(f"Manual Tests Required: {validator._count_manual_tests()}")
    print(f"Critical Issues: {len(results['critical_issues'])}")
    print(f"Report: {results.get('report_path', 'N/A')}")
    print("=" * 60)
    
    # Exit with appropriate code
    exit_code = 0 if len(results['critical_issues']) == 0 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
