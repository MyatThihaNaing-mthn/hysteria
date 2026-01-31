# Hysteria 2 VPN Server - Frequently Asked Questions (FAQ)

## General Questions

### What is Hysteria 2?
Hysteria 2 is a powerful, modern proxy protocol built on QUIC. It provides high-performance, censorship-resistant proxy services that are especially effective over unreliable networks.

### Why use Hysteria instead of other VPN protocols?
- **Faster**: Optimized for high-latency, lossy networks
- **Censorship-resistant**: Masquerades as HTTP/3 traffic
- **Modern**: Built on QUIC protocol (same as HTTP/3)
- **Efficient**: Better performance than traditional VPNs over poor connections

### How many users can one server support?
With the provided configuration, a single server can comfortably support 20-30 concurrent users. With proper resources (4GB RAM, 4vCPU, 2Gbps network), you can support 50-100 users.

## Installation & Setup

### How long does it take to set up?
- **Quick setup**: 10-15 minutes using the Quick Start guide
- **Production setup**: 30-60 minutes with full security hardening

### Do I need a domain name?
**Recommended but not required:**
- **With domain**: Can use Let's Encrypt for automatic TLS certificates
- **Without domain**: Must use self-signed certificates (clients need to trust them)

### What operating systems are supported?
**Server:**
- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- Docker (any OS with Docker support)

**Client:**
- Windows, macOS, Linux
- Android, iOS (via compatible apps)

### Can I run this on a home server?
Yes, but you need:
- Public IP address or port forwarding
- Good upload bandwidth
- 24/7 uptime
- Sufficient power and cooling

Cloud servers are recommended for better reliability and bandwidth.

## Configuration

### How do I change the server port?
Edit `/etc/hysteria/config.yaml`:
```yaml
listen: :8443  # Change from default :443
```
Don't forget to update firewall rules!

### How do I add more users?
**Option 1: Using the management script**
```bash
./manage-users.sh add username
```

**Option 2: Manual edit**
Edit `/etc/hysteria/config.yaml` and add under `auth.userpass`:
```yaml
newuser: "SecurePassword123!"
```
Then restart: `systemctl restart hysteria-server`

### How do I remove a user?
```bash
./manage-users.sh remove username
# OR manually edit config.yaml and restart service
```

### Can I limit bandwidth per user?
Currently, Hysteria doesn't support per-user bandwidth limits. You can only set server-wide limits. Consider using traffic statistics to monitor and manually manage users who abuse bandwidth.

### How do I change the obfuscation password?
1. Edit `/etc/hysteria/config.yaml`
2. Update `obfs.salamander.password`
3. Restart server: `systemctl restart hysteria-server`
4. **Important**: Notify all users to update their client configuration

## Security

### Is Hysteria secure?
Yes, Hysteria uses:
- **TLS encryption**: Same as HTTPS websites
- **QUIC protocol**: Modern, secure transport
- **Obfuscation**: Optional Salamander obfuscation layer
- **Authentication**: Username/password per user

### Should I use obfuscation?
**Yes, if:**
- You're in a country with internet censorship
- Your ISP does deep packet inspection
- You want maximum privacy

**No, if:**
- You're only bypassing geo-restrictions
- You want slightly better performance
- Obfuscation is not needed in your region

### How often should I change passwords?
**Recommendations:**
- Server passwords: Every 3-6 months
- Compromised accounts: Immediately
- Inactive users: Remove after 30 days

### What should I do if my server is detected/blocked?
1. **Change obfuscation password**
2. **Change server port** (try 8443, 443, 53)
3. **Update masquerade target** to a popular website
4. **Consider using a CDN** (CloudFlare) in front
5. **Move to a different IP/provider** as last resort

## Performance

### Why is my connection slow?
**Server-side issues:**
- Check CPU/RAM usage: `htop`
- Check bandwidth: `iftop`
- Review logs: `journalctl -u hysteria-server -n 100`
- Verify bandwidth limits in config

**Client-side issues:**
- Update client bandwidth settings
- Check local network quality
- Try different obfuscation settings

### How can I improve performance?
**Server optimization:**
1. Increase QUIC buffer sizes (see DEPLOYMENT_GUIDE.md)
2. Optimize system network settings
3. Use a faster server/network
4. Reduce concurrent user count

**Client optimization:**
1. Set accurate bandwidth in client config
2. Use UDP (not TCP) for client connection
3. Disable unnecessary features

### What's the typical speed loss?
- **Good conditions**: 5-10% slower than direct connection
- **Poor network**: Can be faster than direct (thanks to QUIC)
- **With obfuscation**: Additional 2-5% overhead

