from .core import ymd
from pathlib import Path
from datetime import datetime

import os
import shutil

import logging

logger = logging.getLogger(__name__)

def copy(file_path, subdir=None):
    purge_path = Path("C:/Scripts/Utilities/purge90") / ymd()
    if subdir: purge_path = purge_path / subdir
    Path(purge_path).mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(file_path, purge_path)
    
def move(file_path, subdir=None):
    purge_path = Path("C:/Scripts/Utilities/purge90") / ymd()
    if subdir: purge_path = purge_path / subdir
    Path(purge_path).mkdir(parents=True, exist_ok=True)
    
    shutil.move(file_path, purge_path)