# Wazuh-Mikrotik-Integration
Deployment of open-source SIEM + EDR solution and integration with Mikrotik routers
Home Network Security: Wazuh + MikroTik Integration

Goal: Deploy Wazuh, a powerful open-source XDR/SIEM platform, on a home network and integrate it with MikroTik routers for enhanced security monitoring at a low cost.



Why Wazuh?

Wazuh is a free, open-source security platform that unifies Extended Detection and Response (XDR) and Security Information and Event Management (SIEM) capabilities. It provides:

✔ Endpoint Security – Malware detection, file integrity monitoring, and log analysis.

✔ Threat Detection & Response – Real-time alerts for suspicious activities.

✔ Compliance Monitoring – Helps meet security standards (NIST, CIS, GDPR).

✔ Elastic Stack Integration – Powerful dashboards for visualizing security events.



Why MikroTik?

MikroTik routers are affordable yet powerful, running RouterOS, a Linux-based OS with:

✔ Firewall & Traffic Filtering – Blocks unauthorized access.

✔ Bandwidth Management – Controls and prioritizes network traffic.

✔ VPN & Hotspot Support – Secure remote access and guest networks.

✔ Logging & Monitoring – Generates security-relevant logs for analysis.



Why This Integration?

By combining Wazuh’s advanced threat detection with MikroTik’s network control, you get:

🔒 Enhanced visibility into network threats.

📡 Real-time monitoring of router security events.

💰 Enterprise-grade security at a low cost (perfect for home labs and SMBs).




Let’s Build It!

This project will guide you through:

1. Deploying Wazuh (server, indexer, dashboard).

2. Configuring MikroTik to forward logs to Wazuh.
  
3. Generating private&public key for ssh communication

4. Setting up alerts & dashboards for proactive security.



🔧 Lab Setup

🛡️ MikroTik Device:
Model: hAP ax2, 
OS: RouterOS 7.18.2

💻 Virtualization:
Host: Proxmox VE 8.2.4, 
VM: Ubuntu 24.04.2 LTS, 
Resources:
8GB RAM, 
70GB disk storage


Step 1: Wazuh Installation

1. Download & Run the Installer


```curl -sO https://packages.wazuh.com/4.11/wazuh-install.sh && sudo bash ./wazuh-install.sh -a```


This script automates the installation of Wazuh manager, indexer, and dashboard.

The -a flag installs all components (single-node deployment).


2. Disable Automatic Updates (Optional but Recommended for Lab Environments)


`sudo sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list`


`sudo apt update`

Step 2: Configure Wazuh Dashboard & Secure Access
1. Reset the Default Password
Run the Wazuh password tool to set a secure password for the admin user:


`sudo bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/wazuh-passwords-tool.sh -u admin -p <YOUR_PASSWORD>`

⚠️ If you put a space before a command, it prevents that command from being saved in the shell's history. This is good security practice so that your plaintext password won't be visible in the history ⚠️

2. Restart Dependent Services
   
Apply the changes by restarting Filebeat and the Wazuh Dashboard:



`sudo systemctl restart filebeat.service`

`sudo systemctl restart wazuh-dashboard.service`

3. Access the Wazuh Dashboard
   
Find your VM’s IP address:

Open a browser and navigate to: https://<YOUR_VM_IP>

Log in with: Username: admin and Password: <YOUR__UPDATED_PASSWORD>

If you see "Wazuh dashboard server is not ready yet":

Wait 1–2 minutes for services to initialize.

Check status with:
`sudo systemctl status wazuh-dashboard`

4. (Recommended) Create a Proxmox Snapshot
   
Before proceeding further, snapshot your VM in Proxmox:

Go to your Proxmox web interface. Locate the Wazuh VM and Click "Snapshot". Name it (e.g., Clean_Wazuh_Base).

Why?

Allows easy rollback if something goes wrong along the way!


Step 3: Configure Wazuh to listen on port 514

   
Edit the main configuration file: `sudo nano /var/ossec/etc/ossec.conf` and add:

`<!-- MikroTik Syslog Integration -->
<remote>
  <connection>syslog</connection>
  <port>514</port>
  <protocol>udp</protocol>     
  <allowed-ips>192.168.1.1</allowed-ips>  <!-- Your MikroTik's IP -->
  <local_ip>192.168.1.63</local_ip>       <!-- Wazuh server IP -->
</remote>`


Restart wazuh `sudo systemctl restart wazuh-manager`

Verify if Wazuh is listening: Install  `apt install net-tools` and run `sudo netstat -tuln | grep 514`

Step 4: Configure MikroTik Log Forwarding


Log into MikroTik via winbox and navigate to: System > Logging > Actions

Click "New" and create new action. Name: remote, Type: remote. Apply and then double click on newly created "remote action" to add adjust more settings. 

Remote Address: <Wazuh server IP>, Remote Port: 514, src address: <MikrotiK's IP>, Remote log format: BDS Syslog, Remote log protocol: UDP. > Apply > OK. 


2. Set Logging Rules for each log type to forward:

Go to System > Logging > Rules, Click "New"

Topics: Select one (e.g., critical), Action: remote > Click Apply > OK

Recommended Topics to Forward: critical, error, firewall, info, system, warning

Step 5: Verify Log Transmission
On Wazuh Server identify your network interface:

`ip a` (e.g., ens18)

Monitor incoming logs by running a command  `sudo tcpdump -i ens18 tcp port 514 -A` and simulate a failed Winbox login → Logs should appear in tcpdump output.







