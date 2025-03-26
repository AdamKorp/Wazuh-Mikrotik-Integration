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
