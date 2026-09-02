import logging
logger = logging.getLogger(__name__)

import subprocess

def ping(addr):
    
    result = subprocess.run(
        ["ping", "-n", "4", addr],
        capture_output=True,
        text=True,
        check=False
    )
    
    result_lines = result.stdout.strip().split("\n")
    
    for line in result_lines:
        logger.info(line)
    
    return(result.stdout)
    
def port_test(host, port):
    
    ps_command = f"Test-NetConnection -ComputerName {host} -Port {port}"
    
    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True
    )
    
    result_lines = result.stdout.strip().split("\n")
    
    for line in result_lines:
        logger.info(line)
    
    return(result.stdout)
    
def nslookup(host):
    
    result = subprocess.run(
        ["nslookup", host],
        capture_output=True,
        text=True,
        check=False
    )
    
    result_lines = result.stdout.strip().split("\n")
    
    for line in result_lines:
        logger.info(line)
    
    return(result.stdout)