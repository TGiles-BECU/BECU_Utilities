from .core import ymd, ymdt
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

import subprocess

def run_cmd(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"{e.stderr} {e.stdout}"

def build(app, count, src, dst):
    
    file_src = Path(src)
    file_dst = Path(dst)
    terror_path = Path("C:/Scripts/Utilities/terror")
    app_name = Path(app).stem
    
    terror_file = terror_path / f"{app_name}-{ymd()}.txt"
    
    # First time in script
    if count <= 1:
        logger.info(f"terror_file: {terror_file}")
        with open(terror_file, "w") as f:
            f.write(run_cmd("echo --- PERMISSION TEST REPORT ---"))
            f.write(run_cmd("echo Date/Time: %date% %time%"))
            f.write(run_cmd("echo Running as user:"))
            f.write(run_cmd("whoami") + "\n")
            
            my_cmd = f'copy "{file_src}" "{file_dst}"'
            f.write(run_cmd(f"echo {my_cmd}"))
            f.write(run_cmd(my_cmd) + "\n")
    
    # All other errors
    else:
        with open(terror_file, "a") as f:
            my_cmd = f'copy "{file_src}" "{file_dst}"'
            f.write(run_cmd(f"echo {my_cmd}"))
            f.write(run_cmd(my_cmd) + "\n")