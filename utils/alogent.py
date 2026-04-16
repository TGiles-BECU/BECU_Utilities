import logging
logger = logging.getLogger(__name__)

from pathlib import Path
import pyodbc # pip install

import os
from dotenv import load_dotenv # pip install
current_file_dir = Path(__file__).resolve().parent.parent
env_path = current_file_dir / '.env'
load_dotenv(dotenv_path=env_path)

import difflib
import re

def mask_acct(unmasked_filename):
    memnum = re.match(r'^(\d+)(.*)', unmasked_filename)
    if not memnum:
        return '*' * 10 + unmasked_filename
    
    clean = memnum.group(1)
    visible = clean[-3:]
    masked = ('*' * (10 - len(visible))) + visible
    return masked + memnum.group(2)

def lname(mxmemnum, mxlnnum=None):
    server = os.getenv("ALOGENT_SERVER")
    database = os.getenv("ALOGENT_DATABASE")
    username = os.getenv("ALOGENT_USERNAME")
    password = os.getenv("ALOGENT_PASSWORD")
    driver = os.getenv("ALOGENT_DRIVER")
    
    connection_string = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'TrustServerCertificate=yes;'
    )
    
    conn = pyodbc.connect(connection_string)
    
    cursor = conn.cursor()
    
    if mxlnnum:
    
        cursor.execute("""
            SELECT TOP 1 Customer.LastName
            FROM Customer
            JOIN Account on Account.Number = Customer.CustomerNumber
            WHERE Customer.CustomerNumber = ?
            AND Account.Description = ?
        """, (mxmemnum, mxlnnum))
        
    else:
    
        cursor.execute("""
            SELECT TOP 1 LastName
            FROM Customer
            WHERE CustomerNumber = ?
        """, (mxmemnum))
    
    row = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if row:
        return row[0]
    else:
        return None

def compare(lname1, lname2):
    
    #The first, left most name should be the name from \\Fastdoc database
    name1 = lname1.lower()
    name2 = lname2.lower()
    
    if name1 == name2: return 100
    
    if name1 in name2 or name2 in name1:
        if len(name1) >= 4 and len(name2) >= 4:
            return 100
        else:
            return 70.86 #real live eg. de IN de la cruz denis
            #since de only 2 characters, we are going to caution this one.
    
    ratio = difflib.SequenceMatcher(None, name1, name2).ratio()
    return int(round(ratio * 100))
    
def sparser(input_str):
    
    # Anything .(dot) anything
    pattern = r"(.*)(\..*$)"
    match = re.match(pattern, input_str)
    if match:
        file = True
        base, ext = match.group(1), match.group(2)
    else:
        file = False
        base, ext = input_str, None
    
    parts = re.split(r'[ _-]+', base)
    
    mxmemnum = None
    mxlname = None
    mxacctnum = None
    fdlname = None
    
    mxrest = None #place hold
    
    number_parts = []
    name_parts = []
    last_name = []
    
    
    for part in parts:
        
        # Pattern has all numbers, atleast 3 digints, may or may not start with an L or S
        pattern = r'^[SsLl]?(\d{3,})'
        match = re.match(pattern, part)
        if match:
            number_parts.append(match.group(1))
        else:
            name_parts.append(part)
    
    # Make a second list of just lower case name parts
    lower_name_parts = [name.lower() for name in name_parts]        
    
    # For now, we are not going to process multiple account or member numbers
    # Ex: 17553_L2001_L2002_Skip Payment.pdf
    if len(number_parts) > 2:
        #raise Exception("Multiple acct numbers")
        name_parts.extend(number_parts[2:])
        del number_parts[2:]
    
    # Lets find which number is member number and which is an account number
    
    # No member or account numbers
    if not number_parts:
        raise Exception("No member number found")
    
    # If only one number, assume it must be memnum
    elif len(number_parts) == 1:
        mxmemnum = number_parts[0]
    
    # Multiple numbers loaded, if one is not equal to 4 digits we are asuming that it is the memnum
    else:
        for num in number_parts:
            if len(num) != 4:
                mxmemnum = num
                number_parts.remove(num)
                break
        
        # All numbers are 4 digits. This is where it gets tricky...
        # One will be member number, other(s) will be accounts...
        if not mxmemnum:
            for num in number_parts:
                if (
                    int(num) not in [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 91, 92] and
                    not (1000 <= int(num) <= 1030) and
                    not (2000 <= int(num) <= 2030) and
                    not (3000 <= int(num) <= 3030)
                ):
                    mxmemnum = num
                    number_parts.remove(num)
                    break
                    
        
        # Both numbers COULD be account numbers in given range above,
        # need to dig deeper!
        if not mxmemnum:
            for num in number_parts:
                possible_lname = lname(num)
                if possible_lname:
                    if possible_lname.lower() in lower_name_parts:
                        mxmemnum = num
                        mxlname = possible_lname
                        number_parts.remove(num)
                        break
                        
        # At this point:
        # Both numbers are exactly 4 digits
        # They are both in account number range (see above)
        # And neither last name returend from FD was found in file/directory name
        if not mxmemnum:
            raise Exception("File name issue")
            
    # Removing memnum from number_parts if they remain
    if mxmemnum in number_parts:
        number_parts.remove(mxmemnum)
    
    # Asuming after we place memnum, the other number must be acct.
    if number_parts:
        mxacctnum = number_parts[0]
        
    # ---------------------------------------------------------------------------------------------------------- #

    if mxmemnum and mxacctnum:
        fdlname = lname(mxmemnum, mxacctnum)
        if not fdlname:
            fdlname = lname(mxmemnum)
            if fdlname:
                # At this point, FD couldnt resolve member AND account numbers, but ONLY the member number by itself
                raise Exception("No acct for this member")
                
                
    if not fdlname:
        fdlname = lname(mxmemnum)
        if not fdlname: raise Exception("Member number not found in FD")
    
    
    multiname = re.split(r'[ -]+', fdlname)
    
    for typed_name in name_parts:
        for fd_name in multiname:
            name_score = compare(fd_name, typed_name)
            if name_score > 80:
                last_name.append(typed_name)
                break
        if len(last_name) >= len(multiname): break
    
    # Match was made!
    if last_name:
        mxlname = fdlname
    if not last_name:
        logger.error(f"Member {mxmemnum} last name in FD: {fdlname}")
        raise Exception("Last name issue")
    
    # Remove matched pieces from name_parts
    if len(name_parts) > 1:
        for name_match in last_name:
            name_parts.remove(name_match)
    
    mxrest = " ".join(name_parts)
    
    return mxmemnum, mxacctnum, mxlname, mxrest