#!/usr/bin/env python3
"""
Hysteria 2 VPN Server Monitoring Script

This script monitors the Hysteria server and displays:
- Server status
- Active connections
- Per-user traffic statistics
- System resource usage
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found.")
    print("Install it with: pip3 install requests")
    sys.exit(1)

# Configuration
TRAFFIC_STATS_URL = "http://127.0.0.1:8080"
TRAFFIC_STATS_SECRET = "YOUR_SECRET_HERE"  # Update this!

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def format_bytes(bytes_value: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def format_bandwidth(bytes_per_sec: float) -> str:
    """Convert bytes per second to human-readable format"""
    bits_per_sec = bytes_per_sec * 8
    for unit in ['bps', 'Kbps', 'Mbps', 'Gbps']:
        if bits_per_sec < 1000.0:
            return f"{bits_per_sec:.2f} {unit}"
        bits_per_sec /= 1000.0
    return f"{bits_per_sec:.2f} Tbps"

def check_service_status() -> Dict[str, any]:
    """Check if Hysteria service is running"""
    status = {
        'running': False,
        'method': None,
        'details': None
    }
    
    # Check systemd
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'hysteria-server'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout.strip() == 'active':
            status['running'] = True
            status['method'] = 'systemd'
            
            # Get service info
            result = subprocess.run(
                ['systemctl', 'status', 'hysteria-server'],
                capture_output=True,
                text=True,
                timeout=5
            )
            status['details'] = result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Check Docker if systemd not found
    if not status['running']:
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=hysteria-server', '--format', '{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                status['running'] = True
                status['method'] = 'docker'
                status['details'] = result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    return status

def get_traffic_stats() -> Optional[Dict]:
    """Fetch traffic statistics from the API"""
    try:
        headers = {'Authorization': TRAFFIC_STATS_SECRET}
        response = requests.get(
            f"{TRAFFIC_STATS_URL}/traffic",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print(f"{Colors.FAIL}Error: Invalid traffic stats secret{Colors.ENDC}")
            return None
        else:
            print(f"{Colors.FAIL}Error: Failed to get traffic stats (HTTP {response.status_code}){Colors.ENDC}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"{Colors.WARNING}Warning: Cannot connect to traffic stats API{Colors.ENDC}")
        print(f"{Colors.WARNING}Make sure trafficStats is enabled in config and server is running{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}Error fetching traffic stats: {e}{Colors.ENDC}")
        return None

def get_system_stats() -> Dict:
    """Get system resource usage"""
    stats = {}
    
    # CPU usage
    try:
        result = subprocess.run(
            ['top', '-bn1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result.stdout.split('\n'):
            if 'Cpu' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'id,':
                        idle = float(parts[i-1])
                        stats['cpu_usage'] = 100 - idle
                        break
    except:
        stats['cpu_usage'] = None
    
    # Memory usage
    try:
        result = subprocess.run(
            ['free', '-m'],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            stats['memory_total'] = total
            stats['memory_used'] = used
            stats['memory_percent'] = (used / total) * 100
    except:
        stats['memory_total'] = None
        stats['memory_used'] = None
        stats['memory_percent'] = None
    
    # Network connections
    try:
        result = subprocess.run(
            ['ss', '-tuln'],
            capture_output=True,
            text=True,
            timeout=5
        )
        connections = len([l for l in result.stdout.split('\n') if ':443' in l])
        stats['connections'] = connections
    except:
        stats['connections'] = None
    
    return stats

def print_header():
    """Print monitoring header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'Hysteria 2 VPN Server Monitor':^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_service_status(status: Dict):
    """Print service status"""
    print(f"{Colors.BOLD}Service Status:{Colors.ENDC}")
    
    if status['running']:
        print(f"  Status: {Colors.OKGREEN}✓ Running{Colors.ENDC}")
        print(f"  Method: {status['method']}")
    else:
        print(f"  Status: {Colors.FAIL}✗ Not Running{Colors.ENDC}")
    print()

def print_system_stats(stats: Dict):
    """Print system statistics"""
    print(f"{Colors.BOLD}System Resources:{Colors.ENDC}")
    
    if stats.get('cpu_usage') is not None:
        cpu_color = Colors.OKGREEN if stats['cpu_usage'] < 70 else Colors.WARNING if stats['cpu_usage'] < 90 else Colors.FAIL
        print(f"  CPU Usage: {cpu_color}{stats['cpu_usage']:.1f}%{Colors.ENDC}")
    
    if stats.get('memory_percent') is not None:
        mem_color = Colors.OKGREEN if stats['memory_percent'] < 70 else Colors.WARNING if stats['memory_percent'] < 90 else Colors.FAIL
        print(f"  Memory: {mem_color}{stats['memory_used']}MB / {stats['memory_total']}MB ({stats['memory_percent']:.1f}%){Colors.ENDC}")
    
    if stats.get('connections') is not None:
        print(f"  Port 443 Listeners: {stats['connections']}")
    
    print()

