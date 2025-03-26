# LinkedIn Job Application Bot

A Python automation tool that helps you apply to jobs on LinkedIn using Selenium. This bot automates the process of searching for jobs with specific criteria and applying to them using LinkedIn's "Easy Apply" feature.

## Features

- **Automated Login**: Securely log in to your LinkedIn account using environment variables
- **Customizable Job Search**: Search for jobs using keywords, location, and filters
- **Easy Apply Automation**: Automatically apply to jobs with the "Easy Apply" button
- **Application Tracking**: Log all application attempts to CSV and Excel files
- **Smart Form Filling**: Automatically fill out common application fields
- **Resume & Cover Letter Upload**: Support for uploading your resume and cover letter
- **Configurable Settings**: Customize the bot's behavior through environment variables or GUI
- **Graphical User Interface**: Simple GUI for configuring and running the bot
- **Anti-Detection Measures**: Random delays and human-like behavior to avoid bot detection

## Requirements

- Python 3.7+
- Chrome browser
- LinkedIn account
- Resume (PDF format recommended)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the `.env.template` file to `.env` and fill in your LinkedIn credentials and preferences:

```bash
cp .env.template .env
```

4. Edit the `.env` file with your information

## Usage

### Command Line Interface

Run the bot from the command line:

```bash
python linkedin_job_bot.py --keywords "Data Analyst" --location "Remote" --max-applications 20
```

Command line arguments:
- `--keywords`: Job keywords to search for (default: "Data Analyst")
- `--location`: Job location to search for (default: "Remote")
- `--max-applications`: Maximum number of applications to submit (default: 20)
- `--headless`: Run in headless mode (browser runs in the background)

### Graphical User Interface

For a more user-friendly experience, run the GUI:

```bash
python gui.py
```

The GUI allows you to:
- Enter your LinkedIn credentials
- Configure job search parameters
- Set application preferences
- View real-time logs
- Start and stop the bot

## Configuration

You can configure the bot using environment variables in the `.env` file:

### LinkedIn Credentials
- `LINKEDIN_EMAIL`: Your LinkedIn email
- `LINKEDIN_PASSWORD`: Your LinkedIn password

### User Information
- `PHONE_NUMBER`: Your phone number
- `RESUME_PATH`: Path to your resume file
- `COVER_LETTER_PATH`: Path to your cover letter file

### Job Search Settings
- `DEFAULT_KEYWORDS`: Default job keywords
- `DEFAULT_LOCATION`: Default job location
- `DEFAULT_MAX_APPLICATIONS`: Default maximum number of applications

### Browser Settings
- `HEADLESS_MODE`: Whether to run the browser in headless mode
- `BROWSER_TIMEOUT`: Browser timeout in seconds

### Application Settings
- `WAIT_TIME_MIN`: Minimum wait time between actions
- `WAIT_TIME_MAX`: Maximum wait time between actions
- `FOLLOW_COMPANIES`: Whether to follow companies after applying

### Default Answers for Application Questions
- `DEFAULT_YEARS_EXPERIENCE`: Default years of experience
- `DEFAULT_EDUCATION`: Default education level
- `WILLING_TO_RELOCATE`: Default answer for relocation questions
- `REQUIRE_SPONSORSHIP`: Default answer for sponsorship questions
- `REMOTE_WORK`: Default answer for remote work questions

## Output

The bot generates the following output files in the `output` directory:

- `applications_YYYYMMDD_HHMMSS.csv`: CSV file with application data
- `summary_YYYYMMDD_HHMMSS.xlsx`: Excel file with application summary
- `linkedin_bot.log`: Log file with detailed information

## Limitations

- The bot can only apply to jobs with the "Easy Apply" button
- Complex application forms may require manual intervention
- LinkedIn may change their website structure, which could break the bot
- Using automation tools may violate LinkedIn's terms of service
- The bot may not be able to handle all types of application questions

## Tips for Success

1. **Start with a small number of applications** to ensure everything is working correctly
2. **Monitor the bot** during the first few applications to ensure it's working as expected
3. **Use a dedicated LinkedIn account** if possible
4. **Be selective with job keywords** to find relevant positions
5. **Keep your resume and profile up to date** to increase your chances of success
6. **Review the application logs** to see which applications were successful

## Legal Disclaimer

This tool is for educational purposes only. Using automated tools to interact with websites may violate their terms of service. Use at your own risk. The authors are not responsible for any consequences of using this tool.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.