from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests
from config import settings


class JobPlatformHandler(ABC):
    """Abstract base class for job platform handlers"""
    
    @abstractmethod
    async def apply_to_job(self, job_url: str, credentials: Any, cover_letter: Optional[str] = None) -> Dict[str, Any]:
        """Apply to a job on the platform"""
        pass
    
    @abstractmethod
    async def search_jobs(self, keywords: str, location: str = "", **kwargs) -> list:
        """Search for jobs on the platform"""
        pass


class LinkedInHandler(JobPlatformHandler):
    """LinkedIn job application handler"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com"
    
    async def apply_to_job(self, job_url: str, credentials: Any, cover_letter: Optional[str] = None) -> Dict[str, Any]:
        """Apply to LinkedIn job using Selenium automation"""
        try:
            # Setup Chrome driver
            chrome_options = Options()
            if settings.webdriver_headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(settings.webdriver_timeout)
            
            try:
                # Login to LinkedIn
                await self._login_linkedin(driver, credentials)
                
                # Navigate to job page
                driver.get(job_url)
                time.sleep(3)
                
                # Find and click apply button
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply') or contains(text(), 'Easy Apply')]"))
                )
                apply_button.click()
                
                # Handle application form
                await self._fill_application_form(driver, cover_letter)
                
                return {
                    "status": "success",
                    "message": "Successfully applied to LinkedIn job",
                    "platform": "LinkedIn"
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to apply to LinkedIn job: {str(e)}",
                "platform": "LinkedIn"
            }
    
    async def search_jobs(self, keywords: str, location: str = "", **kwargs) -> list:
        """Search for jobs on LinkedIn"""
        # This would implement LinkedIn job search
        # For now, return mock data
        return [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "location": location or "Remote",
                "url": "https://linkedin.com/jobs/view/123456",
                "description": "We are looking for a senior software engineer..."
            }
        ]
    
    async def _login_linkedin(self, driver, credentials):
        """Login to LinkedIn"""
        driver.get(f"{self.base_url}/login")
        
        # Enter credentials
        email_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        email_field.send_keys(self._decrypt_credential(credentials.username))
        password_field.send_keys(self._decrypt_credential(credentials.password))
        
        # Submit login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
        )
    
    async def _fill_application_form(self, driver, cover_letter: Optional[str]):
        """Fill out LinkedIn application form"""
        try:
            # Wait for form to load
            time.sleep(2)
            
            # If cover letter field exists, fill it
            if cover_letter:
                try:
                    cover_letter_field = driver.find_element(By.XPATH, "//textarea[contains(@placeholder, 'cover letter') or contains(@placeholder, 'message')]")
                    cover_letter_field.clear()
                    cover_letter_field.send_keys(cover_letter)
                except:
                    pass  # Cover letter field might not exist
            
            # Submit application
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Send')]"))
            )
            submit_button.click()
            
            # Wait for confirmation
            time.sleep(3)
            
        except Exception as e:
            print(f"Error filling application form: {e}")
    
    def _decrypt_credential(self, encrypted_data: str) -> str:
        """Decrypt credential data"""
        from cryptography.fernet import Fernet
        # This should use the same encryption key as other services
        key = settings.encryption_key.encode() if hasattr(settings, 'encryption_key') else Fernet.generate_key()
        fernet = Fernet(key)
        try:
            return fernet.decrypt(encrypted_data.encode()).decode()
        except:
            return encrypted_data  # Return as-is if decryption fails


class NaukriHandler(JobPlatformHandler):
    """Naukri job application handler"""
    
    def __init__(self):
        self.base_url = "https://www.naukri.com"
    
    async def apply_to_job(self, job_url: str, credentials: Any, cover_letter: Optional[str] = None) -> Dict[str, Any]:
        """Apply to Naukri job using Selenium automation"""
        try:
            # Setup Chrome driver
            chrome_options = Options()
            if settings.webdriver_headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(settings.webdriver_timeout)
            
            try:
                # Login to Naukri
                await self._login_naukri(driver, credentials)
                
                # Navigate to job page
                driver.get(job_url)
                time.sleep(3)
                
                # Find and click apply button
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply')]"))
                )
                apply_button.click()
                
                # Handle application confirmation
                time.sleep(2)
                
                return {
                    "status": "success",
                    "message": "Successfully applied to Naukri job",
                    "platform": "Naukri"
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to apply to Naukri job: {str(e)}",
                "platform": "Naukri"
            }
    
    async def search_jobs(self, keywords: str, location: str = "", **kwargs) -> list:
        """Search for jobs on Naukri"""
        # This would implement Naukri job search
        # For now, return mock data
        return [
            {
                "title": "Software Developer",
                "company": "Indian Tech Company",
                "location": location or "Bangalore",
                "url": "https://naukri.com/job-listings/123456",
                "description": "Looking for experienced software developer..."
            }
        ]
    
    async def _login_naukri(self, driver, credentials):
        """Login to Naukri"""
        driver.get(f"{self.base_url}/nlogin/login")
        
        # Enter credentials
        email_field = driver.find_element(By.ID, "usernameField")
        password_field = driver.find_element(By.ID, "passwordField")
        
        email_field.send_keys(self._decrypt_credential(credentials.username))
        password_field.send_keys(self._decrypt_credential(credentials.password))
        
        # Submit login
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nI-gNb-drawer"))
        )
    
    def _decrypt_credential(self, encrypted_data: str) -> str:
        """Decrypt credential data"""
        from cryptography.fernet import Fernet
        key = settings.encryption_key.encode() if hasattr(settings, 'encryption_key') else Fernet.generate_key()
        fernet = Fernet(key)
        try:
            return fernet.decrypt(encrypted_data.encode()).decode()
        except:
            return encrypted_data
