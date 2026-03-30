# purge90_cleanup.py
# by Tyler Giles
# 540-589-0368
# trgiles.com

import sys
sys.path.append(r"C:\Scripts\Utilities")
from utilities import *

import os
import subprocess
import shutil

tlog_express(__file__, 0, "tlog.log")

purge90_path = r"C:\Scripts\Utilities\purge90"

seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"

archives = []
folders = []

for item in os.listdir(purge90_path):
    full_path = os.path.join(purge90_path, item)
    if os.path.isfile(full_path):
        archives.append(item)
    else:
        folders.append(item)
        

for folder in folders:
    full_path = os.path.join(purge90_path, folder)
    if int(folder) < int(ymd(-2)):
        output_archive = f"{full_path}.7z"
        
        tlog(f"Creating archive: {output_archive}")
        
        result = subprocess.run(
            [seven_zip_path, 'a', output_archive, full_path, '-m0=lzma2', '-mx=9'],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print stdout and stderr
        tlog(str(result.stdout))
        tlog(str(result.stderr))
        
        # Check result
        if result.returncode == 0:
            print("Archive is created.")
        else:
            fatal("Archive failed to create.")
        
        result = subprocess.run([seven_zip_path, 't', output_archive], capture_output=True, text=True)
        
        # Print stdout and stderr
        tlog(str(result.stdout))
        tlog(str(result.stderr))
        
        # Check result
        if result.returncode == 0:
            print("Archive is valid.")
        else:
            fatal("Archive is corrupt or test failed.")
        
        shutil.rmtree(full_path)
        tlog(f"Folder removed: {full_path}")
        
for archive in archives:
    full_path = os.path.join(purge90_path, archive)
    archive_date, _ = os.path.splitext(archive)
    
    # This will remove any archives that are more than 90 days old.
    if int(archive_date) < int(ymd(-90)):
        os.remove(full_path)
        tlog(f"Archive removed: {archive}")