def print_traffic_stats(traffic_data: Dict):
    """Print traffic statistics"""
    print(f"{Colors.BOLD}Traffic Statistics:{Colors.ENDC}")
    
    if not traffic_data:
        print(f"  {Colors.WARNING}No traffic data available{Colors.ENDC}")
        return
    
    # Print per-user stats
    users = traffic_data.get('users', {})
    if not users:
        print(f"  {Colors.WARNING}No active users{Colors.ENDC}")
        return
    
    print(f"\n  {'User':<15} {'TX (Upload)':<20} {'RX (Download)':<20} {'Total':<20} {'Online':<10}")
    print(f"  {'-'*85}")
    
    total_tx = 0
    total_rx = 0
    online_count = 0
    
    for username, stats in sorted(users.items()):
        tx = stats.get('tx', 0)
        rx = stats.get('rx', 0)
        online = stats.get('online', False)
        
        total_tx += tx
        total_rx += rx
        if online:
            online_count += 1
        
        online_str = f"{Colors.OKGREEN}Yes{Colors.ENDC}" if online else "No"
        
        print(f"  {username:<15} {format_bytes(tx):<20} {format_bytes(rx):<20} {format_bytes(tx + rx):<20} {online_str}")
    
    print(f"  {'-'*85}")
    print(f"  {'TOTAL':<15} {format_bytes(total_tx):<20} {format_bytes(total_rx):<20} {format_bytes(total_tx + total_rx):<20} {f'{online_count} online'}")
    print()

def print_summary(traffic_data: Optional[Dict], system_stats: Dict):
    """Print summary statistics"""
    print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
    
    if traffic_data and 'users' in traffic_data:
        total_users = len(traffic_data['users'])
        online_users = sum(1 for stats in traffic_data['users'].values() if stats.get('online', False))
        print(f"  Total Users: {total_users}")
        print(f"  Online Users: {Colors.OKGREEN}{online_users}{Colors.ENDC}")
    
    print(f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def monitor_once():
    """Run monitoring once and display results"""
    print_header()
    
    # Check service status
    service_status = check_service_status()
    print_service_status(service_status)
    
    if not service_status['running']:
        print(f"{Colors.WARNING}Server is not running. Start it with:{Colors.ENDC}")
        print(f"  systemctl start hysteria-server")
        print(f"  or")
        print(f"  docker start hysteria-server")
        return
    
    # Get system stats
    system_stats = get_system_stats()
    print_system_stats(system_stats)
    
    # Get traffic stats
    traffic_data = get_traffic_stats()
    print_traffic_stats(traffic_data)
    
    # Print summary
    print_summary(traffic_data, system_stats)

def monitor_continuous(interval: int = 5):
    """Continuously monitor and update display"""
    try:
        while True:
            # Clear screen
            subprocess.run(['clear'], shell=True)
            
            # Display stats
            monitor_once()
            
            # Wait for next update
            print(f"{Colors.OKCYAN}Updating every {interval} seconds... (Press Ctrl+C to exit){Colors.ENDC}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.OKGREEN}Monitoring stopped.{Colors.ENDC}\n")

def main():
    """Main function"""
    import argparse
    
    # Declare globals at the beginning
    global TRAFFIC_STATS_URL, TRAFFIC_STATS_SECRET
    
    parser = argparse.ArgumentParser(
        description='Monitor Hysteria 2 VPN Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # One-time monitoring
  %(prog)s -w                 # Continuous monitoring (5 sec interval)
  %(prog)s -w -i 10           # Continuous monitoring (10 sec interval)
  %(prog)s --secret "ABC123"  # Use custom traffic stats secret

Configuration:
  Edit this script and update TRAFFIC_STATS_SECRET with your actual secret.
        """
    )
    
    parser.add_argument(
        '-w', '--watch',
        action='store_true',
        help='Continuously monitor and update display'
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=5,
        help='Update interval in seconds (default: 5)'
    )
    
    parser.add_argument(
        '--secret',
        type=str,
        help='Traffic stats API secret (overrides script default)'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default=TRAFFIC_STATS_URL,
        help=f'Traffic stats API URL (default: {TRAFFIC_STATS_URL})'
    )
    
    args = parser.parse_args()
    
    # Override configuration if provided
    if args.secret:
        TRAFFIC_STATS_SECRET = args.secret
    if args.url:
        TRAFFIC_STATS_URL = args.url
    
    # Check if secret needs to be updated
    if TRAFFIC_STATS_SECRET == "YOUR_SECRET_HERE":
        print(f"{Colors.WARNING}Warning: Using default secret. Update TRAFFIC_STATS_SECRET in the script{Colors.ENDC}")
        print(f"{Colors.WARNING}or use --secret option.{Colors.ENDC}\n")
    
    # Run monitoring
    if args.watch:
        monitor_continuous(args.interval)
    else:
        monitor_once()

if __name__ == '__main__':
    main()
