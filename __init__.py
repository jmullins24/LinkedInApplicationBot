#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LinkedIn Job Application Bot

A Python automation tool that helps you apply to jobs on LinkedIn using Selenium.
This bot automates the process of searching for jobs with specific criteria and
applying to them using LinkedIn's "Easy Apply" feature.
"""

__version__ = '1.0.0'
__author__ = 'LinkedIn Job Bot Developer'
__email__ = 'example@example.com'

from .linkedin_job_bot import LinkedInJobBot
from .config import get_config, validate_config, create_env_template

__all__ = ['LinkedInJobBot', 'get_config', 'validate_config', 'create_env_template']
