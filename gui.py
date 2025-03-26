#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Graphical User Interface for the LinkedIn Job Application Bot.

This module provides a simple GUI for configuring and running the LinkedIn job
application bot. It allows users to enter search keywords, filters, and other
settings without having to modify the code or environment variables.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Optional, Callable

from dotenv import load_dotenv

# Import local modules
try:
    from config import get_config, validate_config
    from linkedin_job_bot import LinkedInJobBot
except ImportError:
    # Handle case when running as standalone
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from linkedin_job_bot.config import get_config, validate_config
    from linkedin_job_bot.linkedin_job_bot import LinkedInJobBot


class LinkedInJobBotGUI:
    """
    GUI for the LinkedIn Job Application Bot.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("LinkedIn Job Application Bot")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Load configuration
        load_dotenv()
        self.config = get_config()
        
        # Create variables for form fields
        self.email_var = tk.StringVar(value=self.config["linkedin"]["email"] or "")
        self.password_var = tk.StringVar(value=self.config["linkedin"]["password"] or "")
        self.phone_var = tk.StringVar(value=self.config["user"]["phone_number"] or "")
        self.resume_path_var = tk.StringVar(value=self.config["user"]["resume_path"] or "")
        self.cover_letter_path_var = tk.StringVar(value=self.config["user"]["cover_letter_path"] or "")
        self.keywords_var = tk.StringVar(value=self.config["search"]["keywords"] or "")
        self.location_var = tk.StringVar(value=self.config["search"]["location"] or "")
        self.max_applications_var = tk.IntVar(value=self.config["search"]["max_applications"])
        self.headless_var = tk.BooleanVar(value=self.config["browser"]["headless"])
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_credentials_tab()
        self.create_search_tab()
        self.create_settings_tab()
        self.create_log_tab()
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create buttons
        self.start_button = ttk.Button(
            self.buttons_frame, 
            text="Start Job Application Bot", 
            command=self.start_bot
        )
        self.start_button.pack(side=tk.RIGHT, padx=5)
        
        self.save_button = ttk.Button(
            self.buttons_frame, 
            text="Save Settings", 
            command=self.save_settings
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # Initialize log text
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "LinkedIn Job Application Bot\n")
        self.log_text.insert(tk.END, "Please configure your settings and click 'Start Job Application Bot'\n")
        self.log_text.config(state=tk.DISABLED)
        
        # Bot instance and thread
        self.bot = None
        self.bot_thread = None
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_credentials_tab(self) -> None:
        """
        Create the credentials tab.
        """
        credentials_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(credentials_frame, text="Credentials")
        
        # LinkedIn credentials
        ttk.Label(credentials_frame, text="LinkedIn Credentials", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        ttk.Label(credentials_frame, text="Email:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(credentials_frame, textvariable=self.email_var, width=40).grid(
            row=1, column=1, sticky=tk.W, pady=2
        )
        
        ttk.Label(credentials_frame, text="Password:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(credentials_frame, textvariable=self.password_var, show="*", width=40).grid(
            row=2, column=1, sticky=tk.W, pady=2
        )
        
        # User information
        ttk.Label(credentials_frame, text="User Information", font=("", 12, "bold")).grid(
            row=3, column=0, columnspan=3, sticky=tk.W, pady=(20, 10)
        )
        
        ttk.Label(credentials_frame, text="Phone Number:").grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(credentials_frame, textvariable=self.phone_var, width=40).grid(
            row=4, column=1, sticky=tk.W, pady=2
        )
        
        ttk.Label(credentials_frame, text="Resume:").grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        resume_frame = ttk.Frame(credentials_frame)
        resume_frame.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Entry(resume_frame, textvariable=self.resume_path_var, width=30).pack(
            side=tk.LEFT
        )
        ttk.Button(resume_frame, text="Browse...", command=lambda: self.browse_file(
            self.resume_path_var, "Select Resume", [("PDF files", "*.pdf"), ("All files", "*.*")]
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(credentials_frame, text="Cover Letter:").grid(
            row=6, column=0, sticky=tk.W, pady=2
        )
        cover_letter_frame = ttk.Frame(credentials_frame)
        cover_letter_frame.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        ttk.Entry(cover_letter_frame, textvariable=self.cover_letter_path_var, width=30).pack(
            side=tk.LEFT
        )
        ttk.Button(cover_letter_frame, text="Browse...", command=lambda: self.browse_file(
            self.cover_letter_path_var, "Select Cover Letter", [("PDF files", "*.pdf"), ("All files", "*.*")]
        )).pack(side=tk.LEFT, padx=5)
        
        # Add some space at the bottom
        ttk.Label(credentials_frame, text="").grid(row=7, column=0, pady=20)
    
    def create_search_tab(self) -> None:
        """
        Create the search tab.
        """
        search_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(search_frame, text="Job Search")
        
        # Job search settings
        ttk.Label(search_frame, text="Job Search Settings", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        ttk.Label(search_frame, text="Keywords:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(search_frame, textvariable=self.keywords_var, width=40).grid(
            row=1, column=1, sticky=tk.W, pady=2
        )
        
        ttk.Label(search_frame, text="Location:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(search_frame, textvariable=self.location_var, width=40).grid(
            row=2, column=1, sticky=tk.W, pady=2
        )
        
        ttk.Label(search_frame, text="Max Applications:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        ttk.Spinbox(search_frame, from_=1, to=100, textvariable=self.max_applications_var, width=5).grid(
            row=3, column=1, sticky=tk.W, pady=2
        )
        
        # Filters
        ttk.Label(search_frame, text="Filters", font=("", 12, "bold")).grid(
            row=4, column=0, columnspan=3, sticky=tk.W, pady=(20, 10)
        )
        
        # Easy Apply only checkbox
        self.easy_apply_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_frame, text="Easy Apply Only", variable=self.easy_apply_var).grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        
        # Experience level
        ttk.Label(search_frame, text="Experience Level:").grid(
            row=6, column=0, sticky=tk.W, pady=2
        )
        
        self.experience_level_var = tk.StringVar(value="All")
        experience_frame = ttk.Frame(search_frame)
        experience_frame.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        experience_options = ["All", "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]
        experience_dropdown = ttk.Combobox(experience_frame, textvariable=self.experience_level_var, values=experience_options, width=20)
        experience_dropdown.pack(side=tk.LEFT)
        
        # Job type
        ttk.Label(search_frame, text="Job Type:").grid(
            row=7, column=0, sticky=tk.W, pady=2
        )
        
        self.job_type_var = tk.StringVar(value="All")
        job_type_frame = ttk.Frame(search_frame)
        job_type_frame.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        job_type_options = ["All", "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship"]
        job_type_dropdown = ttk.Combobox(job_type_frame, textvariable=self.job_type_var, values=job_type_options, width=20)
        job_type_dropdown.pack(side=tk.LEFT)
        
        # Date posted
        ttk.Label(search_frame, text="Date Posted:").grid(
            row=8, column=0, sticky=tk.W, pady=2
        )
        
        self.date_posted_var = tk.StringVar(value="Any time")
        date_posted_frame = ttk.Frame(search_frame)
        date_posted_frame.grid(row=8, column=1, sticky=tk.W, pady=2)
        
        date_posted_options = ["Any time", "Past 24 hours", "Past week", "Past month"]
        date_posted_dropdown = ttk.Combobox(date_posted_frame, textvariable=self.date_posted_var, values=date_posted_options, width=20)
        date_posted_dropdown.pack(side=tk.LEFT)
        
        # Add some space at the bottom
        ttk.Label(search_frame, text="").grid(row=9, column=0, pady=20)
    
    def create_settings_tab(self) -> None:
        """
        Create the settings tab.
        """
        settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(settings_frame, text="Settings")
        
        # Browser settings
        ttk.Label(settings_frame, text="Browser Settings", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        ttk.Checkbutton(settings_frame, text="Headless Mode (run browser in background)", variable=self.headless_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=2
        )
        
        # Application settings
        ttk.Label(settings_frame, text="Application Settings", font=("", 12, "bold")).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(20, 10)
        )
        
        # Follow companies checkbox
        self.follow_companies_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Follow Companies After Applying", variable=self.follow_companies_var).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=2
        )
        
        # Default answers for common questions
        ttk.Label(settings_frame, text="Default Answers for Common Questions", font=("", 12, "bold")).grid(
            row=4, column=0, columnspan=3, sticky=tk.W, pady=(20, 10)
        )
        
        # Years of experience
        ttk.Label(settings_frame, text="Years of Experience:").grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        self.years_experience_var = tk.StringVar(value=self.config["application"]["default_answers"]["years_of_experience"])
        ttk.Entry(settings_frame, textvariable=self.years_experience_var, width=10).grid(
            row=5, column=1, sticky=tk.W, pady=2
        )
        
        # Education level
        ttk.Label(settings_frame, text="Education Level:").grid(
            row=6, column=0, sticky=tk.W, pady=2
        )
        self.education_level_var = tk.StringVar(value=self.config["application"]["default_answers"]["education_level"])
        education_options = ["High School", "Associate's", "Bachelor's", "Master's", "Doctorate"]
        education_dropdown = ttk.Combobox(settings_frame, textvariable=self.education_level_var, values=education_options, width=15)
        education_dropdown.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Willing to relocate
        ttk.Label(settings_frame, text="Willing to Relocate:").grid(
            row=7, column=0, sticky=tk.W, pady=2
        )
        self.relocate_var = tk.StringVar(value=self.config["application"]["default_answers"]["willing_to_relocate"])
        relocate_frame = ttk.Frame(settings_frame)
        relocate_frame.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(relocate_frame, text="Yes", variable=self.relocate_var, value="Yes").pack(side=tk.LEFT)
        ttk.Radiobutton(relocate_frame, text="No", variable=self.relocate_var, value="No").pack(side=tk.LEFT, padx=10)
        
        # Require sponsorship
        ttk.Label(settings_frame, text="Require Sponsorship:").grid(
            row=8, column=0, sticky=tk.W, pady=2
        )
        self.sponsorship_var = tk.StringVar(value=self.config["application"]["default_answers"]["require_sponsorship"])
        sponsorship_frame = ttk.Frame(settings_frame)
        sponsorship_frame.grid(row=8, column=1, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(sponsorship_frame, text="Yes", variable=self.sponsorship_var, value="Yes").pack(side=tk.LEFT)
        ttk.Radiobutton(sponsorship_frame, text="No", variable=self.sponsorship_var, value="No").pack(side=tk.LEFT, padx=10)
        
        # Remote work
        ttk.Label(settings_frame, text="Remote Work:").grid(
            row=9, column=0, sticky=tk.W, pady=2
        )
        self.remote_work_var = tk.StringVar(value=self.config["application"]["default_answers"]["remote_work"])
        remote_frame = ttk.Frame(settings_frame)
        remote_frame.grid(row=9, column=1, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(remote_frame, text="Yes", variable=self.remote_work_var, value="Yes").pack(side=tk.LEFT)
        ttk.Radiobutton(remote_frame, text="No", variable=self.remote_work_var, value="No").pack(side=tk.LEFT, padx=10)
        
        # Add some space at the bottom
        ttk.Label(settings_frame, text="").grid(row=10, column=0, pady=20)
    
    def create_log_tab(self) -> None:
        """
        Create the log tab.
        """
        log_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(log_frame, text="Log")
        
        # Create log text widget with scrollbar
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)  # Make it read-only
    
    def browse_file(self, var: tk.StringVar, title: str, filetypes: list) -> None:
        """
        Open a file browser dialog and update the variable with the selected file path.
        
        Args:
            var: StringVar to update with the file path.
            title: Dialog title.
            filetypes: List of file type tuples.
        """
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        if filename:
            var.set(filename)
    
    def save_settings(self) -> None:
        """
        Save the current settings to the .env file.
        """
        try:
            # Create .env content
            env_content = f"""# LinkedIn Job Application Bot Configuration

