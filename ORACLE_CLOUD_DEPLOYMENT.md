# Oracle Cloud Free Tier Deployment Guide

Deploy your IBKR trading bot to Oracle Cloud's Always Free tier for 24/7 operation at no cost.

## Why Oracle Cloud?

- **Truly Free Forever**: No credit card required initially, no charges after trial
- **Always Free Resources**: 2 AMD VMs with 1GB RAM each (never expires)
- **24/7 Uptime**: Run your trading bot continuously
- **Generous Limits**: 200GB storage, 10TB outbound data transfer/month

---

## Step 1: Sign Up for Oracle Cloud

1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in your details (email, country, etc.)
4. Verify your email address
5. Complete the registration (may ask for credit card for verification, but won't charge)

---

## Step 2: Create a Compute Instance (VM)

1. **Log in to Oracle Cloud Console**: https://cloud.oracle.com/
2. Click **"Create a VM Instance"** or navigate to: Compute → Instances → Create Instance

3. **Configure the Instance**:
   - **Name**: `ibkr-trading-bot`
   - **Compartment**: Leave as default (root)
   - **Placement**: Leave as default
   
4. **Image and Shape**:
   - **Image**: Select "Ubuntu 22.04" (or latest Ubuntu)
   - **Shape**: Click "Change Shape"
     - Select "Ampere" or "AMD"
     - Choose **VM.Standard.E2.1.Micro** (Always Free eligible)
     - 1 OCPU, 1GB RAM

5. **Networking**:
   - **Virtual Cloud Network**: Create new VCN (or use existing)
   - **Subnet**: Create new public subnet
   - **Assign Public IP**: YES (required for SSH access)

6. **Add SSH Keys**:
   - **Generate SSH Key Pair**: Click "Generate a key pair for me"
   - **Download Private Key**: Save the `.key` file (you'll need this!)
   - **Download Public Key**: Optional, but recommended

7. Click **"Create"** and wait 1-2 minutes for the instance to provision

8. **Note Your Public IP**: Once created, copy the public IP address (e.g., `123.45.67.89`)

---

## Step 3: Configure Firewall Rules

### A. Oracle Cloud Security List (Cloud Firewall)

1. Go to: **Networking → Virtual Cloud Networks**
2. Click your VCN name
3. Click **"Security Lists"** → Click your security list
4. Click **"Add Ingress Rules"**

Add these rules:

**Rule 1: SSH Access**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `22`
- Description: `SSH access`

**Rule 2: IBKR Gateway (HTTPS)**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `5055`
- Description: `IBKR Gateway HTTPS`

**Rule 3: Flask Dashboard (HTTP)**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `5056`
- Description: `Flask Dashboard`

### B. Ubuntu Firewall (iptables)

After SSH'ing into your instance (Step 4), run:

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5055 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5056 -j ACCEPT
sudo netfilter-persistent save
```

---

## Step 4: Connect to Your Instance via SSH

### On Linux/Mac:

```bash
# Set correct permissions for the private key
chmod 400 ~/Downloads/ssh-key-*.key

# SSH into your instance (replace with your public IP and key path)
ssh -i ~/Downloads/ssh-key-*.key ubuntu@YOUR_PUBLIC_IP
```

### On Windows:

Use **PuTTY** or **Windows Terminal**:

```powershell
ssh -i C:\Users\YourName\Downloads\ssh-key-*.key ubuntu@YOUR_PUBLIC_IP
```

---

## Step 5: Install Docker on Ubuntu

Once connected via SSH, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (no need for sudo)
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
```

SSH back in:
```bash
ssh -i ~/Downloads/ssh-key-*.key ubuntu@YOUR_PUBLIC_IP
```

---

## Step 6: Upload Your Project Files

### Option A: Using Git (Recommended)

```bash
# Install git if not already installed
sudo apt install git -y

# Clone your repository
git clone https://github.com/M-oses340/ibkr-dashboard.git
cd ibkr-dashboard
```

### Option B: Using SCP (Manual Upload)

From your local machine:

```bash
# Upload the entire project directory
scp -i ~/Downloads/ssh-key-*.key -r interactive-brokers-web-api ubuntu@YOUR_PUBLIC_IP:~/
```

---

## Step 7: Configure Your Bot

SSH into your instance and edit the configuration:

```bash
cd interactive-brokers-web-api

# Edit conf.yaml with your IBKR credentials
nano conf.yaml
```

Update these fields:
```yaml
ips:
  - YOUR_PUBLIC_IP  # Add your Oracle Cloud public IP

accounts:
  - DUP158699  # Your demo account ID
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 8: Start the Services

```bash
# Start Docker containers
docker-compose up -d

# Check if containers are running
docker ps

# View logs
docker-compose logs -f
```

You should see:
- `ibkr-gateway` running on port 5055
- `ibkr-webapp` running on port 5056

---

## Step 9: Access Your Services

Open your browser:

- **IBKR Gateway**: `https://YOUR_PUBLIC_IP:5055`
- **Flask Dashboard**: `http://YOUR_PUBLIC_IP:5056`

Accept the self-signed certificate warning for the gateway.

---

## Step 10: Start Your Trading Bot

SSH into your instance:

```bash
cd interactive-brokers-web-api/bot

# Install Python dependencies
pip3 install -r requirements.txt

# Run the portfolio bot in the background
nohup python3 portfolio_bot.py > bot.log 2>&1 &

# Check if it's running
ps aux | grep portfolio_bot

# View live logs
tail -f bot.log
```

---

## Step 11: Keep Bot Running (Auto-Restart on Reboot)

Create a systemd service to auto-start your bot:

```bash
sudo nano /etc/systemd/system/ibkr-bot.service
```

Paste this content:

```ini
[Unit]
Description=IBKR Portfolio Trading Bot
After=network.target docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/interactive-brokers-web-api/bot
ExecStart=/usr/bin/python3 /home/ubuntu/interactive-brokers-web-api/bot/portfolio_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/interactive-brokers-web-api/bot/bot.log
StandardError=append:/home/ubuntu/interactive-brokers-web-api/bot/bot.log

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ibkr-bot.service
sudo systemctl start ibkr-bot.service

# Check status
sudo systemctl status ibkr-bot.service

# View logs
sudo journalctl -u ibkr-bot.service -f
```

---

## Useful Commands

### Check Bot Status
```bash
sudo systemctl status ibkr-bot.service
```

### Restart Bot
```bash
sudo systemctl restart ibkr-bot.service
```

### Stop Bot
```bash
sudo systemctl stop ibkr-bot.service
```

### View Bot Logs
```bash
tail -f ~/interactive-brokers-web-api/bot/bot.log
```

### Check Docker Containers
```bash
docker ps
docker-compose logs -f
```

### Update Bot Code (if using Git)
```bash
cd ~/interactive-brokers-web-api
git pull
sudo systemctl restart ibkr-bot.service
```

---

## Monitoring Your Bot

### Check Recent Orders
```bash
cd ~/interactive-brokers-web-api/bot
python3 check_stock_orders.py
```

### Check Portfolio
```bash
python3 get_portfolio.py
```

### Monitor System Resources
```bash
# CPU and memory usage
htop

# Disk usage
df -h

# Network usage
sudo iftop
```

---

## Troubleshooting

### Bot Not Starting
```bash
# Check logs
sudo journalctl -u ibkr-bot.service -n 50

# Check if Python dependencies are installed
pip3 list | grep -E "requests|yfinance"
```

### Can't Access Gateway/Dashboard
```bash
# Check if containers are running
docker ps

# Check firewall rules
sudo iptables -L -n

# Restart Docker containers
docker-compose restart
```

### Out of Memory
```bash
# Check memory usage
free -h

# If needed, create swap space (1GB)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Security Best Practices

1. **Change SSH Port** (optional but recommended):
```bash
sudo nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222
sudo systemctl restart sshd
```

2. **Enable Automatic Security Updates**:
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

3. **Set Up Firewall**:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 5055/tcp
sudo ufw allow 5056/tcp
sudo ufw enable
```

4. **Monitor Failed Login Attempts**:
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Cost Monitoring

Even though it's free, monitor your usage:

1. Go to: **Governance → Cost Analysis**
2. Check your usage stays within Always Free limits:
   - 2 VMs (1 OCPU each)
   - 200GB storage
   - 10TB outbound data transfer/month

---

## Next Steps

Your bot is now running 24/7 on Oracle Cloud! 

- Monitor orders via the Flask dashboard: `http://YOUR_PUBLIC_IP:5056`
- Check logs regularly: `tail -f ~/interactive-brokers-web-api/bot/bot.log`
- Update your bot code as needed and restart the service

Happy trading! 🚀📈
