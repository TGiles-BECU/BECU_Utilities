from .core import ymd
from pathlib import Path
from datetime import datetime

import os
import shutil

import logging

logger = logging.getLogger(__name__)

# purge90.purge() will be legacy compatibility mode
def purge(file, move=False, subdir=None):
    file_path = Path(file)
    purge_path = Path("C:/Scripts/Utilities/purge90") / ymd()
    if subdir: purge_path = purge_path / subdir
    Path(purge_path).mkdir(parents=True, exist_ok=True)
    
    try:
        if move: shutil.move(file_path, purge_path)
        else: shutil.copy2(file_path, purge_path)
    except Exception as e:
        logger.error(f"Could not {'move' if move else 'copy'} file: {file_path}")
        logger.error(f"purge90 failed: {e}")
    

def copy(copy_file, copy_subdir=None):
    purge(copy_file, False, copy_subdir)
    
def move(move_file, move_subdir=None):
    purge(move_file, True, move_subdir)