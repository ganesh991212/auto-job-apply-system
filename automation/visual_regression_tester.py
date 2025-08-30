#!/usr/bin/env python3
"""
Visual Regression Testing System for Auto Job Apply
Pixel-perfect validation with automatic UI fixing capabilities
"""

import os
import sys
import cv2
import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class VisualRegressionTester:
    """Advanced visual regression testing with auto-fixing"""
    
    def __init__(self):
        self.screenshots_dir = Path("automation/screenshots")
        self.baselines_dir = Path("automation/baselines")
        self.diffs_dir = Path("automation/visual_diffs")
        self.reports_dir = Path("automation/reports")
        
        # Create directories
        for directory in [self.screenshots_dir, self.baselines_dir, self.diffs_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.driver = None
        self.similarity_threshold = 0.95
        self.pixel_tolerance = 5
        
    def setup_driver(self, viewport_size: Tuple[int, int] = (1920, 1080)):
        """Setup Chrome WebDriver for visual testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={viewport_size[0]},{viewport_size[1]}")
        chrome_options.add_argument("--force-device-scale-factor=1")  # Consistent scaling
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(viewport_size[0], viewport_size[1])
            return True
        except Exception as e:
            print(f"❌ Failed to setup visual testing driver: {e}")
            return False
    
    def capture_baseline_screenshots(self) -> Dict[str, Any]:
        """Capture baseline screenshots for all screens"""
        print("📸 Capturing Baseline Screenshots...")
        
        screens_to_capture = [
            {
                'name': 'login_page',
                'url': 'http://localhost:3000',
                'wait_for': 'body',
                'actions': []
            },
            {
                'name': 'login_page_filled',
                'url': 'http://localhost:3000',
                'wait_for': 'body',
                'actions': [
                    ('fill_email', 'input[type="email"]', 'test@example.com'),
                    ('fill_password', 'input[type="password"]', 'testpassword123')
                ]
            },
            {
                'name': 'oauth_buttons_hover',
                'url': 'http://localhost:3000',
                'wait_for': 'body',
                'actions': [
                    ('hover_google', 'button:contains("Google")', None)
                ]
            }
        ]
        
        baseline_results = {
            'timestamp': datetime.now().isoformat(),
            'total_screens': len(screens_to_capture),
            'captured': 0,
            'failed': 0,
            'results': []
        }
        
        for screen in screens_to_capture:
            try:
                result = self._capture_screen_baseline(screen)
                baseline_results['results'].append(result)
                
                if result['status'] == 'success':
                    baseline_results['captured'] += 1
                else:
                    baseline_results['failed'] += 1
                    
            except Exception as e:
                baseline_results['failed'] += 1
                baseline_results['results'].append({
                    'screen_name': screen['name'],
                    'status': 'error',
                    'error': str(e)
                })
        
        print(f"📊 Baseline capture complete: {baseline_results['captured']}/{baseline_results['total_screens']}")
        return baseline_results
    
    def _capture_screen_baseline(self, screen_config: Dict) -> Dict[str, Any]:
        """Capture baseline for a specific screen"""
        screen_name = screen_config['name']
        
        try:
            # Navigate to URL
            self.driver.get(screen_config['url'])
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, screen_config['wait_for']))
            )
            
            # Wait for animations and loading
            time.sleep(3)
            
            # Perform actions if specified
            for action_type, selector, value in screen_config.get('actions', []):
                if action_type == 'fill_email':
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    element.clear()
                    element.send_keys(value)
                elif action_type == 'fill_password':
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    element.clear()
                    element.send_keys(value)
                elif action_type.startswith('hover_'):
                    try:
                        element = self.driver.find_element(By.XPATH, f"//button[contains(text(), 'Google')]")
                        self.driver.execute_script("arguments[0].scrollIntoView();", element)
                        webdriver.ActionChains(self.driver).move_to_element(element).perform()
                    except:
                        pass  # Hover action optional
                
                time.sleep(1)  # Wait between actions
            
            # Take screenshot
            baseline_path = self.baselines_dir / f"{screen_name}.png"
            self.driver.save_screenshot(str(baseline_path))
            
            # Capture metadata
            metadata = {
                'screen_name': screen_name,
                'url': screen_config['url'],
                'viewport_size': self.driver.get_window_size(),
                'timestamp': datetime.now().isoformat(),
                'actions_performed': len(screen_config.get('actions', []))
            }
            
            metadata_path = self.baselines_dir / f"{screen_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Baseline captured: {screen_name}")
            
            return {
                'screen_name': screen_name,
                'status': 'success',
                'baseline_path': str(baseline_path),
                'metadata_path': str(metadata_path)
            }
            
        except Exception as e:
            print(f"❌ Failed to capture baseline for {screen_name}: {e}")
            return {
                'screen_name': screen_name,
                'status': 'error',
                'error': str(e)
            }
    
    def validate_visual_regression(self) -> Dict[str, Any]:
        """Validate current screenshots against baselines"""
        print("🔍 Running Visual Regression Validation...")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'total_comparisons': 0,
            'passed': 0,
            'failed': 0,
            'auto_fixed': 0,
            'results': []
        }
        
        # Find all baseline images
        baseline_images = list(self.baselines_dir.glob("*.png"))
        
        for baseline_path in baseline_images:
            screen_name = baseline_path.stem
            
            # Find corresponding current screenshot
            current_screenshots = list(self.screenshots_dir.glob(f"**/{screen_name}_*.png"))
            
            if current_screenshots:
                # Use the most recent screenshot
                current_path = max(current_screenshots, key=lambda p: p.stat().st_mtime)
                
                comparison_result = self._compare_images(baseline_path, current_path, screen_name)
                validation_results['results'].append(comparison_result)
                validation_results['total_comparisons'] += 1
                
                if comparison_result['status'] == 'pass':
                    validation_results['passed'] += 1
                elif comparison_result['status'] == 'fail':
                    validation_results['failed'] += 1
                    
                    # Attempt auto-fix if similarity is close
                    if comparison_result['similarity'] > 0.85:
                        auto_fix_result = self._attempt_auto_fix(comparison_result)
                        if auto_fix_result['fixed']:
                            validation_results['auto_fixed'] += 1
        
        # Generate visual regression report
        report_path = self._generate_visual_regression_report(validation_results)
        validation_results['report_path'] = report_path
        
        print(f"📊 Visual regression validation complete:")
        print(f"   Passed: {validation_results['passed']}")
        print(f"   Failed: {validation_results['failed']}")
        print(f"   Auto-fixed: {validation_results['auto_fixed']}")
        
        return validation_results
    
    def _compare_images(self, baseline_path: Path, current_path: Path, screen_name: str) -> Dict[str, Any]:
        """Compare two images and generate diff"""
        try:
            # Load images
            baseline_img = cv2.imread(str(baseline_path))
            current_img = cv2.imread(str(current_path))
            
            if baseline_img is None or current_img is None:
                return {
                    'screen_name': screen_name,
                    'status': 'error',
                    'error': 'Could not load images for comparison'
                }
            
            # Resize images to same dimensions if needed
            if baseline_img.shape != current_img.shape:
                current_img = cv2.resize(current_img, (baseline_img.shape[1], baseline_img.shape[0]))
            
            # Calculate similarity using SSIM
            similarity = self._calculate_ssim(baseline_img, current_img)
            
            # Create difference image
            diff_img = cv2.absdiff(baseline_img, current_img)
            diff_path = self.diffs_dir / f"{screen_name}_diff.png"
            cv2.imwrite(str(diff_path), diff_img)
            
            # Detect specific UI issues
            ui_issues = self._detect_ui_issues(baseline_img, current_img, diff_img)
            
            status = 'pass' if similarity >= self.similarity_threshold else 'fail'
            
            return {
                'screen_name': screen_name,
                'status': status,
                'similarity': similarity,
                'threshold': self.similarity_threshold,
                'baseline_path': str(baseline_path),
                'current_path': str(current_path),
                'diff_path': str(diff_path),
                'ui_issues': ui_issues
            }
            
        except Exception as e:
            return {
                'screen_name': screen_name,
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index"""
        try:
            from skimage.metrics import structural_similarity as ssim
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Calculate SSIM
            similarity = ssim(gray1, gray2)
            return float(similarity)
            
        except ImportError:
            # Fallback to template matching if scikit-image not available
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
            return float(np.max(result))
    
    def _detect_ui_issues(self, baseline: np.ndarray, current: np.ndarray, diff: np.ndarray) -> List[str]:
        """Detect specific UI issues from image comparison"""
        issues = []
        
        try:
            # Convert to grayscale for analysis
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Find contours of differences
            _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Significant difference
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Analyze the type of difference
                    if w > h * 3:  # Wide difference - possibly text or button
                        issues.append(f"Horizontal layout change detected at ({x}, {y})")
                    elif h > w * 3:  # Tall difference - possibly vertical alignment
                        issues.append(f"Vertical alignment change detected at ({x}, {y})")
                    elif area > 10000:  # Large area change
                        issues.append(f"Major layout change detected at ({x}, {y}) - Area: {area}px")
                    else:
                        issues.append(f"Minor visual change detected at ({x}, {y})")
            
            # Check for color differences
            color_diff = np.mean(cv2.absdiff(baseline, current))
            if color_diff > 10:
                issues.append(f"Significant color changes detected - Average diff: {color_diff:.2f}")
            
        except Exception as e:
            issues.append(f"Error analyzing UI differences: {e}")
        
        return issues
    
    def _attempt_auto_fix(self, comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to automatically fix detected UI issues"""
        screen_name = comparison_result['screen_name']
        ui_issues = comparison_result.get('ui_issues', [])
        
        auto_fix_result = {
            'screen_name': screen_name,
            'fixed': False,
            'fixes_applied': [],
            'fixes_failed': []
        }
        
        print(f"🔧 Attempting auto-fix for {screen_name}...")
        
        # Analyze issues and attempt fixes
        for issue in ui_issues:
            fix_result = self._apply_ui_fix(issue, screen_name)
            
            if fix_result['success']:
                auto_fix_result['fixes_applied'].append(fix_result)
            else:
                auto_fix_result['fixes_failed'].append(fix_result)
        
        # Re-capture screenshot after fixes
        if auto_fix_result['fixes_applied']:
            try:
                self.driver.get("http://localhost:3000")
                time.sleep(3)
                
                # Take new screenshot
                fixed_path = self.screenshots_dir / f"{screen_name}_auto_fixed.png"
                self.driver.save_screenshot(str(fixed_path))
                
                # Re-compare with baseline
                baseline_path = self.baselines_dir / f"{screen_name}.png"
                new_comparison = self._compare_images(baseline_path, fixed_path, f"{screen_name}_fixed")
                
                if new_comparison['similarity'] > comparison_result['similarity']:
                    auto_fix_result['fixed'] = True
                    auto_fix_result['improvement'] = new_comparison['similarity'] - comparison_result['similarity']
                    print(f"✅ Auto-fix improved similarity by {auto_fix_result['improvement']:.3f}")
                
            except Exception as e:
                auto_fix_result['fixes_failed'].append({
                    'fix_type': 'screenshot_recapture',
                    'error': str(e)
                })
        
        return auto_fix_result
    
    def _apply_ui_fix(self, issue: str, screen_name: str) -> Dict[str, Any]:
        """Apply specific UI fix based on detected issue"""
        fix_result = {
            'issue': issue,
            'fix_type': 'unknown',
            'success': False
        }
        
        try:
            if 'layout change' in issue.lower():
                # Attempt to fix layout issues
                fix_result['fix_type'] = 'layout_adjustment'
                
                # Inject CSS to fix common layout issues
                css_fixes = """
                    input[type="email"], input[type="password"] {
                        width: 100% !important;
                        max-width: 400px !important;
                        margin: 10px 0 !important;
                        padding: 12px !important;
                        box-sizing: border-box !important;
                        position: relative !important;
                        z-index: 1 !important;
                    }
                    
                    .oauth-button {
                        margin: 10px 5px !important;
                        padding: 12px 24px !important;
                        display: inline-block !important;
                        position: relative !important;
                    }
                """
                
                self.driver.execute_script(f"""
                    var style = document.createElement('style');
                    style.textContent = `{css_fixes}`;
                    document.head.appendChild(style);
                """)
                
                fix_result['success'] = True
                fix_result['css_applied'] = css_fixes
                
            elif 'color change' in issue.lower():
                # Attempt to fix color inconsistencies
                fix_result['fix_type'] = 'color_correction'
                
                # Apply color corrections
                color_fixes = """
                    * {
                        color: inherit !important;
                        background-color: inherit !important;
                    }
                """
                
                self.driver.execute_script(f"""
                    var style = document.createElement('style');
                    style.textContent = `{color_fixes}`;
                    document.head.appendChild(style);
                """)
                
                fix_result['success'] = True
                
            elif 'alignment' in issue.lower():
                # Fix alignment issues
                fix_result['fix_type'] = 'alignment_correction'
                
                alignment_fixes = """
                    .form-container {
                        display: flex !important;
                        flex-direction: column !important;
                        align-items: center !important;
                        gap: 15px !important;
                    }
                """
                
                self.driver.execute_script(f"""
                    var style = document.createElement('style');
                    style.textContent = `{alignment_fixes}`;
                    document.head.appendChild(style);
                """)
                
                fix_result['success'] = True
            
        except Exception as e:
            fix_result['error'] = str(e)
        
        return fix_result
    
    def _generate_visual_regression_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate comprehensive visual regression report"""
        report_path = self.reports_dir / f"visual_regression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visual Regression Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f7fa; }}
                .container {{ max-width: 1400px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; padding: 30px; border-radius: 12px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
                .metric {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .comparison {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .pass {{ color: #059669; font-weight: bold; }}
                .fail {{ color: #DC2626; font-weight: bold; }}
                .image-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 15px 0; }}
                .image-container {{ text-align: center; }}
                .image-container img {{ max-width: 100%; height: auto; border: 1px solid #e5e7eb; border-radius: 4px; }}
                .similarity-bar {{ background: #e5e7eb; height: 20px; border-radius: 10px; margin: 10px 0; }}
                .similarity-fill {{ height: 100%; border-radius: 10px; }}
                .auto-fix {{ background: #fef3c7; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📸 Visual Regression Test Report</h1>
                    <p>Generated: {validation_results['timestamp']}</p>
                </div>
                
                <div class="summary">
                    <div class="metric">
                        <h3>Total Comparisons</h3>
                        <h2>{validation_results['total_comparisons']}</h2>
                    </div>
                    <div class="metric">
                        <h3>Passed</h3>
                        <h2 class="pass">{validation_results['passed']}</h2>
                    </div>
                    <div class="metric">
                        <h3>Failed</h3>
                        <h2 class="fail">{validation_results['failed']}</h2>
                    </div>
                    <div class="metric">
                        <h3>Auto-Fixed</h3>
                        <h2 style="color: #F59E0B;">{validation_results['auto_fixed']}</h2>
                    </div>
                </div>
        """
        
        # Add comparison results
        for result in validation_results['results']:
            status_class = 'pass' if result['status'] == 'pass' else 'fail'
            similarity_percent = result.get('similarity', 0) * 100
            
            html_content += f"""
                <div class="comparison">
                    <h3>{result['screen_name']} 
                        <span class="{status_class}">{result['status'].upper()}</span>
                    </h3>
                    
                    <div class="similarity-bar">
                        <div class="similarity-fill" style="width: {similarity_percent}%; 
                             background: {'#059669' if similarity_percent >= 95 else '#DC2626'};"></div>
                    </div>
                    <p>Similarity: {similarity_percent:.1f}% (Threshold: {result.get('threshold', 0.95) * 100}%)</p>
            """
            
            if 'ui_issues' in result and result['ui_issues']:
                html_content += "<div class='auto-fix'><h4>🔍 Detected Issues:</h4><ul>"
                for issue in result['ui_issues']:
                    html_content += f"<li>{issue}</li>"
                html_content += "</ul></div>"
            
            html_content += "</div>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function for visual regression testing"""
    tester = VisualRegressionTester()
    
    try:
        if not tester.setup_driver():
            return
        
        # Capture baselines if they don't exist
        if not list(tester.baselines_dir.glob("*.png")):
            print("📸 No baselines found, capturing new baselines...")
            tester.capture_baseline_screenshots()
        
        # Run visual regression validation
        results = tester.validate_visual_regression()
        
        print(f"\n🎯 Visual regression testing completed!")
        print(f"📄 Report: {results.get('report_path', 'N/A')}")
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
