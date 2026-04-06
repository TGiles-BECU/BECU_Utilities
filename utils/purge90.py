from .core import ymd
from pathlib import Path
from datetime import datetime

import os
import shutil

import logging

logger = logging.getLogger(__name__)

def purge90(file_path, move=False, subdir=None):
    purge_path = fr"C:\Scripts\Utilities\purge90\{ymd()}"
    if subdir: purge_path = os.path.join(purge_path, subdir)
    Path(purge_path).mkdir(parents=True, exist_ok=True)
    
    if move: shutil.move(file_path, purge_path)
    else: shutil.copy2(file_path, purge_path)