# LinkedIn credentials
LINKEDIN_EMAIL={self.email_var.get()}
LINKEDIN_PASSWORD={self.password_var.get()}

# User information
PHONE_NUMBER={self.phone_var.get()}
RESUME_PATH={self.resume_path_var.get()}
COVER_LETTER_PATH={self.cover_letter_path_var.get()}

# Job search settings
DEFAULT_KEYWORDS={self.keywords_var.get()}
DEFAULT_LOCATION={self.location_var.get()}
DEFAULT_MAX_APPLICATIONS={self.max_applications_var.get()}

# Browser settings
HEADLESS_MODE={str(self.headless_var.get())}
BROWSER_TIMEOUT=10

# Application settings
WAIT_TIME_MIN=1.0
WAIT_TIME_MAX=3.0
FOLLOW_COMPANIES={str(self.follow_companies_var.get())}

# Output settings
OUTPUT_DIR=output
LOG_LEVEL=INFO

# Default answers for application questions
DEFAULT_YEARS_EXPERIENCE={self.years_experience_var.get()}
DEFAULT_EDUCATION={self.education_level_var.get()}
WILLING_TO_RELOCATE={self.relocate_var.get()}
REQUIRE_SPONSORSHIP={self.sponsorship_var.get()}
REMOTE_WORK={self.remote_work_var.get()}
"""
            
            # Write to .env file
            with open(".env", "w") as f:
                f.write(env_content)
            
            # Show success message
            messagebox.showinfo("Settings Saved", "Settings have been saved to .env file.")
            
            # Update log
            self.update_log("Settings saved to .env file.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            self.update_log(f"Error saving settings: {str(e)}")
    
    def update_log(self, message: str) -> None:
        """
        Update the log text widget with a new message.
        
        Args:
            message: Message to add to the log.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)  # Scroll to the end
        self.log_text.config(state=tk.DISABLED)
    
    def start_bot(self) -> None:
        """
        Start the LinkedIn job application bot in a separate thread.
        """
        # Validate settings
        error = validate_config()
        if error:
            messagebox.showerror("Configuration Error", error)
            self.update_log(f"Error: {error}")
            return
        
        # Check if bot is already running
        if self.bot_thread and self.bot_thread.is_alive():
            messagebox.showinfo("Bot Running", "The bot is already running.")
            return
        
        # Update UI
        self.start_button.config(text="Running...", state=tk.DISABLED)
        self.update_log("Starting LinkedIn Job Application Bot...")
        
        # Create and start bot thread
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def run_bot(self) -> None:
        """
        Run the LinkedIn job application bot.
        This method is executed in a separate thread.
        """
        try:
            # Create bot instance
            self.bot = LinkedInJobBot(headless=self.headless_var.get())
            
            # Set up logging to GUI
            original_info = self.bot.logger.info
            original_warning = self.bot.logger.warning
            original_error = self.bot.logger.error
            
            def log_to_gui(original_func, message):
                original_func(message)
                self.root.after(0, lambda: self.update_log(message))
            
            self.bot.logger.info = lambda message: log_to_gui(original_info, message)
            self.bot.logger.warning = lambda message: log_to_gui(original_warning, message)
            self.bot.logger.error = lambda message: log_to_gui(original_error, message)
            
            # Run the bot
            self.bot.run(
                keywords=self.keywords_var.get(),
                location=self.location_var.get(),
                max_applications=self.max_applications_var.get()
            )
            
            # Update UI when done
            self.root.after(0, lambda: self.update_log("Bot finished running."))
            self.root.after(0, lambda: self.start_button.config(text="Start Job Application Bot", state=tk.NORMAL))
        
        except Exception as e:
            # Handle any exceptions
            error_message = f"Error running bot: {str(e)}"
            self.root.after(0, lambda: self.update_log(error_message))
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
            self.root.after(0, lambda: self.start_button.config(text="Start Job Application Bot", state=tk.NORMAL))
    
    def on_close(self) -> None:
        """
        Handle window close event.
        """
        # Check if bot is running
        if self.bot_thread and self.bot_thread.is_alive():
            if messagebox.askyesno("Quit", "The bot is still running. Are you sure you want to quit?"):
                # Force quit
                self.root.destroy()
        else:
            # Normal quit
            self.root.destroy()


def main():
    """
    Main function to run the GUI.
    """
    root = tk.Tk()
    app = LinkedInJobBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()