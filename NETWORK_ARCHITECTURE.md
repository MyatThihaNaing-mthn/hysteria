# Hysteria 2 VPN Server - Network Architecture Guide
## For 20-30 Users

This document provides network architecture guidance for deploying a Hysteria 2 VPN server to serve 20-30 concurrent users.

## Network Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Firewall/     │
                    │   Router        │
                    │   (Port 443/UDP)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────────────┐
                    │  Hysteria 2 Server      │
                    │  - Port 443/UDP         │
                    │  - Traffic Stats: 8080  │
                    │  - Masquerade: 80/443   │
                    └────────┬────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         ┌────▼─────┐                 ┌────▼─────┐
         │ Target   │                 │ Target   │
         │ Websites │                 │ Services │
         └──────────┘                 └──────────┘
```

## Client Connection Flow

```
┌──────────────┐
│ Client App   │
│ (30 Users)   │
└──────┬───────┘
       │ 1. QUIC Connection (UDP/443)
       │ 2. HTTP/3 POST /auth
       │ 3. Username:Password Auth
       │ 4. Salamander Obfuscation
       │
       ▼
┌──────────────┐
│ Hysteria     │
│ Server       │
└──────┬───────┘
       │ 5. Proxy Request
       │ 6. TCP/UDP Forwarding
       │
       ▼
┌──────────────┐
│ Destination  │
│ Server       │
└──────────────┘
```

## Server Specifications

### Minimum Requirements (20-30 Users)

| Component | Specification | Notes |
|-----------|---------------|-------|
| **CPU** | 2 vCPU @ 2.5 GHz | Higher frequency preferred |
| **RAM** | 2 GB | 4 GB recommended for headroom |
| **Network** | 1 Gbps | ~33 Mbps per user |
| **Storage** | 10 GB SSD | For OS, logs, certificates |
| **OS** | Ubuntu 22.04 LTS | Or equivalent modern Linux |

### Recommended Cloud Providers

| Provider | Instance Type | Monthly Cost (Est.) |
|----------|---------------|---------------------|
| AWS | t3.small or t3a.small | $15-20 |
| Google Cloud | e2-small | $15-18 |
| DigitalOcean | 2GB/2vCPU Droplet | $18 |
| Linode | Linode 2GB | $12 |
| Vultr | 2GB/1vCPU | $12 |
| Hetzner | CX21 | €5.83 (~$6) |

**Note:** Choose providers with:
- Good network connectivity to your target region
- Generous bandwidth allowances (minimum 2TB/month)
- No VPN restrictions in their ToS

## Bandwidth Planning

### Calculation for 30 Users

**Assumption:** Each user needs 50 Mbps on average

```
Total Required Bandwidth:
- Downstream (Server to Clients): 30 users × 50 Mbps = 1500 Mbps = 1.5 Gbps
- Upstream (Clients to Server): 30 users × 50 Mbps = 1500 Mbps = 1.5 Gbps
```

**Recommended Server Connection:** 2 Gbps (to handle peaks)

### Conservative Estimate

Most users won't use full bandwidth simultaneously:

```
Concurrent Peak Usage: 60% of users at 80% capacity
= 30 × 0.6 × 50 Mbps × 0.8
= 720 Mbps

Recommended Server: 1 Gbps connection
```

### Data Transfer Limits

For 30 users with moderate usage (10 GB/user/day):

```
Daily: 30 users × 10 GB = 300 GB/day
Monthly: 300 GB × 30 days = 9 TB/month
```

**Choose cloud providers with:**
- Unlimited bandwidth, OR
- At least 10 TB/month included bandwidth

## Port Configuration

### Required Ports

| Port | Protocol | Purpose | Accessibility |
|------|----------|---------|---------------|
| 443 | UDP | Hysteria main port | Public Internet |
| 8080 | TCP | Traffic stats API | Localhost only |

### Optional Ports (if using masquerade)

| Port | Protocol | Purpose | Accessibility |
|------|----------|---------|---------------|
| 80 | TCP | HTTP masquerade | Public Internet |
| 443 | TCP | HTTPS masquerade | Public Internet |

### Management Ports

| Port | Protocol | Purpose | Accessibility |
|------|----------|---------|---------------|
| 22 | TCP | SSH | Restricted IP only |

## Firewall Rules

### UFW Configuration (Ubuntu/Debian)

```bash
# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (restrict to your IP)
sudo ufw allow from YOUR_IP to any port 22 proto tcp