### Can Hysteria improve my internet speed?
No, Hysteria cannot make your internet faster than your ISP's limits. However, on congested or unreliable networks, QUIC's congestion control can provide better throughput than TCP-based protocols.

## Troubleshooting

### Server won't start
```bash
# Check configuration syntax
hysteria server -c /etc/hysteria/config.yaml --check

# Check logs
journalctl -u hysteria-server -n 100

# Common issues:
# - Invalid YAML syntax
# - Missing certificate files
# - Port already in use
# - Invalid authentication config
```

### Clients can't connect
**Check:**
1. Server is running: `systemctl status hysteria-server`
2. Port is open: `ss -tulpn | grep :443`
3. Firewall allows UDP/443: `ufw status`
4. Credentials are correct
5. Obfuscation password matches
6. Certificate is valid

**Test from server:**
```bash
nc -zvu localhost 443
```

### Authentication keeps failing
- **Check username**: Usernames are case-insensitive
- **Check password**: Passwords are case-sensitive
- **Check format**: Must be `username:password` in client
- **Check config**: Verify user exists in server config
- **Check logs**: `journalctl -u hysteria-server | grep auth`

### Certificate errors
**Let's Encrypt issues:**
- Verify domain DNS points to server
- Check ports 80 and 443 are accessible
- Ensure email is valid
- Wait for DNS propagation (up to 48 hours)

**Self-signed certificate:**
- Clients must explicitly trust the certificate
- Or disable certificate verification (less secure)

### High CPU usage
1. Check number of active users
2. Review bandwidth per user
3. Consider upgrading server
4. Check for CPU-intensive attacks
5. Optimize QUIC settings

### Out of memory errors
1. Check user count vs. RAM
2. Review QUIC buffer settings (reduce if needed)
3. Upgrade server RAM
4. Check for memory leaks (restart server)

## Monitoring & Management

### How do I check server status?
```bash
# Service status
systemctl status hysteria-server

# Real-time monitoring
./monitor.py -w

# View logs
journalctl -u hysteria-server -f
```

### How do I see traffic statistics?
```bash
# Using curl
curl -H "Authorization: YOUR_SECRET" http://127.0.0.1:8080/traffic

# Using monitor script
./monitor.py

# Continuous monitoring
./monitor.py -w
```

### How do I backup my configuration?
```bash
# Manual backup
cp /etc/hysteria/config.yaml /path/to/backup/

# Using management script
./manage-users.sh backup

# Automated daily backup (crontab)
0 2 * * * cp /etc/hysteria/config.yaml /backup/config-$(date +\%Y\%m\%d).yaml
```

### How do I update Hysteria?
```bash
# Using install script
bash <(curl -fsSL https://get.hy2.sh/)

# With Docker
docker pull ghcr.io/apernet/hysteria:latest
docker restart hysteria-server

# Check version
hysteria version
```

## Costs & Scaling

### How much does it cost to run?
**Monthly costs for 20-30 users:**
- Server: $12-30 (depending on provider)
- Domain: $1-2 (annual cost divided by 12)
- **Total**: $13-32/month

**Per user**: $0.43-$1.07/month

### How do I scale to more users?
**30-50 users:**
- Upgrade to 4GB RAM, 4vCPU server
- Increase bandwidth limits
- Monitor resource usage closely

**50+ users:**
- Multiple servers with load balancing
- Geographic distribution
- Automated monitoring and alerting

### Can I charge users?
Yes, many operators charge $2-10/user/month to cover costs and maintenance. Ensure you comply with local laws regarding internet services.

## Advanced Topics

### Can I use this with Docker?
Yes! See `docker-compose.yml` for easy Docker deployment:
```bash
docker-compose up -d
```

### Can I run multiple Hysteria servers?
Yes, you can run multiple servers:
1. On same machine (different ports)
2. On different machines (load balancing)
3. In different regions (GeoDNS routing)

### Does Hysteria support IPv6?
Yes, Hysteria fully supports IPv6. Make sure your server has IPv6 connectivity and update your configuration accordingly.

### Can I integrate with existing authentication systems?
Yes, Hysteria supports:
- HTTP authentication endpoint
- External command authentication
- Custom authentication scripts

See DEPLOYMENT_GUIDE.md for details.

### How do I enable logging?
Logs are automatically sent to systemd journal:
```bash
# View all logs
journalctl -u hysteria-server

# Follow new logs
journalctl -u hysteria-server -f

# Last 100 lines
journalctl -u hysteria-server -n 100

# Errors only
journalctl -u hysteria-server -p err
```

### Can I use this for torrenting?
While technically possible, be aware:
- Check your provider's ToS
- May violate DMCA/copyright laws
- Can consume excessive bandwidth
- Consider limiting or prohibiting in your ToS

