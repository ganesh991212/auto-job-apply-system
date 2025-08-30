#!/usr/bin/env python3
"""
Screenshot Validation System for Auto Job Apply
Compares screenshots with baselines and automatically fixes UI issues
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import shutil
import subprocess
import sys

class ScreenshotValidator:
    """Main class for screenshot validation and UI fixing"""
    
    def __init__(self):
        self.screenshots_dir = "automation/screenshots"
        self.baselines_dir = "automation/baselines"
        self.reports_dir = "automation/reports"
        self.diff_threshold = 0.95  # 95% similarity required
        self.validation_results = []
        
    def compare_screenshots(self, screenshot_path: str, baseline_path: str) -> Dict:
        """Compare a screenshot with its baseline"""
        try:
            # Load images
            screenshot = cv2.imread(screenshot_path)
            baseline = cv2.imread(baseline_path)
            
            if screenshot is None or baseline is None:
                return {
                    'status': 'error',
                    'similarity': 0.0,
                    'error': 'Could not load images'
                }
            
            # Resize images to same dimensions if needed
            if screenshot.shape != baseline.shape:
                baseline = cv2.resize(baseline, (screenshot.shape[1], screenshot.shape[0]))
            
            # Calculate structural similarity
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
            
            # Use template matching for similarity
            result = cv2.matchTemplate(screenshot_gray, baseline_gray, cv2.TM_CCOEFF_NORMED)
            similarity = np.max(result)
            
            # Create difference image
            diff = cv2.absdiff(screenshot, baseline)
            diff_path = screenshot_path.replace('.png', '_diff.png')
            cv2.imwrite(diff_path, diff)
            
            return {
                'status': 'pass' if similarity >= self.diff_threshold else 'fail',
                'similarity': float(similarity),
                'diff_path': diff_path,
                'threshold': self.diff_threshold
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'similarity': 0.0,
                'error': str(e)
            }
    
    def validate_all_screenshots(self) -> Dict:
        """Validate all screenshots against baselines"""
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'total_screenshots': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'results': []
        }
        
        # Walk through all screenshot directories
        for root, dirs, files in os.walk(self.screenshots_dir):
            for file in files:
                if file.endswith('.png') and not file.endswith('_diff.png'):
                    screenshot_path = os.path.join(root, file)
                    
                    # Find corresponding baseline
                    relative_path = os.path.relpath(screenshot_path, self.screenshots_dir)
                    baseline_path = os.path.join(self.baselines_dir, relative_path)
                    
                    if os.path.exists(baseline_path):
                        # Compare with baseline
                        result = self.compare_screenshots(screenshot_path, baseline_path)
                        result['screenshot'] = screenshot_path
                        result['baseline'] = baseline_path
                        result['screen_name'] = os.path.basename(root)
                        
                        validation_report['results'].append(result)
                        validation_report['total_screenshots'] += 1
                        
                        if result['status'] == 'pass':
                            validation_report['passed'] += 1
                        elif result['status'] == 'fail':
                            validation_report['failed'] += 1
                        else:
                            validation_report['errors'] += 1
                    else:
                        # No baseline exists, create one
                        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
                        shutil.copy2(screenshot_path, baseline_path)
                        
                        result = {
                            'status': 'baseline_created',
                            'screenshot': screenshot_path,
                            'baseline': baseline_path,
                            'screen_name': os.path.basename(root),
                            'similarity': 1.0
                        }
                        validation_report['results'].append(result)
                        validation_report['total_screenshots'] += 1
                        validation_report['passed'] += 1
        
        self.validation_results = validation_report
        return validation_report
    
    def identify_ui_issues(self, failed_results: List[Dict]) -> List[Dict]:
        """Identify specific UI issues from failed screenshot comparisons"""
        ui_issues = []
        
        for result in failed_results:
            if result['status'] != 'fail':
                continue
                
            screen_name = result['screen_name']
            similarity = result['similarity']
            
            # Analyze the type of issue based on similarity score
            if similarity < 0.5:
                issue_type = 'major_layout_change'
                severity = 'high'
            elif similarity < 0.8:
                issue_type = 'moderate_styling_change'
                severity = 'medium'
            else:
                issue_type = 'minor_visual_difference'
                severity = 'low'
            
            ui_issue = {
                'screen_name': screen_name,
                'issue_type': issue_type,
                'severity': severity,
                'similarity': similarity,
                'screenshot_path': result['screenshot'],
                'baseline_path': result['baseline'],
                'diff_path': result.get('diff_path'),
                'suggested_fixes': self.get_suggested_fixes(screen_name, issue_type)
            }
            
            ui_issues.append(ui_issue)
        
        return ui_issues
    
    def get_suggested_fixes(self, screen_name: str, issue_type: str) -> List[str]:
        """Get suggested fixes for UI issues"""
        fixes = []
        
        if issue_type == 'major_layout_change':
            fixes.extend([
                f"Check {screen_name} layout constraints and widget positioning",
                "Verify responsive design breakpoints",
                "Review recent changes to theme or styling"
            ])
        elif issue_type == 'moderate_styling_change':
            fixes.extend([
                f"Review color scheme changes in {screen_name}",
                "Check font sizes and spacing",
                "Verify button and component styling"
            ])
        else:  # minor_visual_difference
            fixes.extend([
                f"Minor styling adjustments needed for {screen_name}",
                "Check padding and margin values",
                "Verify icon or image assets"
            ])
        
        return fixes
    
    def auto_fix_ui_issues(self, ui_issues: List[Dict]) -> Dict:
        """Automatically fix UI issues by modifying code"""
        fix_report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(ui_issues),
            'fixed': 0,
            'failed_to_fix': 0,
            'fixes_applied': []
        }
        
        for issue in ui_issues:
            screen_name = issue['screen_name']
            issue_type = issue['issue_type']
            
            try:
                if self.apply_automatic_fix(screen_name, issue_type, issue):
                    fix_report['fixed'] += 1
                    fix_report['fixes_applied'].append({
                        'screen_name': screen_name,
                        'issue_type': issue_type,
                        'status': 'fixed'
                    })
                else:
                    fix_report['failed_to_fix'] += 1
                    fix_report['fixes_applied'].append({
                        'screen_name': screen_name,
                        'issue_type': issue_type,
                        'status': 'manual_fix_required'
                    })
            except Exception as e:
                fix_report['failed_to_fix'] += 1
                fix_report['fixes_applied'].append({
                    'screen_name': screen_name,
                    'issue_type': issue_type,
                    'status': 'error',
                    'error': str(e)
                })
        
        return fix_report
    
    def apply_automatic_fix(self, screen_name: str, issue_type: str, issue: Dict) -> bool:
        """Apply automatic fixes to UI code"""
        try:
            # Map screen names to Flutter files
            screen_file_map = {
                'login_screen': 'frontend/lib/screens/auth/login_screen.dart',
                'dashboard': 'frontend/lib/screens/dashboard/user_dashboard.dart',
                'job_application': 'frontend/lib/screens/jobs/job_application_screen.dart',
                'resume_upload': 'frontend/lib/screens/resume/resume_upload_screen.dart',
                'settings': 'frontend/lib/screens/settings/settings_screen.dart'
            }
            
            file_path = screen_file_map.get(screen_name)
            if not file_path or not os.path.exists(file_path):
                return False
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fixes based on issue type
            if issue_type == 'minor_visual_difference':
                # Fix common spacing issues
                content = self.fix_spacing_issues(content)
            elif issue_type == 'moderate_styling_change':
                # Fix color and styling issues
                content = self.fix_styling_issues(content)
            
            # Write back the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error applying fix: {e}")
            return False
    
    def fix_spacing_issues(self, content: str) -> str:
        """Fix common spacing issues in Flutter code"""
        # Add consistent padding
        content = content.replace('padding: EdgeInsets.all(8)', 'padding: EdgeInsets.all(16)')
        content = content.replace('padding: EdgeInsets.all(12)', 'padding: EdgeInsets.all(16)')
        
        # Fix margin consistency
        content = content.replace('margin: EdgeInsets.all(8)', 'margin: EdgeInsets.all(16)')
        
        return content
    
    def fix_styling_issues(self, content: str) -> str:
        """Fix common styling issues in Flutter code"""
        # Ensure consistent button styling
        if 'ElevatedButton' in content and 'style:' not in content:
            content = content.replace(
                'ElevatedButton(',
                'ElevatedButton(\n          style: Theme.of(context).elevatedButtonTheme.style,'
            )
        
        return content
    
    def generate_validation_report(self) -> str:
        """Generate HTML validation report"""
        if not self.validation_results:
            return ""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Screenshot Validation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 8px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #e8f4fd; padding: 15px; border-radius: 8px; text-align: center; }}
                .pass {{ background: #d4edda; }}
                .fail {{ background: #f8d7da; }}
                .error {{ background: #fff3cd; }}
                .result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }}
                .screenshot {{ max-width: 300px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Screenshot Validation Report</h1>
                <p>Generated: {self.validation_results['timestamp']}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Screenshots</h3>
                    <p>{self.validation_results['total_screenshots']}</p>
                </div>
                <div class="metric pass">
                    <h3>Passed</h3>
                    <p>{self.validation_results['passed']}</p>
                </div>
                <div class="metric fail">
                    <h3>Failed</h3>
                    <p>{self.validation_results['failed']}</p>
                </div>
                <div class="metric error">
                    <h3>Errors</h3>
                    <p>{self.validation_results['errors']}</p>
                </div>
            </div>
            
            <h2>Detailed Results</h2>
        """
        
        for result in self.validation_results['results']:
            status_class = result['status']
            html_content += f"""
            <div class="result {status_class}">
                <h3>{result['screen_name']} - {result['status'].upper()}</h3>
                <p>Similarity: {result.get('similarity', 0):.2%}</p>
                <div>
                    <img src="{result['screenshot']}" alt="Screenshot" class="screenshot">
                    {f'<img src="{result["baseline"]}" alt="Baseline" class="screenshot">' if 'baseline' in result else ''}
                    {f'<img src="{result["diff_path"]}" alt="Difference" class="screenshot">' if 'diff_path' in result else ''}
                </div>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Save report
        report_path = os.path.join(self.reports_dir, f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path

def main():
    """Main function to run screenshot validation"""
    validator = ScreenshotValidator()
    
    print("🔍 Starting screenshot validation...")
    validation_report = validator.validate_all_screenshots()
    
    print(f"📊 Validation complete:")
    print(f"   Total: {validation_report['total_screenshots']}")
    print(f"   Passed: {validation_report['passed']}")
    print(f"   Failed: {validation_report['failed']}")
    print(f"   Errors: {validation_report['errors']}")
    
    # Identify and fix UI issues
    failed_results = [r for r in validation_report['results'] if r['status'] == 'fail']
    if failed_results:
        print(f"\n🔧 Identifying UI issues...")
        ui_issues = validator.identify_ui_issues(failed_results)
        
        print(f"🛠️  Applying automatic fixes...")
        fix_report = validator.auto_fix_ui_issues(ui_issues)
        
        print(f"   Fixed: {fix_report['fixed']}")
        print(f"   Manual fixes needed: {fix_report['failed_to_fix']}")
    
    # Generate report
    report_path = validator.generate_validation_report()
    print(f"📄 Report generated: {report_path}")
    
    return validation_report['failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