# Hysteria
sudo ufw allow 443/udp

# Optional: Masquerade ports
# sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### iptables Configuration

```bash
# Flush existing rules
iptables -F

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH (restrict to your IP)
iptables -A INPUT -p tcp -s YOUR_IP --dport 22 -j ACCEPT

# Hysteria
iptables -A INPUT -p udp --dport 443 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

## Security Architecture

### TLS/SSL Certificates

**Option 1: Let's Encrypt (Recommended)**
- Automatic renewal
- Widely trusted
- Free
- Requires domain name

**Option 2: Self-Signed**
- Quick setup
- No domain required
- Clients must trust certificate
- Good for testing

### Authentication Layers

1. **Network Layer**: UDP port 443
2. **Protocol Layer**: QUIC + HTTP/3
3. **Application Layer**: Hysteria username/password
4. **Obfuscation Layer**: Salamander XOR encryption

### Defense in Depth

```
┌─────────────────────────────────────┐
│  Firewall (UFW/iptables)            │
│  ├─ Drop all except 443/UDP         │
│  └─ Rate limiting                   │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  TLS Encryption                     │
│  ├─ X.509 Certificate               │
│  └─ Perfect Forward Secrecy         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  Salamander Obfuscation             │
│  ├─ XOR with BLAKE2b hash           │
│  └─ Random salt per packet          │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  Authentication                     │
│  ├─ Username/Password               │
│  └─ Per-user tracking               │
└─────────────────────────────────────┘
```

## Load Distribution

### Single Server (Up to 30 users)
```
All clients → Single Hysteria Server
```

**Pros:**
- Simple setup
- Easy management
- Lower cost

**Cons:**
- Single point of failure
- Limited scalability

### Multiple Servers (30+ users)

For more than 30 users, consider:

```
Load Balancer (DNS Round Robin or HAProxy)
        │
        ├─→ Hysteria Server 1 (15 users)
        ├─→ Hysteria Server 2 (15 users)
        └─→ Hysteria Server 3 (15 users)
```

**Implementation:**
- DNS-based: Create multiple A records
- HAProxy: Layer 4 UDP load balancing
- GeoDNS: Route users to nearest server

## Monitoring Architecture

### Metrics to Monitor

1. **Server Health**
   - CPU usage < 80%
   - Memory usage < 80%
   - Disk usage < 80%
   - Network saturation

2. **Service Health**
   - Hysteria process running
   - Port 443/UDP listening
   - TLS certificate validity

3. **User Metrics**
   - Active connections
   - Per-user bandwidth
   - Authentication failures
   - Connection errors

### Monitoring Stack

```
┌──────────────────────────────────────┐
│ Hysteria Server                      │
│ ├─ Traffic Stats API (port 8080)    │
│ ├─ System metrics                   │
│ └─ Application logs                 │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│ monitor │         │  System │
│  .py    │         │  Tools  │
│ script  │         │ (htop,  │
│         │         │  iftop) │
└─────────┘         └─────────┘
```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | 70% | 90% |
| Memory Usage | 75% | 90% |
| Disk Usage | 80% | 95% |
| Network Errors | 1% | 5% |
| Service Down | - | Immediate |

## Disaster Recovery

### Backup Strategy

**What to Backup:**
1. Configuration file (`/etc/hysteria/config.yaml`)
2. TLS certificates (if not using ACME)
3. User list and passwords
4. Server access credentials

**Backup Frequency:**
- Configuration: After each change
- Certificates: Weekly
- Full backup: Daily

**Backup Storage:**
- Encrypted cloud storage
- Separate server
- Local encrypted USB drive

### Recovery Procedure

**Server Failure:**
1. Provision new server (10 minutes)
2. Install Hysteria (5 minutes)
3. Restore configuration (2 minutes)
4. Update DNS if IP changed (5-60 minutes)
5. Notify users if needed

**Total Recovery Time:** ~30 minutes (excluding DNS propagation)

## Cost Analysis

### Monthly Operating Costs (30 Users)

| Item | Cost (USD) |
|------|------------|
| Server (2GB RAM, 2vCPU) | $15-20 |
| Domain name (annual ÷ 12) | $1-2 |
| Bandwidth overage (if any) | $0-10 |
| **Total** | **$16-32/month** |

**Per User Cost:** $0.53 - $1.07/month

### Cost Optimization

1. **Choose the right provider**: Hetzner/Vultr offer better value
2. **Use included bandwidth**: Avoid overage charges
3. **Share costs**: Pass costs to users ($2-5/user/month)
4. **Annual payment**: Often 10-20% discount

## Performance Optimization

### Network Optimization

```bash
# Add to /etc/sysctl.conf
net.core.rmem_max=134217728
net.core.wmem_max=134217728
net.ipv4.tcp_rmem=4096 87380 67108864
net.ipv4.tcp_wmem=4096 65536 67108864
net.core.netdev_max_backlog=5000
net.ipv4.tcp_congestion_control=bbr

