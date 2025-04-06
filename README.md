# Wazuh-Mikrotik-Integration
Deployment of open-source SIEM + EDR solution and integration with Mikrotik routers
Home Network Security: Wazuh + MikroTik Integration

##### Goal: Deploy Wazuh, a powerful open-source XDR/SIEM platform, on a home network and integrate it with MikroTik routers for enhanced security monitoring at a low cost.



### Why Wazuh?

Wazuh is a free, open-source security platform that unifies Extended Detection and Response (XDR) and Security Information and Event Management (SIEM) capabilities. It provides:

✔ Endpoint Security – Malware detection, file integrity monitoring, and log analysis.

✔ Threat Detection & Response – Real-time alerts for suspicious activities.

✔ Compliance Monitoring – Helps meet security standards (NIST, CIS, GDPR).

✔ Elastic Stack Integration – Powerful dashboards for visualizing security events.



### Why MikroTik?

MikroTik routers are affordable yet powerful, running RouterOS, a Linux-based OS with:

✔ Firewall & Traffic Filtering – Blocks unauthorised access.

✔ Bandwidth Management – Controls and prioritises network traffic.

✔ VPN & Hotspot Support – Secure remote access and guest networks.

✔ Logging & Monitoring – Generates security-relevant logs for analysis.



### Why This Integration?

By combining Wazuh’s advanced threat detection with MikroTik’s network control, you get:

🔒 Enhanced visibility into network threats.

📡 Real-time monitoring of router security events.

💰 Enterprise-grade security at a low cost (perfect for home labs and SMBs).




### Let’s Build It!

This project will guide you through:

1. Deploying Wazuh (server, indexer, dashboard).

2. Mikrotik & Wazuh syslog configuration
  
3. Generating private&public keys for ssh communication

4. Creating an active response script for failed logins and AbuseIPDB integration 

### 🔧 Lab Setup

🛡️ MikroTik Device:
Model: hAP ax2, 
OS: RouterOS 7.18.2

💻 Virtualization:
Host: Proxmox VE 8.2.4, 
VM: Ubuntu 24.04.2 LTS, 
Resources:
8GB RAM, 
70GB disk storage


<p>
  <br>
    <br>
    <br>
    </p>

## Step 1: Wazuh Installation & Configuration

• Download & Run the Installer


``` 
curl -sO https://packages.wazuh.com/4.11/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
```

This script automates the installation of Wazuh manager, indexer, and dashboard.

The -a flag installs all components (single-node deployment).


• Disable Automatic Updates (Optional but Recommended for Lab Environments)


```
sudo sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list
sudo apt update
```

• Reset the Default Password

Download password tool by running a command 
```
curl -so wazuh-passwords-tool.sh https://packages.wazuh.com/4.11/wazuh-passwords-tool.sh
```

Run the Wazuh password tool to set a secure password for the admin user:

```
sudo bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/wazuh-passwords-tool.sh -u admin -p <YOUR_PASSWORD>
```

#### ⚠️ If you put a space before a command, it prevents that command from being saved in the shell's history. This is good security practice so that your plaintext password won't be visible in the history ⚠️

• Restart Dependent Services
   
Apply the changes by restarting Filebeat and the Wazuh Dashboard:

```
sudo systemctl restart filebeat.service


sudo systemctl restart wazuh-dashboard.service
```

• Access the Wazuh Dashboard
   
Find your VM’s IP address then open a browser and navigate to: https://<YOUR_VM_IP>

Log in with: Username: admin and Password: <YOUR__UPDATED_PASSWORD>

If you see "Wazuh dashboard server is not ready yet" wait 1–2 minutes for services to initialise.

Check status with:
```
sudo systemctl status wazuh-dashboard
```

• (Recommended) Create a Proxmox Snapshot

Before proceeding further, snapshot your VM in Proxmox:

Go to your Proxmox web interface. Locate the Wazuh VM and Click "Snapshot". Name it (e.g., Clean_Wazuh_Base).


Why?

Allows easy rollback if something goes wrong along the way!


• Configure Wazuh to listen on port 514

   
Edit the main configuration file: 
```
sudo nano /var/ossec/etc/ossec.conf
```
and add:

```
<!-- MikroTik Syslog Integration -->
<remote>
  <connection>syslog</connection>
  <port>514</port>
  <protocol>udp</protocol>     
  <allowed-ips>192.168.1.1</allowed-ips>  <!-- Your MikroTik's IP -->
  <local_ip>192.168.1.63</local_ip>       <!-- Wazuh server IP -->
</remote>
```


