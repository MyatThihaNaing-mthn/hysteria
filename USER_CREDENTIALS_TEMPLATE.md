# Hysteria 2 VPN - User Credentials Template
# 
# Use this template to provide credentials to your users.
# Replace the placeholders with actual values from your server configuration.

================================================================================
                    Hysteria 2 VPN Connection Details
================================================================================

SERVER INFORMATION
------------------
Server Address: your-domain.com:443
Server Location: [Your Server Location, e.g., "United States - New York"]
Server Provider: [Your Organization/Name]

USER CREDENTIALS
----------------
Username: [USERNAME]
Password: [PASSWORD]

IMPORTANT NOTES
---------------
- Keep your credentials secure and do not share them with others
- Your username is case-insensitive
- Contact your administrator if you forget your password
- Report any connection issues immediately

================================================================================
                        CLIENT CONFIGURATION
================================================================================

QUICK SETUP (GUI CLIENTS)
--------------------------
1. Download Hysteria 2 client for your platform:
   - Windows: https://v2.hysteria.network/docs/getting-started/Installation/#windows
   - macOS: https://v2.hysteria.network/docs/getting-started/Installation/#macos
   - Android: https://v2.hysteria.network/docs/getting-started/Installation/#android
   - iOS: Use compatible apps like Shadowrocket or Stash

2. Import using these settings:
   - Server: your-domain.com:443
   - Username: [USERNAME]
   - Password: [PASSWORD]
   - Obfuscation: Salamander
   - Obfuscation Password: [OBFUSCATION_PASSWORD]

ADVANCED SETUP (Configuration File)
------------------------------------
Create a file named 'config.yaml' with the following content:

```yaml
# Server address
server: your-domain.com:443

# Authentication
auth: [USERNAME]:[PASSWORD]

# Bandwidth settings (adjust based on your connection)
bandwidth:
  up: 100 mbps    # Your upload speed
  down: 100 mbps  # Your download speed

# Obfuscation (important for bypassing censorship)
obfs:
  type: salamander
  salamander:
    password: [OBFUSCATION_PASSWORD]

# SOCKS5 proxy (for apps that support SOCKS5)
socks5:
  listen: 127.0.0.1:1080

# HTTP proxy (for apps that support HTTP proxy)
http:
  listen: 127.0.0.1:8080

# Optional: Faster connection establishment
fastOpen: true

# Optional: Enable lazy mode (reduces latency)
lazy: false
```

Then run:
```bash
hysteria client -c config.yaml
```

PROXY SETTINGS
--------------
After starting the client, configure your applications to use:

- SOCKS5 Proxy: 127.0.0.1:1080
- HTTP Proxy: 127.0.0.1:8080

For system-wide proxy:
- Windows: Settings → Network & Internet → Proxy
- macOS: System Preferences → Network → Advanced → Proxies
- Linux: Settings → Network → Network Proxy

BROWSER CONFIGURATION
---------------------
- Firefox: Settings → Network Settings → Manual proxy configuration
  - SOCKS Host: 127.0.0.1, Port: 1080
  - Check "Proxy DNS when using SOCKS v5"
  
- Chrome/Edge: Use proxy extensions like SwitchyOmega
  - Protocol: SOCKS5
  - Server: 127.0.0.1
  - Port: 1080

MOBILE SETUP
------------
Android (Using Clash/Surfboard):
1. Download Clash for Android or Surfboard
2. Import the configuration using the profile URL or manual config
3. Enable VPN connection

iOS (Using Shadowrocket/Stash):
1. Download Shadowrocket or Stash from App Store
2. Add server manually:
   - Type: Hysteria 2
   - Server: your-domain.com
   - Port: 443
   - Username: [USERNAME]
   - Password: [PASSWORD]
   - Obfuscation: Salamander
   - Obfs Password: [OBFUSCATION_PASSWORD]
3. Connect

================================================================================
                        TROUBLESHOOTING
================================================================================

CONNECTION FAILED
-----------------
1. Verify your credentials are correct
2. Check your internet connection
3. Ensure port 443/UDP is not blocked by your firewall
4. Try disabling antivirus temporarily
5. Contact administrator if problem persists

SLOW CONNECTION
---------------
1. Adjust bandwidth settings in client config
2. Try a different server location (if available)
3. Check your local network congestion
4. Restart the client application

CLIENT NOT CONNECTING
---------------------
1. Update to the latest client version
2. Verify server address and port
3. Check if obfuscation password matches
4. Review client logs for errors

WEBSITES NOT LOADING
--------------------
1. Check proxy settings are correct
2. Verify VPN is connected
3. Try changing DNS settings
4. Clear browser cache

GET HELP
--------
Contact your VPN administrator:
- Email: [ADMIN_EMAIL]
- Support Portal: [SUPPORT_URL]
- Emergency Contact: [EMERGENCY_CONTACT]

================================================================================
                        SPEED TEST
================================================================================

Test your connection speed:
1. Connect to the VPN
2. Visit: https://fast.com or https://speedtest.net
3. Compare with your base internet speed
4. Report significant degradation to administrator

Expected performance: 80-95% of your base internet speed

================================================================================
                        SECURITY REMINDERS
================================================================================

✓ Always keep your client software up to date
✓ Use strong, unique passwords
✓ Do not share your credentials
✓ Enable two-factor authentication if available
✓ Report any suspicious activity
✓ Regularly check for client updates
✓ Be aware of phishing attempts

================================================================================
                        ACCEPTABLE USE POLICY
================================================================================

By using this VPN service, you agree to:
- Use the service legally and responsibly
- Not engage in illegal activities
- Not share your account with others
- Not attempt to bypass security measures
- Respect bandwidth limits and fair usage
- Report security vulnerabilities

Violation of these terms may result in account suspension or termination.

================================================================================
                        ADDITIONAL RESOURCES
================================================================================

Official Documentation: https://v2.hysteria.network/
Client Downloads: https://v2.hysteria.network/docs/getting-started/Installation/
Community Support: https://t.me/hysteria_github
FAQ: https://v2.hysteria.network/docs/FAQ/

================================================================================
Last Updated: [DATE]
Configuration Version: 1.0
================================================================================
