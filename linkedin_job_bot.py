#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LinkedIn Job Application Bot

This script automates the process of applying to jobs on LinkedIn using Selenium.
It logs in to LinkedIn, searches for jobs with specified criteria, and applies to
jobs with the "Easy Apply" button.
"""

import os
import time
import csv
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linkedin_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LinkedInJobBot:
    """
    A bot that automates applying to jobs on LinkedIn.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the LinkedIn Job Bot.
        
        Args:
            headless: Whether to run the browser in headless mode.
        """
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.phone_number = os.getenv("PHONE_NUMBER", "")
        self.resume_path = os.getenv("RESUME_PATH", "")
        
        if not self.email or not self.password:
            raise ValueError("LinkedIn email and password must be set in environment variables.")
        
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        self.applications_data = []
        
        # Create output directory if it doesn't exist
        Path("output").mkdir(exist_ok=True)
        
        # Initialize CSV file with headers if it doesn't exist
        self.csv_path = f"output/applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Job Title', 'Company', 'Location', 'Application Status', 
                    'Application Date', 'Job URL', 'Notes'
                ])
    
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """
        Set up the Chrome WebDriver.
        
        Args:
            headless: Whether to run the browser in headless mode.
            
        Returns:
            The configured WebDriver instance.
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Add additional options to make the browser more stable
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        
        # Add user agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def login(self) -> bool:
        """
        Log in to LinkedIn.
        
        Returns:
            True if login is successful, False otherwise.
        """
        try:
            logger.info("Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for the login page to load
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            
            # Enter email and password
            logger.info("Entering login credentials...")
            self.driver.find_element(By.ID, "username").send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            
            # Click login button
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for login to complete
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module")))
            
            logger.info("Successfully logged in to LinkedIn")
            return True
        
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to log in to LinkedIn: {str(e)}")
            return False
    
    def verify_login(self) -> bool:
        """
        Verify if already logged in to LinkedIn.
        
        Returns:
            True if already logged in, False otherwise.
        """
        try:
            logger.info("Navigating to LinkedIn homepage...")
            self.driver.get("https://www.linkedin.com/feed/")
            
            # Wait for a short time to see if we're redirected to login page
            time.sleep(3)
            
            # Check if we're on the login page
            if "/login" in self.driver.current_url:
                logger.info("Not logged in. Proceeding to login...")
                return self.login()
            
            # Check for an element that's only visible when logged in
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module")))
            logger.info("Already logged in to LinkedIn")
            return True
        
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Login verification failed: {str(e)}")
            logger.info("Attempting to log in...")
            return self.login()
    
    def navigate_to_jobs(self) -> bool:
        """
        Navigate to the LinkedIn Jobs page.
        
        Returns:
            True if navigation is successful, False otherwise.
        """
        try:
            logger.info("Navigating to LinkedIn Jobs page...")
            self.driver.get("https://www.linkedin.com/jobs/")
            
            # Wait for the jobs page to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-box")))
            
            logger.info("Successfully navigated to LinkedIn Jobs page")
            return True
        
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to navigate to LinkedIn Jobs page: {str(e)}")
            return False
    
    def search_jobs(self, keywords: str, location: str = "Remote", easy_apply_only: bool = True) -> bool:
        """
        Search for jobs with specified criteria.
        
        Args:
            keywords: Job keywords to search for.
            location: Job location to search for.
            easy_apply_only: Whether to filter for Easy Apply jobs only.
            
        Returns:
            True if search is successful, False otherwise.
        """
        try:
            logger.info(f"Searching for jobs with keywords: {keywords}, location: {location}")
            
            # Clear and enter keywords
            keywords_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
            ))
            keywords_input.clear()
            keywords_input.send_keys(keywords)
            
            # Clear and enter location
            location_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
            ))
            location_input.clear()
            location_input.send_keys(location)
            
            # Click search button
            search_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-tracking-control-name='public_jobs_jobs-search-bar_base-search-button']")
            ))
            search_button.click()
            
            # Wait for search results to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results")))
            
            # Apply Easy Apply filter if requested
            if easy_apply_only:
                logger.info("Applying 'Easy Apply' filter...")
                try:
                    # Click on the filters button
                    filters_button = self.wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button[aria-label='Filter by']")
                    ))
                    filters_button.click()
                    
                    # Wait for filter modal to appear
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".artdeco-modal")))
                    
                    # Click on Easy Apply checkbox
                    easy_apply_checkbox = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//label[contains(., 'Easy Apply')]")
                    ))
                    easy_apply_checkbox.click()
                    
                    # Click on Show results button
                    show_results_button = self.wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button[data-control-name='filter_pill_apply']")
                    ))
                    show_results_button.click()
                    
                    # Wait for filtered results to load
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results")))
                    
                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                    logger.warning(f"Failed to apply Easy Apply filter: {str(e)}")
            
            logger.info("Successfully searched for jobs")
            return True
        
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            logger.error(f"Failed to search for jobs: {str(e)}")
            return False
    
    def scroll_through_jobs(self, max_jobs: int = 100) -> List[Dict]:
        """
        Scroll through job listings and collect job data.
        
        Args:
            max_jobs: Maximum number of jobs to collect.
            
        Returns:
            List of job data dictionaries.
        """
        logger.info(f"Scrolling through job listings (max: {max_jobs})...")
        
        job_listings = []
        job_cards_selector = ".jobs-search-results__list-item"
        
        # Initial wait for job cards to load
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, job_cards_selector)))
        except TimeoutException:
            logger.error("No job listings found")
            return []
        
        # Scroll and collect job data
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        job_count = 0
        
        while job_count < max_jobs:
            # Get current job cards
            try:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, job_cards_selector)
            except NoSuchElementException:
                break
            
            # Process new job cards
            for i in range(job_count, min(len(job_cards), max_jobs)):
                try:
                    # Scroll to the job card
                    self.driver.execute_script("arguments[0].scrollIntoView();", job_cards[i])
                    time.sleep(random.uniform(0.5, 1.5))  # Random delay to avoid detection
                    
                    # Click on the job card to view details
                    job_cards[i].click()
                    time.sleep(random.uniform(1.0, 2.0))  # Wait for job details to load
                    
                    # Extract job data
                    job_data = self._extract_job_data()
                    if job_data:
                        job_listings.append(job_data)
                        job_count += 1
                        logger.info(f"Collected job {job_count}/{max_jobs}: {job_data['title']} at {job_data['company']}")
                
                except (StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException) as e:
                    logger.warning(f"Error processing job card {i}: {str(e)}")
                    continue
            
            # Scroll down to load more jobs
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.0, 2.0))  # Wait for new content to load
            
            # Check if we've reached the end of the page
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Try clicking "Show more jobs" button if available
                try:
                    show_more_button = self.driver.find_element(
                        By.CSS_SELECTOR, "button.infinite-scroller__show-more-button"
                    )
                    show_more_button.click()
                    time.sleep(random.uniform(1.0, 2.0))
                except NoSuchElementException:
                    logger.info("Reached end of job listings")
                    break
            
            last_height = new_height
        
        logger.info(f"Collected {len(job_listings)} job listings")
        return job_listings
    
    def _extract_job_data(self) -> Optional[Dict]:
        """
        Extract job data from the current job details page.
        
        Returns:
            Dictionary containing job data, or None if extraction failed.
        """
        try:
            # Wait for job details to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card")))
            
            # Extract job title
            title_element = self.driver.find_element(
                By.CSS_SELECTOR, ".jobs-unified-top-card__job-title"
            )
            title = title_element.text.strip()
            
            # Extract company name
            company_element = self.driver.find_element(
                By.CSS_SELECTOR, ".jobs-unified-top-card__company-name"
            )
            company = company_element.text.strip()
            
            # Extract location
            location_element = self.driver.find_element(
                By.CSS_SELECTOR, ".jobs-unified-top-card__bullet"
            )
            location = location_element.text.strip()
            
            # Check if Easy Apply button exists
            try:
                easy_apply_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-control-name='jobdetails_topcard_inapply']"
                )
                has_easy_apply = True
            except NoSuchElementException:
                has_easy_apply = False
            
            # Get job URL
            job_url = self.driver.current_url
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "has_easy_apply": has_easy_apply,
                "url": job_url
            }
        
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Failed to extract job data: {str(e)}")
            return None
    
    def apply_to_job(self, job_data: Dict) -> Tuple[bool, str]:
        """
        Apply to a job using Easy Apply.
        
        Args:
            job_data: Dictionary containing job data.
            
        Returns:
            Tuple of (success status, notes).
        """
        if not job_data.get("has_easy_apply", False):
            return False, "Not an Easy Apply job"
        
        try:
            logger.info(f"Applying to job: {job_data['title']} at {job_data['company']}")
            
            # Navigate to the job URL
            self.driver.get(job_data["url"])
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card")))
            
            # Click Easy Apply button
            easy_apply_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-control-name='jobdetails_topcard_inapply']")
            ))
            easy_apply_button.click()
            
            # Wait for application modal to appear
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-easy-apply-content")))
            
            # Process application steps
            return self._process_application_steps()
        
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            logger.error(f"Failed to apply to job: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def _process_application_steps(self) -> Tuple[bool, str]:
        """
        Process the steps in an Easy Apply application.
        
        Returns:
            Tuple of (success status, notes).
        """
        notes = []
        current_step = 1
        max_steps = 10  # Arbitrary limit to prevent infinite loops
        
        while current_step <= max_steps:
            try:
                # Check if we're on the review step
                review_button = self.driver.find_elements(
                    By.CSS_SELECTOR, "button[aria-label='Review your application']"
                )
                if review_button:
                    logger.info("Reviewing application...")
                    review_button[0].click()
                    time.sleep(random.uniform(1.0, 2.0))
                
                # Check if we're on the submit step
                submit_button = self.driver.find_elements(
                    By.CSS_SELECTOR, "button[aria-label='Submit application']"
                )
                if submit_button:
                    logger.info("Submitting application...")
                    submit_button[0].click()
                    
                    # Wait for confirmation
                    self.wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".artdeco-modal__content")
                    ))
                    
                    # Check for success message
                    success_elements = self.driver.find_elements(
                        By.XPATH, "//*[contains(text(), 'Application submitted')]"
                    )
                    if success_elements:
                        logger.info("Application submitted successfully")
                        
                        # Close the confirmation dialog
                        close_button = self.driver.find_element(
                            By.CSS_SELECTOR, "button[aria-label='Dismiss']"
                        )
                        close_button.click()
                        
                        return True, "Application submitted successfully"
                    else:
                        logger.warning("Application may not have been submitted")
                        notes.append("Submission status unclear")
                
                # Check for any required fields
                required_fields = self.driver.find_elements(
                    By.CSS_SELECTOR, ".artdeco-text-input--error"
                )
                if required_fields:
                    for field in required_fields:
                        field_id = field.get_attribute("id")
                        label_element = self.driver.find_element(
                            By.CSS_SELECTOR, f"label[for='{field_id}']"
                        )
                        field_name = label_element.text.strip()
                        notes.append(f"Required field: {field_name}")
                    
                    logger.warning(f"Application has required fields: {', '.join(notes)}")
                    
                    # Try to fill in phone number if it's required
                    phone_inputs = self.driver.find_elements(
                        By.CSS_SELECTOR, "input[type='tel']"
                    )
                    if phone_inputs and self.phone_number:
                        for phone_input in phone_inputs:
                            if not phone_input.get_attribute("value"):
                                phone_input.send_keys(self.phone_number)
                                notes.append("Filled in phone number")
                
                # Check for resume upload
                resume_uploads = self.driver.find_elements(
                    By.CSS_SELECTOR, "input[type='file']"
                )
                if resume_uploads and self.resume_path:
                    for upload in resume_uploads:
                        upload.send_keys(self.resume_path)
                        notes.append("Uploaded resume")
                        time.sleep(random.uniform(1.0, 2.0))
                
                # Check for follow/unfollow company checkbox
                follow_checkboxes = self.driver.find_elements(
                    By.CSS_SELECTOR, "label[for='follow-company-checkbox']"
                )
                if follow_checkboxes:
                    # Uncheck the box (we don't want to follow)
                    follow_checkboxes[0].click()
                    notes.append("Unchecked 'Follow company'")
                
                # Click the Next/Continue button
                next_button = self.driver.find_elements(
                    By.CSS_SELECTOR, "button[aria-label='Continue to next step']"
                )
                if next_button:
                    logger.info(f"Moving to step {current_step + 1}...")
                    next_button[0].click()
                    time.sleep(random.uniform(1.0, 2.0))
                    current_step += 1
                    continue
                
                # If we can't find a next button and we're not on the submit step,
                # we might be stuck or the application requires manual intervention
                if not submit_button:
                    logger.warning("Application requires manual intervention")
                    notes.append("Requires manual intervention")
                    
                    # Try to exit the application
                    exit_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR, "button[aria-label='Dismiss']"
                    )
                    if exit_buttons:
                        exit_buttons[0].click()
                        
                        # Confirm exit if prompted
                        time.sleep(1)
                        discard_buttons = self.driver.find_elements(
                            By.CSS_SELECTOR, "button[data-control-name='discard_application_confirm_btn']"
                        )
                        if discard_buttons:
                            discard_buttons[0].click()
                    
                    return False, "Application requires manual intervention: " + ", ".join(notes)
            
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                logger.warning(f"Error in application step {current_step}: {str(e)}")
                notes.append(f"Error in step {current_step}: {str(e)}")
                
                # Try to exit the application
                try:
                    exit_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR, "button[aria-label='Dismiss']"
                    )
                    if exit_buttons:
                        exit_buttons[0].click()
                        
                        # Confirm exit if prompted
                        time.sleep(1)
                        discard_buttons = self.driver.find_elements(
                            By.CSS_SELECTOR, "button[data-control-name='discard_application_confirm_btn']"
                        )
                        if discard_buttons:
                            discard_buttons[0].click()
                except Exception:
                    pass
                
                return False, "Error during application: " + ", ".join(notes)
        
        return False, "Application process took too many steps"
    
    def log_application(self, job_data: Dict, status: bool, notes: str) -> None:
        """
        Log application data to CSV file.
        
        Args:
            job_data: Dictionary containing job data.
            status: Whether the application was successful.
            notes: Notes about the application.
        """
        application_data = {
            'Job Title': job_data.get('title', 'Unknown'),
            'Company': job_data.get('company', 'Unknown'),
            'Location': job_data.get('location', 'Unknown'),
            'Application Status': 'Success' if status else 'Failed',
            'Application Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Job URL': job_data.get('url', ''),
            'Notes': notes
        }
        
        # Add to applications data list
        self.applications_data.append(application_data)
        
        # Write to CSV file
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                application_data['Job Title'],
                application_data['Company'],
                application_data['Location'],
                application_data['Application Status'],
                application_data['Application Date'],
                application_data['Job URL'],
                application_data['Notes']
            ])
        
        logger.info(f"Logged application for {application_data['Job Title']} at {application_data['Company']}")
    
    def run(self, keywords: str, location: str = "Remote", max_applications: int = 20) -> None:
        """
        Run the LinkedIn job application bot.
        
        Args:
            keywords: Job keywords to search for.
            location: Job location to search for.
            max_applications: Maximum number of applications to submit.
        """
        try:
            # Verify login or log in
            if not self.verify_login():
                logger.error("Failed to log in to LinkedIn. Exiting...")
                return
            
            # Navigate to jobs page
            if not self.navigate_to_jobs():
                logger.error("Failed to navigate to LinkedIn Jobs page. Exiting...")
                return
            
            # Search for jobs
            if not self.search_jobs(keywords, location, easy_apply_only=True):
                logger.error("Failed to search for jobs. Exiting...")
                return
            
            # Scroll through job listings
            job_listings = self.scroll_through_jobs(max_jobs=max_applications * 2)  # Get more than we need in case some fail
            
            # Apply to jobs
            application_count = 0
            for job_data in job_listings:
                if application_count >= max_applications:
                    break
                
                if job_data.get("has_easy_apply", False):
                    status, notes = self.apply_to_job(job_data)
                    self.log_application(job_data, status, notes)
                    
                    if status:
                        application_count += 1
                        logger.info(f"Successfully applied to job {application_count}/{max_applications}")
                    
                    # Add random delay between applications
                    time.sleep(random.uniform(3.0, 7.0))
            
            # Generate summary
            successful_applications = sum(1 for app in self.applications_data if app['Application Status'] == 'Success')
            failed_applications = len(self.applications_data) - successful_applications
            
            logger.info(f"Application process completed.")
            logger.info(f"Successful applications: {successful_applications}")
            logger.info(f"Failed applications: {failed_applications}")
            logger.info(f"Application data saved to: {self.csv_path}")
            
            # Create a summary DataFrame
            if self.applications_data:
                df = pd.DataFrame(self.applications_data)
                summary_path = f"output/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(summary_path, index=False)
                logger.info(f"Summary Excel file saved to: {summary_path}")
        
        finally:
            # Close the browser
            logger.info("Closing browser...")
            self.driver.quit()


def main():
    """
    Main function to run the LinkedIn job application bot.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Bot')
    parser.add_argument('--keywords', type=str, default='Data Analyst', 
                        help='Job keywords to search for')
    parser.add_argument('--location', type=str, default='Remote', 
                        help='Job location to search for')
    parser.add_argument('--max-applications', type=int, default=20, 
                        help='Maximum number of applications to submit')
    parser.add_argument('--headless', action='store_true', 
                        help='Run in headless mode')
    
    args = parser.parse_args()
    
    logger.info("Starting LinkedIn Job Application Bot")
    logger.info(f"Job Keywords: {args.keywords}")
    logger.info(f"Job Location: {args.location}")
    logger.info(f"Max Applications: {args.max_applications}")
    logger.info(f"Headless Mode: {args.headless}")
    
    bot = LinkedInJobBot(headless=args.headless)
    bot.run(args.keywords, args.location, args.max_applications)


if __name__ == "__main__":
    main()