# Apply
sysctl -p
```

### Process Limits

```bash
# Add to /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
```

### QUIC Optimization

In `server-config.yaml`:
```yaml
quic:
  initStreamReceiveWindow: 16777216    # 16MB for high-speed
  maxStreamReceiveWindow: 16777216
  initConnReceiveWindow: 41943040      # 40MB for multiple streams
  maxConnReceiveWindow: 41943040
  maxIncomingStreams: 1024             # High concurrency
  disablePathMTUDiscovery: false       # Auto-optimize packet size
```

## Geographic Considerations

### Server Location Selection

**Factors to consider:**
1. **Latency to users**: <100ms ideal
2. **Content access**: Location of services users want to access
3. **Legal/Political**: Favorable privacy laws
4. **Network quality**: Tier 1 transit, low packet loss

**Recommended Locations:**
- **For US users**: US East (Virginia) or US West (California)
- **For EU users**: Germany, Netherlands, or UK
- **For Asia users**: Singapore or Japan
- **For global users**: Multiple servers in different regions

### Multi-Region Setup

For users in different continents:

```
North America        Europe           Asia
     │                 │               │
     ▼                 ▼               ▼
  Server 1          Server 2       Server 3
  (US East)       (Frankfurt)    (Singapore)
     │                 │               │
     └─────────────────┴───────────────┘
              GeoDNS Routing
         (vpn.yourdomain.com)
```

## Compliance and Legal

### Data Retention

**Recommended policy:**
- Keep minimal logs (errors only)
- Rotate logs daily
- No long-term storage of user activity
- Document retention policy

### Terms of Service

Include in user agreement:
- Acceptable use policy
- No illegal activities
- No bandwidth abuse
- No account sharing
- Privacy policy
- Data handling

### Privacy Considerations

- Don't log destination addresses
- Don't log request contents
- Use encrypted backups
- Minimize stored credentials
- Clear logs regularly

## Scalability Path

### Growth Stages

**Stage 1: 1-30 users**
- Single server
- Basic monitoring
- Manual user management

**Stage 2: 30-100 users**
- Upgrade server resources
- Automated monitoring
- Consider load balancing

**Stage 3: 100+ users**
- Multiple servers
- Geographic distribution
- Automated provisioning
- Advanced monitoring/alerting
- Customer support system

## Conclusion

This architecture supports 20-30 users with:
- ✅ High performance (>90% line speed)
- ✅ Strong security (multiple layers)
- ✅ Easy management (scripts and monitoring)
- ✅ Low cost ($15-30/month)
- ✅ High reliability (99%+ uptime possible)

For questions or improvements, refer to the [Deployment Guide](DEPLOYMENT_GUIDE.md) or [Quick Start](QUICK_START.md).
