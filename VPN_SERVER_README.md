# Hysteria 2 VPN Server Setup for 20-30 Users

This repository now includes complete deployment configuration and documentation for setting up a Hysteria 2 VPN server that can accommodate 20-30 concurrent users.

## 📁 What's Included

### Configuration Files
- **`server-config.yaml`** - Production-ready server configuration with 30 user slots
- **`docker-compose.yml`** - Docker Compose configuration for containerized deployment
- **`hysteria-server.service`** - Systemd service file for native Linux deployment

### Documentation
- **`QUICK_START.md`** - Get your server running in 10 minutes
- **`DEPLOYMENT_GUIDE.md`** - Comprehensive deployment and operations guide
- **`USER_CREDENTIALS_TEMPLATE.md`** - Template for distributing credentials to users

### Tools
- **`manage-users.sh`** - Script for easy user management (add/remove/password changes)

## 🚀 Quick Start

### For the Impatient (2 Commands)

```bash
# 1. Install Hysteria
bash <(curl -fsSL https://get.hy2.sh/)

# 2. Use the provided configuration
sudo cp server-config.yaml /etc/hysteria/config.yaml
# Edit config.yaml to change passwords, then start:
sudo systemctl start hysteria-server
```

**That's it!** Your VPN server is running.

⚠️ **Important:** Before connecting, you must:
1. Edit `/etc/hysteria/config.yaml` to change default passwords
2. Setup TLS certificates (see Quick Start guide)

## 📖 Getting Started

Choose your path:

### 🏃 Fast Track (10 minutes)
Read **[QUICK_START.md](QUICK_START.md)** - Get your server up in 10 minutes with minimal configuration.

### 🎓 Complete Setup (30 minutes)
Read **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Full deployment guide with monitoring, security hardening, and best practices.

### 🐳 Docker Deployment
```bash
# 1. Update server-config.yaml with your settings
# 2. Start with Docker Compose
docker-compose up -d
```

## 🔑 Key Features

### Server Configuration
- ✅ **Optimized for 20-30 users** with appropriate QUIC buffer sizes
- ✅ **Username/password authentication** - Easy to manage multiple users
- ✅ **Bandwidth management** - Fair distribution across all users
- ✅ **Salamander obfuscation** - Bypass censorship and DPI
- ✅ **Traffic statistics API** - Monitor per-user bandwidth usage
- ✅ **UDP relay support** - For gaming and video calls
- ✅ **HTTP/3 masquerading** - Looks like a normal website

### Security
- 🔒 TLS encryption with Let's Encrypt support
- 🔒 Strong password requirements
- 🔒 Traffic obfuscation
- 🔒 Per-user authentication and tracking
- 🔒 Secure defaults

### Management
- 🛠️ Easy user management script
- 🛠️ Automated backups
- 🛠️ Health monitoring
- 🛠️ Detailed logging
- 🛠️ Traffic statistics

## 📊 Server Requirements

For optimal performance with 20-30 users:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 1 core | 2+ cores |
| **RAM** | 1GB | 4GB |
| **Network** | 500 Mbps | 1 Gbps |
| **Storage** | 5GB | 10GB+ |
| **OS** | Linux | Ubuntu 22.04 LTS |

## 👥 User Management

### Add a User
```bash
./manage-users.sh add alice
# Generates secure password automatically
```

### Remove a User
```bash
./manage-users.sh remove bob
```

### Change Password
```bash
./manage-users.sh password alice
```

### List All Users
```bash
./manage-users.sh list
```

## 📈 Monitoring

### Check Server Status
```bash
systemctl status hysteria-server
```

### View Logs
```bash
journalctl -u hysteria-server -f
```

### Traffic Statistics
```bash
curl -H "Authorization: YOUR_SECRET" http://127.0.0.1:8080/traffic
```

## 🔧 Configuration Overview

### Key Settings to Customize

1. **User Credentials** (`auth.userpass`)
   ```yaml
   userpass:
     user1: "StrongPassword1!"
     user2: "StrongPassword2!"
   ```

2. **Bandwidth Limits** (`bandwidth`)
   ```yaml
   bandwidth:
     up: 1 gbps    # Server upload to clients
     down: 1 gbps  # Server download from clients
   ```

3. **Obfuscation Password** (`obfs.salamander.password`)
   ```yaml
   salamander:
     password: "YourObfuscationSecret!"
   ```

4. **TLS Certificate** (`tls`)
   ```yaml
   # Option 1: Let's Encrypt (auto)
   tls:
     acme:
       domains: ["your-domain.com"]
       email: "you@example.com"
   
   # Option 2: Your own certificates
   tls:
     cert: /path/to/cert.pem
     key: /path/to/key.pem
   ```

## 🎯 Client Setup

After setting up the server, provide users with credentials using `USER_CREDENTIALS_TEMPLATE.md`.

Basic client configuration:
```yaml
server: your-domain.com:443
auth: username:password
obfs:
  type: salamander
  salamander:
    password: YOUR_OBFS_PASSWORD
socks5:
  listen: 127.0.0.1:1080
```

## 🆘 Troubleshooting

### Server won't start
```bash
# Check configuration
hysteria server -c /etc/hysteria/config.yaml --check

# View error logs
journalctl -u hysteria-server -n 100
```

### Can't connect from client
1. Check firewall allows UDP port 443
2. Verify credentials are correct
3. Ensure obfuscation password matches
4. Check server logs for authentication errors

### Slow performance
1. Increase bandwidth limits in config
2. Optimize QUIC buffer sizes
3. Check server resource usage (CPU/RAM/Network)
4. Review system network limits

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

## 📚 Documentation Structure

```
.
├── QUICK_START.md                 # 10-minute setup guide
├── DEPLOYMENT_GUIDE.md            # Complete deployment documentation
├── USER_CREDENTIALS_TEMPLATE.md   # User credential distribution template
├── server-config.yaml             # Server configuration (30 users)
├── docker-compose.yml             # Docker deployment config
├── hysteria-server.service        # Systemd service file
└── manage-users.sh               # User management script
```

## 🔐 Security Best Practices

1. **Change all default passwords** before deployment
2. **Use strong passwords** (16+ characters, mixed case, numbers, symbols)
3. **Enable firewall** and only open necessary ports
4. **Use Let's Encrypt** for TLS certificates
5. **Keep server updated** regularly
6. **Monitor logs** for suspicious activity
7. **Rotate passwords** periodically
8. **Backup configuration** regularly

## 📝 License

This deployment configuration follows the same license as the Hysteria project (MIT License).

## 🤝 Contributing

Found an issue or have a suggestion? Please open an issue or pull request.

## 📞 Support

- **Documentation Issues**: Open a GitHub issue
- **Hysteria Questions**: https://v2.hysteria.network/
- **Community**: https://t.me/hysteria_github

## 🎓 Additional Resources

- [Official Hysteria Documentation](https://v2.hysteria.network/)
- [Hysteria GitHub Repository](https://github.com/apernet/hysteria)
- [Client Installation Guide](https://v2.hysteria.network/docs/getting-started/Installation/)
- [Protocol Specification](PROTOCOL.md)

---

**Ready to deploy?** Start with [QUICK_START.md](QUICK_START.md)!