### How do I implement rate limiting?
Hysteria has built-in bandwidth limits:
```yaml
bandwidth:
  up: 1 gbps    # Total server upload
  down: 1 gbps  # Total server download
```

For per-user limits, you'll need to:
- Monitor via traffic stats API
- Automatically disable users exceeding limits
- Or use external traffic shaping tools

## Client Configuration

### What's the minimal client configuration?
```yaml
server: your-domain.com:443
auth: username:password
socks5:
  listen: 127.0.0.1:1080
```

### How do users get connected?
1. **Provide credentials** using USER_CREDENTIALS_TEMPLATE.md
2. **User downloads** Hysteria client for their platform
3. **User configures** client with provided credentials
4. **User connects** and starts browsing

### What clients are available?
- **Official CLI**: Windows, macOS, Linux
- **GUI Clients**: Various third-party apps
- **Mobile**: Apps supporting Hysteria 2 protocol
- See: https://v2.hysteria.network/docs/getting-started/Installation/

### Can I use Hysteria with existing proxy software?
Yes, Hysteria provides:
- SOCKS5 proxy (most compatible)
- HTTP proxy
- Can integrate with browsers, apps, system proxy

## Compliance & Legal

### Is running a VPN server legal?
**Depends on your location:**
- Legal in most countries for personal/business use
- Some countries restrict or ban VPN services
- Check local laws before deploying
- Commercial use may require licensing

### What logs should I keep?
**Recommended (minimal logging):**
- Server errors and crashes
- Authentication failures
- Service start/stop events

**NOT recommended:**
- User traffic content
- Destination addresses
- Connection timestamps (beyond rotation)

### Do I need a business license?
**Depends on usage:**
- Personal use: Usually no
- Friends/family: Usually no
- Commercial service: Likely yes
- Check local business regulations

### What about GDPR/privacy laws?
If serving EU users:
- Have a privacy policy
- Minimize data collection
- Secure stored data
- Allow data deletion requests
- Document your processes

## Getting Help

### Where can I get support?
1. **Documentation**: Check DEPLOYMENT_GUIDE.md and QUICK_START.md
2. **Official Docs**: https://v2.hysteria.network/
3. **Community**: Telegram group https://t.me/hysteria_github
4. **GitHub**: Open an issue for bugs
5. **This FAQ**: Search here first!

### How do I report a bug?
1. Check if it's already reported on GitHub
2. Gather relevant information:
   - Server OS and version
   - Hysteria version
   - Configuration (sanitized)
   - Error logs
   - Steps to reproduce
3. Open issue at: https://github.com/apernet/hysteria/issues

### How can I contribute?
- Report bugs and issues
- Suggest improvements
- Submit pull requests
- Help other users in community
- Improve documentation
- Share your setup/experience

### Where do I find more advanced documentation?
- **Official Docs**: https://v2.hysteria.network/
- **Protocol Spec**: See PROTOCOL.md
- **Network Architecture**: See NETWORK_ARCHITECTURE.md
- **Deployment Guide**: See DEPLOYMENT_GUIDE.md
- **GitHub Wiki**: Community guides and tips

## Common Error Messages

### "Failed to bind to address"
- Port already in use
- Another service using port 443
- Try: `ss -tulpn | grep :443`
- Solution: Stop other service or change port

### "TLS handshake failed"
- Invalid certificate
- Certificate expired
- Client doesn't trust certificate
- Check certificate validity and configuration

### "Authentication failed"
- Wrong username or password
- User not in config file
- Check username case (case-insensitive)
- Verify password (case-sensitive)

### "Connection timeout"
- Firewall blocking UDP/443
- Server not running
- Wrong server address
- Network issues

### "Too many open files"
- Increase file descriptor limit
- Edit /etc/security/limits.conf
- Restart server

## Best Practices

### Security Best Practices
1. Use strong, unique passwords
2. Change default obfuscation password
3. Keep server software updated
4. Use Let's Encrypt certificates
5. Enable firewall
6. Monitor logs regularly
7. Remove inactive users
8. Regular backups

### Performance Best Practices
1. Use SSD storage
2. Choose server close to users
3. Optimize QUIC buffer sizes
4. Monitor resource usage
5. Don't oversubscribe bandwidth
6. Regular server restarts (weekly)

### Management Best Practices
1. Document your setup
2. Keep configuration backed up
3. Monitor traffic statistics
4. Have a disaster recovery plan
5. Test client connections regularly
6. Keep user credentials secure
7. Maintain user communication channel

---

**Didn't find your answer?** Check the [Deployment Guide](DEPLOYMENT_GUIDE.md) or ask in the [community](https://t.me/hysteria_github).
