#!/usr/bin/env python3
"""
Manual Testing Checklist Generator for Auto Job Apply System
Creates interactive checklists for QA team manual testing
"""

import os
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ManualTestingChecklistGenerator:
    """Generates comprehensive manual testing checklists"""
    
    def __init__(self):
        self.checklist_dir = Path("automation/manual_testing")
        self.checklist_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_comprehensive_checklist(self) -> str:
        """Generate comprehensive manual testing checklist"""
        checklist_data = self._create_checklist_data()
        
        # Generate interactive HTML checklist
        html_path = self._generate_interactive_html_checklist(checklist_data)
        
        # Generate JSON checklist for automation integration
        json_path = self._generate_json_checklist(checklist_data)
        
        print(f"📋 Manual testing checklist generated:")
        print(f"   HTML: {html_path}")
        print(f"   JSON: {json_path}")
        
        return html_path
    
    def _create_checklist_data(self) -> Dict[str, Any]:
        """Create comprehensive checklist data"""
        return {
            "checklist_info": {
                "title": "Auto Job Apply System - Manual Testing Checklist",
                "version": "1.0",
                "generated": datetime.now().isoformat(),
                "tester_name": "QA Team Member",
                "test_environment": "http://localhost:3000"
            },
            "test_categories": {
                "authentication_flows": {
                    "title": "🔐 Authentication & OAuth Testing",
                    "priority": "critical",
                    "estimated_time": "30 minutes",
                    "test_cases": [
                        {
                            "id": "AUTH-001",
                            "title": "Google OAuth Login Flow",
                            "steps": [
                                "1. Open http://localhost:3000",
                                "2. Click 'Sign in with Google' button",
                                "3. Verify button is clickable and not overlapping",
                                "4. Observe redirect to Google OAuth page",
                                "5. Enter valid Google credentials",
                                "6. Grant permissions when prompted",
                                "7. Verify successful redirect back to app",
                                "8. Confirm user is logged in (dashboard visible)"
                            ],
                            "expected_result": "Successful login and redirect to dashboard",
                            "edge_cases": [
                                "Test with popup blocker enabled",
                                "Test user cancellation during OAuth",
                                "Test with invalid Google account",
                                "Test with expired Google session"
                            ]
                        },
                        {
                            "id": "AUTH-002", 
                            "title": "Microsoft OAuth Login Flow",
                            "steps": [
                                "1. Open http://localhost:3000",
                                "2. Click 'Sign in with Microsoft' button",
                                "3. Verify button styling and positioning",
                                "4. Observe redirect to Microsoft OAuth page",
                                "5. Enter valid Microsoft credentials",
                                "6. Handle 2FA if prompted",
                                "7. Verify successful redirect back to app",
                                "8. Confirm user is logged in"
                            ],
                            "expected_result": "Successful login and redirect to dashboard",
                            "edge_cases": [
                                "Test with corporate Microsoft account",
                                "Test with personal Microsoft account",
                                "Test with 2FA enabled",
                                "Test account lockout scenarios"
                            ]
                        },
                        {
                            "id": "AUTH-003",
                            "title": "Apple OAuth Login Flow",
                            "steps": [
                                "1. Open http://localhost:3000",
                                "2. Click 'Sign in with Apple' button",
                                "3. Verify button exists and is functional",
                                "4. Observe redirect to Apple OAuth page",
                                "5. Enter valid Apple ID credentials",
                                "6. Choose email sharing preference",
                                "7. Verify successful redirect back to app",
                                "8. Confirm user is logged in"
                            ],
                            "expected_result": "Successful login with email preference handling",
                            "edge_cases": [
                                "Test 'Hide My Email' option",
                                "Test without Apple ID",
                                "Test on non-Apple devices",
                                "Test with Apple ID 2FA"
                            ]
                        },
                        {
                            "id": "AUTH-004",
                            "title": "Email/Password Login",
                            "steps": [
                                "1. Open http://localhost:3000",
                                "2. Enter valid email in email field",
                                "3. Verify email field is properly positioned",
                                "4. Enter valid password in password field", 
                                "5. Verify password field is not overlapping email field",
                                "6. Click 'Sign In' button",
                                "7. Verify successful login"
                            ],
                            "expected_result": "Successful email/password login",
                            "ui_validations": [
                                "Email field fully visible and not cut off",
                                "Password field properly positioned below email",
                                "No overlapping between fields",
                                "Tab navigation works correctly",
                                "Error messages display properly"
                            ]
                        }
                    ]
                },
                "ui_layout_validation": {
                    "title": "🎨 UI Layout & Field Rendering",
                    "priority": "high",
                    "estimated_time": "45 minutes",
                    "test_cases": [
                        {
                            "id": "UI-001",
                            "title": "Login Form Field Alignment",
                            "steps": [
                                "1. Open login page in Chrome",
                                "2. Inspect email field positioning using DevTools",
                                "3. Verify field is within container bounds",
                                "4. Check password field positioning",
                                "5. Verify no overlapping elements",
                                "6. Test on different zoom levels (50%, 100%, 150%)",
                                "7. Repeat in Firefox and Edge browsers"
                            ],
                            "expected_result": "All fields properly aligned and visible",
                            "failure_indicators": [
                                "Email field cut off or outside container",
                                "Password field overlapping email field",
                                "Fields not responsive to zoom changes",
                                "Browser-specific rendering issues"
                            ]
                        },
                        {
                            "id": "UI-002",
                            "title": "Responsive Design Validation",
                            "steps": [
                                "1. Open app in desktop browser (1920x1080)",
                                "2. Verify all elements are properly positioned",
                                "3. Resize to tablet view (768x1024)",
                                "4. Check layout adapts correctly",
                                "5. Resize to mobile view (375x667)",
                                "6. Verify mobile layout is functional",
                                "7. Test landscape orientation on mobile"
                            ],
                            "expected_result": "Layout adapts properly at all breakpoints",
                            "critical_checks": [
                                "No horizontal scrolling on mobile",
                                "Touch targets are adequate size (44px minimum)",
                                "Text remains readable at all sizes",
                                "Navigation remains accessible"
                            ]
                        },
                        {
                            "id": "UI-003",
                            "title": "Cross-Browser Compatibility",
                            "steps": [
                                "1. Test in Chrome (latest version)",
                                "2. Test in Firefox (latest version)",
                                "3. Test in Edge (latest version)",
                                "4. Test in Safari (if available)",
                                "5. Compare OAuth button rendering",
                                "6. Compare form field positioning",
                                "7. Test JavaScript functionality"
                            ],
                            "expected_result": "Consistent behavior across all browsers",
                            "browser_specific_checks": [
                                "Chrome: OAuth popup handling",
                                "Firefox: File upload functionality",
                                "Edge: Microsoft OAuth integration",
                                "Safari: Apple OAuth integration"
                            ]
                        }
                    ]
                },
                "accessibility_testing": {
                    "title": "♿ Accessibility & WCAG Compliance",
                    "priority": "high",
                    "estimated_time": "30 minutes",
                    "test_cases": [
                        {
                            "id": "A11Y-001",
                            "title": "Keyboard Navigation",
                            "steps": [
                                "1. Open login page",
                                "2. Use only Tab key to navigate",
                                "3. Verify logical tab order",
                                "4. Test Shift+Tab for reverse navigation",
                                "5. Verify focus indicators are visible",
                                "6. Test Enter key on buttons",
                                "7. Test Escape key functionality"
                            ],
                            "expected_result": "Complete keyboard accessibility",
                            "wcag_criteria": [
                                "2.1.1 Keyboard accessible",
                                "2.4.3 Focus order",
                                "2.4.7 Focus visible"
                            ]
                        },
                        {
                            "id": "A11Y-002",
                            "title": "Screen Reader Compatibility",
                            "steps": [
                                "1. Enable screen reader (NVDA/JAWS)",
                                "2. Navigate through login form",
                                "3. Verify field labels are announced",
                                "4. Test error message announcements",
                                "5. Verify button descriptions",
                                "6. Test form submission feedback"
                            ],
                            "expected_result": "All elements properly announced",
                            "wcag_criteria": [
                                "1.3.1 Info and relationships",
                                "3.3.2 Labels or instructions",
                                "4.1.2 Name, role, value"
                            ]
                        }
                    ]
                },
                "performance_testing": {
                    "title": "⚡ Performance & Load Testing",
                    "priority": "medium",
                    "estimated_time": "20 minutes",
                    "test_cases": [
                        {
                            "id": "PERF-001",
                            "title": "Page Load Performance",
                            "steps": [
                                "1. Open DevTools Network tab",
                                "2. Navigate to login page",
                                "3. Measure page load time",
                                "4. Check for render-blocking resources",
                                "5. Verify images are optimized",
                                "6. Test with slow 3G simulation"
                            ],
                            "expected_result": "Page loads under 3 seconds",
                            "performance_thresholds": {
                                "first_contentful_paint": "< 1.5s",
                                "largest_contentful_paint": "< 2.5s",
                                "cumulative_layout_shift": "< 0.1"
                            }
                        }
                    ]
                }
            }
        }
    
    def _generate_interactive_html_checklist(self, checklist_data: Dict) -> str:
        """Generate interactive HTML checklist"""
        html_path = self.checklist_dir / "interactive_testing_checklist.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Manual Testing Checklist - Auto Job Apply</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #6366F1, #EC4899); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
                .category {{ background: white; margin: 20px 0; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .test-case {{ background: #f8fafc; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #6366F1; }}
                .checklist-item {{ margin: 8px 0; }}
                .checklist-item input[type="checkbox"] {{ margin-right: 10px; transform: scale(1.2); }}
                .priority-critical {{ border-left-color: #DC2626; }}
                .priority-high {{ border-left-color: #F59E0B; }}
                .priority-medium {{ border-left-color: #10B981; }}
                .progress-bar {{ background: #e5e7eb; height: 20px; border-radius: 10px; margin: 20px 0; }}
                .progress-fill {{ background: linear-gradient(90deg, #6366F1, #8B5CF6); height: 100%; border-radius: 10px; width: 0%; transition: width 0.3s; }}
                .edge-case {{ background: #fef3c7; padding: 10px; margin: 10px 0; border-radius: 6px; }}
                .ui-validation {{ background: #dbeafe; padding: 10px; margin: 10px 0; border-radius: 6px; }}
                .failure-indicator {{ background: #fee2e2; padding: 10px; margin: 10px 0; border-radius: 6px; }}
                .test-credentials {{ background: #ecfdf5; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .quick-links {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .quick-link {{ background: #6366F1; color: white; padding: 15px; text-align: center; border-radius: 8px; text-decoration: none; }}
                .quick-link:hover {{ background: #4F46E5; }}
            </style>
            <script>
                function updateProgress() {{
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    const checked = document.querySelectorAll('input[type="checkbox"]:checked');
                    const progress = (checked.length / checkboxes.length) * 100;
                    document.getElementById('progress-fill').style.width = progress + '%';
                    document.getElementById('progress-text').textContent = 
                        `${{checked.length}} / ${{checkboxes.length}} tests completed (${{Math.round(progress)}}%)`;
                }}
                
                function saveProgress() {{
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    const progress = {{}};
                    checkboxes.forEach(cb => {{
                        progress[cb.id] = cb.checked;
                    }});
                    localStorage.setItem('testProgress', JSON.stringify(progress));
                    alert('Progress saved!');
                }}
                
                function loadProgress() {{
                    const saved = localStorage.getItem('testProgress');
                    if (saved) {{
                        const progress = JSON.parse(saved);
                        Object.keys(progress).forEach(id => {{
                            const checkbox = document.getElementById(id);
                            if (checkbox) checkbox.checked = progress[id];
                        }});
                        updateProgress();
                    }}
                }}
                
                function exportResults() {{
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    const results = [];
                    checkboxes.forEach(cb => {{
                        const testCase = cb.closest('.test-case');
                        const category = cb.closest('.category');
                        results.push({{
                            category: category.querySelector('h2').textContent,
                            test_id: cb.id,
                            test_name: testCase.querySelector('h4').textContent,
                            status: cb.checked ? 'PASS' : 'PENDING',
                            timestamp: new Date().toISOString()
                        }});
                    }});
                    
                    const blob = new Blob([JSON.stringify(results, null, 2)], {{type: 'application/json'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'manual_test_results.json';
                    a.click();
                }}
            </script>
        </head>
        <body onload="loadProgress()">
            <div class="container">
                <div class="header">
                    <h1>🧪 Manual Testing Checklist</h1>
                    <h2>Auto Job Apply System</h2>
                    <p>Generated: {checklist_data['checklist_info']['generated']}</p>
                    <p>Environment: {checklist_data['checklist_info']['test_environment']}</p>
                </div>
                
                <div class="progress-bar">
                    <div id="progress-fill" class="progress-fill"></div>
                </div>
                <p id="progress-text" style="text-align: center; font-weight: bold;">0 / 0 tests completed (0%)</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <button onclick="saveProgress()" style="background: #10B981; color: white; padding: 10px 20px; border: none; border-radius: 6px; margin: 5px;">💾 Save Progress</button>
                    <button onclick="exportResults()" style="background: #6366F1; color: white; padding: 10px 20px; border: none; border-radius: 6px; margin: 5px;">📊 Export Results</button>
                </div>
                
                <div class="test-credentials">
                    <h3>🔐 Test Credentials</h3>
                    <p><strong>Test User:</strong> autotest_1756529234_x7k9m2@gmail.com</p>
                    <p><strong>Password:</strong> TestPass123!</p>
                    <p><strong>Super User:</strong> admin@autojobapply.com</p>
                    <p><strong>Super Password:</strong> SuperAdmin123!</p>
                </div>
                
                <div class="quick-links">
                    <a href="http://localhost:3000" target="_blank" class="quick-link">🌐 Open App</a>
                    <a href="http://localhost:8001/docs" target="_blank" class="quick-link">📚 Auth API</a>
                    <a href="http://localhost:8002/docs" target="_blank" class="quick-link">📚 Core API</a>
                    <a href="automation/screenshots/" target="_blank" class="quick-link">📸 Screenshots</a>
                </div>
        """
        
        # Generate test categories
        for category_key, category_data in checklist_data['test_categories'].items():
            priority_class = f"priority-{category_data['priority']}"
            
            html_content += f"""
                <div class="category {priority_class}">
                    <h2>{category_data['title']}</h2>
                    <p><strong>Priority:</strong> {category_data['priority'].title()}</p>
                    <p><strong>Estimated Time:</strong> {category_data['estimated_time']}</p>
            """
            
            for i, test_case in enumerate(category_data['test_cases']):
                test_id = test_case['id']
                
                html_content += f"""
                    <div class="test-case">
                        <h4>
                            <input type="checkbox" id="{test_id}" onchange="updateProgress()">
                            {test_case['title']} ({test_case['id']})
                        </h4>
                        
                        <div class="ui-validation">
                            <strong>📋 Test Steps:</strong>
                            <ol>
                """
                
                for step in test_case['steps']:
                    html_content += f"<li>{step}</li>"
                
                html_content += f"""
                            </ol>
                            <p><strong>Expected Result:</strong> {test_case['expected_result']}</p>
                        </div>
                """
                
                # Add UI validations if present
                if 'ui_validations' in test_case:
                    html_content += """
                        <div class="ui-validation">
                            <strong>🎨 UI Validations:</strong>
                            <ul>
                    """
                    for validation in test_case['ui_validations']:
                        html_content += f"<li>{validation}</li>"
                    html_content += "</ul></div>"
                
                # Add edge cases if present
                if 'edge_cases' in test_case:
                    html_content += """
                        <div class="edge-case">
                            <strong>⚠️ Edge Cases to Test:</strong>
                            <ul>
                    """
                    for edge_case in test_case['edge_cases']:
                        html_content += f"<li>{edge_case}</li>"
                    html_content += "</ul></div>"
                
                # Add failure indicators if present
                if 'failure_indicators' in test_case:
                    html_content += """
                        <div class="failure-indicator">
                            <strong>🚨 Failure Indicators:</strong>
                            <ul>
                    """
                    for indicator in test_case['failure_indicators']:
                        html_content += f"<li>{indicator}</li>"
                    html_content += "</ul></div>"
                
                html_content += "</div>"
            
            html_content += "</div>"
        
        html_content += """
                <div class="category">
                    <h2>📊 Testing Summary</h2>
                    <p>Complete all test cases above and export results for review.</p>
                    <p>Any failures should be documented with screenshots and detailed reproduction steps.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <button onclick="exportResults()" style="background: #059669; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px;">
                            ✅ Export Final Test Results
                        </button>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_path)
    
    def _generate_json_checklist(self, checklist_data: Dict) -> str:
        """Generate JSON checklist for automation integration"""
        json_path = self.checklist_dir / "testing_checklist.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(checklist_data, f, indent=2)
        
        return str(json_path)

def main():
    """Main function for checklist generation"""
    generator = ManualTestingChecklistGenerator()
    html_path = generator.generate_comprehensive_checklist()
    
    print(f"\n🎯 Manual Testing Checklist Ready!")
    print(f"📄 Open: {html_path}")
    
    # Auto-open the checklist
    try:
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
        print("👀 Checklist opened in browser")
    except Exception as e:
        print(f"⚠️ Could not auto-open: {e}")

if __name__ == "__main__":
    main()
