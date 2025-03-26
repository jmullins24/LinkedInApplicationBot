#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility functions for the LinkedIn Job Application Bot.

This module provides helper functions for common tasks such as random delays,
logging, and handling specific application scenarios.
"""

import os
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """
    Wait for a random amount of time to simulate human behavior.
    
    Args:
        min_seconds: Minimum wait time in seconds.
        max_seconds: Maximum wait time in seconds.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def setup_logger(name: str, log_file: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name.
        log_file: Path to log file.
        level: Logging level.
        
    Returns:
        Configured logger.
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Convert level string to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set formatter for handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def safe_click(driver: webdriver.Chrome, element: WebElement, wait_time: float = 1.0) -> bool:
    """
    Safely click an element with error handling.
    
    Args:
        driver: Selenium WebDriver instance.
        element: Element to click.
        wait_time: Time to wait after clicking.
        
    Returns:
        True if click was successful, False otherwise.
    """
    try:
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        random_delay(0.5, 1.0)
        
        # Try to click the element
        element.click()
        random_delay(wait_time, wait_time + 1.0)
        return True
    
    except (ElementClickInterceptedException, StaleElementReferenceException) as e:
        try:
            # Try JavaScript click as a fallback
            driver.execute_script("arguments[0].click();", element)
            random_delay(wait_time, wait_time + 1.0)
            return True
        
        except Exception as js_error:
            logging.warning(f"Failed to click element: {str(e)}, JS fallback error: {str(js_error)}")
            return False


def wait_for_element(
    driver: webdriver.Chrome, 
    locator: Tuple[By, str], 
    timeout: int = 10,
    condition: str = "presence"
) -> Optional[WebElement]:
    """
    Wait for an element to be present or clickable.
    
    Args:
        driver: Selenium WebDriver instance.
        locator: Tuple of (By, selector).
        timeout: Maximum time to wait in seconds.
        condition: 'presence' or 'clickable'.
        
    Returns:
        The element if found, None otherwise.
    """
    try:
        wait = WebDriverWait(driver, timeout)
        
        if condition == "clickable":
            element = wait.until(EC.element_to_be_clickable(locator))
        else:  # Default to presence
            element = wait.until(EC.presence_of_element_located(locator))
        
        return element
    
    except TimeoutException:
        logging.warning(f"Timed out waiting for element: {locator}")
        return None


def fill_text_field(
    driver: webdriver.Chrome, 
    locator: Tuple[By, str], 
    text: str, 
    clear_first: bool = True
) -> bool:
    """
    Fill a text field with the given text.
    
    Args:
        driver: Selenium WebDriver instance.
        locator: Tuple of (By, selector).
        text: Text to enter.
        clear_first: Whether to clear the field first.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        element = wait_for_element(driver, locator)
        if not element:
            return False
        
        if clear_first:
            element.clear()
        
        element.send_keys(text)
        return True
    
    except Exception as e:
        logging.warning(f"Failed to fill text field {locator}: {str(e)}")
        return False


def select_dropdown_option(
    driver: webdriver.Chrome, 
    locator: Tuple[By, str], 
    option_text: str
) -> bool:
    """
    Select an option from a dropdown by visible text.
    
    Args:
        driver: Selenium WebDriver instance.
        locator: Tuple of (By, selector).
        option_text: Text of the option to select.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        element = wait_for_element(driver, locator)
        if not element:
            return False
        
        select = Select(element)
        select.select_by_visible_text(option_text)
        return True
    
    except Exception as e:
        logging.warning(f"Failed to select dropdown option {option_text} for {locator}: {str(e)}")
        return False


def check_radio_or_checkbox(
    driver: webdriver.Chrome, 
    locator: Tuple[By, str], 
    check: bool = True
) -> bool:
    """
    Check or uncheck a radio button or checkbox.
    
    Args:
        driver: Selenium WebDriver instance.
        locator: Tuple of (By, selector).
        check: Whether to check (True) or uncheck (False).
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        element = wait_for_element(driver, locator)
        if not element:
            return False
        
        # Check if the element is already in the desired state
        if element.is_selected() != check:
            return safe_click(driver, element)
        
        return True  # Already in desired state
    
    except Exception as e:
        logging.warning(f"Failed to {'check' if check else 'uncheck'} element {locator}: {str(e)}")
        return False


def is_element_present(driver: webdriver.Chrome, locator: Tuple[By, str]) -> bool:
    """
    Check if an element is present on the page.
    
    Args:
        driver: Selenium WebDriver instance.
        locator: Tuple of (By, selector).
        
    Returns:
        True if element is present, False otherwise.
    """
    try:
        driver.find_element(locator[0], locator[1])
        return True
    except NoSuchElementException:
        return False


def save_to_csv(data: List[Dict], filepath: str, append: bool = False) -> None:
    """
    Save data to a CSV file.
    
    Args:
        data: List of dictionaries to save.
        filepath: Path to save the CSV file.
        append: Whether to append to an existing file.
    """
    mode = 'a' if append and os.path.exists(filepath) else 'w'
    write_header = mode == 'w' or not os.path.exists(filepath)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Write to CSV
    df = pd.DataFrame(data)
    df.to_csv(filepath, mode=mode, header=write_header, index=False)


def save_to_excel(data: List[Dict], filepath: str) -> None:
    """
    Save data to an Excel file.
    
    Args:
        data: List of dictionaries to save.
        filepath: Path to save the Excel file.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Write to Excel
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False)