Restart wazuh 
```
sudo systemctl restart wazuh-manager
```

To verify if Wazuh is listening, install  
```
apt install net-tools
```
and run
```
sudo netstat -tuln | grep 514
```
<p>
  <br>
    <br>
    </p>
    
## Step 2: Configure MikroTik Log Forwarding


Log into MikroTik via winbox and navigate to: System > Logging > Actions

Click "New" and create new action. Name: remote, Type: remote. Apply and then double click on newly created "remote action" to add adjust more settings. 

Remote Address: <Wazuh server IP>, Remote Port: 514, src address: <MikrotiK's IP>, Remote log format: BDS Syslog, Remote log protocol: UDP. > Apply > OK. 


• Set Logging Rules for each log type to forward:

Go to System > Logging > Rules, Click "New"

Topics: Select one (e.g., critical), Action: remote > Click Apply > OK

Recommended Topics to Forward: critical, error, firewall, info, system, warning

Step 5: Verify Log Transmission
On Wazuh Server identify your network interface:

```
ip a
```
(e.g., ens18)

Monitor incoming logs by running a command  
```
sudo tcpdump -i ens18 tcp port 514 -A
```
 and simulate a failed Winbox login → Logs should appear in tcpdump output.

Now, to double-check that Wazuh is correctly receiving them, go to the Wazuh dashboard. In the top left corner, go to the menu, then > Explore > Discover. Search for 'winbox' to check if you can see the output log.

<p>
  <br>
    <br>
    </p>
    
## 🔑 Step 3: SSH Key Setup for Wazuh → MikroTik
We’ll generate an SSH key for the wazuh user to enable secure, passwordless access (for future active response scripts).

#### • 🛠️ Generate SSH Key

run 
```
ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa
```

Leave passphrase empty (press Enter twice)

#### • 🔒 Set permissions:

```
chmod 700 ~/.ssh

chmod 600 ~/.ssh/id_rsa

chmod 644 ~/.ssh/id_rsa.pub
```
#### •  📋 Copy the Public Key

```
cat ~/.ssh/id_rsa.pub
```

#### • 📌 Save the output (starts with ssh-rsa AAA...) as a .txt file on your PC.

#### •  ⚙️ Configure MikroTik

Create wazuh user:

Winbox: System > Users > "+" > Name: wazuh | Group: full → Apply/OK

Import SSH key: Upload the .txt file via Files

System > Users > SSH Keys > Import: User: wazuh, Key File: Select your uploaded file > Click Import Key

#### •  ✅ Test Connection

```
ssh wazuh@<MikroTik-IP>
```

#### 🎉 Success? You’ll log in instantly without a password.
<p>
  <br>
    <br>
    </p>

## Step 4: Creating an active response script for failed logins and AbuseIPDB integration 🛡️

 #### 💻 Navigate to the active response directory:
 ```
cd /var/ossec/active-response/bin
````
#### ✍️ Open the script file for editing:


```
nano abuseipdb-reputation.py
```
📋 Paste the script from the project (you can find it at the top of the page), then save and exit. DON'T FORGET TO REPLACE YOUR API-KEY WITHIN THE SCRIPT 💾

#### 🔑 Change permissions for the script:
```
sudo chmod +x abuseipdb-reputation.py
sudo chown root:wazuh abuseipdb-reputation.py
```

🖥️ Log into the Wazuh dashboard and add the Mikrotik decoders and rules uploaded to this project (also available at the top of the page), then save. 🔒

📝 Edit the ossec.conf file and add the following:

```
    <command>
    <name>abuseipdb-check</name>
    <executable>abuseipdb-reputation.py</executable>
    <timeout_allowed>yes</timeout_allowed>
  </command>

  <active-response>
    <disabled>no</disabled>
    <command>abuseipdb-check</command>
    <location>server</location>  <!-- Runs on the Wazuh server, not agents -->
    <rules_id>115002</rules_id>  <!-- Trigger when rule 115002 is fired -->
    <timeout>60</timeout>
  </active-response>
```

#### 🔄 Finally, restart the Wazuh manager. 

<p>
  <br>
    </p>
All done! Wazuh and MikroTik are now integrated. Wazuh will effectively communicate with MikroTik to recognise potentially malicious login attempts and quarantine IP addresses with a bad reputation.



