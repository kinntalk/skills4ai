"""
Test script with permission abuse patterns
"""
import os
import subprocess
import requests

def excessive_filesystem_access():
    """HIGH: Excessive file operations without limits"""
    for root, dirs, files in os.walk('/'):
        for file in files:
            with open(os.path.join(root, file)) as f:
                process(f.read())

def unvalidated_network_access(urls):
    """HIGH: Multiple network operations without validation"""
    for url in urls:
        response = requests.get(url)
        process(response.text)

def unchecked_system_commands(commands):
    """HIGH: System commands without safeguards"""
    for cmd in commands:
        os.system(cmd)

def sensitive_data_export():
    """HIGH: Sensitive data access without checks"""
    data = database.query("SELECT * FROM users")
    save_to_file(data, 'all_users.json')

def unrestricted_file_operations():
    """HIGH: Unrestricted file operations"""
    import shutil
    shutil.copytree('/source', '/destination')
    shutil.rmtree('/tmp')

def unlimited_subprocess():
    """HIGH: Unlimited subprocess execution"""
    while True:
        cmd = get_next_command()
        subprocess.run(cmd, shell=True)
