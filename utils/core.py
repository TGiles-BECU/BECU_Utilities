import logging
logger = logging.getLogger(__name__)

from .be_email import send as be_send
from .jsm import open as jsm_open

from datetime import datetime, timedelta
from pathlib import Path

# core.fatal()
import inspect
import sys


def ymd(days=0, return_list=0):
    # returns date like 20260101
    selected_date = (datetime.now() + timedelta(days=days)).strftime("%Y%m%d")
    if not return_list:
        return selected_date
    else:
        return [
            selected_date[:4],
            selected_date[4:6],
            selected_date[6:],
        ]
        
def ymdt():
    # returns date AND time like 20260101-042017
    selected_date = datetime.now().strftime("%Y%m%d-%H%M%S")
    return selected_date
    
def ymdy():
    # Returns yesterday's date, but when ran on Monday or Sunday it will return Friday's date
    if datetime.now().weekday() == 6:   # Sunday -2
        return ymd(-2)
    if datetime.now().weekday() == 0:   # Monday -3
        return ymd(-3)
    else:                               # Tues-Satruday, yesterday is just -1
        return ymd(-1)
    
def fatal(message, solution='', ticket=0):
    
    # stack()[1] is the immediate caller
    frame = inspect.stack()[1]
    
    # Get the filename
    caller_path = Path(frame.filename)
    caller_filename = caller_path.name
    
    # Get the line number where it happened
    line_no = frame.lineno
    
    fatal_summary = f"FATAL ERROR on {caller_filename}"
    
    fatal_body = f"""
FATAL ERROR SUMMARY
-------------------
Script:  {caller_filename}
Line:    {line_no}
Path:    {caller_path}

ERROR MESSAGE:
{message}

SUGGESTED SOLUTION:
{solution if solution else 'None'}
"""
    
    #print(f"!!! FATAL ERROR IN [{caller_filename}] at line {line_no} !!!")
    #print(f"Message: {message}")
    
    if ticket:
        if ticket not in (10001, 4, 3, 2, 10000): ticket = 3
        jsm_key = jsm_open(fatal_summary, fatal_body, ticket)
        logger.critical(f"JSM ticket open: {jsm_key}")
        fatal_body += f"""
JSM TICKET:
Key:     {jsm_key}
URL:     https://blueeaglecreditunion.atlassian.net/browse/{jsm_key}
"""
    
    print(fatal_body)
    
    be_send("tyler.giles", fatal_summary, fatal_body)
        
    # Exit the script
    sys.exit(1)
    
    
    #logger.critical(f"FATAL ERROR: {message}")
    #if solution: logger.critical(f"FATAL ERROR: {solution}")