# Hysteria 2 VPN Server - Quick Start Guide
## Get Your VPN Server Running in 10 Minutes

This guide will get your Hysteria 2 VPN server up and running quickly to support 20-30 users.

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] A Linux server (Ubuntu/Debian/CentOS) with root access
- [ ] A public IP address
- [ ] A domain name pointing to your server (recommended)
- [ ] At least 2GB RAM and 2 CPU cores
- [ ] Port 443/UDP open in firewall

## Step-by-Step Setup

### Step 1: Install Hysteria Server (2 minutes)

**Option A: One-Line Install (Recommended)**
```bash
bash <(curl -fsSL https://get.hy2.sh/)
```

**Option B: Using Docker**
```bash
# Install Docker if not already installed
curl -fsSL https://get.docker.com | sh

# Pull Hysteria image
docker pull ghcr.io/apernet/hysteria:latest
```

### Step 2: Prepare Configuration (3 minutes)

```bash
# Create config directory
sudo mkdir -p /etc/hysteria

# Copy the example configuration
sudo cp server-config.yaml /etc/hysteria/config.yaml

# Edit the configuration
sudo nano /etc/hysteria/config.yaml
```

**Required Changes:**

1. **Update Authentication** - Change usernames and passwords:
   ```yaml
   auth:
     type: userpass
     userpass:
       alice: "YourStrongPassword1!"
       bob: "YourStrongPassword2!"
       charlie: "YourStrongPassword3!"
       # Add up to 30 users...
   ```

2. **Update Obfuscation Password**:
   ```yaml
   obfs:
     type: salamander
     salamander:
       password: "YourSecretObfuscationKey!"
   ```

3. **Update Traffic Stats Secret**:
   ```yaml
   trafficStats:
     secret: "YourTrafficStatsSecret!"
   ```

### Step 3: Setup TLS Certificate (3 minutes)

**Option A: Self-Signed (Quick Test)**
```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -newkey rsa:4096 \
  -keyout /etc/hysteria/server.key \
  -out /etc/hysteria/server.crt \
  -days 365 \
  -subj "/CN=yourdomain.com"

sudo chmod 600 /etc/hysteria/server.key
```

**Option B: Let's Encrypt (Recommended for Production)**

Edit `/etc/hysteria/config.yaml` and replace the TLS section:
```yaml
tls:
  acme:
    domains:
      - your-domain.com
    email: your-email@example.com
```

Remove or comment out the `cert:` and `key:` lines.

### Step 4: Start the Server (1 minute)

**If using systemd:**
```bash
# Copy the service file
sudo cp hysteria-server.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Start and enable the service
sudo systemctl start hysteria-server
sudo systemctl enable hysteria-server

# Check status
sudo systemctl status hysteria-server
```

**If using Docker:**
```bash
# Using docker-compose
docker-compose up -d

# Or using docker run
docker run -d \
  --name hysteria-server \
  --restart always \
  --network host \
  -v /etc/hysteria:/etc/hysteria \
  ghcr.io/apernet/hysteria:latest \
  server -c /etc/hysteria/config.yaml
```

### Step 5: Verify Installation (1 minute)

```bash
# Check if server is running
sudo systemctl status hysteria-server
# OR
docker ps | grep hysteria

# Check logs
sudo journalctl -u hysteria-server -n 50
# OR
docker logs hysteria-server

# Verify port is listening
sudo ss -tulpn | grep :443
```

You should see output showing the server is running on port 443.

## Firewall Configuration

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 443/udp
sudo ufw enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --add-port=443/udp --permanent
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p udp --dport 443 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

## Provide Credentials to Users

Use the template in `USER_CREDENTIALS_TEMPLATE.md` to create credentials for each user.

**Quick example:**

```
Server: your-domain.com:443
Username: alice
Password: YourStrongPassword1!

Client Config:
server: your-domain.com:443
auth: alice:YourStrongPassword1!
obfs:
  type: salamander
  salamander:
    password: YourSecretObfuscationKey!
```

## Testing the Connection

From a client machine:

```bash
# Create client config
cat > client-config.yaml << EOF
server: your-domain.com:443
auth: alice:YourStrongPassword1!

obfs:
  type: salamander
  salamander:
    password: YourSecretObfuscationKey!

socks5:
  listen: 127.0.0.1:1080

http:
  listen: 127.0.0.1:8080
EOF

# Start client
hysteria client -c client-config.yaml
```

