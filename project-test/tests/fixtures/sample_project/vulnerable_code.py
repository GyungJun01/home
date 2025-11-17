"""Test fixture: Vulnerable Python code for Bandit scanning"""

# TAG-REQ-SEC-001: Bandit test cases
# HIGH severity issues
PASSWORD = "admin123"  # B105: Hardcoded password string

# MEDIUM severity issues
import pickle  # B403: Pickle and modules that wrap it can be unsafe

def load_data(filename):
    """Unsafe pickle usage"""
    with open(filename, "rb") as f:
        return pickle.load(f)  # B301: Pickle usage

# LOW severity issues
import subprocess

def run_command():
    """Shell command execution"""
    subprocess.call("ls -la", shell=True)  # B602: shell=True identified
