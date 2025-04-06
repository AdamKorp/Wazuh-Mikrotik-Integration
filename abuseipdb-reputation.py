#!/usr/bin/python3

import sys
import json
import requests
import os
import datetime
import subprocess

# Configuration
LOG_FILE = "/var/ossec/logs/active-responses.log"
MIKROTIK_IP = "192.168.1.1"  # Mikrotik Router IP
SSH_KEY_PATH = "/var/ossec/.ssh/id_rsa"  # Path to the private SSH key
ABUSEIPDB_API_KEY = "<YOUR-API-KEY-HERE>"  # Replace with your API KEY
ABUSEIPDB_API_URL = "https://api.abuseipdb.com/api/v2/check"
FIREWALL_COMMAND = "/ip firewall address-list add list=\"blocked-by-wazuh\" address={ip} timeout=90d comment=\"Added by Wazuh\""
REPUTATION_THRESHOLD = 25  # Confidence score threshold (0-100), adjust as needed

# Constants
OS_SUCCESS = 0
OS_INVALID = -1

def write_debug_file(script_name, msg, log_file=LOG_FILE):
    """Write debug messages to the specified log file."""
    with open(log_file, mode="a") as file:
        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        file.write(f"{timestamp} {script_name}: {msg}\n")

def query_abuseipdb(ip, script_name):
    """Query AbuseIPDB for the IP reputation and return the result."""
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90  # Check reports from the last 90 days
    }

    try:
        response = requests.get(ABUSEIPDB_API_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        confidence_score = result["data"]["abuseConfidenceScore"]
        return confidence_score  # Return the score (0-100)
    except requests.RequestException:
        return None  # Return None if the query fails

def run_ssh_command(command):
    """Execute the command on Mikrotik router via SSH."""
    try:
        cmd = [
            "ssh",
            "-i", SSH_KEY_PATH,
            "-o", "StrictHostKeyChecking=no",
            f"wazuh@{MIKROTIK_IP}",
            command
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Success:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed:", e.stderr)

def main(argv):
    script_name = os.path.basename(argv[0])
    write_debug_file(script_name, "IP Reputation check started")

    # Read alert from STDIN
    input_str = sys.stdin.readline().strip()

    # Parse JSON
    try:
        data = json.loads(input_str)
    except ValueError:
        write_debug_file(script_name, "IP reputation check failed, please investigate")
        sys.exit(OS_INVALID)

    # Check command
    command = data.get("command", "")
    if command != "add":
        write_debug_file(script_name, "IP reputation check failed, please investigate")
        sys.exit(OS_INVALID)

    # Extract srcip from alert
    alert = data.get("parameters", {}).get("alert", {})
    srcip = alert.get("data", {}).get("srcip", "")
    if not srcip:
        write_debug_file(script_name, "IP reputation check failed, please investigate")
        sys.exit(OS_INVALID)

    # Query AbuseIPDB and get the reputation score
    reputation_score = query_abuseipdb(srcip, script_name)

    # Determine the final log message based on the reputation score
    if reputation_score is None:
        write_debug_file(script_name, "IP reputation check failed, please investigate")
    elif reputation_score > REPUTATION_THRESHOLD:
        bad_ip_msg = f"IP reputation check completed and reputation is bad. {srcip} will be blocked at the router firewall"
        write_debug_file(script_name, bad_ip_msg)  # Write to active-responses.log

        # Block the IP on the Mikrotik router via SSH
        run_ssh_command(FIREWALL_COMMAND.format(ip=srcip))
    else:
        write_debug_file(script_name, f"IP reputation check completed and reputation is good for {srcip}")

    sys.exit(OS_SUCCESS)

if __name__ == "__main__":
    main(sys.argv)
