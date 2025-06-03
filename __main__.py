#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for the LinkedIn Job Application Bot.

This script allows the bot to be run as a module:
python -m linkedin_job_bot

It parses command line arguments and runs the bot accordingly.
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Import local modules
try:
    from .linkedin_job_bot import LinkedInJobBot
    from .config import validate_config
except ImportError:
    # Handle case when running as standalone
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from linkedin_job_bot import LinkedInJobBot
    from config import validate_config


def main():
    """
    Main function to run the LinkedIn job application bot from the command line.
    """
    # Load environment variables
    load_dotenv()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Bot')
    parser.add_argument('--keywords', type=str, default=os.getenv('DEFAULT_KEYWORDS', 'Data Analyst'), 
                        help='Job keywords to search for')
    parser.add_argument('--location', type=str, default=os.getenv('DEFAULT_LOCATION', 'Remote'), 
                        help='Job location to search for')
    parser.add_argument('--max-applications', type=int, default=int(os.getenv('DEFAULT_MAX_APPLICATIONS', '20')), 
                        help='Maximum number of applications to submit')
    parser.add_argument('--headless', action='store_true', default=os.getenv('HEADLESS_MODE', 'False').lower() == 'true',
                        help='Run in headless mode')
    parser.add_argument('--gui', action='store_true',
                        help='Launch the graphical user interface')
    
    args = parser.parse_args()
    
    # If GUI flag is set, launch the GUI
    if args.gui:
        try:
            from gui import main as gui_main
            gui_main()
            return
        except ImportError:
            print("Error: GUI module not found. Running in command line mode.")
    
    # Validate configuration
    error = validate_config()
    if error:
        print(f"Configuration error: {error}")
        print("Please check your .env file or provide the necessary environment variables.")
        sys.exit(1)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("linkedin_bot.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info("Starting LinkedIn Job Application Bot")
    logger.info(f"Job Keywords: {args.keywords}")
    logger.info(f"Job Location: {args.location}")
    logger.info(f"Max Applications: {args.max_applications}")
    logger.info(f"Headless Mode: {args.headless}")
    
    try:
        # Create and run the bot
        bot = LinkedInJobBot(headless=args.headless)
        bot.run(args.keywords, args.location, args.max_applications)
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
