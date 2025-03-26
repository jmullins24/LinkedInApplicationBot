#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration module for the LinkedIn Job Application Bot.

This module handles loading environment variables and provides default settings
for the bot. Users can customize these settings by creating a .env file.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# User information
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")
RESUME_PATH = os.getenv("RESUME_PATH", "")
COVER_LETTER_PATH = os.getenv("COVER_LETTER_PATH", "")

# Job search settings
DEFAULT_KEYWORDS = os.getenv("DEFAULT_KEYWORDS", "Data Analyst")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Remote")
DEFAULT_MAX_APPLICATIONS = int(os.getenv("DEFAULT_MAX_APPLICATIONS", "20"))

# Browser settings
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "10"))

# Application settings
WAIT_TIME_MIN = float(os.getenv("WAIT_TIME_MIN", "1.0"))
WAIT_TIME_MAX = float(os.getenv("WAIT_TIME_MAX", "3.0"))
FOLLOW_COMPANIES = os.getenv("FOLLOW_COMPANIES", "False").lower() == "true"

# Output settings
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Application questions defaults
DEFAULT_ANSWERS = {
    "years_of_experience": os.getenv("DEFAULT_YEARS_EXPERIENCE", "2"),
    "education_level": os.getenv("DEFAULT_EDUCATION", "Bachelor's"),
    "willing_to_relocate": os.getenv("WILLING_TO_RELOCATE", "No"),
    "require_sponsorship": os.getenv("REQUIRE_SPONSORSHIP", "No"),
    "remote_work": os.getenv("REMOTE_WORK", "Yes"),
}

# Create output directory if it doesn't exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)


def get_config() -> Dict[str, Any]:
    """
    Get the configuration as a dictionary.
    
    Returns:
        Dictionary containing all configuration settings.
    """
    return {
        "linkedin": {
            "email": LINKEDIN_EMAIL,
            "password": LINKEDIN_PASSWORD,
        },
        "user": {
            "phone_number": PHONE_NUMBER,
            "resume_path": RESUME_PATH,
            "cover_letter_path": COVER_LETTER_PATH,
        },
        "search": {
            "keywords": DEFAULT_KEYWORDS,
            "location": DEFAULT_LOCATION,
            "max_applications": DEFAULT_MAX_APPLICATIONS,
        },
        "browser": {
            "headless": HEADLESS_MODE,
            "timeout": BROWSER_TIMEOUT,
        },
        "application": {
            "wait_time_min": WAIT_TIME_MIN,
            "wait_time_max": WAIT_TIME_MAX,
            "follow_companies": FOLLOW_COMPANIES,
            "default_answers": DEFAULT_ANSWERS,
        },
        "output": {
            "dir": OUTPUT_DIR,
            "log_level": LOG_LEVEL,
        },
    }


def validate_config() -> Optional[str]:
    """
    Validate the configuration.
    
    Returns:
        Error message if configuration is invalid, None otherwise.
    """
    if not LINKEDIN_EMAIL:
        return "LinkedIn email is not set. Please set the LINKEDIN_EMAIL environment variable."
    
    if not LINKEDIN_PASSWORD:
        return "LinkedIn password is not set. Please set the LINKEDIN_PASSWORD environment variable."
    
    if RESUME_PATH and not os.path.exists(RESUME_PATH):
        return f"Resume file not found at {RESUME_PATH}. Please check the RESUME_PATH environment variable."
    
    if COVER_LETTER_PATH and not os.path.exists(COVER_LETTER_PATH):
        return f"Cover letter file not found at {COVER_LETTER_PATH}. Please check the COVER_LETTER_PATH environment variable."
    
    return None


def create_env_template(output_path: str = ".env.template") -> None:
    """
    Create a template .env file with all available configuration options.
    
    Args:
        output_path: Path to write the template file.
    """
    template = """# LinkedIn Job Application Bot Configuration

# LinkedIn credentials
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

# User information
PHONE_NUMBER=1234567890
RESUME_PATH=path/to/your/resume.pdf
COVER_LETTER_PATH=path/to/your/cover_letter.pdf

# Job search settings
DEFAULT_KEYWORDS=Data Analyst
DEFAULT_LOCATION=Remote
DEFAULT_MAX_APPLICATIONS=20

# Browser settings
HEADLESS_MODE=False
BROWSER_TIMEOUT=10

# Application settings
WAIT_TIME_MIN=1.0
WAIT_TIME_MAX=3.0
FOLLOW_COMPANIES=False

# Output settings
OUTPUT_DIR=output
LOG_LEVEL=INFO

# Default answers for application questions
DEFAULT_YEARS_EXPERIENCE=2
DEFAULT_EDUCATION=Bachelor's
WILLING_TO_RELOCATE=No
REQUIRE_SPONSORSHIP=No
REMOTE_WORK=Yes
"""
    
    with open(output_path, "w") as f:
        f.write(template)
    
    print(f"Created environment template at {output_path}")


if __name__ == "__main__":
    # If this script is run directly, create a template .env file
    create_env_template()