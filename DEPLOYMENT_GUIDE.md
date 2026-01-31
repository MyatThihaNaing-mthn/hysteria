# Hysteria 2 VPN Server Deployment Guide
## For 20-30 Users

This guide will help you deploy and manage a Hysteria 2 VPN server that can accommodate 20-30 concurrent users.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [User Management](#user-management)
- [Certificate Setup](#certificate-setup)
- [Running the Server](#running-the-server)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Prerequisites

### Server Requirements
For 20-30 concurrent users, you'll need:

- **Operating System**: Linux (Ubuntu 20.04/22.04, Debian 11/12, CentOS 8+, or similar)
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum, 4GB+ recommended
- **Network**: 
  - 1 Gbps network connection recommended
  - At least 33 Mbps per user (1 Gbps / 30 users)
  - Public IP address
  - Open port 443 (or your chosen port) for incoming connections
- **Storage**: 10GB+ free space

### Domain Name (Recommended)
- A domain name pointing to your server's IP address
- Required for automatic TLS certificate generation via Let's Encrypt

## Quick Start

### One-Line Install (Linux)
```bash
bash <(curl -fsSL https://get.hy2.sh/) --install-server
```

### Configure and Start
```bash
# Copy the example configuration
cp server-config.yaml /etc/hysteria/config.yaml

# Edit the configuration file
nano /etc/hysteria/config.yaml

# Start the server
systemctl start hysteria-server
systemctl enable hysteria-server
```

## Installation

### Method 1: Using Install Script (Recommended)
```bash
# Download and run the installation script
bash <(curl -fsSL https://get.hy2.sh/)

# Or use the local install script
bash scripts/install_server.sh
```

### Method 2: Using Docker
```bash
# Pull the latest image
docker pull ghcr.io/apernet/hysteria:latest

# Create config directory
mkdir -p /etc/hysteria

# Copy configuration
cp server-config.yaml /etc/hysteria/config.yaml

# Run the server
docker run -d \
  --name hysteria-server \
  --restart always \
  -p 443:443/udp \
  -v /etc/hysteria:/etc/hysteria \
  ghcr.io/apernet/hysteria:latest server -c /etc/hysteria/config.yaml
```

### Method 3: Using Docker Compose
See `docker-compose.yml` in this repository.

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### Method 4: Manual Installation
```bash
# Download the latest release
VERSION=$(curl -s https://api.github.com/repos/apernet/hysteria/releases/latest | grep tag_name | cut -d '"' -f 4)
wget https://github.com/apernet/hysteria/releases/download/$VERSION/hysteria-linux-amd64

# Make executable and move to system path
chmod +x hysteria-linux-amd64
mv hysteria-linux-amd64 /usr/local/bin/hysteria

# Create config directory
mkdir -p /etc/hysteria

# Copy configuration
cp server-config.yaml /etc/hysteria/config.yaml
```

## Configuration

### 1. Edit Server Configuration
```bash
nano /etc/hysteria/config.yaml
```

### 2. Update Critical Settings

#### Listen Address
Change the listening port if needed (default is 443):
```yaml
listen: :443
```

#### Bandwidth Limits
Adjust based on your server's capacity:
```yaml
bandwidth:
  up: 1 gbps    # Total upload bandwidth
  down: 1 gbps  # Total download bandwidth
```

For 30 users on a 1 Gbps connection:
- Each user gets approximately 33 Mbps
- Adjust these values based on your actual server bandwidth

#### Authentication
Update usernames and passwords in the `auth` section:
```yaml
auth:
  type: userpass
  userpass:
    alice: "SecurePassword123!"
    bob: "AnotherSecurePass456!"
    # ... add more users
```

#### Obfuscation (Important for Censorship Resistance)
Change the obfuscation password:
```yaml
obfs:
  type: salamander
  salamander:
    password: "YourSecretObfuscationKey!"
```

#### Traffic Statistics Secret
Change the secret for the traffic stats API:
```yaml
trafficStats:
  secret: "YourTrafficStatsSecret!"
```

## User Management

### Adding New Users
1. Edit `/etc/hysteria/config.yaml`
2. Add user under `auth.userpass`:
   ```yaml
   newuser: "NewSecurePassword!"
   ```
3. Restart the server:
   ```bash
   systemctl restart hysteria-server
   ```

### Removing Users
1. Edit `/etc/hysteria/config.yaml`
2. Remove or comment out the user line
3. Restart the server

### Generating Strong Passwords
```bash
# Generate a random password
openssl rand -base64 32
```

### User Credentials Template
Create individual credential files for each user:

**user-credentials-template.txt**:
```
Hysteria 2 VPN Credentials
==========================

Server: your-server-domain.com:443
Username: [USERNAME]
Password: [PASSWORD]
Obfuscation: salamander
Obfuscation Password: [OBFS_PASSWORD from config]

Client Configuration:
server: your-server-domain.com:443
auth: [USERNAME]:[PASSWORD]
obfs:
  type: salamander
  salamander:
    password: [OBFS_PASSWORD]
```

## Certificate Setup

### Option 1: Automatic Certificates (Let's Encrypt) - Recommended

1. Update your DNS to point to your server
2. Modify `/etc/hysteria/config.yaml`:
   ```yaml
   tls:
     acme:
       domains:
         - your-domain.com
       email: your-email@example.com
   ```
3. Remove or comment out the `cert` and `key` lines

### Option 2: Manual Certificates

#### Using Let's Encrypt (Certbot)
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
# Update config.yaml:
```
```yaml
tls:
  cert: /etc/letsencrypt/live/your-domain.com/fullchain.pem
  key: /etc/letsencrypt/live/your-domain.com/privkey.pem
```

#### Using Self-Signed Certificates (Testing Only)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -newkey rsa:4096 \
  -keyout /etc/hysteria/server.key \
  -out /etc/hysteria/server.crt \
  -days 365 \
  -subj "/CN=your-domain.com"

# Update permissions
chmod 600 /etc/hysteria/server.key
```

## Running the Server

### Using Systemd (Recommended)

Create systemd service file:
```bash
sudo nano /etc/systemd/system/hysteria-server.service
```

Add the following content:
```ini
[Unit]
Description=Hysteria 2 VPN Server
After=network.target

[Service]
Type=simple
User=nobody
WorkingDirectory=/etc/hysteria
ExecStart=/usr/local/bin/hysteria server -c /etc/hysteria/config.yaml
Restart=on-failure
RestartSec=10s
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hysteria-server
sudo systemctl start hysteria-server
```

### Check Status
```bash
# Check if service is running
systemctl status hysteria-server

# View logs
journalctl -u hysteria-server -f

# View recent logs
journalctl -u hysteria-server -n 100
```

### Using Docker
```bash
# Start
docker start hysteria-server

# Stop
docker stop hysteria-server

# Restart
docker restart hysteria-server

# View logs
docker logs -f hysteria-server
```

## Monitoring

### Traffic Statistics API

The traffic stats API provides real-time monitoring of user connections and bandwidth usage.

#### Enable Traffic Stats
Already enabled in the default config on `127.0.0.1:8080`.

#### Query Traffic Stats
```bash
# Get traffic statistics
curl -H "Authorization: YOUR_SECRET_HERE" http://127.0.0.1:8080/traffic

# Get online users
curl -H "Authorization: YOUR_SECRET_HERE" http://127.0.0.1:8080/online
```

#### Example Python Script for Monitoring
```python
#!/usr/bin/env python3
import requests
import json

STATS_URL = "http://127.0.0.1:8080/traffic"
SECRET = "YourTrafficStatsSecret!"

headers = {"Authorization": SECRET}
response = requests.get(STATS_URL, headers=headers)

if response.status_code == 200:
    stats = response.json()
    print(json.dumps(stats, indent=2))
else:
    print(f"Error: {response.status_code}")
```

### System Monitoring

#### Check Server Load
```bash
# CPU and memory usage
htop

# Network traffic
iftop

# Disk usage
df -h
```

#### Monitor Connections
```bash
# Number of connections on port 443
ss -tuln | grep :443

# Active connections
ss -tn | grep ESTABLISHED | wc -l
```

### Log Monitoring
```bash
# Real-time logs
journalctl -u hysteria-server -f

# Errors only
journalctl -u hysteria-server -p err -f

# Last hour
journalctl -u hysteria-server --since "1 hour ago"
```

## Troubleshooting

### Server Won't Start

1. **Check configuration syntax**:
   ```bash
   hysteria server -c /etc/hysteria/config.yaml --check
   ```

2. **Check port availability**:
   ```bash
   ss -tuln | grep :443
   ```

3. **Check firewall**:
   ```bash
   # UFW
   sudo ufw allow 443/udp
   
   # firewalld
   sudo firewall-cmd --add-port=443/udp --permanent
   sudo firewall-cmd --reload
   ```

### Certificate Issues

1. **Check certificate files**:
   ```bash
   ls -la /etc/hysteria/server.{crt,key}
   ```

2. **Verify certificate**:
   ```bash
   openssl x509 -in /etc/hysteria/server.crt -text -noout
   ```

### Connection Issues

1. **Test from server**:
   ```bash
   nc -zvu localhost 443
   ```

2. **Check logs**:
   ```bash
   journalctl -u hysteria-server -n 100
   ```

3. **Verify DNS**:
   ```bash
   nslookup your-domain.com
   ```

### Performance Issues

1. **Monitor bandwidth usage**:
   ```bash
   iftop -i eth0
   ```

2. **Check system resources**:
   ```bash
   top
   free -h
   df -h
   ```

3. **Increase file descriptors**:
   ```bash
   ulimit -n 65536
   ```

## Security Best Practices

### 1. Use Strong Passwords
- Minimum 16 characters
- Mix of letters, numbers, and symbols
- Unique per user
- Generate using: `openssl rand -base64 32`

### 2. Keep Software Updated
```bash
# Update Hysteria
bash <(curl -fsSL https://get.hy2.sh/)

# Update system
sudo apt update && sudo apt upgrade -y
```

### 3. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 443/udp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

### 4. Fail2ban Protection
Install fail2ban to protect against brute force:
```bash
sudo apt install fail2ban
```

### 5. Regular Monitoring
- Check logs daily
- Monitor traffic statistics
- Review user access patterns

### 6. Backup Configuration
```bash
# Create backup
cp /etc/hysteria/config.yaml /etc/hysteria/config.yaml.backup

# Automated backup
echo "0 2 * * * cp /etc/hysteria/config.yaml /etc/hysteria/config.yaml.$(date +\%Y\%m\%d)" | crontab -
```

### 7. Rate Limiting
Already configured in `server-config.yaml`:
- Per-user bandwidth limits
- Connection idle timeout
- Maximum concurrent streams

### 8. Disable Unused Services
```bash
# Check running services
systemctl list-unit-files --state=enabled
```

### 9. Regular Audits
- Review user list monthly
- Remove inactive users
- Update passwords quarterly

### 10. Secure the Traffic Stats API
- Keep it on localhost (127.0.0.1)
- Use a strong secret
- Consider VPN access only for remote monitoring

## Performance Tuning

### For 20-30 Users on High-Speed Network

```yaml
quic:
  initStreamReceiveWindow: 16777216    # 16MB
  maxStreamReceiveWindow: 16777216     # 16MB
  initConnReceiveWindow: 41943040      # 40MB
  maxConnReceiveWindow: 41943040       # 40MB
  maxIncomingStreams: 1024
```

### Network Optimizations

```bash
# Increase system limits
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728
sudo sysctl -w net.ipv4.tcp_rmem='4096 87380 67108864'
sudo sysctl -w net.ipv4.tcp_wmem='4096 65536 67108864'

# Make permanent
echo "net.core.rmem_max=134217728" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max=134217728" | sudo tee -a /etc/sysctl.conf
```

## Client Configuration

Provide this template to your users:

```yaml
server: your-domain.com:443

auth: username:password

bandwidth:
  up: 100 mbps
  down: 100 mbps

obfs:
  type: salamander
  salamander:
    password: YOUR_OBFS_PASSWORD

socks5:
  listen: 127.0.0.1:1080

http:
  listen: 127.0.0.1:8080
```

## Maintenance Schedule

### Daily
- Check service status
- Review error logs
- Monitor resource usage

### Weekly
- Review traffic statistics
- Check for software updates
- Verify certificate validity

### Monthly
- Audit user list
- Review security logs
- Backup configuration
- Test disaster recovery

### Quarterly
- Update user passwords
- Review and update firewall rules
- Security audit

## Support and Resources

- Official Documentation: https://v2.hysteria.network/
- GitHub Repository: https://github.com/apernet/hysteria
- Community Support: https://t.me/hysteria_github
- Issue Tracker: https://github.com/apernet/hysteria/issues

## License

This deployment guide is provided as-is. Hysteria is licensed under MIT License.