def create_timestamp_filename(prefix: str, extension: str) -> str:
    """
    Create a filename with a timestamp.
    
    Args:
        prefix: Prefix for the filename.
        extension: File extension.
        
    Returns:
        Filename with timestamp.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"


def extract_text_safely(element: Optional[WebElement]) -> str:
    """
    Safely extract text from an element.
    
    Args:
        element: WebElement to extract text from.
        
    Returns:
        Text from the element, or empty string if element is None.
    """
    if element is None:
        return ""
    
    try:
        return element.text.strip()
    except Exception:
        return ""


def parse_boolean_response(text: str) -> bool:
    """
    Parse a text response as a boolean.
    
    Args:
        text: Text to parse.
        
    Returns:
        True for "yes", "true", "y", "1", etc., False otherwise.
    """
    text = text.lower().strip()
    return text in ["yes", "true", "y", "1", "t"]


def get_answer_for_question(question: str, default_answers: Dict[str, str]) -> Optional[str]:
    """
    Get an answer for a common application question.
    
    Args:
        question: The question text.
        default_answers: Dictionary of default answers.
        
    Returns:
        Answer for the question, or None if no match found.
    """
    question = question.lower()
    
    # Experience questions
    if any(kw in question for kw in ["years of experience", "how long", "work experience"]):
        return default_answers.get("years_of_experience")
    
    # Education questions
    if any(kw in question for kw in ["education", "degree", "qualification"]):
        return default_answers.get("education_level")
    
    # Relocation questions
    if any(kw in question for kw in ["relocate", "relocation", "willing to move"]):
        return default_answers.get("willing_to_relocate")
    
    # Sponsorship questions
    if any(kw in question for kw in ["sponsorship", "visa", "work authorization"]):
        return default_answers.get("require_sponsorship")
    
    # Remote work questions
    if any(kw in question for kw in ["remote", "work from home", "telecommute"]):
        return default_answers.get("remote_work")
    
    return None


def take_screenshot(driver: webdriver.Chrome, filepath: str) -> None:
    """
    Take a screenshot of the current browser window.
    
    Args:
        driver: Selenium WebDriver instance.
        filepath: Path to save the screenshot.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Take screenshot
    driver.save_screenshot(filepath)
    logging.info(f"Screenshot saved to {filepath}")