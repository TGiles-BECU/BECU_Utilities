# super_parser.py
# by Tyler Giles
# 540-589-0368
# trgiles.com

debug = False

import sys
sys.path.append(r"C:\Scripts\Utilities")
from utilities import *

import os
import re

tlog_express(__file__, 0, "tlog.log")

def super_parser(input_str):
    
    # First we see if input string is a file or not (folder).
    base, ext = os.path.splitext(input_str)
    if bool(ext) and len(ext) > 1: file = True
    else: file = False
    
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
        
        # This top pattern resolves when MAs put hyphens in filenaems
        # This actually happens a lot, ex: 17553-L2001_Putter_File.doc
        pattern = r'^[SsLl]?(\d{3,})-[SsLl]?(\d{3,})-?(.*)'
        match = re.match(pattern, part)
        if match:
            print("I don't think this part runs any more...")
            number_parts.extend([match.group(1), match.group(2)])
            if match.group(3):
                name_parts.append(match.group(3))
            continue
        
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
        #tlog(f"No member numbers included: {input_str}")
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
                possible_lname = get_fd_lname(num)
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
            #tlog("Could not resolve member number from {input_str}")
            raise Exception("File name issue")
            
    # Removing memnum from number_parts if they remain
    if mxmemnum in number_parts:
        number_parts.remove(mxmemnum)
    
    # Asuming after we place memnum, the other number must be acct.
    if number_parts:
        mxacctnum = number_parts[0]
        
    # ---------------------------------------------------------------------------------------------------------- #

    if mxmemnum and mxacctnum:
        fdlname = get_fd_lname(mxmemnum, mxacctnum)
        if not fdlname:
            #tlog(f"Could not resolve member: {mxmemnum} and account: {mxacctnum} in FastDocs.")
            fdlname = get_fd_lname(mxmemnum)
            if fdlname:
                # At this point, FD couldnt resolve member AND account numbers, but ONLY the member number by itself
                #tlog(f"We could find account for just member number: {mxmemnum}")
                #tlog("This indicated that account has yet to be added to FD or maybe the member number is wrong/typo")
                raise Exception("No acct for this member")
                
                
    if not fdlname:
        fdlname = get_fd_lname(mxmemnum)
        if not fdlname: raise Exception("Member number not found in FD")
    
    
    multiname = re.split(r'[ -]+', fdlname)
    
    for typed_name in name_parts:
        for fd_name in multiname:
            name_score = compare_last_names(fd_name, typed_name)
            if debug: print(f"{fd_name} vs. {typed_name}  -->  Name Score: {name_score}")
            if name_score > 80:
                last_name.append(typed_name)
                break
        if len(last_name) >= len(multiname): break
    
    # Match was made!
    if last_name:
        mxlname = fdlname
    if not last_name: raise Exception("Last name issue")
    
    # Remove matched pieces from name_parts
    if len(name_parts) > 1:
        for name_match in last_name:
            name_parts.remove(name_match)
    
    mxrest = " ".join(name_parts)
    
    return mxmemnum, mxacctnum, mxlname, mxrest