Then test the proxy:
```bash
# Test SOCKS5 proxy
curl -x socks5h://127.0.0.1:1080 https://ifconfig.me

# Should show your server's IP
```

## User Management

Use the management script to easily add/remove users:

```bash
# Make script executable
chmod +x manage-users.sh

# List all users
./manage-users.sh list

# Add a new user (auto-generates password)
./manage-users.sh add john

# Add a user with specific password
./manage-users.sh add jane MyPassword123!

# Change password
./manage-users.sh password john

# Remove a user
./manage-users.sh remove john

# Restart server after changes
./manage-users.sh restart
```

## Monitoring

### Check Server Status
```bash
# Service status
sudo systemctl status hysteria-server

# Resource usage
htop

# Network connections
sudo ss -tuln | grep :443

# Active users
sudo journalctl -u hysteria-server | grep Connect
```

### Traffic Statistics
```bash
# Get current traffic stats
curl -H "Authorization: YourTrafficStatsSecret!" \
  http://127.0.0.1:8080/traffic
```

## Common Issues and Solutions

### 1. Server won't start
```bash
# Check configuration syntax
hysteria server -c /etc/hysteria/config.yaml --check

# Check logs
sudo journalctl -u hysteria-server -n 100
```

### 2. Port already in use
```bash
# Check what's using port 443
sudo lsof -i :443

# Change port in config.yaml if needed
listen: :8443
```

### 3. Certificate errors
```bash
# Verify certificate files exist
ls -la /etc/hysteria/server.{crt,key}

# Check certificate validity
openssl x509 -in /etc/hysteria/server.crt -text -noout
```

### 4. Connection refused
```bash
# Check firewall
sudo ufw status
sudo firewall-cmd --list-all

# Verify server is listening
sudo ss -tulpn | grep :443
```

## Performance Tuning for 20-30 Users

If you experience performance issues:

1. **Increase system limits:**
```bash
# Edit /etc/sysctl.conf
sudo nano /etc/sysctl.conf

# Add these lines:
net.core.rmem_max=134217728
net.core.wmem_max=134217728
net.ipv4.tcp_rmem=4096 87380 67108864
net.ipv4.tcp_wmem=4096 65536 67108864

# Apply changes
sudo sysctl -p
```

2. **Adjust bandwidth in config:**
```yaml
bandwidth:
  up: 2 gbps    # Increase if you have more capacity
  down: 2 gbps
```

3. **Increase QUIC buffers:**
```yaml
quic:
  initStreamReceiveWindow: 16777216   # 16MB
  maxStreamReceiveWindow: 16777216
  initConnReceiveWindow: 41943040     # 40MB
  maxConnReceiveWindow: 41943040
  maxIncomingStreams: 1024
```

## Security Checklist

- [ ] Changed all default passwords
- [ ] Using strong passwords (16+ characters)
- [ ] Updated obfuscation password
- [ ] Updated traffic stats secret
- [ ] Firewall configured (only port 443/UDP open)
- [ ] Using HTTPS certificates (Let's Encrypt or valid cert)
- [ ] Server software up to date
- [ ] Regular monitoring enabled
- [ ] Backups configured

## Maintenance

**Daily:**
- Check logs for errors: `sudo journalctl -u hysteria-server -p err`
- Monitor resource usage: `htop`

**Weekly:**
- Check for updates: `bash <(curl -fsSL https://get.hy2.sh/)`
- Review traffic stats

**Monthly:**
- Backup configuration: `cp /etc/hysteria/config.yaml /etc/hysteria/config.yaml.backup`
- Review user list
- Update certificates if needed

## Next Steps

1. Read the full [Deployment Guide](DEPLOYMENT_GUIDE.md) for advanced configuration
2. Setup automated monitoring and alerts
3. Configure log rotation
4. Setup automated backups
5. Document your specific configuration for your team

## Getting Help

- **Documentation:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Official Docs:** https://v2.hysteria.network/
- **Community:** https://t.me/hysteria_github
- **Issues:** https://github.com/apernet/hysteria/issues

## Success! 🎉

Your Hysteria 2 VPN server is now running and ready to serve 20-30 users!

Remember to:
- Save all passwords securely
- Provide credentials to users using the template
- Monitor server performance regularly
- Keep the server software updated
